import pytest
from core.security import create_access_token


@pytest.mark.asyncio
async def test_successful_project_creation(async_client, auth_headers):
    headers = auth_headers
    response = await async_client.post('/api/v1/projects', \
                                       json={'project_name': 'Test_project', 'project_description': ''},headers=headers)
    assert response.status_code == 201
    assert response.json()['project_id']
    assert response.json()['project_name'] == 'Test_project'

@pytest.mark.asyncio
async def test_attempt_create_project_without_authorization(async_client):
    response = await async_client.post('/api/v1/projects', \
        json={'project_name': 'Test_project', 'project_description': ''})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_attempt_create_project_with_incorrect_data(async_client, auth_headers):
    headers = auth_headers
    response = await async_client.post('/api/v1/projects', \
        json={'project_name': '', 'project_description': '12345'},headers=headers)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_authorized_admin_projects_returned(async_client, auth_headers):
    headers = auth_headers
    response = await async_client.get('/api/v1/projects', headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_attempt_get_non_existent_project(async_client, auth_headers):
    headers = auth_headers
    response = await async_client.get('/api/v1/projects/9999', headers=headers)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Проект не найден!'

@pytest.mark.asyncio
async def test_attempt_get_project_that_user_not_part(async_client, test_project, test_users):
    outsider = test_users.get('outsider')
    token = create_access_token({'sub': outsider.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    response = await async_client.get(f'/api/v1/projects/{test_project.project_id}',headers=headers)
    assert response.status_code == 403 

@pytest.mark.asyncio
async def test_authorized_user_projects_returned(async_client, auth_headers):
    headers = auth_headers
    response = await async_client.get('/api/v1/projects/all', headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_getting_project_lets_project_participant_see_details(async_client, member_auth_headers, \
                                                                    test_project):
    headers = member_auth_headers
    response = await async_client.get(f'/api/v1/projects/{test_project.project_id}', \
                                        headers=headers)
    assert response.status_code == 200
    assert response.json()['project_name'] == test_project.project_name

@pytest.mark.asyncio
async def test_admin_update_project(async_client, auth_headers, test_users, test_project):
    update_data = {'project_name': 'Update_name','project_description': 'Update_description'}
    headers = auth_headers
    response = await async_client.put(f'/api/v1/projects/{test_project.project_id}', \
                                        json=update_data,headers=headers)
    assert response.status_code == 200
    assert response.json()['message'] in ('Ничего не изменилось!', 'Проект обновлен!')

@pytest.mark.asyncio
async def test_updating_not_existent_project(async_client, auth_headers):
    headers = auth_headers
    response = await async_client.put('/api/v1/projects/999', headers=headers)
    assert response.status_code == 404     
    assert response.json()['detail'] == 'Проект не найден!'

@pytest.mark.asyncio
async def test_deleting_not_existent_project(async_client, member_auth_headers):
    headers = member_auth_headers
    response = await async_client.delete('/api/v1/projects/999', headers=headers)
    assert response.status_code == 404       
    assert response.json()['detail'] == 'Проект не найден!'

@pytest.mark.asyncio
async def test_regular_participant_not_update_project(async_client, member_auth_headers, test_project):
    headers = member_auth_headers
    response = await async_client.put(f'/api/v1/projects/{test_project.project_id}',headers=headers)
    assert response.status_code == 403    
    assert response.json()['detail'] == 'Пользователь не может менять проект, он не админ!'

@pytest.mark.asyncio
async def test_admin_delete_project(async_client, auth_headers, test_project):
    headers = auth_headers
    response = await async_client.delete(f'/api/v1/projects/{test_project.project_id}',headers=headers)
    assert response.status_code == 200        
    assert response.json()['message'] == 'Проект успешно удален!'

@pytest.mark.asyncio
async def test_regular_participant_not_delete_project(async_client, member_auth_headers, test_project):
    headers = member_auth_headers
    response = await async_client.delete(f'/api/v1/projects/{test_project.project_id}',headers=headers)
    assert response.status_code == 403  
    assert response.json()['detail'] == 'Вы не админ этого проекта!'

@pytest.mark.asyncio
async def test_admin_add_existing_user(async_client, auth_headers, test_project, test_users):
    headers = auth_headers       
    outsider = test_users.get('outsider')
    response = await async_client.post(f'/api/v1/projects/{test_project.project_id}/members', \
                                            json={'user_id': outsider.user_id}, headers=headers)
    assert response.status_code == 201
    assert response.json()['message'] == 'Пользователь добавлен в проект!'

@pytest.mark.asyncio
async def test_adding_yourself(async_client, member_auth_headers, test_project, test_users):
    headers = member_auth_headers
    member = test_users.get('member')
    response = await async_client.post(f'/api/v1/projects/{test_project.project_id}/members', \
                                            json={'user_id': member.user_id}, headers=headers)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_admin_not_add_user_already_in_project(async_client, auth_headers, test_project, test_users):
    headers = auth_headers
    member = test_users.get('member')
    response = await async_client.post(f'/api/v1/projects/{test_project.project_id}/members', \
                                            json={'user_id': member.user_id}, headers=headers)
    assert response.status_code == 409
    assert response.json()['detail'] == 'Пользователь уже состоит в проекте'

@pytest.mark.asyncio
async def test_admin_delete_anyone(async_client, auth_headers, test_project, test_users):
    admin_headers = auth_headers
    outsider = test_users.get('outsider')
    await async_client.post(f'/api/v1/projects/{test_project.project_id}/members', json={'user_id': outsider.user_id}, \
                                headers=admin_headers)
    response = await async_client.delete(f'/api/v1/projects/{test_project.project_id}/members', \
                                            json={'user_id': outsider.user_id}, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()['message'] == 'Пользователь удален из проекта!'

@pytest.mark.asyncio
async def test_regular_member_not_delete_anyone(async_client, member_auth_headers, test_project, test_users):
    headers = member_auth_headers
    outsider = test_users.get('outsider')
    response = await async_client.delete(f'/api/v1/projects/{test_project.project_id}/members', \
                                            json={'user_id': outsider.user_id}, headers=headers)
    assert response.status_code == 403
    assert response.json()['detail'] == 'Нельзя удалить пользователя: вы не админ проекта!'

@pytest.mark.asyncio
async def test_admin_raise_or_lower_role(async_client, auth_headers, test_project, test_users):
    admin_headers = auth_headers
    member = test_users.get('member')
    response = await async_client.patch(f'/api/v1/projects/{test_project.project_id}/members/{member.user_id}/role', \
                                            params={'role': 'admin'}, headers=admin_headers)
    assert response.status_code == 200
    response = await async_client.patch(f'/api/v1/projects/{test_project.project_id}/members/{member.user_id}/role', \
                                            params={'role': 'member'}, headers=admin_headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_not_demote_only_admin(async_client, auth_headers, test_project, test_users):
    admin_headers = auth_headers
    admin_user = test_users.get('admin')
    response = await async_client.patch(f'/api/v1/projects/{test_project.project_id}/members/{admin_user.user_id}/role', \
                                            params={'role': 'member'}, headers=admin_headers)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_empty_projects_list_for_new_user(async_client, test_users):
    new_user = test_users.get('outsider')
    token = create_access_token({'sub': new_user.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    response = await async_client.get('/api/v1/projects/all', headers=headers)
    assert response.status_code == 200
    assert response.json() == []              

@pytest.mark.asyncio
async def test_regular_member_add_user_to_project(async_client, member_auth_headers, test_project_with_member, test_users):
    headers = member_auth_headers
    project = test_project_with_member['project']
    outsider = test_users.get('outsider')
    response = await async_client.post(f'/api/v1/projects/{project.project_id}/members', \
                                            json={'user_id': outsider.user_id}, headers=headers)
    assert response.status_code == 403
    assert response.json()['detail'] == 'Нельзя добавить пользователя: вы не админ проекта!'

@pytest.mark.asyncio
async def test_admin_add_non_existent_user(async_client, auth_headers, test_project):
    headers = auth_headers
    response = await async_client.post(f'/api/v1/projects/{test_project.project_id}/members', \
                                            json={'user_id': 99999}, headers=headers)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Нельзя добавить пользователя: его не существует!'

@pytest.mark.asyncio
async def test_admin_delete_user_not_in_project(async_client, auth_headers, test_project, test_users):
    headers = auth_headers
    outsider = test_users.get('outsider')
    response = await async_client.delete(f'/api/v1/projects/{test_project.project_id}/members', \
                                            json={'user_id': outsider.user_id}, headers=headers)
    assert response.status_code == 409
    assert response.json()['detail'] == 'Пользователь не состоит в проекте!'

@pytest.mark.asyncio
async def test_member_projects_list(async_client, member_auth_headers, test_project_with_member):
    headers = member_auth_headers
    response = await async_client.get('/api/v1/projects/all', headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['project_id'] == test_project_with_member['project'].project_id

@pytest.mark.asyncio
async def test_regular_member_change_role(async_client, member_auth_headers, test_project, test_users):
    headers = member_auth_headers
    member = test_users.get('member')
    response = await async_client.patch(f'/api/v1/projects/{test_project.project_id}/members/{member.user_id}/role', \
                                            params={'role': 'admin'}, headers=headers)
    assert response.status_code == 403
    assert response.json()['detail'] == 'Нельзя изменить роль: вы не админ проекта!'

@pytest.mark.asyncio
async def test_add_user_to_non_existent_project(async_client, auth_headers, test_users):
    headers = auth_headers
    outsider = test_users.get('outsider')
    response = await async_client.post('/api/v1/projects/99999/members', json={'user_id': outsider.user_id}, \
        headers=headers)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Проект не найден!'

@pytest.mark.asyncio
async def test_update_project_with_no_changes(async_client, auth_headers, test_project):
    headers = auth_headers
    response = await async_client.put(f'/api/v1/projects/{test_project.project_id}', \
                                        json={}, headers=headers)
    assert response.status_code == 200
    assert response.json()['message'] == 'Ничего не изменилось!'

@pytest.mark.asyncio
async def test_update_project_user_not_member(async_client, test_project, test_users):
    outsider = test_users.get('outsider')
    token = create_access_token({'sub': outsider.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    response = await async_client.put(f'/api/v1/projects/{test_project.project_id}', \
        json={'project_name': 'New Name'}, headers=headers)
    assert response.status_code == 403
    assert response.json()['detail'] == 'Пользователь не является участником проекта!'

@pytest.mark.asyncio
async def test_admin_delete_self_from_project(async_client, auth_headers, test_project, test_users):
    headers = auth_headers
    admin_user = test_users.get('admin')
    response = await async_client.delete(f'/api/v1/projects/{test_project.project_id}/members', \
        json={'user_id': admin_user.user_id}, headers=headers)
    assert response.status_code == 400