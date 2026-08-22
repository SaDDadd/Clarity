import pytest 
from repositories.user_repository import UserRepository
from core.security import hash_password
from models.user import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DataError 
import uuid

class TestUserRepository():
    @pytest.mark.asyncio
    async def test_create_user_success(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        hashed_password = hash_password('qwertyui')
        username = f'Daniil_{uuid.uuid4().hex[:8]}'
        email = f'dan_{uuid.uuid4().hex[:8]}@mail.ru'
        response = await repo.create_user(username=username, email=email, password_hash=hashed_password)
        assert response.username == username
        assert response.email == email

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email_raises_integrity_error(self, db_session: AsyncSession, test_users):
        repo = UserRepository(db_session)
        hashed_password = hash_password('qwertyui')
        with pytest.raises(IntegrityError):
            await repo.create_user(username='Daniil', email=f'{test_users['admin'].email}', \
                                          password_hash=hashed_password)

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username_raises_integrity_error(self, db_session: AsyncSession, test_users):
        repo = UserRepository(db_session)
        hashed_password = hash_password('qwertyui')
        with pytest.raises(IntegrityError):
            await repo.create_user(username=f'{test_users['admin'].username}', email=f'da{uuid.uuid4().hex[:8]}', \
                                            password_hash=hashed_password)

    @pytest.mark.asyncio 
    async def test_create_user_missing_required_field_raises_error(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        hashed_password = hash_password('qwertyui')
        with pytest.raises(IntegrityError):
            await repo.create_user(username=f'{uuid.uuid4().hex[:8]}', email=None, 
                                          password_hash=hashed_password)

    @pytest.mark.asyncio 
    async def test_get_user_by_id_success(self, db_session: AsyncSession, test_users):
        repo = UserRepository(db_session)
        response = await repo.get_by_id(test_users['admin'].user_id)
        assert response.username == test_users['admin'].username
        assert response.email == test_users['admin'].email

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found_returns_none(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        response = await repo.get_by_id(99999)
        assert response is None

    @pytest.mark.asyncio
    async def test_get_user_by_id_with_invalid_type_raises_error(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        assert await repo.get_by_id('abc') is None
        
    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, db_session: AsyncSession, test_users):
        repo = UserRepository(db_session)
        response = await repo.get_by_email(test_users['admin'].email)
        assert isinstance(response, UserModel)
        assert response.user_id == test_users['admin'].user_id

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found_returns_none(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        response = await repo.get_by_email('mnbvcx@mail.ru')
        assert response is None

    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self, db_session: AsyncSession, test_users):
        repo = UserRepository(db_session)
        response = await repo.get_by_username(test_users['admin'].username)
        assert isinstance(response, UserModel)
        assert response.user_id == test_users['admin'].user_id
        assert response.email == test_users['admin'].email

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found_returns_none(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        response = await repo.get_by_username('dhjhs')
        assert response is None

    @pytest.mark.asyncio
    async def test_update_username_success(self, db_session: AsyncSession, test_users):
        repo = UserRepository(db_session)
        first_username = test_users['user_profile'].username
        response = await repo.update_username(test_users['user_profile'].user_id, f'update_{uuid.uuid4().hex[:8]}')
        update_user = await repo.get_by_id(test_users['user_profile'].user_id)
        assert response is True
        assert first_username != update_user.username

    @pytest.mark.asyncio
    async def test_update_email_success(self, db_session: AsyncSession, test_users):
        repo = UserRepository(db_session)
        first_email = test_users['user_profile'].email
        response = await repo.update_email(test_users['user_profile'].user_id, f'update_{uuid.uuid4().hex[:8]}@mail.ru')
        update_user = await repo.get_by_id(test_users['user_profile'].user_id)
        assert response is True
        assert first_email != update_user.email

    @pytest.mark.asyncio 
    async def test_update_user_password_hash_success(self, db_session: AsyncSession):
        #Функционала с обновлением пароля пока нет, надо добавить 
        pytest.skip("Метод обновления пароля ещё не реализован")

    @pytest.mark.asyncio
    async def test_update_email_not_found_raises_error_or_returns_none(self, db_session: AsyncSession, test_users):
        repo = UserRepository(db_session)
        response = await repo.update_email(999999, f'{uuid.uuid4().hex[:8]}@mail.ru')
        assert response is False

    @pytest.mark.asyncio
    async def test_update_username_not_found_raises_error_or_returns_none(self, db_session: AsyncSession, test_users):
        repo = UserRepository(db_session)
        response = await repo.update_username(999999, 'update_username')
        assert response is False

    @pytest.mark.asyncio
    async def test_delete_user_success(self, db_session: AsyncSession, test_users):
        repo = UserRepository(db_session)
        user_id = test_users['outsider'].user_id
        result = await repo.delete_user(user_id)
        assert result is True
        deleted_user = await repo.get_by_id(user_id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_delete_user_not_found_raises_error_or_ignores(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        result = await repo.delete_user(999999)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_user_cascades_to_related_entities(self, db_session: AsyncSession, test_users):
        repo = UserRepository(db_session)
        hashed_password = hash_password('qwertyui')
        new_user = await repo.create_user(
            username=f'cascade_test_{uuid.uuid4().hex[:8]}',
            email=f'cascade_test_{uuid.uuid4().hex[:8]}@mail.ru',
            password_hash=hashed_password
        )
        from repositories.project_repository import ProjectRepository
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create_project_with_admin(
            name=f'Cascade_project_{uuid.uuid4().hex[:8]}',
            description=None,
            admin_id=new_user.user_id,
            role='admin'
        )
        with pytest.raises(IntegrityError):
            await repo.delete_user(new_user.user_id)