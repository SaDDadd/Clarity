from core.exceptions import ConflictException, LackOfInformationException, NotFoundException
from repositories.user_repository import UserRepository


async def update_user_username(db, username: str, current_user_id: int) -> dict:
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


async def update_user_email(db, email: str, current_user_id: int) -> dict:
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