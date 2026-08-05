# Создание, назначение, изменение статуса задач
from repositories.task_repository import TaskRepository

async def get_task_by_id(db, project_id: int, task_id: int):
    repo = TaskRepository(db)
    return await repo.get_task_by_id(project_id, task_id)