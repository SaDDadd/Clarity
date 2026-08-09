from sqlalchemy import select, update 
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import verify_password
from models.user import UserModel


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Создать пользователя
    async def create_user(self, username: str, email: str, password_hash: str) -> UserModel:
        user = UserModel(username=username, email=email, password_hash=password_hash)
        self.session.add(user)
        await self.session.commit()
        return user

    # Получить пользователя по ID
    async def get_by_id(self, user_id: int) -> UserModel | None:
        result = await self.session.execute(select(UserModel).where(UserModel.user_id == user_id))
        if result:
            user = result.scalar_one_or_none()
            return user
        return None

    # Получить пользователя по имени
    async def get_by_username(self, username: str) -> UserModel | None:
        result = await self.session.execute(select(UserModel).where(UserModel.username == username))
        user = result.scalar_one_or_none()
        return user

    # Получить пользователя по email
    async def get_by_email(self, email: str) -> UserModel | None:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        user = result.scalar_one_or_none()
        return user

    # Проверить существование пользователя по ID
    async def check_user_exists(self, user_id: int) -> bool:
        result = await self.session.execute(select(UserModel).where(UserModel.user_id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            return False
        return True

    # Проверить существование пользователя по имени
    async def check_user_exists_by_username(self, username: str) -> bool:
        result = await self.session.execute(select(UserModel).where(UserModel.username == username))
        user = result.scalar_one_or_none()
        if user is None:
            return False
        return True

    # Проверить существование пользователя по email
    async def check_user_exists_by_email(self, email: str) -> bool:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        user = result.scalar_one_or_none()
        if user is None:
            return False
        return True

    # Проверить пароль по email
    async def check_user_correct_password_by_email(self, email: str, password: str) -> bool:
        user = await self.get_by_email(email)
        if user:
            if verify_password(password, user.password_hash):
                return True
            return False
        return False

    # Проверить пароль по имени
    async def check_user_correct_password_by_username(self, username: str, password: str) -> bool:
        user = await self.get_by_username(username)
        if user:
            if verify_password(password, user.password_hash):
                return True
            return False
        return False

    # Обновить имя пользователя 
    async def update_username(self, current_user_id: int, username: str) -> bool:
        task = await self.session.execute(update(UserModel).values(username=username).where(UserModel.user_id == current_user_id))
        numb_result = task.rowcount
        await self.session.commit()
        if numb_result == 0:
            return False
        else:
            return True

    # Обновить email пользователя
    async def update_email(self, current_user_id: int, email: str) -> bool:
        task = await self.session.execute(update(UserModel).values(email=email).where(UserModel.user_id == current_user_id))
        numb_result = task.rowcount
        await self.session.commit()
        if numb_result == 0:
            return False
        else:
            return True
        
    # Удалить пользователя
    async def delete_user(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if user is None:
            return False
        await self.session.delete(user)
        await self.session.commit()
        return True