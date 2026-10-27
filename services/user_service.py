from core.exceptions import AppException, ConflictException, LackOfInformationException, NotFoundException
from repositories.user_repository import UserRepository
from repositories.project_repository import ProjectRepository
from repositories.project_invitation_repository import ProjectInvitationRepository
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserResponse, UpdateUsernameRequest, UpdateEmailRequest, \
        UpdatePasswordRequest
from core.security import async_hash_password
from cache.cache_keys import (user_key, user_cache_patterns, project_key,
                              project_tasks_key, project_invitations_key,
                              user_projects_key, user_invitations_key,
                              project_invitations_pattern, PROJECT_PREFIX)
from cache.cache_service import (delete_cache, delete_cache_by_pattern)


async def update_user_username(db: AsyncSession,  user_data: UpdateUsernameRequest, current_user_id: int) -> dict:
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
        raise AppException(500, 'Не удалось изменить имя пользователя.')
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
        raise AppException(500, 'Не удалось изменить email.')
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
        raise AppException(500, 'Не удалось изменить пароль.')
    await delete_cache(user_key(current_user_id))
    return {'message': 'Пароль пользователя обновлен!'}


async def search_by_username(db: AsyncSession, search_user: str, current_user_username: str) -> list[UserResponse]:
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
    """Удалить профиль пользователя."""
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
        project_members_map[project.project_id] = [
            m.user_id for m in info['members'] if m.user_id != current_user_id
        ]
    for pid in project_ids:
        pending = await repo_inv.get_invitation_for_project(pid)
        for inv in pending:
            affected_invitee_ids.add(inv.invitee_id)
    try:
        for project in admin_projects:
            new_owner_id = await repo_project.automatically_assign_admin(
                project.project_id, current_user_id
            )
            if new_owner_id is None:
                await repo_project.delete_project(project.project_id)
        await repo_project.unassign_all_tasks_from_user(current_user_id)
        await repo.delete_user(current_user_id)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось удалить профиль!')
    for pid in project_ids:
        await delete_cache(project_key(pid))
        await delete_cache(project_tasks_key(pid))
        await delete_cache(project_invitations_key(pid)) 
        await delete_cache_by_pattern(f"{PROJECT_PREFIX}:{pid}:task*")
        await delete_cache_by_pattern(project_invitations_pattern(pid))
    for members in project_members_map.values():
        for mid in members:
            await delete_cache(user_projects_key(mid, 'all'))
            await delete_cache(user_projects_key(mid, 'admin'))
    for iid in affected_invitee_ids:
        await delete_cache(user_invitations_key(iid, 'all'))
    for pattern in user_cache_patterns(current_user_id):
        await delete_cache_by_pattern(pattern)
    return {'message': 'Профиль удален!'}