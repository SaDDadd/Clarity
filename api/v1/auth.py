from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import current_user, get_db
from models.user import UserModel
from schemas.auth import UserLogin, UserRegister
from schemas.user import UserResponse
from services.auth_service import login_user, register_user

router = APIRouter()


@router.post('/auth/register', tags=['Аутентификация'],
             summary='Принимает значения пользователя при регистрации', status_code=201)
async def user_registration_endpoint(user: UserRegister, db: AsyncSession = Depends(get_db)) -> dict:
    """Регистрация нового пользователя."""
    return await register_user(db, user)


@router.post('/auth/login', tags=['Аутентификация'],
             summary='Вход в систему')
async def user_log_endpoint(user: UserLogin, db: AsyncSession = Depends(get_db)):
    """Аутентификация пользователя и выдача JWT-токена."""
    return await login_user(db, user)


@router.get('/auth/me', tags=['Аутентификация'],
            summary='Получение информации о пользователе')
async def get_user_info_endpoint(user: UserModel = Depends(current_user)) -> UserResponse:
    """Получить информацию о текущем авторизованном пользователе."""
    return UserResponse.model_validate(user)