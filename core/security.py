from datetime import datetime, timedelta, timezone

import bcrypt
import aiobcrypt
from jose import JWTError, jwt
from core.exceptions import AuthenticationException

from core.config import settings

ACCESS_TOKEN = 'access'
REFRESH_TOKEN = 'refresh'


def hash_password(password: str) -> str:
    """Синхронное хеширование (используется только в seed_data и тестах)."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    return hashed


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Синхронная проверка пароля."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


async def async_hash_password(password: str) -> str:
    """Асинхронно хеширует пароль с помощью aiobcrypt."""
    salt = await aiobcrypt.gensalt()
    hashed = await aiobcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


async def async_verify_password(plain_password: str, hashed_password: str) -> bool:
    """Асинхронно проверяет пароль."""
    return await aiobcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def create_jwt(token_type: str, token_data: dict, expires_delta: timedelta | None = None) -> str:
    """Создание access и refresh токенов."""
    jwt_payload = {'type': token_type}
    jwt_payload.update(token_data)
    if expires_delta is None:
        if token_type == ACCESS_TOKEN:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        else:
            expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(timezone.utc) + expires_delta
    jwt_payload.update({'exp': expire})
    if token_type == ACCESS_TOKEN:
        jwt_payload['sub'] = str(jwt_payload['sub'])
        jwt_payload['username'] = str(jwt_payload['username'])
    else:
        jwt_payload['sub'] = str(jwt_payload['sub'])
    return jwt.encode(jwt_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)



def create_access_token(data: dict) -> str:
    """Создание токена доступ."""
    token_data = {'sub': data['sub'], 
                  'username': data.get('username')}
    return create_jwt(token_type=ACCESS_TOKEN, token_data=token_data, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    


def create_refresh_token(data: dict) -> str:
    """Создание refresh токена."""
    token_data = {'sub': data['sub']}
    return create_jwt(token_type=REFRESH_TOKEN, token_data=token_data, expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))


def decode_token(token: str) -> dict:
    """Декодирование токена доступа."""
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return decoded
    except JWTError as e:
        raise AuthenticationException('Недействительный токен') from e