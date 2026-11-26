from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from core.dependencies import get_uow, current_user_for_refresh
from schemas.auth import UserLogin, UserRegister
from services.auth_service import login_user, register_user, refresh_tokens
from core.uow import UnitOfWork
from schemas.auth import Token

router = APIRouter()


@router.post('/auth/register', tags=['Аутентификация'],
             summary='Принимает значения пользователя при регистрации', status_code=201)
async def user_registration_endpoint(user: UserRegister, uow: UnitOfWork = Depends(get_uow)) -> dict:
    """Регистрация нового пользователя."""
    return await register_user(uow, user)


@router.post('/auth/login', tags=['Аутентификация'],
             summary='Вход в систему')
async def user_log_endpoint(user: UserLogin, uow: UnitOfWork = Depends(get_uow)):
    """Аутентификация пользователя и выдача JWT-токена."""
    return await login_user(uow, user)


@router.post('/auth/token', tags=['Аутентификация'], 
             summary='Логин для Swagger')
async def login_user_swagger(data: OAuth2PasswordRequestForm = Depends(), 
                             uow: UnitOfWork = Depends(get_uow)):
    """Принимает data (username, password), возвращает access_token.
    Нужен только для кнопки Authorize в Swagger UI."""
    user = UserLogin(username_or_email=data.username, password=data.password)
    return await login_user(uow, user)


@router.post('/refresh', tags=['Аутентификация'], summary='Обновить пару токенов.')
async def refresh_jwt(user = Depends(current_user_for_refresh)) -> Token:
    return await refresh_tokens(user)