import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Импортируем ваши настройки и базовый класс
from core.config import settings
from core.database import Base
from models.user import UserModel
from models.project import ProjectModel
from models.task import TaskModel
from models.project_members import ProjectMemberModel
from models.project_invitations import ProjectInvitationModel  # или перечислите все файлы: from models import user, project, task, ...

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Настройка логгирования (если нужно)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Устанавливаем метаданные
target_metadata = Base.metadata

# Переопределяем URL из настроек приложения
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_server_default=True)

async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # Если цикла нет — создаём новый (как было)
        asyncio.run(run_async_migrations())
    else:
        # Если цикл уже запущен — выполняем в нём
        loop.run_until_complete(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()