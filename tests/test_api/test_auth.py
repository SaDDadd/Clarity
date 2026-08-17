import pytest
import uuid

@pytest.mark.asyncio
async def test_register_success(async_client):
    response = await async_client.post('/api/v1/auth/register', json={'username': f'{uuid.uuid4()}', 'email': f'{uuid.uuid4}@mail.ru',
                                                                      'password': '123456789'})
    assert response.status_code == 201
    assert response.json() == {"message": "Пользователь создан"}

async def test_register_duplicate_username():

async def test_register_duplicate_email():

async def test_register_invalid_data():

async def test_login_success_username():

async def test_login_success_email():

async def test_login_wrong_password():

async def test_login_user_not_found():

async def test_login_empty_fields():