# Регистрация, аутентификация, выдача токена
from core.config import settings
from core.exceptions import (
    AuthenticationException,
    ConflictException,
    LackOfInformationException,
)
from core.security import create_access_token, hash_password, verify_password
from repositories.user_repository import UserRepository
from schemas.auth import Token, UserLogin, UserRegister
from pydantic import EmailStr

# Регистрация нового пользователя
async def register_user(db, user_date: UserRegister):
    repo = UserRepository(db)
    if len(user_date.username) == 0 or len(user_date.email) == 0:
        raise LackOfInformationException('Нехватка информации!')
    if await repo.check_user_exists_by_username(user_date.username):
        raise ConflictException('Имя пользователя уже существует!')
    if isinstance(user_date.email, EmailStr):
        raise AuthenticationException('Неверные тип почты!')
    elif await repo.check_user_exists_by_email(user_date.email):
        raise ConflictException('Email пользователя уже существует!')
    else:
        if len(user_date.password) < 8:
            raise LackOfInformationException('Пароль короткий, должен быть больше 8 символов!')
        hashed_password = hash_password(user_date.password)
        await repo.create_user(user_date.username, user_date.email, hashed_password)
        return {'message': 'Пользователь создан'}

# Аутентификация пользователя и выдача токена
async def login_user(db, user_date: UserLogin):
    repo = UserRepository(db)
    if len(user_date.username_or_email) == 0 or len(user_date.password) == 0:
        raise LackOfInformationException('Нехватка информации!')
    user = await repo.get_by_username(user_date.username_or_email)
    if user:
        if verify_password(user_date.password, user.password_hash):
            token = create_access_token({'sub': user.user_id})
            return Token(
                access_token=token,
                token_type='bearer',
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        else:
            raise AuthenticationException('Неверные учётные данные!')
    else:
        user = await repo.get_by_email(user_date.username_or_email)
        if user:
            if verify_password(user_date.password, user.password_hash):
                token = create_access_token({'sub': user.user_id})
                return Token(
                    access_token=token,
                    token_type='bearer',
                    expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
                )
            else:
                raise AuthenticationException('Неверные учётные данные!')
        else:
            raise AuthenticationException('Неверные учётные данные!')