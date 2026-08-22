import pytest 
from repositories.user_repository import UserRepository
from core.security import hash_password
from models.user import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

class TestUserRepository():
    @pytest.mark.asyncio
    async def test_create_user_success(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        hashed_password = hash_password('qwertyui')
        response = await repo.create_user(username='Daniil', email='dan@mail.ru', \
                                          password_hash=hashed_password)
        assert isinstance(response, UserModel)
        assert response.username == 'Daniil'
        assert response.email == 'dan@mail.ru'
        assert await repo.get_by_id(response.user_id) is not None

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email_raises_integrity_error(self, db_session: AsyncSession, test_users):
        repo = UserRepository(db_session)
        hashed_password = hash_password('qwertyui')
        response = await repo.create_user(username='Daniil', email=f'{test_users['admin'].email}', \
                                          password_hash=hashed_password)
        assert isinstance(response, IntegrityError)

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username_raises_integrity_error(self, db_session: AsyncSession, test_users):
        repo = UserRepository(db_session)
        hashed_password = hash_password('qwertyui')
        response = await repo.create_user(username=f'{test_users['admin'].username}', email=f'da{uuid.uuid4().hex[:8]}', \
                                            password_hash=hashed_password)
        assert isinstance(response, IntegrityError)

    @pytest.mark.asyncio 
    async def test_create_user_missing_required_field_raises_error(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        hashed_password = hash_password('qwertyui')
        response = await repo.create_user(username=f'{uuid.uuid4().hex[:8]}', email=None, 
                                          password_hash=hashed_password)
        assert 

    @pytest.mark.asyncio 
    async def test_get_user_by_id_success():

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found_returns_none():

    @pytest.mark.asyncio
    async def test_get_user_by_id_with_invalid_type_raises_error():

    @pytest.mark.asyncio
    async def test_get_user_by_email_success():

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found_returns_none():

    @pytest.mark.asyncio
    async def test_get_user_by_email_case_insensitive():

    @pytest.mark.asyncio
    async def test_get_user_by_username_success():

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found_returns_none():

    @pytest.mark.asyncio
    async def test_get_user_by_username_case_sensitive():

    @pytest.mark.asyncio
    async def test_update_user_success():

    @pytest.mark.asyncio 
    async def test_update_user_password_hash_success():

    @pytest.mark.asyncio
    async def test_update_user_duplicate_email_raises_integrity_error():

    @pytest.mark.asyncio
    async def test_update_user_duplicate_username_raises_integrity_error():

    @pytest.mark.asyncio
    async def test_update_user_not_found_raises_error_or_returns_none():

    @pytest.mark.asyncio
    async def test_delete_user_success():

    @pytest.mark.asyncio
    async def test_delete_user_not_found_raises_error_or_ignores():

    @pytest.mark.asyncio
    async def test_delete_user_cascades_to_related_entities():

    @pytest.mark.asyncio
    async def test_get_all_users_returns_list():

    @pytest.mark.asyncio 
    async def test_get_all_users_with_pagination():

    @pytest.mark.asyncio
    async def test_get_all_users_with_sorting():

    @pytest.mark.asyncio
    async def test_exists_by_email_returns_true_if_exists():

    @pytest.mark.asyncio
    async def test_exists_by_email_returns_false_if_not_exists():

    @pytest.mark.asyncio
    async def test_exists_by_username_returns_true_if_exists():

    @pytest.mark.asyncio
    async def test_exists_by_username_returns_false_if_not_exists():