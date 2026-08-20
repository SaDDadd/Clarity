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
    """Создаёт движок БД, применяет миграции перед сессией тестов и откатывает после."""
    AlembicConfig = Config(Path(__file__).parent.parent / 'alembic.ini')
    AlembicConfig.set_main_option('sqlalchemy.url', test_settings.DATABASE_URL)
    command.upgrade(AlembicConfig, 'head')
    engine = create_async_engine(test_settings.DATABASE_URL)
    yield engine
    await engine.dispose()
    command.downgrade(AlembicConfig, 'base')

@pytest_asyncio.fixture(scope='function')
async def db_session(engine):
    """Создаёт новую сессию БД для каждого теста, откатывает транзакцию после."""
    session = None
    try:
        session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
        session = session_factory()
        yield session
    finally:
        if session is not None:
            await session.rollback()
            await session.close()

@pytest_asyncio.fixture(scope='function')
async def async_client(db_session):
    """Создаёт HTTP-клиент для тестирования эндпоинтов, подменяет зависимость get_db."""
    async def override_get_db():
        return db_session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        yield client
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope='function')
async def create_test_user(db_session, password='qwertyui'):
    """Вспомогательная функция для создания пользователя с уникальными полями."""
    repo = UserRepository(db_session)
    hashed_password = hash_password(password)
    timestamp = time.time_ns()
    uui = uuid.uuid4()
    user = await repo.create_user(
        f'testuser_{timestamp}',
        f'test_{uui}@mail.ru',
        hashed_password
    )
    return user

@pytest_asyncio.fixture(scope='function')
async def test_users(db_session):
    """Создаёт трёх пользователей: admin, member, outsider."""
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
    """Возвращает заголовки авторизации для администратора проекта."""
    user = test_users.get('admin')
    token = create_access_token({'sub': user.user_id})
    return {'Authorization': f'Bearer {token}'}

@pytest_asyncio.fixture(scope='function')
async def test_project(db_session, test_users):
    """Создаёт проект с администратором admin."""
    repo = ProjectRepository(db_session)
    user = test_users.get('admin')
    uui = uuid.uuid4()
    project = await repo.create_project_with_admin(
        name=f'Test_project_<{uui}>',
        description=None,
        admin_id=user.user_id,
        role='admin'
    )
    return project

@pytest_asyncio.fixture(scope='function')
async def test_project_with_member(db_session, test_project, test_users):
    """Создаёт проект и добавляет в него участника member."""
    repo = ProjectRepository(db_session)
    member = test_users.get('member')
    await repo.add_user(test_project.project_id, member.user_id)
    return {'project': test_project, 'member': member}

@pytest_asyncio.fixture(scope='function')
async def member_auth_headers(test_users):
    """Возвращает заголовки авторизации для участника проекта."""
    user = test_users.get('member')
    token = create_access_token({'sub': user.user_id})
    return {'Authorization': f'Bearer {token}'}

@pytest_asyncio.fixture(scope='function')
async def test_task(db_session, test_project):
    """Создаёт задачу в проекте (напрямую через репозиторий) для использования в тестах."""
    repo = TaskRepository(db_session)
    create = TaskCreate(
        title='Test_task',
        task_description=None,
        task_status='pending',
        assigned_to=None,
        deadline=None
    )
    task = await repo.create_task(project_id=test_project.project_id, task=create)
    return task