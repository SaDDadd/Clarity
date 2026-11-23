import pytest
import uuid
from core.uow import UnitOfWork
from core.exceptions import ConflictException, NotFoundException
from services.user_service import update_user_username, update_user_email
from schemas.user import UpdateUsernameRequest, UpdateEmailRequest

class TestUserService:
    @pytest.mark.asyncio
    async def test_update_username_success(self, uow: UnitOfWork, test_users):
        user = test_users['user_profile']
        new_username = f"new_{uuid.uuid4().hex[:8]}"
        request = UpdateUsernameRequest(username=new_username)
        result = await update_user_username(uow, request, user.user_id)
        assert result == {'message': 'Имя пользователя обновлено!'}
        updated = await uow.user.get_by_id(user.user_id)
        assert updated.username == new_username


    @pytest.mark.asyncio
    async def test_update_username_conflict(self, uow: UnitOfWork, test_users):
        user = test_users['user_profile']
        existing_username = test_users['member'].username
        request = UpdateUsernameRequest(username=existing_username)
        with pytest.raises(ConflictException) as exc:
            await update_user_username(uow, request, user.user_id)
        assert exc.value.detail == 'Пользователь с таким именем уже существует!'


    @pytest.mark.asyncio
    async def test_update_username_user_not_found(self, uow: UnitOfWork):
        request = UpdateUsernameRequest(username="new")
        with pytest.raises(NotFoundException) as exc:
            await update_user_username(uow, request, 99999)
        assert exc.value.detail == 'Пользователь не найден!'


    @pytest.mark.asyncio
    async def test_update_email_success(self, uow: UnitOfWork, test_users):
        user = test_users['user_profile']
        new_email = f"new_{uuid.uuid4().hex[:8]}@mail.ru"
        request = UpdateEmailRequest(email=new_email)
        result = await update_user_email(uow, request, user.user_id)
        assert result == {'message': 'Email пользователя обновлено!'}
        updated = await uow.user.get_by_id(user.user_id)
        assert updated.email == new_email


    @pytest.mark.asyncio
    async def test_update_email_conflict(self, uow: UnitOfWork, test_users):
        user = test_users['user_profile']
        existing_email = test_users['member'].email
        request = UpdateEmailRequest(email=existing_email)
        with pytest.raises(ConflictException) as exc:
            await update_user_email(uow, request, user.user_id)
        assert exc.value.detail == 'Пользователь с таким email уже существует!'


    @pytest.mark.asyncio
    async def test_update_email_user_not_found(self, uow: UnitOfWork):
        request = UpdateEmailRequest(email="test@mail.ru")
        with pytest.raises(NotFoundException) as exc:
            await update_user_email(uow, request, 99999)
        assert exc.value.detail == 'Пользователь не найден!'