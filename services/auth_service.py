from core.config import settings
from core.exceptions import AuthenticationException, ConflictException, LackOfInformationException, \
                                AppException
from core.security import create_access_token, async_hash_password, async_verify_password
from repositories.user_repository import UserRepository
from schemas.auth import Token, UserLogin, UserRegister
from sqlalchemy.ext.asyncio import AsyncSession


async def register_user(db: AsyncSession, user_data: UserRegister) -> dict:
    """Регистрация пользователя."""
    repo = UserRepository(db)
    if await repo.check_user_exists_by_username(user_data.username):
        raise ConflictException('Имя пользователя уже существует!')
    elif await repo.check_user_exists_by_email(user_data.email):
        raise ConflictException('Email пользователя уже существует!')
    else:
        hashed_password = await async_hash_password(user_data.password)
        try:
            await repo.create_user(user_data.username, user_data.email, hashed_password)
            await db.commit()
        except Exception:
            await db.rollback()
            raise AppException(500, 'Не удалось зарегистрироваться.')
    return {'message': 'Пользователь создан'}


async def login_user(db: AsyncSession, user_data: UserLogin) -> Token:
    """Вход пользователя."""
    repo = UserRepository(db)
    if len(user_data.username_or_email) == 0 or len(user_data.password) == 0:
        raise LackOfInformationException('Нехватка информации!')
    user = await repo.get_by_username(user_data.username_or_email)
    if user:
        if await async_verify_password(user_data.password, user.password_hash):
            try:
                token = create_access_token({'sub': user.user_id})
                await db.commit()
            except Exception:
                await db.rollback()
                raise AppException(500, 'Не удалось войти в профиль.')
            return Token(
                access_token=token,
                token_type='bearer',
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        else:
            raise AuthenticationException('Неверные учётные данные!')
    else:
        user = await repo.get_by_email(user_data.username_or_email)
        if user:
            if await async_verify_password(user_data.password, user.password_hash):
                try:
                    token = create_access_token({'sub': user.user_id})
                    await db.commit()
                except Exception:
                    await db.rollback()
                    raise AppException(500, 'Не удалось войти в профиль.')
                return Token(
                    access_token=token,
                    token_type='bearer',
                    expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
                )
            else:
                raise AuthenticationException('Неверные учётные данные!')
        else:
            raise AuthenticationException('Неверные учётные данные!')