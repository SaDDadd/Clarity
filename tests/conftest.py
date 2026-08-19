# клиент, база данных, тестовый пользователь, токен
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from main import app
from core.dependencies import get_db
from alembic import command
from core.config import test_settings
from pathlib import Path
from alembic.config import Config
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
async def create_test_user(db_session, password='qwertyui'):
    repo = UserRepository(db_session)
    hashed_password = hash_password(password)
    timestamp = time.time_ns()
    uui = uuid.uuid4()
    user = await repo.create_user(f'testuser_{timestamp}',f'test_{uui}@mail.ru', \
                                    hashed_password)
    return user

@pytest_asyncio.fixture(scope='function')
async def test_users(db_session):
    user1 = await create_test_user(db_session)
    user2 = await create_test_user(db_session)
    user3 = await create_test_user(db_session)
    return {
        'admin': user1,
        'member': user2,
        'outsider': user3
    }

@pytest_asyncio.fixture(scope='function')
async def auth_headers(test_users):
    user = test_users.get('admin')
    token = create_access_token({'sub': user.user_id})
    return {'Authorization': f'Bearer {token}'}

@pytest_asyncio.fixture(scope='function')
async def test_project(db_session, test_users):
    repo = ProjectRepository(db_session)
    user = test_users.get('admin')
    uui = uuid.uuid4()
    project = await repo.create_project_with_admin(name=f'Test_project_<{uui}>', description=None, \
                                                   admin_id=user.user_id, role='admin')
    return project

@pytest_asyncio.fixture(scope='function')
async def test_project_add_member(db_session, test_project, test_users):
    repo = ProjectRepository(db_session)
    user = test_users.get('member')
    add_user = await repo.add_user(test_project.project_id, user.user_id)
    return add_user

@pytest_asyncio.fixture(scope='function')
async def member_auth_headers(test_users):
    user = test_users.get('member')
    token = create_access_token({'sub': user.user_id})
    return {'Authorization': f'Bearer {token}'}

@pytest_asyncio.fixture(scope='function')
async def test_task(db_session, test_project):
    repo = TaskRepository(db_session)
    create = TaskCreate(title='Test_task', task_description=None, task_status='pending', \
                        assigned_to=None, deadline=None)
    task = await repo.create_task(project_id=test_project.project_id, task=create)
    return task