# клиент, база данных, тестовый пользователь, токен
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, \
    AsyncSession
from httpx import AsyncClient, ASGITransport
from main import app
from core.dependencies import get_db
from alembic import command
from core.config import test_settings
from pathlib import Path
from alembic.config import Config

@pytest_asyncio.fixture(scope='session')
async def engine():
    AlembicConfig = Config(Path(__file__).parent.parent / 'alembic.ini') # Передача всех параметров из alembic.ini
    AlembicConfig.set_main_option('sqlalchemy.url', test_settings.DATABASE_URL) # Переопределяем URL базы данных
    command.upgrade(AlembicConfig, 'head') # Применение миграций
    engine = create_async_engine(test_settings.DATABASE_URL) # Создание асинхронного движка SQLAlchemy
    yield engine # Отдаем джижок тестам
    await engine.dispose() # Закрываем движок
    command.downgrade(AlembicConfig, 'base') # Откатываем миграции

@pytest_asyncio.fixture(scope='function')
async def db_session(engine):
    session = None # На случай исключений
    try:
        session_factory = async_sessionmaker(bind=engine, expire_on_commit=False) # Создаем фабрику сессий привязанную к движку
        session = session_factory() # Создание новой сессии
        yield session # Отдаем сессию
    finally:
        if session is not None: # Если сессия была, откатываем транзакцию
            await session.rollback()
            await session.close()

@pytest_asyncio.fixture(scope='function')
async def async_client(db_session):
    async def override_get_db(): # Функция подменяет get_db
        return db_session
    app.dependency_overrides[get_db] = override_get_db # Переопределяем зависимость get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client: # Создание клиента, который тестирует без запуска сервера
        yield client # Отдаем клиент тесту
    app.dependency_overrides.clear() # После теста очищаем переопределение

@pytest_asyncio.fixture
async def auth_headers():

@pytest_asyncio.fixture
async def test_project():

@pytest_asyncio.fixture
async def test_task():