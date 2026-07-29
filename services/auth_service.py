# Регистрация, аутентификация, выдача токена
from repositories.user_repository import UserRepository
from core.exceptions import ConflictException, AuthenticationException
from core.security import hash_password, create_access_token, verify_password
from schemas.auth import UserRegister, UserLogin
from schemas.auth import Token
from core.config import settings

async def register_user(db, user_date:UserRegister):
    repo = UserRepository(db)
    if await repo.check_user_exists_by_username(user_date.username):
        raise ConflictException('Имя пользователя уже существует!')
    elif await repo.check_user_exists_by_email(user_date.email):
        raise ConflictException('Email пользователя уже существует!')
    else:
        hashed_password = hash_password(user_date.password)
        await repo.create_user(user_date.username, user_date.email, hashed_password)
        return {'message':'Пользователь создан'}

async def login_user(db, user_date:UserLogin):
    repo = UserRepository(db)
    if '@' not in user_date.username_or_email:
        user = await repo.get_by_username(user_date.username_or_email)
        if user:
            if verify_password(user_date.password, user.password_hash):
                token = create_access_token({'sub':user.user_id})
                return Token(access_token=token, 
                            token_type='bearer',
                            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
            else:
                raise AuthenticationException('Неверные учётные данные!')
        else:
            raise AuthenticationException('Неверные учётные данные!')
    else:
        user = await repo.get_by_email(user_date.username_or_email)
        if user:
            if verify_password(user_date.password, user.password_hash):
                token = create_access_token({'sub':user.user_id})
                return Token(access_token=token, 
                            token_type='bearer',
                            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
            else:
                raise AuthenticationException('Неверные учётные данные!')
        else:
            raise AuthenticationException('Неверные учётные данные!')