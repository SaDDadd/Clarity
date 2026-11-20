import pytest
import uuid
from core.uow import UnitOfWork
from core.exceptions import LackOfInformationException, ConflictException, NotFoundException
from services.user_service import update_user_username, update_user_email
from repositories.user_repository import UserRepository

class TestUserService:
    @pytest.mark.asyncio
    async def test_update_username_success(self, uow: UnitOfWork, test_users):
        user = test_users['user_profile']
        new_username = f"new_{uuid.uuid4().hex[:8]}"
        result = await update_user_username(uow, new_username, user.user_id)
        assert result == {'message': 'Имя пользователя обновлено!'}
        updated = await uow.user.get_by_id(user.user_id)
        assert updated.username == new_username

    @pytest.mark.asyncio
    async def test_update_username_empty(self, uow: UnitOfWork, test_users):
        user = test_users['user_profile']
        with pytest.raises(LackOfInformationException) as exc:
            await update_user_username(uow, "", user.user_id)
        assert exc.value.detail == 'Имя не может быть пустым или превышать 50 символов!'

    @pytest.mark.asyncio
    async def test_update_username_too_long(self, uow: UnitOfWork, test_users):
        user = test_users['user_profile']
        long_name = "a" * 51
        with pytest.raises(LackOfInformationException) as exc:
            await update_user_username(uow, long_name, user.user_id)
        assert exc.value.detail == 'Имя не может быть пустым или превышать 50 символов!'

    @pytest.mark.asyncio
    async def test_update_username_conflict(self, uow: UnitOfWork, test_users):
        user = test_users['user_profile']
        existing_username = test_users['member'].username
        with pytest.raises(ConflictException) as exc:
            await update_user_username(uow, existing_username, user.user_id)
        assert exc.value.detail == 'Пользователь с таким именем уже существует!'

    @pytest.mark.asyncio
    async def test_update_username_user_not_found(self, uow: UnitOfWork):
        with pytest.raises(NotFoundException) as exc:
            await update_user_username(uow, "new", 99999)
        assert exc.value.detail == 'Пользователь не найден!'

    @pytest.mark.asyncio
    async def test_update_email_success(self, uow: UnitOfWork, test_users):
        user = test_users['user_profile']
        new_email = f"new_{uuid.uuid4().hex[:8]}@mail.ru"
        result = await update_user_email(uow, new_email, user.user_id)
        assert result == {'message': 'Email пользователя обновлено!'}
        updated = await uow.user.get_by_id(user.user_id)
        assert updated.email == new_email

    @pytest.mark.asyncio
    async def test_update_email_empty(self, uow: UnitOfWork, test_users):
        user = test_users['user_profile']
        with pytest.raises(LackOfInformationException) as exc:
            await update_user_email(uow, "", user.user_id)
        assert exc.value.detail == 'Email не может быть пустым или превышать 100 символов!'

    @pytest.mark.asyncio
    async def test_update_email_too_long(self, uow: UnitOfWork, test_users):
        user = test_users['user_profile']
        long_email = "a" * 101 + "@mail.ru"
        with pytest.raises(LackOfInformationException) as exc:
            await update_user_email(uow, long_email, user.user_id)
        assert exc.value.detail == 'Email не может быть пустым или превышать 100 символов!'

    @pytest.mark.asyncio
    async def test_update_email_conflict(self, uow: UnitOfWork, test_users):
        user = test_users['user_profile']
        existing_email = test_users['member'].email
        with pytest.raises(ConflictException) as exc:
            await update_user_email(uow, existing_email, user.user_id)
        assert exc.value.detail == 'Пользователь с таким email уже существует!'

    @pytest.mark.asyncio
    async def test_update_email_user_not_found(self, uow: UnitOfWork):
        with pytest.raises(NotFoundException) as exc:
            await update_user_email(uow, "test@mail.ru", 99999)
        assert exc.value.detail == 'Пользователь не найден!'