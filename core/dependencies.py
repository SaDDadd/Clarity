from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from core.database import AsyncSessionLocal
from core.security import decode_access_token
from models.user import UserModel
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer
from repositories.user_repository import UserRepository
from core.exceptions import AuthenticationException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login') # URL эндпоинта логина

async def get_db() -> AsyncGenerator[AsyncSession, None]: # Генератор, создающий сессию БД и закрывающий ее по завершению
    async with AsyncSessionLocal() as session:
        yield session

async def current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(token)
        user_id = payload.get('sub')
        if user_id is None:
            raise AuthenticationException('Недействительный токен')
        # Приводим к int, если пришло строкой
        user_id = int(user_id)
        repo = UserRepository(db)
        user = await repo.get_by_id(user_id)
        if user is None:
            raise AuthenticationException('Пользователь не найден')
        return user
    except (JWSError, ValueError):
        raise AuthenticationException('Недействительный токен')