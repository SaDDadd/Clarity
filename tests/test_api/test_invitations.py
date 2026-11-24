import pytest
from core.security import create_access_token


@pytest.mark.asyncio
async def test_send_invitation_by_non_admin(async_client, test_project, test_users, member_auth_headers):
    """Проверяет, что участник (не админ) не может отправить приглашение."""
    headers = member_auth_headers
    project_id = test_project.project_id
    invitee_id = test_users['outsider'].user_id

    response = await async_client.post(
        f'/api/v1/projects/{project_id}/invitations',
        json={'user_id': invitee_id, 'message': 'test'},
        headers=headers
    )
    assert response.status_code == 403


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
    invitee = test_users['outsider']
    token = create_access_token({'sub': invitee.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    invitation_id = test_invitation.invitation_id

    response = await async_client.patch(
        f'/api/v1/invitations/{invitation_id}',
        json={'action': 'accepted'},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'Приглашение accepted!'

@pytest.mark.asyncio
async def test_reject_invitation(async_client, test_invitation, test_users):
    invitee = test_users['outsider']
    token = create_access_token({'sub': invitee.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    invitation_id = test_invitation.invitation_id

    response = await async_client.patch(
        f'/api/v1/invitations/{invitation_id}',
        json={'action': 'declined'},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'Приглашение declined!'


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
    assert response.json()['message'] == 'Приглашение удалено!'


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
        json={'action': 'accepted'},
        headers=headers
    )
    response = await async_client.patch(
        f'/api/v1/invitations/{invitation_id}',
        json={'action': 'accepted'},
        headers=headers
    )
    assert response.status_code == 409

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
async def test_send_invitation_to_existing_member(async_client, test_project_with_member, test_users, auth_headers):
    headers = auth_headers
    project = test_project_with_member['project']
    member_id = test_users['member'].user_id
    response = await async_client.post(
        f'/api/v1/projects/{project.project_id}/invitations',
        json={'user_id': member_id, 'message': 'test'},
        headers=headers
    )
    assert response.status_code == 409
    assert response.json()['detail'] == 'Пользователь уже является участником проекта!'

@pytest.mark.asyncio
async def test_send_invitation_to_self(async_client, test_project, auth_headers, test_users):
    """Админ приглашает самого себя."""
    headers = auth_headers
    project_id = test_project.project_id
    admin_id = test_users['admin'].user_id
    response = await async_client.post(
        f'/api/v1/projects/{project_id}/invitations',
        json={'user_id': admin_id, 'message': 'test'},
        headers=headers
    )
    assert response.status_code in (400, 409)


@pytest.mark.asyncio
async def test_send_invitation_to_nonexistent_user(async_client, test_project, auth_headers):
    headers = auth_headers
    project_id = test_project.project_id
    response = await async_client.post(
        f'/api/v1/projects/{project_id}/invitations',
        json={'user_id': 99999, 'message': 'test'},
        headers=headers
    )
    assert response.status_code == 404
    assert response.json()['detail'] == 'Пользователь не найден!'

@pytest.mark.asyncio
async def test_reject_invitation_already_processed(async_client, test_invitation, test_users):
    invitee = test_users['outsider']
    token = create_access_token({'sub': invitee.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    inv_id = test_invitation.invitation_id

    # сначала принимаем
    await async_client.patch(
        f'/api/v1/invitations/{inv_id}',
        json={'action': 'accepted'},
        headers=headers
    )
    # теперь пытаемся отклонить
    response = await async_client.patch(
        f'/api/v1/invitations/{inv_id}',
        json={'action': 'declined'},
        headers=headers
    )
    assert response.status_code == 409
    assert response.json()['detail'] == 'Приглашение уже было принято или отклонено!'

@pytest.mark.asyncio
async def test_accept_invitation_already_rejected(async_client, test_invitation, test_users):
    invitee = test_users['outsider']
    token = create_access_token({'sub': invitee.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    inv_id = test_invitation.invitation_id

    # сначала отклоняем
    await async_client.patch(
        f'/api/v1/invitations/{inv_id}',
        json={'action': 'declined'},
        headers=headers
    )
    # теперь пытаемся принять
    response = await async_client.patch(
        f'/api/v1/invitations/{inv_id}',
        json={'action': 'accepted'},
        headers=headers
    )
    assert response.status_code == 409
    assert response.json()['detail'] == 'Приглашение уже было принято или отклонено!'

@pytest.mark.asyncio
async def test_cancel_invitation_already_processed(async_client, test_invitation, auth_headers, test_users):
    headers = auth_headers
    inv_id = test_invitation.invitation_id

    # принимаем от имени приглашённого
    invitee = test_users['outsider']
    token = create_access_token({'sub': invitee.user_id})
    accept_headers = {'Authorization': f'Bearer {token}'}
    await async_client.patch(
        f'/api/v1/invitations/{inv_id}',
        json={'action': 'accepted'},
        headers=accept_headers
    )

    # пытаемся отменить админом
    response = await async_client.delete(
        f'/api/v1/invitations/{inv_id}',
        headers=headers
    )
    assert response.status_code == 409
    assert response.json()['detail'] == 'Приглашение уже обработано!'