# get_current_user, get_db
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, AsyncGenerator
from core.database import AsyncSessionLocal
from core.security import decode_access_token
from models.user import User
from repositories.user_repository import get_by_id
from jose import JWSError
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login') # URL эндпоинта логина

async def get_db() -> AsyncGenerator[AsyncSession, None]: # Генератор, создающий сессию БД и закрывающий ее по завершению
    async with AsyncSessionLocal() as session:
        yield session

async def current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User: # Зависимость, которая извлекает JWT-токен, декодирует его и возвращает объект текущего пользователя; выбрасывает 401 при ошибке.
    try:
        payload = decode_access_token(token)
    except JWSError as error:
        raise HTTPException(status_code=401, detail='Недействительный или просроченный токен')
    user_id = payload.get('sub')
    if user_id is not None and type(user_id) is int:
        user = await get_by_id(db, user_id)
        if user is None:
            raise HTTPException(status_code=401, detail='Недействительный или просроченный токен')
        else:
            return user
    else:
        raise HTTPException(status_code=401, detail='Недействительный или просроченный токен')