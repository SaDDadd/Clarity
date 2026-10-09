from core.exceptions import ConflictException, LackOfInformationException, NotFoundException, AppException
from repositories.user_repository import UserRepository
from repositories.project_repository import ProjectRepository
from sqlalchemy.ext.asyncio import AsyncSession 
from schemas.user import UserResponse
from core.security import async_hash_password
from cache.cache_keys import user_key, user_cache_patterns
from cache.cache_service import delete_cache


async def update_user_username(db: AsyncSession, username: str, current_user_id: int) -> dict:
    """Обновляет имя пользователя."""
    repo = UserRepository(db)
    if len(username) == 0 or len(username) > 50:
        raise LackOfInformationException('Имя не может быть пустым или превышать 50 символов!')
    if await repo.check_user_exists_by_username_excluding_current(username, current_user_id):
        raise ConflictException('Пользователь с таким именем уже существует!')
    if await repo.update_username(current_user_id, username):
        await delete_cache(user_key(current_user_id))
        return {'message': 'Имя пользователя обновлено!'}
    else:
        raise NotFoundException('Пользователь не найден!')

async def update_user_email(db: AsyncSession, email: str, current_user_id: int) -> dict:
    """Обновляет email пользователя."""
    repo = UserRepository(db)
    if len(email) == 0 or len(email) > 100:
        raise LackOfInformationException('Email не может быть пустым или превышать 100 символов!')
    if await repo.check_user_exists_by_email_excluding_current(email, current_user_id):
        raise ConflictException('Пользователь с таким email уже существует!')
    if await repo.update_email(current_user_id, email):
        await delete_cache(user_key(current_user_id))
        return {'message': 'Email пользователя обновлено!'}
    else:
        raise NotFoundException('Пользователь не найден!')

async def update_user_password(db: AsyncSession, password: str, current_user_id: int) -> dict:
    """Обновление пароля пользователя"""
    repo = UserRepository(db)
    if len(password) < 8 or len(password) > 100:
        raise LackOfInformationException('Пароль не может быть пустым или превышать 100 символов!')
    hashed_password = await async_hash_password(password)
    if await repo.update_password(current_user_id, hashed_password):
        await delete_cache(user_key(current_user_id))
        return {'message': 'Пароль пользователя обновлен!'}
    else:
        raise NotFoundException('Пользователь не найден!')

async def search_by_username(db: AsyncSession, search_user: str, current_user_username: str) -> list[UserResponse]:
    """Запрос пользователя на поиск другого пользователя"""
    repo = UserRepository(db)
    if len(search_user) == 0:
        raise NotFoundException('Нельзя найти пользователя, введите ник!')
    if search_user == current_user_username:
        raise ConflictException('Нельзя искать самого себя!')
    user = await repo.search_by_username(search_user)
    if user:
        return user
    else:
        raise NotFoundException('Пользователь не найден!')

async def delete_profile(db: AsyncSession, current_user_id: int) -> dict:
    """Удаление профиля пользователя"""
    repo = UserRepository(db)
    repo_project = ProjectRepository(db)
    user_projects = await repo_project.get_projects_by_admin(current_user_id)
    user = await repo.get_by_id(current_user_id)
    if user is None:
        raise NotFoundException('Пользователь не найден!')
    for project in user_projects:
        count_admins = await repo_project.get_admins_list(project.project_id)
        if len(count_admins) == 1:
            count_members = await repo_project.get_number_members(project.project_id)
            if count_members == 0:
                await repo_project.delete_project(project.project_id)
            else:
                await repo_project.automatically_assign_admin(project.project_id, current_user_id)
    if await repo.delete_user(current_user_id) is True:
        await delete_cache(user_cache_patterns(current_user_id))
        return {'message': 'Профиль удален!'}
    else:
        raise AppException(500, 'Не удалось удалить проект')