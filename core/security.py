from datetime import datetime, timedelta

import bcrypt
import aiobcrypt
from jose import JWTError, jwt

from core.config import settings


# ---------- Синхронные функции (для обратной совместимости, например, в тестах) ----------
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

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    if 'sub' in to_encode:
        to_encode['sub'] = str(to_encode['sub'])
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        print(f"[DEBUG] Decoding with secret: {settings.JWT_SECRET_KEY[:10]}...")
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        print("[DEBUG] Decoded OK")
        return decoded
    except JWTError as error:
        print(f"[DEBUG] JWT decode error: {error}")
        raise error