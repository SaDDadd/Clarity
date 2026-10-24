from core.exceptions import AppException, ConflictException, LackOfInformationException, NotFoundException
from repositories.user_repository import UserRepository
from repositories.project_repository import ProjectRepository
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserResponse
from core.security import async_hash_password
from cache.cache_keys import (user_key, user_cache_patterns, project_key,
                              project_tasks_key, project_invitations_key,
                              PROJECT_PREFIX)
from cache.cache_service import (delete_cache, delete_cache_by_pattern)


async def update_user_username(db: AsyncSession, username: str, current_user_id: int) -> dict:
    """Изменить имя пользователя."""
    repo = UserRepository(db)
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


async def update_user_email(db: AsyncSession, email: str, current_user_id: int) -> dict:
    """Изменить email пользователя."""
    repo = UserRepository(db)
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


async def update_user_password(db: AsyncSession, password: str, current_user_id: int) -> dict:
    """Изменить пароль пользователя."""
    repo = UserRepository(db)
    if len(password) < 8 or len(password) > 50:
        raise LackOfInformationException('Пароль не может быть пустым или превышать 50 символов!')
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
    user = await repo.get_by_id(current_user_id)
    if user is None:
        raise NotFoundException('Пользователь не найден!')
    admin_projects = await repo_project.get_projects_by_creator(current_user_id)
    member_projects = await repo_project.get_user_projects(current_user_id)
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
    for project in admin_projects:
        await delete_cache(project_key(project.project_id))
        await delete_cache(project_tasks_key(project.project_id))
        await delete_cache(project_invitations_key(project.project_id, 'admin'))
        await delete_cache_by_pattern(f"{PROJECT_PREFIX}:{project.project_id}:task*")
    for project in member_projects:
        await delete_cache(project_key(project.project_id))
        await delete_cache(project_tasks_key(project.project_id))
        await delete_cache(project_invitations_key(project.project_id, 'admin'))
        await delete_cache_by_pattern(f"{PROJECT_PREFIX}:{project.project_id}:task*")
    for pattern in user_cache_patterns(current_user_id):
        await delete_cache_by_pattern(pattern)
    return {'message': 'Профиль удален!'}