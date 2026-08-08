# Создание, назначение, изменение статуса задач
from core.exceptions import NotFoundException, PermissionDeniedException
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from schemas.common import TaskStatus
from schemas.task import TaskStatusUpdate

# Создать задачу
async def create_task(db, project_id: int, current_user_id: int, task):
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if task.assigned_to is not None:
        if not await repo_proj.is_user_in_project(project_id, task.assigned_to):
            raise PermissionDeniedException('Добавляемого пользователя нет в проекте!')
    return await repo.create_task(project_id, task)

# Получить все задачи проекта
async def get_project_tasks(db, project_id: int, current_user_id: int):
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Пользователя нет в проекте!')
    else:
        return await repo.get_project_tasks(project_id)

# Получить информацию о задаче
async def get_task_info(db, project_id: int, current_user_id: int, task_id: int):
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo_proj.get_project_by_id(project_id) is None:
        raise PermissionDeniedException('Данного проекта не существует!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    result = await repo.get_task_by_id(task_id)
    if result is None:
        raise NotFoundException('Нет информации про эту задачу!')
    else:
        return result

# Получить задачи пользователя
async def get_tasks_user(db, current_user_id: int):
    repo = TaskRepository(db)
    return await repo.get_tasks_by_user(current_user_id)

# Обновить задачу
async def update_task(db, project_id: int, task_id: int, current_user_id: int, task):
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    repo_user = UserRepository(db)
    slov = task.model_dump(exclude_unset=True)
    if len(slov) == 0:
        return {'message': 'Нет данных для обновления!'}
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if 'assigned_to' in slov and slov['assigned_to'] is not None:
        if not await repo_user.check_user_exists(slov['assigned_to']):
            raise NotFoundException('Такого пользователя не существует!')
        if not await repo_proj.is_user_in_project(project_id, slov['assigned_to']):
            raise PermissionDeniedException('Добавляемого пользователя нет в проекте!')
    if await repo.update_task_by_id(project_id, task_id, slov) is False:
        raise NotFoundException('Задача не найдена!')
    else:
        return {'message': 'Задача обновилась!'}

# Изменить статус задачи
async def change_status(db, project_id: int, task_id: int, current_user_id: int, task_status: TaskStatusUpdate):
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo_proj.get_project_by_id(project_id) is None:
        raise PermissionDeniedException('Данного проекта не существует!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    if await repo.update_task_status(project_id, task_id, task_status.task_status.value):
        return {'message': 'Статус обновлен!'}
    else:
        return {'message': 'Статус уже установлен'}

# Удалить задачу
async def delete_task(db, project_id: int, task_id: int, current_user_id: int):
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo_proj.get_project_by_id(project_id) is None:
        raise PermissionDeniedException('Данного проекта не существует!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    if not await repo.delete_task(task_id):
        raise NotFoundException('Не удалось удалить задачу')
    else:
        return {'message': 'Задача удалена из проекта!'}