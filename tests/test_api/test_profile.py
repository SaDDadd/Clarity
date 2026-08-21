import pytest

@pytest.mark.asyncio
async def test_update_username_success(async_client, auth_headers):
    """Проверяет, что аутентифицированный пользователь может успешно обновить своё имя."""
    headers = auth_headers
    new_username = "new_username_123"
    response = await async_client.put(
        '/api/v1/profile/username',
        json={"username": new_username},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'Имя пользователя обновлено!'

@pytest.mark.asyncio
async def test_update_username_unauthorized(async_client):
    """Проверяет, что запрос без токена возвращает."""
    response = await async_client.put(
        '/api/v1/profile/username',
        json={"username": "new_username"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_email_success(async_client, auth_headers):
    """Проверяет, что аутентифицированный пользователь может успешно обновить email."""
    headers = auth_headers
    new_email = "new_email@example.com"
    response = await async_client.put(
        '/api/v1/profile/email',
        json={"email": new_email},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'Email пользователя обновлено!'

@pytest.mark.asyncio
async def test_update_email_unauthorized(async_client):
    """Проверяет, что запрос без токена возвращает."""
    response = await async_client.put(
        '/api/v1/profile/email',
        json={"email": "new_email@example.com"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_profile_success(async_client, auth_headers, test_users):
    """Проверяет, что аутентифицированный пользователь может получить свои данные."""
    headers = auth_headers
    response = await async_client.get('/api/v1/profile', headers=headers)
    assert response.status_code == 200
    data = response.json()
    admin = test_users['admin']
    assert data['user_id'] == admin.user_id
    assert data['username'] == admin.username
    assert data['email'] == admin.email

@pytest.mark.asyncio
async def test_update_username_conflict(async_client, auth_headers, test_users):
    """Обновление username на уже существующий."""
    headers = auth_headers
    conflicting_username = test_users['member'].username
    response = await async_client.put(
        '/api/v1/profile/username',
        json={'username': conflicting_username},
        headers=headers
    )
    assert response.status_code == 409
    assert response.json()['detail'] == 'Пользователь с таким именем уже существует!'

@pytest.mark.asyncio
async def test_update_email_conflict(async_client, auth_headers, test_users):
    """Обновление email на уже существующий."""
    headers = auth_headers
    conflicting_email = test_users['member'].email
    response = await async_client.put(
        '/api/v1/profile/email',
        json={'email': conflicting_email},
        headers=headers
    )
    assert response.status_code == 409
    assert response.json()['detail'] == 'Пользователь с таким email уже существует!'

@pytest.mark.asyncio
async def test_update_username_empty(async_client, auth_headers):
    """Обновление username на пустую строку."""
    headers = auth_headers
    response = await async_client.put(
        '/api/v1/profile/username',
        json={'username': ''},
        headers=headers
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_email_invalid(async_client, auth_headers):
    """Обновление email на невалидный."""
    headers = auth_headers
    response = await async_client.put(
        '/api/v1/profile/email',
        json={'email': 'invalid_email'},
        headers=headers
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_username_too_long(async_client, auth_headers):
    """Обновление username на слишком длинное значение."""
    headers = auth_headers
    long_username = 'a' * 1000
    response = await async_client.put(
        '/api/v1/profile/username',
        json={'username': long_username},
        headers=headers
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_email_too_long(async_client, auth_headers):
    """Обновление email на слишком длинное значение."""
    headers = auth_headers
    long_email = 'a' * 1000 + '@example.com'
    response = await async_client.put(
        '/api/v1/profile/email',
        json={'email': long_email},
        headers=headers
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_profile_unauthorized(async_client):
    """Запрос /profile без токена."""
    response = await async_client.get('/api/v1/profile')
    assert response.status_code == 401