import os

os.environ["ENV"] = "test"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "3306"
os.environ["DB_USER"] = "root"
os.environ["DB_PASSWORD"] = "2007"
os.environ["DB_NAME"] = "task_to_do_test"
os.environ["JWT_SECRET_KEY"] = "your_very_secret_key_here_32_chars_min"
os.environ["CORS_ORIGINS"] = "http://localhost:3000,http://127.0.0.1:3000"

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from main import app
from core.dependencies import get_db
from alembic import command
from core.config import settings
from pathlib import Path
from alembic.config import Config
from core.security import hash_password, create_access_token
from repositories.user_repository import UserRepository
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository
from repositories.project_invitation_repository import ProjectInvitationRepository
import uuid
import time
from schemas.task import TaskCreate
import pytest
from sqlalchemy import create_engine  # синхронный
from dotenv import load_dotenv
from core.database import Base

# Явно устанавливаем ENV=test

@pytest.fixture(scope='session')
def sync_engine():
    # Теперь settings уже содержит тестовый URL
    raw_url = settings.DATABASE_URL
    sync_url = raw_url.replace('+aiomysql', '+pymysql')
    engine = create_engine(sync_url)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest_asyncio.fixture
async def async_engine(sync_engine):
    async_engine = create_async_engine(settings.DATABASE_URL)
    yield async_engine
    await async_engine.dispose()

@pytest_asyncio.fixture(scope='function')
async def db_session(async_engine):
    """Создаёт новую сессию БД для каждого теста, откатывает транзакцию после."""
    session = None
    try:
        session_factory = async_sessionmaker(bind=async_engine, expire_on_commit=False)
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
        f'test_{uui.hex[:8]}',
        f'test_{uui.hex[:8]}@mail.ru',
        hashed_password
    )
    return user

@pytest_asyncio.fixture(scope='function')
async def test_users(db_session):
    """Создаёт трёх пользователей: admin, member, outsider."""
    # Создаём пользователей через репозиторий напрямую, а не через фикстуру
    repo = UserRepository(db_session)
    hashed_password = hash_password('qwertyui')
    
    user1 = await repo.create_user(
        f'test_{uuid.uuid4().hex[:8]}',
        f'test_{uuid.uuid4().hex[:8]}@mail.ru',
        hashed_password
    )
    user2 = await repo.create_user(
        f'test_{uuid.uuid4().hex[:8]}',
        f'test_{uuid.uuid4().hex[:8]}@mail.ru',
        hashed_password
    )
    user3 = await repo.create_user(
        f'test_{uuid.uuid4().hex[:8]}',
        f'test_{uuid.uuid4().hex[:8]}@mail.ru',
        hashed_password
    )
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

@pytest_asyncio.fixture(scope='function')
async def test_invitation(db_session, test_project, test_users):
    """Создаёт приглашение в проект для пользователя outsider."""
    repo = ProjectInvitationRepository(db_session)
    project = test_project
    inviter = test_users.get('admin')
    invitee = test_users.get('outsider')
    invitation = await repo.create_invitation(
        project_id=project.project_id,
        inviter_id=inviter.user_id,
        invitee_id=invitee.user_id,
        message="Приглашение для теста"
    )
    return invitation