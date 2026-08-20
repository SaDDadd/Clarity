import pytest
import datetime
from core.security import create_access_token

@pytest.mark.asyncio
async def test_creating_task_in_project_by_member(async_client, test_project_with_member, test_users, member_auth_headers):
    """Проверяет, что участник проекта может создать задачу в этом проекте."""
    headers = await member_auth_headers
    assigned_to = test_users['member'].user_id
    response = await async_client.post(f'/api/v1/projects/{test_project_with_member['project'].project_id}/tasks', \
                                       json={'title': 'Test_task', 'task_description': 'Test_description', 'assigned_to': assigned_to, 'deadline': datetime.datetime.now() + datetime.timedelta(days=7)}, \
                                        headers=headers)
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_attempt_create_task_by_non_participant(async_client, auth_headers, test_project, test_users):
    """Проверяет, что пользователь, не состоящий в проекте, не может создать задачу."""
    outsider = test_users.get('outsider')
    token = create_access_token({'sub': outsider.user_id})
    headers = {'Authorization': f'Bearer {token}'}
    response = await async_client.post(f'/api/v1/projects/{test_project.project_id}/tasks', json={'title': 'Test'}, headers=headers)
    assert response.status_code == 403
    assert response.json()['detail'] == 'Текущего пользователя нет в проекте!'

