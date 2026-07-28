from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import UserModel
from core.security import hash_password, verify_password

# Переписать под SQLAlchemy

class UserRepository:
    def __init__(self, session: AsyncSession) -> None: # Инициализация с подключением к БД
        self.session = session

    async def create_user(self, username: str, email: str, password: str) -> UserModel: # Создать 
        # пользователя
        hashed_password = hash_password(password)
        user = UserModel(username=username, email=email, password_hash=hashed_password)
        self.session.add(user)
        await self.session.commit()
        return user

    async def get_by_id(self, user_id: int) -> UserModel | None: # Получить пользователя по ID
        result = await self.session.execute(select(UserModel).where(UserModel.user_id == user_id))
        if result:
            user = result.scalar_one_or_none()
            return user
        return None

    async def get_by_username(self, username: str) -> UserModel | None: # Получить пользователя по имени
        result = await self.session.execute(select(UserModel).where(UserModel.username == username))
        user = result.scalar_one_or_none()
        return user
       

    async def get_by_email(self, email: str) -> UserModel | None: # Получить пользователя по email
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        user = result.scalar_one_or_none()
        return user

    async def delete_user(self, user_id: int) -> bool: # Удалить пользователя
        user = await self.get_by_id(user_id)
        if user is None:
            return False
        await self.session.delete(user)
        await self.session.commit()
        return True

    async def check_user_exists(self, user_id: int) -> bool: # Проверить существование 
        # пользователя по ID
        result = await self.session.execute(select(UserModel).where(UserModel.user_id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            return False
        return True

    async def check_user_exists_by_username(self, username: str) -> bool: # Проверить 
        # существование пользователя по имени
        result = await self.session.execute(select(UserModel).where(UserModel.username == username))
        user = result.scalar_one_or_none()
        if user is None:
            return False
        return True

    async def check_user_exists_by_email(self, email: str) -> bool: # Проверить существование 
        # пользователя по email
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        user = result.scalar_one_or_none()
        if user is None:
            return False
        return True

    async def check_user_correct_password_by_email(self, email: str, password: str) -> bool: # Проверить 
        # пароль по email
        user = await self.get_by_email(email)
        if user:
            if verify_password(password, user.password_hash):
                return True
            return False
        return False
            
    
    async def check_user_correct_password_by_username(self, username: str, password: str) -> bool: 
        # Проверить пароль по имени
        user = await self.get_by_username(username)
        if user:
            if verify_password(password, user.password_hash):
                return True
            return False
        return False