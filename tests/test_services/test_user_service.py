import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from core.exceptions import LackOfInformationException, ConflictException, NotFoundException
from services.user_service import update_user_username, update_user_email
from repositories.user_repository import UserRepository

class TestUserService:
    @pytest.mark.asyncio
    async def test_update_username_success(self, db_session: AsyncSession, test_users):
        user = test_users['user_profile']
        new_username = f"new_{uuid.uuid4().hex[:8]}"
        result = await update_user_username(db_session, new_username, user.user_id)
        assert result == {'message': 'Имя пользователя обновлено!'}
        repo = UserRepository(db_session)
        updated = await repo.get_by_id(user.user_id)
        assert updated.username == new_username

    @pytest.mark.asyncio
    async def test_update_username_empty(self, db_session: AsyncSession, test_users):
        user = test_users['user_profile']
        with pytest.raises(LackOfInformationException) as exc:
            await update_user_username(db_session, "", user.user_id)
        assert exc.value.detail == 'Имя не может быть пустым или превышать 50 символов!'

    @pytest.mark.asyncio
    async def test_update_username_too_long(self, db_session: AsyncSession, test_users):
        user = test_users['user_profile']
        long_name = "a" * 51
        with pytest.raises(LackOfInformationException) as exc:
            await update_user_username(db_session, long_name, user.user_id)
        assert exc.value.detail == 'Имя не может быть пустым или превышать 50 символов!'

    @pytest.mark.asyncio
    async def test_update_username_conflict(self, db_session: AsyncSession, test_users):
        user = test_users['user_profile']
        existing_username = test_users['member'].username
        with pytest.raises(ConflictException) as exc:
            await update_user_username(db_session, existing_username, user.user_id)
        assert exc.value.detail == 'Пользователь с таким именем уже существует!'

    @pytest.mark.asyncio
    async def test_update_username_user_not_found(self, db_session: AsyncSession):
        with pytest.raises(NotFoundException) as exc:
            await update_user_username(db_session, "new", 99999)
        assert exc.value.detail == 'Пользователь не найден!'

    @pytest.mark.asyncio
    async def test_update_email_success(self, db_session: AsyncSession, test_users):
        user = test_users['user_profile']
        new_email = f"new_{uuid.uuid4().hex[:8]}@mail.ru"
        result = await update_user_email(db_session, new_email, user.user_id)
        assert result == {'message': 'Email пользователя обновлено!'}
        repo = UserRepository(db_session)
        updated = await repo.get_by_id(user.user_id)
        assert updated.email == new_email

    @pytest.mark.asyncio
    async def test_update_email_empty(self, db_session: AsyncSession, test_users):
        user = test_users['user_profile']
        with pytest.raises(LackOfInformationException) as exc:
            await update_user_email(db_session, "", user.user_id)
        assert exc.value.detail == 'Email не может быть пустым или превышать 100 символов!'

    @pytest.mark.asyncio
    async def test_update_email_too_long(self, db_session: AsyncSession, test_users):
        user = test_users['user_profile']
        long_email = "a" * 101 + "@mail.ru"
        with pytest.raises(LackOfInformationException) as exc:
            await update_user_email(db_session, long_email, user.user_id)
        assert exc.value.detail == 'Email не может быть пустым или превышать 100 символов!'

    @pytest.mark.asyncio
    async def test_update_email_conflict(self, db_session: AsyncSession, test_users):
        user = test_users['user_profile']
        existing_email = test_users['member'].email
        with pytest.raises(ConflictException) as exc:
            await update_user_email(db_session, existing_email, user.user_id)
        assert exc.value.detail == 'Пользователь с таким email уже существует!'

    @pytest.mark.asyncio
    async def test_update_email_user_not_found(self, db_session: AsyncSession):
        with pytest.raises(NotFoundException) as exc:
            await update_user_email(db_session, "test@mail.ru", 99999)
        assert exc.value.detail == 'Пользователь не найден!'