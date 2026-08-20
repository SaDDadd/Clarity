import pytest

@pytest.mark.asyncio
async def test_update_username_success(async_client, auth_headers):
    """Проверяет, что аутентифицированный пользователь может успешно обновить своё имя."""
    headers = await auth_headers
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
    """Проверяет, что запрос без токена возвращает 401."""
    response = await async_client.put(
        '/api/v1/profile/username',
        json={"username": "new_username"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_email_success(async_client, auth_headers):
    """Проверяет, что аутентифицированный пользователь может успешно обновить email."""
    headers = await auth_headers
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
    """Проверяет, что запрос без токена возвращает 401."""
    response = await async_client.put(
        '/api/v1/profile/email',
        json={"email": "new_email@example.com"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_profile_success(async_client, auth_headers, test_user):
    """Проверяет, что аутентифицированный пользователь может получить свои данные."""
    headers = await auth_headers
    response = await async_client.get('/api/v1/profile', headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data['user_id'] == test_user.user_id
    assert data['username'] == test_user.username
    assert data['email'] == test_user.email