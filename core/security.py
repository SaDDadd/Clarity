# JWT, хеширование
from jose import JWTError, jwt 
from datetime import datetime, timedelta
import bcrypt 
from core.config import settings

def hash_password(password: str) -> str: # Хэширование пароля
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    return hashed_password

def verify_password(plain_password: str, hashed_password: str) -> bool: # Проверка пароля
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
     
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str: # генерация JWT-токена для авторизированного пользователя
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> dict: # Расшифровка токена и извлекание данных, чтобы индентифицировать пользователя
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return decoded
    except JWTError as error:
        raise error