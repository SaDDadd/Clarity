import pytest
import uuid

@pytest.mark.asyncio
async def test_register_success(async_client):
    response = await async_client.post('/api/v1/auth/register', json={'username': f'{uuid.uuid4()}', \
                                            'email': f'{uuid.uuid4()}@mail.ru','password': '123456789'})
    assert response.status_code == 201
    assert response.json() == {"message": "Пользователь создан"}

@pytest.mark.asyncio
async def test_register_duplicate_username(async_client, test_user):
    response = await async_client.post('/api/v1/auth/register', json={'username': f'{test_user[0].username}', 'email': f'{uuid.uuid4()}@mail.ru', \
                                                                      'password': '123456789'})
    assert response.status_code == 409
    assert response.json()['detail'] == 'Имя пользователя уже существует!'

@pytest.mark.asyncio
async def test_register_duplicate_email(async_client, test_user):
    response = await async_client.post('/api/v1/auth/register', json={'username': f'{uuid.uuid4()}', 'email': f'{test_user[0].email}', \
                                                                      'password': '123456789'})
    assert response.status_code == 409
    assert response.json()['detail'] == 'Email пользователя уже существует!'

@pytest.mark.asyncio
async def test_login_success_username(async_client, test_user):
    response = await async_client.post('/api/v1/auth/login', json={'username_or_email': f'{test_user[0].username}', \
                                                                   'password': f'{test_user[1].password}'})
    data = response.json()
    len_token = len(data['access_token'].split('.'))
    assert response.status_code == 200
    assert data['access_token'] and data['token_type']
    assert data['token_type'] == 'bearer'
    assert isinstance(data['access_token'], str)
    assert len_token == 3

@pytest.mark.asyncio
async def test_login_success_email(async_client, test_user):
    response = await async_client.post('/api/v1/auth/login', json={'username_or_email': f'{test_user[0].email}', \
                                                                   'password': f'{test_user[1].password}'})
    data = response.json()
    len_token = len(data['access_token'].split('.'))
    assert response.status_code == 200
    assert data['access_token'] and data['token_type']
    assert data['token_type'] == 'bearer'
    assert isinstance(data['access_token'], str)
    assert len_token == 3

@pytest.mark.asyncio
async def test_login_wrong_password(async_client, test_user):
    response = await async_client.post('/api/v1/auth/login', json={'username_or_email': f'{test_user[0].email}', \
                                                                  'password': f'{uuid.uuid4()}'})
    assert response.status_code == 401
    assert response.json()['detail'] == 'Неверные учётные данные!'

@pytest.mark.asyncio
async def test_login_user_not_found(async_client):
    response = await async_client.post('/api/v1/auth/login', json={'username_or_email': f'{uuid.uuid4()}', \
                                                                  'password': f'{uuid.uuid4()}'})
    assert response.status_code == 401
    assert response.json()['detail'] == 'Неверные учётные данные!'

@pytest.mark.asyncio
async def test_login_empty_fields(async_client):
    response = await async_client.post('/api/v1/auth/login', json={'username_or_email': '', \
                                                                   'password': ''})
    assert response.status_code == 422
    assert response.json()['detail'] == 'Нехватка информации!'

@pytest.mark.asyncio
async def test_short_password(async_client):
    response = await async_client.post('/api/v1/auth/register', json={'username': f'{uuid.uuid4()}', 'email': f'{uuid.uuid4()}@mail.ru', \
                                                                      'password': '1234'})
    assert response.status_code == 422
    assert response.json()['detail'] == 'Пароль короткий, должен быть больше 8 символов!'

@pytest.mark.asyncio
async def test_get_current_user_info(async_client, auth_headers, test_user):
    """Проверяет, что аутентифицированный пользователь может получить свои данные через /auth/me."""
    headers = await auth_headers
    response = await async_client.get('/api/v1/auth/me', headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data['user_id'] == test_user.user_id
    assert data['username'] == test_user.username
    assert data['email'] == test_user.email