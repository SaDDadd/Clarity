from core.config import settings
from core.exceptions import AuthenticationException, ConflictException
from core.security import create_access_token, async_hash_password, async_verify_password
from schemas.auth import Token, UserLogin, UserRegister
from core.uow import UnitOfWork


async def register_user(uow: UnitOfWork, user_data: UserRegister) -> dict:
    """Регистрация пользователя."""
    if await uow.user.check_user_exists_by_username(user_data.username):
        raise ConflictException('Имя пользователя уже существует!')
    elif await uow.user.check_user_exists_by_email(user_data.email):
        raise ConflictException('Email пользователя уже существует!')
    hashed_password = await async_hash_password(user_data.password)
    await uow.user.create_user(user_data.username, user_data.email, hashed_password)
    return {'message': 'Пользователь создан!'}


async def login_user(uow: UnitOfWork, user_data: UserLogin) -> Token:
    """Аутентифицирует пользователя и возвращает токен."""
    user = await uow.user.get_by_username(user_data.username_or_email)
    if user is None:
        user = await uow.user.get_by_email(user_data.username_or_email)
    if user is None or not await async_verify_password(user_data.password, user.password_hash):
        raise AuthenticationException('Неверные учётные данные!')
    token = create_access_token({'sub': user.user_id})
    return Token(
        access_token=token,
        token_type='bearer',
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )