from typing import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from core.exceptions import AuthenticationException
from core.security import decode_token, ACCESS_TOKEN, REFRESH_TOKEN
from models.user import UserModel
from core.uow import UnitOfWork

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')

#Для проверки в Swagger
http_bearer = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/token')


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Получить сессию."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_uow(db: AsyncSession = Depends(get_db)) -> AsyncGenerator[UnitOfWork, None]:
    """Запустить транзакцию."""
    async with UnitOfWork(db) as uow:
        yield uow


async def get_user_from_token(token: str, token_type: str, uow: UnitOfWork) -> UserModel:
    """Получить пользователя из токена."""
    payload = decode_token(token)
    if payload.get('type') != token_type:
        raise AuthenticationException('Недействительный токен!')
    user_id = payload.get('sub')
    if user_id is None:
        raise AuthenticationException('Недействительный токен!')
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise AuthenticationException('Недействительный токен!')
    user = await uow.user.get_by_id(int(user_id))
    if user is None:
        raise AuthenticationException('Пользователь не найден!')
    return user


async def current_user(token: str = Depends(oauth2_scheme),
                       uow: UnitOfWork = Depends(get_uow)) -> UserModel:
    """Получить актуального пользователя через access."""
    return await get_user_from_token(token, ACCESS_TOKEN, uow)


async def current_user_for_refresh(token: str = Depends(oauth2_scheme),
                                   uow: UnitOfWork = Depends(get_uow)) -> UserModel: 
    """Получить актуального пользователя через refresh."""
    return await get_user_from_token(token, REFRESH_TOKEN, uow)
