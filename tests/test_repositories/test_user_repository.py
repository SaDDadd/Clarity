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
        """Проверяет успешное создание пользователя."""
        repo = UserRepository(db_session)
        hashed_password = hash_password('qwertyui')
        username = f'Daniil_{uuid.uuid4().hex[:8]}'
        email = f'dan_{uuid.uuid4().hex[:8]}@mail.ru'
        response = await repo.create_user(username=username, email=email, password_hash=hashed_password)
        assert response.username == username
        assert response.email == email

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email_raises_integrity_error(self, db_session: AsyncSession, test_users):
        """Проверяет, что при попытке создать пользователя с существующим email выбрасывается IntegrityError."""
        repo = UserRepository(db_session)
        hashed_password = hash_password('qwertyui')
        with pytest.raises(IntegrityError):
            await repo.create_user(username='Daniil', email=f'{test_users['admin'].email}', \
                                          password_hash=hashed_password)

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username_raises_integrity_error(self, db_session: AsyncSession, test_users):
        """Проверяет, что при попытке создать пользователя с существующим username выбрасывается IntegrityError."""
        repo = UserRepository(db_session)
        hashed_password = hash_password('qwertyui')
        with pytest.raises(IntegrityError):
            await repo.create_user(username=f'{test_users['admin'].username}', email=f'da{uuid.uuid4().hex[:8]}', \
                                            password_hash=hashed_password)

    @pytest.mark.asyncio 
    async def test_create_user_missing_required_field_raises_error(self, db_session: AsyncSession):
        """Проверяет, что при отсутствии обязательного поля (email) выбрасывается IntegrityError."""
        repo = UserRepository(db_session)
        hashed_password = hash_password('qwertyui')
        with pytest.raises(IntegrityError):
            await repo.create_user(username=f'{uuid.uuid4().hex[:8]}', email=None, 
                                          password_hash=hashed_password)

    @pytest.mark.asyncio 
    async def test_get_user_by_id_success(self, db_session: AsyncSession, test_users):
        """Проверяет получение пользователя по существующему ID."""
        repo = UserRepository(db_session)
        response = await repo.get_by_id(test_users['admin'].user_id)
        assert response.username == test_users['admin'].username
        assert response.email == test_users['admin'].email

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found_returns_none(self, db_session: AsyncSession):
        """Проверяет, что при несуществующем ID возвращается None."""
        repo = UserRepository(db_session)
        response = await repo.get_by_id(99999)
        assert response is None

    @pytest.mark.asyncio
    async def test_get_user_by_id_with_invalid_type_raises_error(self, db_session: AsyncSession):
        """Проверяет, что при передаче некорректного типа возвращается None (ошибка не выбрасывается)."""
        repo = UserRepository(db_session)
        assert await repo.get_by_id('abc') is None
        
    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, db_session: AsyncSession, test_users):
        """Проверяет получение пользователя по email."""
        repo = UserRepository(db_session)
        response = await repo.get_by_email(test_users['admin'].email)
        assert isinstance(response, UserModel)
        assert response.user_id == test_users['admin'].user_id

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found_returns_none(self, db_session: AsyncSession):
        """Проверяет, что при несуществующем email возвращается None."""
        repo = UserRepository(db_session)
        response = await repo.get_by_email('mnbvcx@mail.ru')
        assert response is None

    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self, db_session: AsyncSession, test_users):
        """Проверяет получение пользователя по username."""
        repo = UserRepository(db_session)
        response = await repo.get_by_username(test_users['admin'].username)
        assert isinstance(response, UserModel)
        assert response.user_id == test_users['admin'].user_id
        assert response.email == test_users['admin'].email

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found_returns_none(self, db_session: AsyncSession):
        """Проверяет, что при несуществующем username возвращается None."""
        repo = UserRepository(db_session)
        response = await repo.get_by_username('dhjhs')
        assert response is None

    @pytest.mark.asyncio
    async def test_update_username_success(self, db_session: AsyncSession, test_users):
        """Проверяет успешное обновление username."""
        repo = UserRepository(db_session)
        first_username = test_users['user_profile'].username
        response = await repo.update_username(test_users['user_profile'].user_id, f'update_{uuid.uuid4().hex[:8]}')
        update_user = await repo.get_by_id(test_users['user_profile'].user_id)
        assert response is True
        assert first_username != update_user.username

    @pytest.mark.asyncio
    async def test_update_email_success(self, db_session: AsyncSession, test_users):
        """Проверяет успешное обновление email."""
        repo = UserRepository(db_session)
        first_email = test_users['user_profile'].email
        response = await repo.update_email(test_users['user_profile'].user_id, f'update_{uuid.uuid4().hex[:8]}@mail.ru')
        update_user = await repo.get_by_id(test_users['user_profile'].user_id)
        assert response is True
        assert first_email != update_user.email

    @pytest.mark.asyncio 
    async def test_update_user_password_hash_success(self, db_session: AsyncSession):
        """Тест для обновления пароля (пропущен, так как метод не реализован)."""
        #Функционала с обновлением пароля пока нет, надо добавить 
        pytest.skip("Метод обновления пароля ещё не реализован")

    @pytest.mark.asyncio
    async def test_update_email_not_found_raises_error_or_returns_none(self, db_session: AsyncSession):
        """Проверяет, что при обновлении email несуществующего пользователя возвращается False."""
        repo = UserRepository(db_session)
        response = await repo.update_email(999999, f'{uuid.uuid4().hex[:8]}@mail.ru')
        assert response is False

    @pytest.mark.asyncio
    async def test_update_username_not_found_raises_error_or_returns_none(self, db_session: AsyncSession):
        """Проверяет, что при обновлении username несуществующего пользователя возвращается False."""
        repo = UserRepository(db_session)
        response = await repo.update_username(999999, 'update_username')
        assert response is False

    @pytest.mark.asyncio
    async def test_delete_user_success(self, db_session: AsyncSession, test_users):
        """Проверяет успешное удаление пользователя."""
        repo = UserRepository(db_session)
        user_id = test_users['outsider'].user_id
        result = await repo.delete_user(user_id)
        assert result is True
        deleted_user = await repo.get_by_id(user_id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_delete_user_not_found_raises_error_or_ignores(self, db_session: AsyncSession):
        """Проверяет, что при удалении несуществующего пользователя возвращается False."""
        repo = UserRepository(db_session)
        result = await repo.delete_user(999999)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_user_cascades_to_related_entities(self, db_session: AsyncSession):
        """Проверяет, что удаление пользователя, у которого есть связанные проекты, вызывает IntegrityError (из-за внешнего ключа)."""
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
            admin_id=new_user.user_id
        )
        with pytest.raises(IntegrityError):
            await repo.delete_user(new_user.user_id)

    @pytest.mark.asyncio
    async def test_check_user_exists_true(self, db_session: AsyncSession, test_users):
        """Проверяет, что для существующего пользователя возвращается True."""
        repo = UserRepository(db_session)
        user = test_users['admin']
        result = await repo.check_user_exists(user.user_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_check_user_exists_false(self, db_session: AsyncSession):
        """Проверяет, что для несуществующего пользователя возвращается False."""
        repo = UserRepository(db_session)
        result = await repo.check_user_exists(99999)
        assert result is False

    @pytest.mark.asyncio
    async def test_check_user_exists_by_username_true(self, db_session: AsyncSession, test_users):
        """Проверяет, что для существующего username возвращается True."""
        repo = UserRepository(db_session)
        user = test_users['admin']
        result = await repo.check_user_exists_by_username(user.username)
        assert result is True

    @pytest.mark.asyncio
    async def test_check_user_exists_by_username_false(self, db_session: AsyncSession):
        """Проверяет, что для несуществующего username возвращается False."""
        repo = UserRepository(db_session)
        result = await repo.check_user_exists_by_username('nonexistent')
        assert result is False

    @pytest.mark.asyncio
    async def test_check_user_exists_by_email_true(self, db_session: AsyncSession, test_users):
        """Проверяет, что для существующего email возвращается True."""
        repo = UserRepository(db_session)
        user = test_users['admin']
        result = await repo.check_user_exists_by_email(user.email)
        assert result is True

    @pytest.mark.asyncio
    async def test_check_user_exists_by_email_false(self, db_session: AsyncSession):
        """Проверяет, что для несуществующего email возвращается False."""
        repo = UserRepository(db_session)
        result = await repo.check_user_exists_by_email('nonexistent@mail.ru')
        assert result is False

    @pytest.mark.asyncio
    async def test_check_user_correct_password_by_email_success(self, db_session: AsyncSession, test_users):
        """Проверяет успешную проверку пароля по email."""
        repo = UserRepository(db_session)
        user = test_users['admin']
        result = await repo.check_user_correct_password_by_email(user.email, 'qwertyui')
        assert result is True

    @pytest.mark.asyncio
    async def test_check_user_correct_password_by_email_wrong_password(self, db_session: AsyncSession, test_users):
        """Проверяет, что при неверном пароле возвращается False."""
        repo = UserRepository(db_session)
        user = test_users['admin']
        result = await repo.check_user_correct_password_by_email(user.email, 'wrongpass')
        assert result is False

    @pytest.mark.asyncio
    async def test_check_user_correct_password_by_email_user_not_found(self, db_session: AsyncSession):
        """Проверяет, что для несуществующего email возвращается False."""
        repo = UserRepository(db_session)
        result = await repo.check_user_correct_password_by_email('nonexistent@mail.ru', 'qwertyui')
        assert result is False

    @pytest.mark.asyncio
    async def test_check_user_exists_by_username_excluding_current_true(self, db_session: AsyncSession, test_users):
        """Проверяет, что существует другой пользователь с таким же username (кроме текущего)."""
        repo = UserRepository(db_session)
        admin = test_users['admin']
        member = test_users['member']
        result = await repo.check_user_exists_by_username_excluding_current(member.username, admin.user_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_check_user_exists_by_username_excluding_current_false(self, db_session: AsyncSession, test_users):
        """Проверяет, что при поиске самого себя возвращается False (исключение работает)."""
        repo = UserRepository(db_session)
        admin = test_users['admin']
        result = await repo.check_user_exists_by_username_excluding_current(admin.username, admin.user_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_check_user_exists_by_email_excluding_current_true(self, db_session: AsyncSession, test_users):
        """Проверяет, что существует другой пользователь с таким же email (кроме текущего)."""
        repo = UserRepository(db_session)
        admin = test_users['admin']
        member = test_users['member']
        result = await repo.check_user_exists_by_email_excluding_current(member.email, admin.user_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_check_user_exists_by_email_excluding_current_false(self, db_session: AsyncSession, test_users):
        """Проверяет, что при поиске самого себя возвращается False (исключение работает)."""
        repo = UserRepository(db_session)
        admin = test_users['admin']
        result = await repo.check_user_exists_by_email_excluding_current(admin.email, admin.user_id)
        assert result is False