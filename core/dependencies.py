from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from core.database import AsyncSessionLocal
from core.security import decode_access_token
from models.user import UserModel
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer
from repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login') # URL эндпоинта логина

async def get_db() -> AsyncGenerator[AsyncSession, None]: # Генератор, создающий сессию БД и закрывающий ее по завершению
    async with AsyncSessionLocal() as session:
        yield session

async def current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> UserModel: # Зависимость, которая извлекает JWT-токен, декодирует его и возвращает объект текущего пользователя; выбрасывает 401 при ошибке.
    try:
        payload = decode_access_token(token)
    except JWTError as error:
        raise HTTPException(status_code=401, detail='Недействительный или просроченный токен')
    user_id = payload.get('sub')
    if user_id is not None:
        try:
            user_id = int(user_id)
        except ValueError as error:
            raise HTTPException(status_code=401, detail='Недействительный или просроченный токен')
        repo = UserRepository(db)
        user = await repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail='Недействительный или просроченный токен')
        else:
            return user
    else:
        raise HTTPException(status_code=401, detail='Недействительный или просроченный токен')