import pytest

@pytest.mark.asyncio
async def test_successful_project_creation(async_client, auth_headers):
    headers = await auth_headers
    response = await async_client.post('/api/v1/projects', json={'project_name': 'Test_project', \
                                                                 'project_description': ''}, headers=headers)
    assert response.status_code == 201
    assert response.json()['project_id']
    assert response.json()['project_name'] == 'Test_project'

@pytest.mark.asyncio
async def test_attempt_create_project_without_authorization(async_client):
    response = await async_client.post('/api/v1/projects', json={'project_name': 'Test_project', \
                                                                 'project_description': ''})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_attempt_create_project_with_incorrect_data(async_client, auth_headers):
    headers = await auth_headers
    response = await async_client.post('/api/v1/projects', json={'project_name': '', 'project_description': '12345'}, \
                                       headers=headers)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_authorized_admin_projects_returned(async_client, auth_headers):
    headers = await auth_headers
    response = await async_client.get('/api/v1/projects', headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_attempt_get_non_existent_project(async_client, auth_headers): # 404
    headers = await auth_headers
    response = await async_client.get(f'/api/v1/projects/{9999}', headers=headers)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Пользователь не является участником проекта!'

@pytest.mark.asyncio
async def test_attempt_get_project_that_user_not_part(async_client, auth_headers, test_project, test_users): # 403
    headers = await auth_headers
    response = await async_client.get(f'/api/v1/projects/{test_project.project_id}', test_users['outsider'], headers=headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_authorized_user_projects_returned(async_client, auth_headers):
    headers = await auth_headers
    response = await async_client.get('/api/v1/projects/all', headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_getting_project_lets_project_participant_see_details(async_client, auth_headers, test_project):
    headers = await auth_headers
    response = await async_client.get(f'/api/v1/projects/{test_project.project_id}', headers=headers)
    assert response.status_code == 200
    assert response.json()['project_name'] == test_project.project_name

@pytest.mark.asyncio
async def test_admin_update_project(async_client, auth_headers, test_users, test_project): # 200
    headers = await auth_headers
    response = await async_client.put(f'/api/v1/projects/{test_project.project_id}', test_users['admin'], headers=headers)
    assert response.status_code == 200
    assert response.json()['message'] == 'Ничего не изменилось!' | response.json()['message'] == 'Проект обновлен!'

@pytest.mark.asyncio
async def test_updating_not_existent_project(async_client, auth_headers, test_users): # 404
    headers = await auth_headers
    response = await async_client.put(f'/api/v1/projects/{999}', test_users['admin'], headers=headers)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Проект не найден!'

@pytest.mark.asyncio
async def test_deleting_not_existent_project(async_client, auth_headers, test_users): # 404
    headers = await auth_headers
    response = await async_client.put(f'/api/v1/projects/{999}', test_users['admin'], headers=headers)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Проект не найден!'

@pytest.mark.asyncio
async def test_regular_participant_not_update_project(async_client, auth_headers, test_users, test_project): # 403
    headers = await auth_headers
    response = await async_client.put(f'/api/v1/projects/{test_project.project_id}', test_users['member'], headers=headers)
    assert response.status_code == 403
    assert response.json()['detail'] == 'Пользователь не может менять проект, он не админ!'

@pytest.mark.asyncio
async def test_admin_delete_project(async_client, auth_headers, test_users, test_project): # 200
    headers = await auth_headers
    response = await async_client.delete(f'/api/v1/projects/{test_project.project_id}', test_users['admin'], headers=headers)
    assert response.status_code == 200
    assert response.json()['message'] == 'Проект успешно удален!'
    
@pytest.mark.asyncio
async def test_regular_participant_not_delete_project(): # 403

@pytest.mark.asyncio
async def test_admin_add_existing_user(): # 201

@pytest.mark.asyncio
async def test_adding_yourself(): # 400

@pytest.mark.asyncio
async def test_admin_not_add_user_already_in_project(): # 409

@pytest.mark.asyncio
async def test_admin_delete_anyone(): # 200

@pytest.mark.asyncio
async def test_regular_member_not_delete_anyone(): # 403

@pytest.mark.asyncio
async def test_admin_raise_or_lower_role(): # 200

@pytest.mark.asyncio
async def test_not_demote_only_admin(): # 400

@pytest.mark.asyncio
async def test_empty_projects_list_for_new_user(): # 200