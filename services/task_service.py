# Создание, назначение, изменение статуса задач
from repositories.task_repository import TaskRepository
from core.exceptions import NotFoundException, PermissionDeniedException
from schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse
from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository
from schemas.common import TaskStatus

async def get_project_tasks(db, project_id: int, current_user_id: int):
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Пользователя нет в проекте!')
    else:
        return await repo.get_project_tasks(project_id)

async def create_task(db, project_id: int, current_user_id: int, task):
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if task.assigned_to is not None:
        if not await repo_proj.is_user_in_project(project_id, task.assigned_to):
            raise PermissionDeniedException('Добавляемого пользователя нет в проекте!')
    return await repo.create_task(project_id, task)

async def update_task(db, project_id: int, task_id: int, current_user_id: int, task):
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    repo_user = UserRepository(db)
    slov = task.dict(exclude_unset=True)
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if await repo_user.get_by_id(task.assigned_to) is None:
        raise PermissionDeniedException('Такого пользователя не существует!')
    if 'assigned_to' in slov and slov['assigned_to'] != None:
        if not await repo_proj.is_user_in_project(project_id, task.assigned_to):
                raise PermissionDeniedException('Добавляемого пользователя нет в проекте!')
    if len(slov) == 0:
        return {'message': 'Нет данных для обновления!'}
    else:
        if await repo.update_task_by_id(project_id, task_id, slov) is False:
            raise NotFoundException('Задача не найдена!')
        else:
            return {'message': 'Задача обновилась!'}                                                           