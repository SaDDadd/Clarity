from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import settings

engine = create_async_engine(settings.DATABASE_URL) # движок управления пулом и выполнением запросов

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False) # создание новых сессий при вызове

Base = declarative_base() # класс, от которого наследуются все таблицы