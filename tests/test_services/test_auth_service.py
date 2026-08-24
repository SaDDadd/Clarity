import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from services.auth_service import register_user, login_user
from repositories.user_repository import UserRepository
from schemas.auth import UserRegister, UserLogin, Token
from core.exceptions import LackOfInformationException, ConflictException, AuthenticationException
from core.security import decode_access_token


class TestAuthService:
    @pytest.mark.asyncio
    async def test_register_user_success(self, db_session: AsyncSession):
        """Проверяет успешную регистрацию нового пользователя."""
        repo = UserRepository(db_session)
        user_data = UserRegister(
            username=f'{uuid.uuid4().hex[:8]}',
            email=f'{uuid.uuid4().hex[:8]}@gmail.com',
            password='qwertyui'
        )
        response = await register_user(db_session, user_data)
        assert response.get('message') == 'Пользователь создан'
        assert await repo.get_by_username(user_data.username) is not None

    @pytest.mark.asyncio
    async def test_register_user_empty_username(self, db_session: AsyncSession):
        """Проверяет, что при пустом имени пользователя выбрасывается LackOfInformationException."""
        with pytest.raises(LackOfInformationException) as exc_info:
            user_data = UserRegister(
                username='',
                email=f'{uuid.uuid4().hex[:8]}@gmail.com',
                password='qwertyui'
            )
            await register_user(db_session, user_data)
        assert exc_info.value.detail == 'Нехватка информации!'
        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_register_user_short_password(self, db_session: AsyncSession):
        """Проверяет, что при пароле короче 8 символов выбрасывается LackOfInformationException."""
        with pytest.raises(LackOfInformationException) as exc_info:
            user_data = UserRegister(
                username=f'{uuid.uuid4().hex[:8]}',
                email=f'{uuid.uuid4().hex[:8]}@gmail.com',
                password='12'
            )
            await register_user(db_session, user_data)
        assert exc_info.value.detail == 'Пароль короткий, должен быть больше 8 символов!'
        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_register_user_duplicate_username(self, db_session: AsyncSession, test_users):
        """Проверяет, что при попытке использовать уже существующее имя пользователя выбрасывается ConflictException."""
        with pytest.raises(ConflictException) as exc_info:
            user_data = UserRegister(
                username=test_users['admin'].username,
                email=f'{uuid.uuid4().hex[:8]}@gmail.com',
                password='qwertyui'
            )
            await register_user(db_session, user_data)
        assert exc_info.value.detail == 'Имя пользователя уже существует!'
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, db_session: AsyncSession, test_users):
        """Проверяет, что при попытке использовать уже существующий email выбрасывается ConflictException."""
        with pytest.raises(ConflictException) as exc_info:
            user_data = UserRegister(
                username=f'{uuid.uuid4().hex[:8]}',
                email=test_users['admin'].email,
                password='qwertyui'
            )
            await register_user(db_session, user_data)
        assert exc_info.value.detail == 'Email пользователя уже существует!'
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_login_user_success_by_username(self, db_session: AsyncSession, test_users):
        """Проверяет успешный вход пользователя по имени пользователя, возвращается объект Token."""
        user_data = UserLogin(
            username_or_email=test_users['admin'].username,
            password='qwertyui'
        )
        response = await login_user(db_session, user_data)
        assert isinstance(response, Token)
        assert response.token_type == 'bearer'
        assert response.expires_in == 30 * 60

    @pytest.mark.asyncio
    async def test_login_user_success_by_email(self, db_session: AsyncSession, test_users):
        """Проверяет успешный вход пользователя по email, возвращается объект Token."""
        user_data = UserLogin(
            username_or_email=test_users['admin'].email,
            password='qwertyui'
        )
        response = await login_user(db_session, user_data)
        assert isinstance(response, Token)
        assert response.token_type == 'bearer'

    @pytest.mark.asyncio
    async def test_login_user_wrong_password(self, db_session: AsyncSession, test_users):
        """Проверяет, что при неверном пароле выбрасывается AuthenticationException."""
        with pytest.raises(AuthenticationException) as exc_info:
            user_data = UserLogin(
                username_or_email=test_users['admin'].username,
                password='wrongpassword'
            )
            await login_user(db_session, user_data)
        assert exc_info.value.detail == 'Неверные учётные данные!'
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, db_session: AsyncSession):
        """Проверяет, что при несуществующем пользователе выбрасывается AuthenticationException."""
        with pytest.raises(AuthenticationException) as exc_info:
            user_data = UserLogin(
                username_or_email=f'{uuid.uuid4().hex[:8]}',
                password='qwertyui'
            )
            await login_user(db_session, user_data)
        assert exc_info.value.detail == 'Неверные учётные данные!'
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_user_empty_username_or_email(self, db_session: AsyncSession):
        """Проверяет, что при пустом поле username_or_email выбрасывается LackOfInformationException."""
        with pytest.raises(LackOfInformationException) as exc_info:
            user_data = UserLogin(
                username_or_email='',
                password='qwertyui'
            )
            await login_user(db_session, user_data)
        assert exc_info.value.detail == 'Нехватка информации!'
        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_login_user_empty_password(self, db_session: AsyncSession, test_users):
        """Проверяет, что при пустом пароле выбрасывается LackOfInformationException."""
        with pytest.raises(LackOfInformationException) as exc_info:
            user_data = UserLogin(
                username_or_email=test_users['admin'].username,
                password=''
            )
            await login_user(db_session, user_data)
        assert exc_info.value.detail == 'Нехватка информации!'
        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_login_user_returns_valid_token(self, db_session: AsyncSession, test_users):
        """Проверяет, что возвращаемый токен содержит корректный sub и exp, а также правильные token_type и expires_in."""
        user_data = UserLogin(
            username_or_email=test_users['admin'].username,
            password='qwertyui'
        )
        response = await login_user(db_session, user_data)
        assert isinstance(response, Token)
        payload = decode_access_token(response.access_token)
        assert 'sub' in payload
        assert str(test_users['admin'].user_id) == payload['sub']
        assert 'exp' in payload
        assert isinstance(payload['exp'], int)
        assert response.token_type == 'bearer'
        assert response.expires_in == 30 * 60

    @pytest.mark.asyncio
    async def test_login_user_wrong_password_by_email(self, db_session: AsyncSession, test_users):
        """Проверяет, что при входе по email с неверным паролем выбрасывается AuthenticationException."""
        with pytest.raises(AuthenticationException) as exc_info:
            user_data = UserLogin(
                username_or_email=test_users['admin'].email,
                password='wrongpassword'
            )
            await login_user(db_session, user_data)
        assert exc_info.value.detail == 'Неверные учётные данные!'
        assert exc_info.value.status_code == 401