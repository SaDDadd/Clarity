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
from models.user import UserModel
from core.security import hash_password, create_access_token
from repositories.user_repository import UserRepository
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository
import uuid
import time
from schemas.task import TaskCreate

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

@pytest_asyncio.fixture(scope='function')
async def test_user(db_session):
    repo = UserRepository(db_session)
    hashed_password = hash_password('qwertyui')
    timestamp = time.time_ns()
    uui = uuid.uuid4()
    user = await repo.create_user(f'testuser_<{timestamp}>', f'test_<{uui}>@mail.ru', hashed_password)
    return user

@pytest_asyncio.fixture(scope='function')
async def auth_headers(test_user):
    token = create_access_token({'sub': test_user.user_id})
    return {'Authorization': f'Bearer {token}'}

@pytest_asyncio.fixture(scope='function')
async def test_project(db_session, test_user):
    repo = ProjectRepository(db_session)
    uui = uuid.uuid4()
    project = await repo.create_project_with_admin(name=f'Test_project_<{uui}>', description=None, \
                                                   admin_id=test_user.user_id, role='admin')
    return project

@pytest_asyncio.fixture(scope='function')
async def test_task(db_session, test_project, test_user):
    repo = TaskRepository(db_session)
    create = TaskCreate(title='Test_task', task_description=None, task_status='pending', \
                        assigned_to=None, deadline=None)
    task = await repo.create_task(project_id=test_project.project_id, task=create)
    return task