# тесты обновления профиля.
import pytest
from httpx import AsyncClient, ASGITransport
from repositories.user_repository import UserRepository
from core.dependencies import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from main import app

# Обновление имени (успех, конфликт при дубликате, невалидная длина).
@pytest.mark.asyncio 
async def test_put_username():

# Обновление email (аналогично).
@pytest.mark.asyncio
async def test_put_email():