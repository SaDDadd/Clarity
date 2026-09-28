from core.exceptions import ConflictException, LackOfInformationException, NotFoundException
from repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession 
from models.user import UserModel


async def update_user_username(db: AsyncSession, username: str, current_user_id: int) -> dict:
    """Обновляет имя пользователя."""
    repo = UserRepository(db)
    if len(username) == 0 or len(username) > 50:
        raise LackOfInformationException('Имя не может быть пустым или превышать 50 символов!')
    if await repo.check_user_exists_by_username_excluding_current(username, current_user_id):
        raise ConflictException('Пользователь с таким именем уже существует!')
    if await repo.update_username(current_user_id, username):
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
        return {'message': 'Email пользователя обновлено!'}
    else:
        raise NotFoundException('Пользователь не найден!')

async def update_user_password(db: AsyncSession, password: str, current_user_id: int) -> dict:
    """Обновление пароля пользователя"""
    repo = UserRepository(db)
    if len(password) < 8 or len(password) > 100:
        raise LackOfInformationException('Пароль не может быть пустым или превышать 100 символов!')
    if await repo.update_password(current_user_id, password):
        return {'message': 'Пароль пользователя обновлен!'}
    else:
        raise NotFoundException('Пользователь не найден!')

async def search_by_username(db: AsyncSession, search_user: str, current_user_username: str) -> UserModel | dict:
    """Запрос пользователя на поиск другого пользователя"""
    repo = UserRepository(db)
    if len(search_user) == 0:
        raise NotFoundException('Нельзя найти пользователя, введите ник!')
    if search_user == current_user_username:
        return {'message': ''}
    user = await repo.search_by_username(search_user)
    if user:
        return user
    else:
        raise NotFoundException('Пользователь не найден!')