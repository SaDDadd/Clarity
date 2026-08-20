import pytest
from core.security import create_access_token
import uuid

@pytest.mark.asyncio
async def test_send_invitation_by_admin(async_client, test_project, test_users, auth_headers):
    """Проверяет, что администратор проекта может отправить приглашение."""
    headers = auth_headers
    project_id = test_project.project_id
    invitee_id = test_users['outsider'].user_id

    response = await async_client.post(
        f'/api/v1/projects/{project_id}/invitations',
        json={
            'user_id': invitee_id,
            'message': 'Присоединяйся к нашему проекту!'
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data['invitee_id'] == invitee_id
    assert data['status_invited'] == 'pending'

@pytest.mark.asyncio
async def test_send_invitation_by_non_admin(async_client, test_project, test_users, member_auth_headers):
    """Проверяет, что участник (не админ) не может отправить приглашение."""
    headers = member_auth_headers
    project_id = test_project.project_id
    invitee_id = test_users['outsider'].user_id

    response = await async_client.post(
        f'/api/v1/projects/{project_id}/invitations',
        json={'user_id': invitee_id},
        headers=headers
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_user_invitations(async_client, test_invitation, auth_headers):
    """Проверяет получение списка входящих приглашений для пользователя."""
    headers = auth_headers

    response = await async_client.get(
        '/api/v1/invitations',
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

@pytest.mark.asyncio
async def test_get_project_invitations_by_admin(async_client, test_project, test_invitation, auth_headers):
    """Проверяет, что администратор получает список приглашений проекта."""
    headers = auth_headers
    project_id = test_project.project_id

    response = await async_client.get(
        f'/api/v1/invitations/project/{project_id}',
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

@pytest.mark.asyncio
async def test_get_project_invitations_by_non_admin(async_client, test_project, member_auth_headers):
    """Проверяет, что участник (не админ) не может получить список приглашений проекта."""
    headers = member_auth_headers
    project_id = test_project.project_id

    response = await async_client.get(
        f'/api/v1/invitations/project/{project_id}',
        headers=headers
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_accept_invitation(async_client, test_invitation, test_users):
    """Проверяет, что пользователь может принять приглашение."""
    invitee = test_users['outsider']
    token = create_access_token({'sub': invitee.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    invitation_id = test_invitation.invitation_id

    response = await async_client.patch(
        f'/api/v1/invitations/{invitation_id}',
        json={'status': 'accepted'},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'Приглашение принято'

@pytest.mark.asyncio
async def test_reject_invitation(async_client, test_invitation, test_users):
    """Проверяет, что пользователь может отклонить приглашение."""
    invitee = test_users['outsider']
    token = create_access_token({'sub': invitee.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    invitation_id = test_invitation.invitation_id

    response = await async_client.patch(
        f'/api/v1/invitations/{invitation_id}',
        json={'status': 'rejected'},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'Приглашение отклонено'


@pytest.mark.asyncio
async def test_cancel_invitation_by_admin(async_client, test_invitation, auth_headers):
    """Проверяет, что администратор может отменить приглашение."""
    headers = auth_headers
    invitation_id = test_invitation.invitation_id

    response = await async_client.delete(
        f'/api/v1/invitations/{invitation_id}',
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'Приглашение отменено'


@pytest.mark.asyncio
async def test_cancel_invitation_by_non_admin(async_client, test_invitation, member_auth_headers):
    """Проверяет, что участник (не админ и не пригласивший) не может отменить приглашение."""
    headers = member_auth_headers
    invitation_id = test_invitation.invitation_id

    response = await async_client.delete(
        f'/api/v1/invitations/{invitation_id}',
        headers=headers
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_accept_already_processed_invitation(async_client, test_invitation, test_users):
    """Проверяет, что нельзя принять уже обработанное приглашение."""
    invitee = test_users['outsider']
    token = create_access_token({'sub': invitee.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    invitation_id = test_invitation.invitation_id

    await async_client.patch(
        f'/api/v1/invitations/{invitation_id}',
        json={'status': 'accepted'},
        headers=headers
    )
    response = await async_client.patch(
        f'/api/v1/invitations/{invitation_id}',
        json={'status': 'accepted'},
        headers=headers
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_cancel_invitation_by_outsider(async_client, test_invitation, test_users):
    """Проверяет, что посторонний пользователь не может отменить приглашение."""
    outsider = test_users['outsider']
    token = create_access_token({'sub': outsider.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    invitation_id = test_invitation.invitation_id

    response = await async_client.delete(
        f'/api/v1/invitations/{invitation_id}',
        headers=headers
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_project_invitations_by_outsider(async_client, test_project, test_users):
    """Проверяет, что пользователь, не состоящий в проекте, не может получить список приглашений проекта."""
    outsider = test_users['outsider']
    token = create_access_token({'sub': outsider.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    project_id = test_project.project_id

    response = await async_client.get(
        f'/api/v1/invitations/project/{project_id}',
        headers=headers
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_send_invitation_to_existing_member(async_client, test_project, test_users, auth_headers):
    """Приглашение пользователя, уже состоящего в проекте."""
    headers = auth_headers
    project_id = test_project.project_id
    member_id = test_users['member'].user_id
    response = await async_client.post(
        f'/api/v1/projects/{project_id}/invitations',
        json={'user_id': member_id},
        headers=headers
    )
    assert response.status_code == 409
    assert response.json()['detail'] == 'Пользователь уже состоит в проекте'

@pytest.mark.asyncio
async def test_send_invitation_to_self(async_client, test_project, auth_headers, test_users):
    """Админ приглашает самого себя."""
    headers = auth_headers
    project_id = test_project.project_id
    admin_id = test_users['admin'].user_id
    response = await async_client.post(
        f'/api/v1/projects/{project_id}/invitations',
        json={'user_id': admin_id},
        headers=headers
    )
    assert response.status_code in (400, 409)


@pytest.mark.asyncio
async def test_send_invitation_to_nonexistent_user(async_client, test_project, auth_headers):
    """Приглашение несуществующего пользователя."""
    headers = auth_headers
    project_id = test_project.project_id
    response = await async_client.post(
        f'/api/v1/projects/{project_id}/invitations',
        json={'user_id': 99999},
        headers=headers
    )
    assert response.status_code == 404
    assert response.json()['detail'] == 'Пользователь не найден'

@pytest.mark.asyncio
async def test_reject_invitation_already_processed(async_client, test_invitation, test_users):
    """Отклонение уже принятого приглашения."""
    invitee = test_users['outsider']
    token = create_access_token({'sub': invitee.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    inv_id = test_invitation.invitation_id

    # сначала принимаем
    await async_client.patch(
        f'/api/v1/invitations/{inv_id}',
        json={'status': 'accepted'},
        headers=headers
    )
    # теперь пытаемся отклонить
    response = await async_client.patch(
        f'/api/v1/invitations/{inv_id}',
        json={'status': 'rejected'},
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()['detail'] == 'Приглашение уже обработано'

@pytest.mark.asyncio
async def test_accept_invitation_already_rejected(async_client, test_invitation, test_users):
    """Принятие уже отклонённого приглашения."""
    invitee = test_users['outsider']
    token = create_access_token({'sub': invitee.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    inv_id = test_invitation.invitation_id

    # сначала отклоняем
    await async_client.patch(
        f'/api/v1/invitations/{inv_id}',
        json={'status': 'rejected'},
        headers=headers
    )
    # теперь пытаемся принять
    response = await async_client.patch(
        f'/api/v1/invitations/{inv_id}',
        json={'status': 'accepted'},
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()['detail'] == 'Приглашение уже обработано'

@pytest.mark.asyncio
async def test_cancel_invitation_already_processed(async_client, test_invitation, auth_headers, test_users):
    """Отмена уже принятого приглашения администратором."""
    headers = auth_headers
    inv_id = test_invitation.invitation_id

    # принимаем от имени приглашённого
    invitee = test_users['outsider']
    token = create_access_token({'sub': invitee.user_id})
    accept_headers = {'Authorization': f'Bearer {token}'}
    await async_client.patch(
        f'/api/v1/invitations/{inv_id}',
        json={'status': 'accepted'},
        headers=accept_headers
    )

    # пытаемся отменить админом
    response = await async_client.delete(
        f'/api/v1/invitations/{inv_id}',
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()['detail'] == 'Приглашение уже обработано'

@pytest.mark.asyncio
async def test_get_user_invitations_empty(async_client):
    """Пользователь без приглашений получает пустой список."""
    # регистрируем нового пользователя
    new_username = str(uuid.uuid4())
    new_email = f'{uuid.uuid4()}@mail.ru'
    reg_resp = await async_client.post(
        '/api/v1/auth/register',
        json={'username': new_username, 'email': new_email, 'password': '123456789'}
    )
    assert reg_resp.status_code == 201

    # логинимся, получаем токен
    login_resp = await async_client.post(
        '/api/v1/auth/login',
        json={'username_or_email': new_username, 'password': '123456789'}
    )
    token = login_resp.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # проверяем список приглашений – должен быть пустым
    response = await async_client.get('/api/v1/invitations', headers=headers)
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_get_project_invitations_empty(async_client, auth_headers):
    """Проект без приглашений возвращает пустой список."""
    headers = auth_headers
    # создаём новый проект
    create_resp = await async_client.post(
        '/api/v1/projects',
        json={'project_name': 'EmptyProject', 'project_description': ''},
        headers=headers
    )
    assert create_resp.status_code == 201
    project_id = create_resp.json()['project_id']

    # запрашиваем приглашения этого проекта
    response = await async_client.get(
        f'/api/v1/invitations/project/{project_id}',
        headers=headers
    )
    assert response.status_code == 200
    assert response.json() == []