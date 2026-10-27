import os
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

def resolve_env_file() -> str:
    """Выбирает .env-файл в зависимости от переменной ENV."""
    return '.env.test' if os.getenv('ENV', '').lower() == 'test' else '.env'

class Settings(BaseSettings):
    DB_HOST: str = 'localhost'
    DB_PORT: int = 3306
    DB_USER: str = 'root'
    DB_PASSWORD: str = ''
    DB_NAME: str = 'task_to_do'
    DB_DRIVER: str = 'aiomysql'

    @property
    def DATABASE_URL(self) -> str:
        """Формирует URL подключения к базе данных."""
        return f"mysql+{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CORS_ORIGINS: str = ''

    @property
    def cors_origins_list(self) -> List[str]:
        """Возвращает список разрешённых CORS-источников."""
        if not self.CORS_ORIGINS:
            return []
        return [item.strip() for item in self.CORS_ORIGINS.split(',') if item.strip()]

    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ''
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        """Формирует URL подключения к Redis."""
        if self.REDIS_PASSWORD:
            return f'redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}' 
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}'

    @property
    def is_test_env(self) -> bool:
        """True, если активен тестовый сценарий (pytest или нагрузочные тесты)."""
        return os.getenv('ENV', '').lower() == 'test'
    
    model_config = SettingsConfigDict(
            env_file=resolve_env_file(),
            env_file_encoding='utf-8',
            extra='ignore'
        )

settings = Settings()