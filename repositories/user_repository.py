from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import async_verify_password
from models.user import UserModel
from schemas.user import UserResponse


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(self, username: str, email: str, password_hash: str) -> UserModel:
        """Создать пользователя."""
        user = UserModel(username=username, email=email, password_hash=password_hash)
        self.session.add(user)
        await self.session.commit()
        return user

    async def get_by_id(self, user_id: int) -> UserModel | None:
        """Получить пользователя по ID."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> UserModel | None:
        """Получить пользователя по имени."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        user = result.scalar_one_or_none()
        return user

    async def get_by_email(self, email: str) -> UserModel | None:
        """Получить пользователя по email."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        user = result.scalar_one_or_none()
        return user

    async def check_user_exists(self, user_id: int) -> bool:
        """Проверить существование пользователя по ID."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return False
        return True

    async def check_user_exists_by_username(self, username: str) -> bool:
        """Проверить существование пользователя по имени."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return False
        return True

    async def check_user_exists_by_email(self, email: str) -> bool:
        """Проверить существование пользователя по email."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return False
        return True

    async def check_user_correct_password_by_email(self, email: str, password: str) -> bool:
        """Проверить пароль по email."""
        user = await self.get_by_email(email)
        if user:
            if async_verify_password(password, user.password_hash):
                return True
            return False
        return False

    async def check_user_exists_by_username_excluding_current(self, username: str, user_id: int) -> bool:
        """Проверяет, существует ли другой пользователь с таким же именем."""
        result = await self.session.execute(
            select(UserModel).where(
                UserModel.username == username,
                UserModel.user_id != user_id,
            )
        )
        user = result.scalar_one_or_none()
        return user is not None

    async def check_user_exists_by_email_excluding_current(self, email: str, user_id: int) -> bool:
        """Проверяет, существует ли другой пользователь с таким же email."""
        result = await self.session.execute(
            select(UserModel).where(
                UserModel.email == email,
                UserModel.user_id != user_id,
            )
        )
        user = result.scalar_one_or_none()
        return user is not None

    async def update_username(self, current_user_id: int, username: str) -> bool:
        """Обновить имя пользователя."""
        task = await self.session.execute(
            update(UserModel)
            .values(username=username)
            .where(UserModel.user_id == current_user_id)
        )
        numb_result = task.rowcount
        await self.session.commit()
        if numb_result == 0:
            return False
        else:
            return True

    async def update_email(self, current_user_id: int, email: str) -> bool:
        """Обновить email пользователя."""
        task = await self.session.execute(
            update(UserModel)
            .values(email=email)
            .where(UserModel.user_id == current_user_id)
        )
        numb_result = task.rowcount
        await self.session.commit()
        if numb_result == 0:
            return False
        else:
            return True

    async def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя."""
        user = await self.get_by_id(user_id)
        if user is None:
            return False
        await self.session.delete(user)
        await self.session.commit()
        return True

    async def update_password(self, user_id: int, password: str) -> bool:
        """Обновить пароль пользователя."""
        task = await self.session.execute(
            update(UserModel)
            .values(password_hash=password)
            .where(UserModel.user_id == user_id)
        )
        numb_result = task.rowcount
        await self.session.commit()
        if numb_result == 0:
            return False
        else:
            return True

    async def search_by_username(self, username: str) -> list[UserResponse] | None:
        """Поиск пользователей по имени."""
        task = await self.session.execute(
            select(
                UserModel.user_id,
                UserModel.email,
                UserModel.username,
                UserModel.created_date,
            ).where(UserModel.username.ilike(f"%{username}%"))
        )
        return [task.all()]