import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_HOST: str = 'localhost'
    DB_PORT: int = 3306
    DB_USER: str = 'root'
    DB_PASSWORD: str = '${DB_PASSWORD}'  # интерполируется из переменной или .env
    DB_NAME: str = 'task_to_do'
    DB_DRIVER: str = 'aiomysql'

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Используем validation_alias вместо устаревшего env=...
    JWT_SECRET_KEY: str = Field(..., validation_alias="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CORS_ORIGINS: str = ''

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.CORS_ORIGINS:
            return []
        return [item.strip() for item in self.CORS_ORIGINS.split(',') if item.strip()]

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

class SettingsTEST(BaseSettings):
    # Явные значения по умолчанию, но они будут переопределены переменными окружения
    DB_HOST: str = 'localhost'
    DB_PORT: int = 3306
    DB_USER: str = 'root'
    DB_PASSWORD: str = '2007'          # явный пароль для тестов
    DB_NAME: str = 'task_to_do_test'
    DB_DRIVER: str = 'aiomysql'

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    JWT_SECRET_KEY: str = Field(..., validation_alias="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CORS_ORIGINS: str = ''

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.CORS_ORIGINS:
            return []
        return [item.strip() for item in self.CORS_ORIGINS.split(',') if item.strip()]

    model_config = SettingsConfigDict(
        env_file='.env.test',
        env_file_encoding='utf-8',
        extra='ignore'
    )

def get_settings():
    env = os.getenv('ENV', '')
    if env == 'test':
        return SettingsTEST()
    return Settings()

settings = get_settings()