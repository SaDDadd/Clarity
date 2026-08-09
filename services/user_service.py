from core.exceptions import 
from repositories.user_repository import UserRepository

async def update_user_username(db, username: str, current_user_id: int):
    repo = UserRepository(db)
    if len(username) == 0 or len(username) > 50:
        raise
    if repo.update_username(current_user_id, username):
        return {'message': 'Имя пользователя обновлено!'}
    else:
        raise

async def update_user_email(db, email: str, current_user_id: int):
    repo = UserRepository(db)
    if len(email) == 0 or len(email) > 100:
        raise
    if repo.update_email(current_user_id, email):
        return {'message': 'Email пользователя обновлено!'}
    else:
        raise