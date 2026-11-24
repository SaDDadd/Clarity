import pytest
import datetime
from core.security import create_access_token


@pytest.mark.asyncio
async def test_attempt_create_task_by_non_participant(async_client, test_project, test_users):
    outsider = test_users['outsider']
    token = create_access_token({'sub': outsider.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    response = await async_client.post(
        f'/api/v1/projects/{test_project.project_id}/tasks',
        json={'title': 'Test', 'task_description': None, 'task_status': 'pending'},
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()['detail'] == 'Текущего пользователя нет в проекте!'


@pytest.mark.asyncio
async def test_getting_task_by_ID(async_client, test_project_with_member, member_auth_headers, test_task):
    """Проверяет получение конкретной задачи по ID (участник проекта)."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    response = await async_client.get(
        f'/api/v1/projects/{project_id}/tasks/{test_task.task_id}',
        headers=headers
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_task(async_client, test_project_with_member, member_auth_headers, test_task):
    """Проверяет удаление задачи."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    response = await async_client.delete(
        f'/api/v1/projects/{project_id}/tasks/{test_task.task_id}',
        headers=headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_attempt_get_non_existent_task(async_client, test_project_with_member, member_auth_headers):
    """Проверяет запрос несуществующей задачи."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    response = await async_client.get(
        f'/api/v1/projects/{project_id}/tasks/999',
        headers=headers
    )
    assert response.status_code == 404
    assert response.json()['detail'] == 'Задачи нет в проекте!'


@pytest.mark.asyncio
async def test_get_task_info_by_participant(async_client, test_project_with_member, member_auth_headers, test_task):
    """Проверяет получение информации о задаче участником проекта."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    response = await async_client.get(
        f'/api/v1/projects/{project_id}/tasks/{test_task.task_id}',
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data['task_id'] == test_task.task_id
    assert data['title'] == test_task.title

@pytest.mark.asyncio
async def test_get_task_info_by_non_participant(async_client, test_project, test_users, test_task):
    """Проверяет, что не участник не может получить информацию о задаче."""
    outsider = test_users['outsider']
    token = create_access_token({'sub': outsider.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    response = await async_client.get(
        f'/api/v1/projects/{test_project.project_id}/tasks/{test_task.task_id}',
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()['detail'] == 'Текущего пользователя нет в проекте!'

@pytest.mark.asyncio
async def test_get_task_info_for_non_existent_task(async_client, test_project_with_member, member_auth_headers):
    """Проверяет получение информации о несуществующей задаче."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    response = await async_client.get(
        f'/api/v1/projects/{project_id}/tasks/9999',
        headers=headers
    )
    assert response.status_code == 404
    assert response.json()['detail'] == 'Задачи нет в проекте!'

@pytest.mark.asyncio
async def test_update_task_by_admin(async_client, test_project, auth_headers, test_task):
    """Проверяет, что администратор проекта может обновить любую задачу."""
    headers = auth_headers
    response = await async_client.put(
        f'/api/v1/projects/{test_project.project_id}/tasks/{test_task.task_id}',
        json={'title': 'Updated by admin'},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'Задача обновилась!'


@pytest.mark.asyncio
async def test_update_task_set_assigned_to_not_in_project(async_client, test_project_with_member, member_auth_headers, test_task, test_users):
    """Проверяет назначение задачи на пользователя вне проекта при обновлении."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    outsider_id = test_users['outsider'].user_id
    response = await async_client.put(
        f'/api/v1/projects/{project_id}/tasks/{test_task.task_id}',
        json={'assigned_to': outsider_id},
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()['detail'] == 'Задачу могут обновлять только админ, куратор или назначенный исполнитель!'

@pytest.mark.asyncio
async def test_delete_task_by_admin(async_client, test_project, auth_headers, test_task):
    """Проверяет удаление задачи администратором."""
    headers = auth_headers
    response = await async_client.delete(
        f'/api/v1/projects/{test_project.project_id}/tasks/{test_task.task_id}',
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'Задача удалена из проекта!'


@pytest.mark.asyncio
async def test_change_status_to_invalid(async_client, test_project_with_member, member_auth_headers, test_task):
    """Проверяет попытку установить недопустимый статус."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    response = await async_client.patch(
        f'/api/v1/projects/{project_id}/tasks/{test_task.task_id}/status',
        json={'task_status': 'invalid_status'},
        headers=headers
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_change_status_of_non_existent_task(async_client, test_project_with_member, member_auth_headers):
    """Проверяет изменение статуса у несуществующей задачи."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    response = await async_client.patch(
        f'/api/v1/projects/{project_id}/tasks/9999/status',
        json={'task_status': 'in_progress'},
        headers=headers
    )
    assert response.status_code == 404
    assert response.json()['detail'] == 'Задачи нет в проекте!'

@pytest.mark.asyncio
async def test_change_status_by_non_participant(async_client, test_project, test_users, test_task):
    """Проверяет, что не участник не может изменить статус задачи."""
    outsider = test_users['outsider']
    token = create_access_token({'sub': outsider.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    response = await async_client.patch(
        f'/api/v1/projects/{test_project.project_id}/tasks/{test_task.task_id}/status',
        json={'task_status': 'in_progress'},
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()['detail'] == 'Текущего пользователя нет в проекте!'