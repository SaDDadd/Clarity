from typing import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from core.exceptions import AuthenticationException
from core.security import decode_access_token as decode_token
from models.user import UserModel
from repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def current_user(token: str = Depends(oauth2_scheme),
                       db: AsyncSession = Depends(get_db)) -> UserModel:
    try:
        print(f"[DEBUG] Received token: {token[:20]}...")
        payload = decode_token(token)
        print(f"[DEBUG] Decoded payload: {payload}")
        user_id = payload.get('sub')
        if user_id is None:
            raise AuthenticationException('Недействительный токен')
        user_id = int(user_id)
        print(f"[DEBUG] Looking for user_id: {user_id}")
        repo = UserRepository(db)
        user = await repo.get_by_id(user_id)
        print(f"[DEBUG] User found: {user}")
        if user is None:
            raise AuthenticationException('Пользователь не найден')
        return user
    except Exception as e:
        print(f"[DEBUG] Exception in current_user: {e}")
        raise AuthenticationException('Недействительный токен')