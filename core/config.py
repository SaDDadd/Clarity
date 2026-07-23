from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    DB_HOST: str = 'localhost'
    DB_PORT: int = 3306
    DB_USER: str = 'root'
    DB_PASSWORD: str = '2007'
    DB_NAME: str = 'task_to_do'
    DB_DRIVER: str = 'aiomysql' # Драйвер для SQLAlchemy

    @property
    def DATABASE_URL(self) -> str: # Строка подключения к БД
        return f"mysql+{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")  # Секретный ключ для подписи JWT
    JWT_ALGORITHM: str = 'HS256' # Алгоритм шифрования для JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Время жизни токена в минутах, после истечения времени пользователь должен заново войти
    CORS_ORIGINS: List[str] = [] # Список разрешенных источников для CORS

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v): # Преобразует строку с источниками из .env 
                                    # в список разрешённых адресов для CORS.
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file = '.env',
        env_file_encoding = 'utf-8',
        extra = 'ignore' # игнорирование лишних переменных в .env
    )
settings = Settings()