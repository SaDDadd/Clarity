import pytest
from core.security import create_access_token

@pytest.mark.asyncio
async def test_send_invitation_by_admin(async_client, test_project, test_users, auth_headers):
    """Проверяет, что администратор проекта может отправить приглашение."""
    headers = await auth_headers
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
    headers = await member_auth_headers
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
    headers = await auth_headers

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
    headers = await auth_headers
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
    headers = await member_auth_headers
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
    headers = await auth_headers
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
    headers = await member_auth_headers
    invitation_id = test_invitation.invitation_id

    response = await async_client.delete(
        f'/api/v1/invitations/{invitation_id}',
        headers=headers
    )
    assert response.status_code == 403