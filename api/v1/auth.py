from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db, current_user
from models.user import UserModel
from schemas.auth import UserRegister, UserLogin
from schemas.user import UserResponse
from services.auth_service import login_user, register_user

router = APIRouter()

@router.post('/auth/register', tags=['Аутентификация'], \
             summary='Принимает значения пользователя при регистрации') # Регистрация нового пользователя
async def user_registration(user: UserRegister, db: AsyncSession = Depends(get_db)):
    return await register_user(db, user)
    
@router.post('/auth/login', tags=['Аутентификация'], \
             summary='Вход в систему') # Вход в систему
async def user_log(user: UserLogin, db: AsyncSession = Depends(get_db)):
    return await login_user(db, user)

@router.get('/auth/me', tags=['Аутентификация'], \
            summary='Получение информации о пользователе') # Получить информацию о пользователе
async def get_user_info(user: UserModel = Depends(current_user)):
    return UserResponse.model_validate(user)