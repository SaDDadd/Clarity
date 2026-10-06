import datetime

from core.exceptions import InvalidDeadlineException, NotFoundException, \
    PermissionDeniedException
from models.task import TaskModel
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from schemas.common import TaskStatus
from sqlalchemy.ext.asyncio import AsyncSession 
from cache.cache_keys import project_tasks_key, user_tasks_key, task_key, TTL_TASK, TTL_TASK_LIST
from cache.cache_service import get_cache, delete_cache, set_cache

async def create_task(db: AsyncSession, project_id: int, current_user_id: int, task) -> TaskModel:
    """Создаёт задачу в проекте."""
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if task.deadline is not None:
        if task.deadline < datetime.date.today():
            raise InvalidDeadlineException('Время дэдлайна не может быть меньше сегодняшнего дня!')
    if task.assigned_to is not None:
        if not await repo_proj.is_user_in_project(project_id, task.assigned_to):
            raise PermissionDeniedException('Добавляемого пользователя нет в проекте!')
    result = await repo.create_task(project_id, task)
    await delete_cache(project_tasks_key(project_id))
    if task.assigned_to is not None:
        await delete_cache(user_tasks_key(task.assigned_to, 'all'))
    return result


async def get_project_tasks(db: AsyncSession, project_id: int, current_user_id: int) -> list[dict] | None:
    """Возвращает все задачи проекта."""
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Пользователя нет в проекте!')
    key = project_tasks_key(project_id)
    cached = await get_cache(key)
    if cached is not None:
        return cached
    data = await repo.get_project_tasks(project_id)
    answer = [
        {
            'task_id':i.task_id,
            'project_id':i.project_id,
            'title':i.title,
            'description':i.task_description,
            'status':i.task_status,
            'assigned_to':i.assigned_to,
            'deadline':i.deadline,
            'created_at':i.created_date.isoformat() if i.created_date else None,
        } 
        for i in data
    ]
    await set_cache(key, answer, TTL_TASK_LIST)
    return answer


async def get_task_info(db: AsyncSession, project_id: int, current_user_id: int, task_id: int) -> list | None:
    """Возвращает информацию о задаче."""
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo_proj.get_project_by_id(project_id) is None:
        raise PermissionDeniedException('Данного проекта не существует!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    key = task_key(project_id, task_id)
    cached = await get_cache(key)
    if cached is not None:
        return cached
    data = await repo.get_task_by_id(task_id)
    answer = [
        {
            'task_id':data.task_id,
            'project_id':data.project_id,
            'title':data.title, 
            'description':data.task_description,
            'status':data.task_status,
            'assigned_to':data.assigned_to,
            'deadline':data.deadline.isoformat() if data.deadline else None,
            'created_at':data.created_date.isoformat() if data.created_date else None,
        }
    ]
    await set_cache(key, answer, TTL_TASK)
    return answer


async def get_tasks_user(db: AsyncSession, current_user_id: int) -> list[TaskModel]:
    """Возвращает все задачи, назначенные на пользователя."""
    repo = TaskRepository(db)
    key = user_tasks_key(current_user_id, 'all')
    cached = await get_cache(key)
    if cached is not None:
        return cached
    data = await repo.get_tasks_by_user(current_user_id)
    answer = [
        {
            'task_id':i.task_id,
            'project_id':i.project_id,
            'title':i.title,
            'description':i.task_description,
            'status':i.task_status,
            'deadline':i.deadline.isoformat() if i.deadline else None,
            'created_at':i.created_date.isoformat() if i.created_date else None,
        } 
        for i in data
    ]
    await set_cache(key, answer, TTL_TASK_LIST)
    return answer


async def update_task(db: AsyncSession, project_id: int, task_id: int, current_user_id: int, task) -> dict:
    """Обновляет задачу."""
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
    if 'deadline' in slov and slov['deadline'] is not None:
        if slov['deadline'] < datetime.date.today():
            raise InvalidDeadlineException('Время дэдлайна не может быть меньше сегодняшнего дня!')
    if 'assigned_to' in slov and slov['assigned_to'] is not None:
        if not await repo_user.check_user_exists(slov['assigned_to']):
            raise NotFoundException('Такого пользователя не существует!')
        if not await repo_proj.is_user_in_project(project_id, slov['assigned_to']):
            raise PermissionDeniedException('Добавляемого пользователя нет в проекте!')
    if await repo.update_task_by_id(project_id, task_id, slov) is False:
        raise NotFoundException('Задача не найдена!')
    await delete_cache(task_key(project_id, task_id))
    await delete_cache(project_tasks_key(project_id))
    if 'assigned_to' in slov and slov['assigned_to'] is not None:
        await delete_cache(user_tasks_key(slov['assigned_to'], 'all'))
    if task.assigned_to:
        await delete_cache(user_tasks_key(task.assigned_to, 'all'))
    return {'message': 'Задача обновилась!'}


async def change_status(db: AsyncSession, project_id: int, task_id: int, current_user_id: int,
                        task_status: TaskStatus) -> dict:
    """Изменяет статус задачи."""
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo_proj.get_project_by_id(project_id) is None:
        raise PermissionDeniedException('Данного проекта не существует!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    task = await repo.get_task_by_id(task_id)
    assignee = task.assigned_to if task else None 
    if await repo.update_task_status(project_id, task_id, task_status.value):
        await delete_cache(task_key(project_id, task_id))
        await delete_cache(project_tasks_key(project_id))
        if assignee:
            await delete_cache(user_tasks_key(assignee, 'all'))
        return {'message': 'Статус обновлен!'}
    else:
        return {'message': 'Статус уже установлен'}


async def delete_task(db: AsyncSession, project_id: int, task_id: int, current_user_id: int) -> dict:
    """Удаляет задачу."""
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo_proj.get_project_by_id(project_id) is None:
        raise PermissionDeniedException('Данного проекта не существует!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    if not await repo_proj.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('Не админ не может удалить задачу!')
    task = await repo.get_task_by_id(task_id)
    assignee = task.assigned_to if task else None
    if not await repo.delete_task(task_id):
        raise NotFoundException('Не удалось удалить задачу')
    await delete_cache(task_key(project_id, task_id))
    await delete_cache(project_tasks_key(project_id))
    if assignee:
        await delete_cache(user_tasks_key(assignee, 'all'))
    return {'message': 'Задача удалена из проекта!'}