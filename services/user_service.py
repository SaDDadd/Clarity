from core.exceptions import AppException, ConflictException, LackOfInformationException, NotFoundException
from repositories.user_repository import UserRepository
from repositories.project_repository import ProjectRepository
from repositories.project_invitation_repository import ProjectInvitationRepository
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import (UserResponse, UpdateUsernameRequest, UpdateEmailRequest, 
                          UpdatePasswordRequest, UserSearchResponse)
from models.user import UserModel
from core.security import async_hash_password
from cache.cache_keys import (user_key, user_all_pattern, user_projects_pattern,
                              user_invitations_pattern, project_all_pattern, TTL_USER)
from cache.cache_service import (set_cache, get_cache, delete_cache, delete_cache_by_pattern)


async def update_user_username(db: AsyncSession, user_data: UpdateUsernameRequest, current_user_id: int) -> dict:
    """Изменить имя пользователя."""
    repo = UserRepository(db)
    update_data = user_data.model_dump(exclude_unset=True)
    if not update_data or update_data.get('username') is None:
        raise LackOfInformationException('Не указано новое имя пользователя!')
    username = update_data['username'].strip()
    if len(username) == 0 or len(username) > 50:
        raise LackOfInformationException('Имя не может быть пустым или превышать 50 символов!')
    if await repo.check_user_exists_by_username_excluding_current(username, current_user_id):
        raise ConflictException('Пользователь с таким именем уже существует!')
    try:
        await repo.update_username(current_user_id, username)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось изменить имя пользователя!')
    await delete_cache(user_key(current_user_id))
    return {'message': 'Имя пользователя обновлено!'}


async def update_user_email(db: AsyncSession, user_data: UpdateEmailRequest, current_user_id: int) -> dict:
    """Изменить email пользователя."""
    repo = UserRepository(db)
    update_data = user_data.model_dump(exclude_unset=True)
    if not update_data or update_data.get('email') is None:
        raise LackOfInformationException('Не указан новый email!')
    email = str(update_data['email'])
    if len(email) == 0 or len(email) > 100:
        raise LackOfInformationException('Email не может быть пустым или превышать 100 символов!')
    if await repo.check_user_exists_by_email_excluding_current(email, current_user_id):
        raise ConflictException('Пользователь с таким email уже существует!')
    try:
        await repo.update_email(current_user_id, email)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось изменить email!')
    await delete_cache(user_key(current_user_id))
    return {'message': 'Email пользователя обновлено!'}


async def update_user_password(db: AsyncSession, user_data: UpdatePasswordRequest, current_user_id: int) -> dict:
    """Изменить пароль пользователя."""
    repo = UserRepository(db)
    update_data = user_data.model_dump(exclude_unset=True)
    if not update_data or update_data.get('password') is None:
        raise LackOfInformationException('Не указан новый пароль!')
    password = update_data['password']
    if len(password) < 8 or len(password) > 50:
        raise LackOfInformationException('Пароль должен быть от 8 до 50 символов!')
    hashed_password = await async_hash_password(password)
    try:
        await repo.update_password(current_user_id, hashed_password)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось изменить пароль!')
    await delete_cache(user_key(current_user_id))
    return {'message': 'Пароль пользователя обновлен!'}


async def search_by_username(db: AsyncSession, search_user: str, current_user_username: str) -> list[UserSearchResponse]:
    """Поиск пользователя по имени."""
    repo = UserRepository(db)
    if len(search_user) == 0:
        raise NotFoundException('Нельзя найти пользователя, введите ник!')
    if search_user == current_user_username:
        raise ConflictException('Нельзя искать самого себя!')
    user = await repo.search_by_username(search_user)
    if user:
        return user
    raise NotFoundException('Пользователь не найден!')


async def delete_profile(db: AsyncSession, current_user_id: int) -> dict:
    """Удаление профиля пользователя."""
    repo = UserRepository(db)
    repo_project = ProjectRepository(db)
    repo_inv = ProjectInvitationRepository(db)
    user = await repo.get_by_id(current_user_id)
    if user is None:
        raise NotFoundException('Пользователь не найден!')
    admin_projects = await repo_project.get_projects_by_creator(current_user_id)
    member_projects = await repo_project.get_user_projects(current_user_id)
    project_members_map: dict[int, list[int]] = {}
    project_ids: set[int] = set()
    affected_invitee_ids: set[int] = set()
    for project in member_projects:
        project_ids.add(project.project_id)
        info = await repo_project.get_project_all_info(project.project_id)
        project_members_map[project.project_id] = [m.user_id for m in info['members'] if m.user_id != current_user_id]
    for pid in project_ids:
        pending = await repo_inv.get_invitation_for_project(pid)
        affected_invitee_ids.update(inv.invitee_id for inv in pending)
    try:
        for project in admin_projects:
            new_owner_id = await repo_project.automatically_assign_admin(project.project_id, current_user_id)
            if new_owner_id is None:
                await repo_project.delete_project(project.project_id)
        await repo.delete_user(current_user_id)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось удалить профиль!')
    for pid in project_ids:
        await delete_cache_by_pattern(project_all_pattern(pid))
    for members in project_members_map.values():
        for mid in members:
            await delete_cache_by_pattern(user_projects_pattern(mid))
    for iid in affected_invitee_ids:
        await delete_cache_by_pattern(user_invitations_pattern(iid))
    await delete_cache_by_pattern(user_all_pattern(current_user_id))
    return {'message': 'Профиль удален!'}


async def get_profile_info(current_user: UserModel) -> dict:
    """Возвращает данные текущего пользователя."""
    key = user_key(current_user.user_id)
    cached = await get_cache(key)
    if cached is not None:
        return cached
    data = UserResponse.model_validate(current_user).model_dump(mode='json')
    await set_cache(key, data, TTL_USER)
    return data