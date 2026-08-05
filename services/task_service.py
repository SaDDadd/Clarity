# Создание, назначение, изменение статуса задач
from repositories.task_repository import TaskRepository
from core.exceptions import NotFoundException, PermissionDeniedException
from schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse
from repositories.project_repository import ProjectRepository
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
    if not await repo_proj.is_user_in_project(project_id, current_user_id) or not await repo_proj.is_user_in_project(project_id, task.assigned_to):
        raise PermissionDeniedException('Пользователя нет в проекте!')
    else:
        return await repo.create_task(project_id, task)