@pytest.mark.asyncio
async def test_getting_project_task_list(async_client, auth_headers, test_project):
    """Проверяет, что участник проекта получает список задач проекта."""
    headers = await auth_headers
    response = await async_client.get(f'/api/v1/projects/{test_project.project_id}/tasks', headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_getting_task_by_ID(async_client, test_project_with_member, member_auth_headers, test_task):
    """Проверяет получение конкретной задачи по ID (участник проекта)."""
    headers = await member_auth_headers
    response = await async_client.get(f'/api/v1/projects/{test_project_with_member['project'].project_id}/tasks/{test_task.task_id}', \
                                      headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_task(async_client, test_project_with_member, member_auth_headers, test_task):
    """Проверяет обновление задачи (участник или админ)."""
    headers = await member_auth_headers
    response = await async_client.put(f'/api/v1/projects/{test_project_with_member['project'].project_id}/tasks/{test_task.task_id}', \
                                      json={'title': 'Update_Test_task', 'task_description': 'Test_description'}, headers=headers)
    assert response.status_code == 200
    assert response.json()['message'] == 'Задача обновилась!'
    response = await async_client.put(f'/api/v1/projects/{test_project_with_member['project'].project_id}/tasks/{test_task.task_id}', \
                                      json={'title': 'Test_task', 'task_description': None}, headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncion
async def test_delete_task(async_client, test_project_with_member, member_auth_headers, test_task, db_session, test_project):
    """Проверяет удаление задачи."""
    headers = await member_auth_headers
    response = await async_client.delete(f'/api/v1/projects/{test_project_with_member['project'].project_id}/tasks/{test_task.task_id}', \
                                         headers=headers)
    assert response.status_code == 200
    assert response.json()['message'] == 'Задача удалена из проекта!'

@pytest.mark.asyncio
async def test_changing_task_status(async_client, test_project_with_member, member_auth_headers, test_task):
    """Проверяет изменение статуса задачи."""
    headers = await member_auth_headers
    response = await async_client.put(f'/api/v1/projects/{test_project_with_member['project'].project_id}/tasks/{test_task.task_id}/status', \
                                      json={'task_status': 'in_progress'}, headers=headers)
    assert response.status_code == 200
    assert response.json()['message'] == 'Статус обновлен!' or response.json()['message'] == 'Статус уже установлен'

@pytest.mark.asyncio
async def test_attempt_get_non_existent_task(async_client, test_project_with_member, member_auth_headers):
    """Проверяет запрос несуществующей задачи."""
    headers = await member_auth_headers
    response = await async_client.get(f'/api/v1/projects/{test_project_with_member['project'].project_id}/tasks/{999}', headers=headers)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Задачи нет в проекте!'

@pytest.mark.asyncio
async def test_create_task_with_deadline_in_past(async_client, test_project_with_member, member_auth_headers, test_task, db_session, test_project):
    """Проверяет создание задачи с дэдлайном в прошлом – ошибка валидации."""
    headers = await member_auth_headers
    response = await async_client.post(f'/api/v1/projects/{test_project_with_member['project'].project_id}/tasks', \
                                      json={'deadline': datetime.datetime.now() - datetime.timedelta(days=1)}, headers=headers)
    assert response.status_code == 400
    assert response.json()['detail'] == 'Время дэдлайна не может быть меньше сегодняшнего дня!'

@pytest.mark.asyncio
async def test_create_task_with_assigned_to_not_in_project(async_client, test_project_with_member, member_auth_headers, test_task, test_users):
    """Проверяет назначение задачи пользователю, не входящему в проект."""
    headers = await member_auth_headers
    response = await async_client.post(f'/api/v1/projects/{test_project_with_member['project'].project_id}/tasks', \
                                      json={'assigned_to': test_users['outsider'].user_id}, headers=headers)
    assert response.status_code == 403
    assert response.json()['detail'] == 'Добавляемого пользователя нет в проекте!'

@pytest.mark.asyncio
async def test_get_tasks_for_current_user(async_client, test_project_with_member, member_auth_headers):
    """Проверяет получение списка задач, назначенных на текущего пользователя (эндпоинт /tasks)."""
    headers = await member_auth_headers
    response = await async_client.get(f'/api/v1/projects/tasks', \
                                      headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_task_info_by_participant():
    """Проверяет получение информации о задаче участником проекта."""

@pytest.mark.asyncio
async def test_get_task_info_by_non_participant():
    """Проверяет, что не участник не может получить информацию о задаче."""

@pytest.mark.asyncio
async def test_get_task_info_for_non_existent_task():
    """Проверяет получение информации о несуществующей задаче."""
    
@pytest.mark.asyncio
async def test_update_task_by_admin():
    """Проверяет, что администратор проекта может обновить любую задачу."""

@pytest.mark.asyncio
async def test_update_task_by_member():
    """
    Проверяет, что участник проекта может обновить задачу (если разрешено).
    Ожидаемый статус: 200 OK.
    """
    # TODO: реализовать

@pytest.mark.asyncio
async def test_update_task_with_invalid_deadline():
    """
    Проверяет обновление дэдлайна на прошедшую дату – ошибка.
    Ожидаемый статус: 400/422.
    """
    # TODO: реализовать

@pytest.mark.asyncio
async def test_update_task_set_assigned_to_not_in_project():
    """
    Проверяет назначение задачи на пользователя вне проекта при обновлении.
    Ожидаемый статус: 403 Forbidden.
    """
    # TODO: реализовать

@pytest.mark.asyncio
async def test_delete_task_by_admin():
    """
    Проверяет удаление задачи администратором.
    Ожидаемый статус: 200 OK.
    """
    # TODO: реализовать

@pytest.mark.asyncio
async def test_delete_task_by_member():
    """
    Проверяет удаление задачи участником (возможно, запрещено).
    Ожидаемый статус: 403 или 200 в зависимости от прав.
    """
    # TODO: реализовать

@pytest.mark.asyncio
async def test_change_status_to_valid():
    """
    Проверяет изменение статуса на допустимое значение.
    Ожидаемый статус: 200 OK.
    """
    # TODO: реализовать

@pytest.mark.asyncio
async def test_change_status_to_invalid():
    """Проверяет попытку установить недопустимый статус."""

@pytest.mark.asyncio
async def test_change_status_of_non_existent_task():
    """Проверяет изменение статуса у несуществующей задачи."""

@pytest.mark.asyncio
async def test_change_status_by_non_participant():
    """Проверяет, что не участник не может изменить статус задачи."""