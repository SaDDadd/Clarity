from core.exceptions import ConflictException, LackOfInformationException, NotFoundException
from repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession 
from schemas.user import UserResponse
from core.security import async_hash_password
from cache.cache_keys import user_key
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