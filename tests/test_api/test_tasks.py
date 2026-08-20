import pytest
import datetime
from core.security import create_access_token

@pytest.mark.asyncio
async def test_creating_task_in_project_by_member(async_client, test_project_with_member, test_users, member_auth_headers):
    """Проверяет, что участник проекта может создать задачу в этом проекте."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    assigned_to = test_users['member'].user_id
    deadline = datetime.datetime.now() + datetime.timedelta(days=7)
    response = await async_client.post(f'/api/v1/projects/{project_id}/tasks',
        json={
            'title': 'Test_task',
            'task_description': 'Test_description',
            'assigned_to': assigned_to,
            'deadline': deadline.isoformat()
        }, headers=headers)
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_attempt_create_task_by_non_participant(async_client, test_project, test_users):
    """Проверяет, что пользователь, не состоящий в проекте, не может создать задачу."""
    outsider = test_users['outsider']
    token = create_access_token({'sub': outsider.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    response = await async_client.post(
        f'/api/v1/projects/{test_project.project_id}/tasks',
        json={'title': 'Test'},
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()['detail'] == 'Текущего пользователя нет в проекте!'

@pytest.mark.asyncio
async def test_getting_project_task_list(async_client, auth_headers, test_project):
    """Проверяет, что участник проекта получает список задач проекта."""
    headers = auth_headers
    response = await async_client.get(
        f'/api/v1/projects/{test_project.project_id}/tasks',
        headers=headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

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
async def test_update_task(async_client, test_project_with_member, member_auth_headers, test_task):
    """Проверяет обновление задачи (участник)."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    response = await async_client.put(
        f'/api/v1/projects/{project_id}/tasks/{test_task.task_id}',
        json={'title': 'Update_Test_task', 'task_description': 'Test_description'},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'Задача обновилась!'
    response = await async_client.put(
        f'/api/v1/projects/{project_id}/tasks/{test_task.task_id}',
        json={'title': 'Test_task', 'task_description': None},
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
    assert response.status_code == 200
    assert response.json()['message'] == 'Задача удалена из проекта!'

@pytest.mark.asyncio
async def test_changing_task_status(async_client, test_project_with_member, member_auth_headers, test_task):
    """Проверяет изменение статуса задачи."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    response = await async_client.put(
        f'/api/v1/projects/{project_id}/tasks/{test_task.task_id}/status',
        json={'task_status': 'in_progress'},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()['message'] in ('Статус обновлен!', 'Статус уже установлен')

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
async def test_create_task_with_deadline_in_past(async_client, test_project_with_member, member_auth_headers):
    """Проверяет создание задачи с дэдлайном в прошлом – ошибка валидации."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    past_deadline = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
    response = await async_client.post(
        f'/api/v1/projects/{project_id}/tasks',
        json={'deadline': past_deadline},
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()['detail'] == 'Время дэдлайна не может быть меньше сегодняшнего дня!'

@pytest.mark.asyncio
async def test_create_task_with_assigned_to_not_in_project(async_client, test_project_with_member, member_auth_headers, test_users):
    """Проверяет назначение задачи пользователю, не входящему в проект."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    outsider_id = test_users['outsider'].user_id
    response = await async_client.post(
        f'/api/v1/projects/{project_id}/tasks',
        json={'assigned_to': outsider_id},
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()['detail'] == 'Добавляемого пользователя нет в проекте!'

@pytest.mark.asyncio
async def test_get_tasks_for_current_user(async_client, member_auth_headers):
    """Проверяет получение списка задач, назначенных на текущего пользователя."""
    headers = member_auth_headers
    response = await async_client.get('/api/v1/tasks', headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

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
async def test_update_task_by_member(async_client, test_project_with_member, member_auth_headers, test_task):
    """Проверяет, что участник проекта может обновить задачу."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    response = await async_client.put(
        f'/api/v1/projects/{project_id}/tasks/{test_task.task_id}',
        json={'title': 'Updated by member'},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'Задача обновилась!'

@pytest.mark.asyncio
async def test_update_task_with_invalid_deadline(async_client, test_project_with_member, member_auth_headers, test_task):
    """Проверяет обновление дэдлайна на прошедшую дату – ошибка."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    past_deadline = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
    response = await async_client.put(
        f'/api/v1/projects/{project_id}/tasks/{test_task.task_id}',
        json={'deadline': past_deadline},
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()['detail'] == 'Время дэдлайна не может быть меньше сегодняшнего дня!'

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
    assert response.json()['detail'] == 'Добавляемого пользователя нет в проекте!'

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
async def test_delete_task_by_member(async_client, test_project_with_member, member_auth_headers, test_task):
    """Проверяет удаление задачи участником (разрешено)."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    response = await async_client.delete(
        f'/api/v1/projects/{project_id}/tasks/{test_task.task_id}',
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'Задача удалена из проекта!'

@pytest.mark.asyncio
async def test_change_status_to_valid(async_client, test_project_with_member, member_auth_headers, test_task):
    """Проверяет изменение статуса на допустимое значение."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    response = await async_client.put(
        f'/api/v1/projects/{project_id}/tasks/{test_task.task_id}/status',
        json={'task_status': 'completed'},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'Статус обновлен!'

@pytest.mark.asyncio
async def test_change_status_to_invalid(async_client, test_project_with_member, member_auth_headers, test_task):
    """Проверяет попытку установить недопустимый статус."""
    headers = member_auth_headers
    project_id = test_project_with_member['project'].project_id
    response = await async_client.put(
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
    response = await async_client.put(
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
    response = await async_client.put(
        f'/api/v1/projects/{test_project.project_id}/tasks/{test_task.task_id}/status',
        json={'task_status': 'in_progress'},
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()['detail'] == 'Текущего пользователя нет в проекте!'