import pytest 
import datetime
from core.security import create_access_token

@pytest.mark.asyncio
async def test_creating_task_in_project_by_member(async_client, test_project_with_member , test_users, member_auth_headers):
    headers = await member_auth_headers
    assigned_to = test_users['member'].user_id
    response = await async_client.post(f'/api/v1/projects/{test_project_with_member.project_id}/tasks', \
                                       json={'title': 'Test_task', 'task_description': 'Test_description', 'assigned_to': assigned_to, 'deadline': datetime.now() + datetime.timedelta(days=7)}, \
                                        headers=headers)
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_attempt_create_task_by_non_participant(async_client, auth_headers, test_project, test_users):
    outsider = test_users.get('outsider')
    token = create_access_token({'sub': outsider.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    response = await async_client.post(f'/api/v1/projects/{test_project.project_id}/tasks', json={'title': 'Test'}, headers=headers)
    assert response.status_code == 403
    assert response.json()['detail'] == 'Текущего пользователя нет в проекте!'

@pytest.mark.asyncio
async def test_getting_project_task_list(async_client, auth_headers, test_project):
    headers = await auth_headers
    response = await async_client.get(f'/api/v1/projects/{test_project.project_id}/tasks', headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_getting_task_by_ID():

@pytest.mark.asyncio
async def test_update_task():

@pytest.mark.asyncio
async def test_delete_task():

@pytest.mark.asyncio
async def test_changing_task_status():

@pytest.mark.asyncio
async def test_attempt_update_or_delete_someone_task():

@pytest.mark.asyncio
async def test_attempt_get_non_existent_task():

@pytest.mark.asynsio
async def test_create_task_with_deadline_in_past():

@pytest.mark.asyncio
async def test_create_task_with_assigned_to_not_in_project():

@pytest.mark.asyncio
async def test_get_tasks_for_current_user():

@pytest.mark.asyncio
async def test_get_task_info_by_participant():

@pytest.mark.asyncio
async def test_get_task_info_by_non_participant():

@pytest.mark.asyncio
async def test_get_task_info_for_non_existent_task():

@pytest.mark.asyncio
async def test_update_task_by_admin():

@pytest.mark.asyncio
async def test_update_task_by_member():

@pytest.mark.asyncio
async def test_update_task_with_invalid_deadline():

@pytest.mark.asyncio
async def test_update_task_set_assigned_to_not_in_project():

@pytest.mark.asyncio
async def test_delete_task_by_admin():

@pytest.mark.asyncio
async def test_delete_task_by_member():

@pytest.mark.asyncio
async def test_change_status_to_valid():

@pytest.mark.asyncio
async def test_change_status_to_invalid():

@pytest.mark.asyncio
async def test_change_status_of_non_existent_task():

@pytest.mark.asycnio
async def test_change_status_by_non_participant():