import datetime

from core.exceptions import InvalidDeadlineException, NotFoundException, \
    PermissionDeniedException, LackOfInformationException, AppException, \
    ConflictException
from models.task import TaskModel
from models.task_comments import TaskCommentsModel
from schemas.task import TaskResponse, TaskCreate, TaskUpdate
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from schemas.common import TaskStatus
from sqlalchemy.ext.asyncio import AsyncSession 
from cache.cache_keys import project_tasks_key, user_tasks_key, task_key, TTL_TASK, TTL_TASK_LIST
from cache.cache_service import get_cache, delete_cache, set_cache

async def create_task(db: AsyncSession, project_id: int, current_user_id: int, task: TaskCreate) -> TaskModel:
    """Создаёт задачу в проекте."""
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo_proj.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует! ')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if task.deadline is not None:
        if task.deadline < datetime.date.today():
            raise InvalidDeadlineException('Время дэдлайна не может быть меньше сегодняшнего дня!')
    if task.assigned_to is not None:
        if not await repo_proj.is_user_in_project(project_id, task.assigned_to):
            raise PermissionDeniedException('Добавляемого пользователя нет в проекте!')
    try:
        result = await repo.create_task(project_id, task)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось создать задачу.')
    await delete_cache(project_tasks_key(project_id))
    if task.assigned_to is not None:
        await delete_cache(user_tasks_key(task.assigned_to, 'all'))
    return result


async def get_project_tasks(db: AsyncSession, project_id: int, current_user_id: int) -> list[dict]:
    """Возвращает все задачи проекта."""
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo_proj.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Пользователя нет в проекте!')
    key = project_tasks_key(project_id)
    cached = await get_cache(key)
    if cached is not None:
        return cached
    data = await repo.get_project_tasks(project_id)
    answer = [TaskResponse.model_validate(i).model_dump(mode='json') for i in data]
    await set_cache(key, answer, TTL_TASK_LIST)
    return answer


async def get_task_info(db: AsyncSession, project_id: int, current_user_id: int, task_id: int) -> dict | None:
    """Возвращает информацию о задаче."""
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo_proj.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    key = task_key(project_id, task_id)
    cached = await get_cache(key)
    if cached is not None:
        return cached
    data = await repo.get_task_by_id(task_id)
    answer = TaskResponse.model_validate(data).model_dump(mode='json')
    await set_cache(key, answer, TTL_TASK)
    return answer


async def get_tasks_user(db: AsyncSession, current_user_id: int) -> list[dict]:
    """Возвращает все задачи, назначенные на пользователя."""
    repo = TaskRepository(db)
    key = user_tasks_key(current_user_id, 'all')
    cached = await get_cache(key)
    if cached is not None:
        return cached
    data = await repo.get_tasks_by_user(current_user_id)
    answer = [TaskResponse.model_validate(i).model_dump(mode='json') for i in data]
    await set_cache(key, answer, TTL_TASK_LIST)
    return answer


async def update_task(db: AsyncSession, project_id: int, task_id: int, current_user_id: int, 
                        task: TaskUpdate) -> dict:
    """Обновляет задачу."""
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    repo_user = UserRepository(db)
    slov = task.model_dump(exclude_unset=True)
    if not slov:
        return {'message': 'Нет данных для обновления!'}
    if 'title' in slov and slov['title'] is None:
        raise LackOfInformationException('Название задачи не может быть пустым!')
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    is_performer = await repo.is_user_task_performer(task_id, current_user_id)
    is_admin = await repo_proj.is_user_admin_or_curator(project_id, current_user_id)
    if not (is_performer or is_admin):
        raise PermissionDeniedException('Задачу могут обновлять только админ, куратор или назначенный исполнитель!')
    if not is_admin:
        restricted = {'deadline', 'assigned_to', 'task_priority'} & set(slov.keys())
        if restricted:
            raise PermissionDeniedException('Только администратор или куратор может менять дедлайн, '
                'исполнителя и приоритет задачи!')
    if 'deadline' in slov and slov['deadline'] is not None:
        if slov['deadline'] < datetime.date.today():
            raise InvalidDeadlineException('Время дэдлайна не может быть меньше сегодняшнего дня!')
    if 'assigned_to' in slov and slov['assigned_to'] is not None:
        if not await repo_user.check_user_exists(slov['assigned_to']):
            raise NotFoundException('Такого пользователя не существует!')
        if not await repo_proj.is_user_in_project(project_id, slov['assigned_to']):
            raise PermissionDeniedException('Добавляемого пользователя нет в проекте!')
    old_info = await repo.get_task_by_id(task_id)
    previous_performer = old_info.assigned_to
    try:
        await repo.update_task_by_id(project_id, task_id, slov)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось обновить задачу.')
    await delete_cache(task_key(project_id, task_id))
    await delete_cache(project_tasks_key(project_id))
    if 'assigned_to' in slov and slov['assigned_to'] is not None:
        await delete_cache(user_tasks_key(slov['assigned_to'], 'all'))
        await delete_cache(user_tasks_key(previous_performer, 'all'))
    return {'message': 'Задача обновилась!'}


async def change_status(db: AsyncSession, project_id: int, task_id: int, current_user_id: int,
                        task_status: TaskStatus) -> dict:
    """Изменяет статус задачи."""
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo_proj.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    task = await repo.get_task_by_id(task_id)
    assignee = task.assigned_to if task else None
    is_admin = await repo_proj.is_user_admin_or_curator(project_id, current_user_id)
    is_assignee = current_user_id == assignee
    if not (is_admin or is_assignee):
        raise PermissionDeniedException('Не админ и не назначенный на задачу не может менять статус задачи!')
    try:
        changed = await repo.update_task_status(project_id, task_id, task_status.value)
        await db.commit()           
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось изменить статус задачи.')
    if not changed:
        return {'message': 'Статус уже установлен'}
    await delete_cache(task_key(project_id, task_id))
    await delete_cache(project_tasks_key(project_id))
    if assignee:
        await delete_cache(user_tasks_key(assignee, 'all'))
    return {'message': 'Статус обновлен!'}


async def delete_task(db: AsyncSession, project_id: int, task_id: int, current_user_id: int) -> dict:
    """Удаляет задачу."""
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo_proj.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    if not await repo_proj.is_user_admin_or_curator(project_id, current_user_id):
        raise PermissionDeniedException('Только создатель или куратор может удалить задачу.')
    task = await repo.get_task_by_id(task_id)
    assignee = task.assigned_to if task else None
    try:
        await repo.delete_task(task_id)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось удалить задачу.')
    await delete_cache(task_key(project_id, task_id))
    await delete_cache(project_tasks_key(project_id))
    if assignee:
        await delete_cache(user_tasks_key(assignee, 'all'))
    return {'message': 'Задача удалена из проекта!'}


async def create_task_comment(db: AsyncSession, project_id: int, 
                              task_id: int, message: str, current_user_id: int) -> TaskCommentsModel:
    """Создание комментария к задаче."""
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo_proj.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    try:
        result = await repo.create_comment(project_id, task_id, current_user_id, message)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось создать комментарий.')
    return result


async def delete_task_comment(db: AsyncSession, project_id: int, task_id: int, comment_id: int, 
                              current_user_id: int) -> dict:
    """Удалить комментарий у задачи."""
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo_proj.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    if await repo.get_comment_by_id(comment_id) is None:
        raise NotFoundException('Комментарий не найден!')
    comment_info = await repo.get_comment_by_id(comment_id)
    if comment_info.project_id != project_id or comment_info.task_id != task_id:
        raise ConflictException('Данные не подходят!')
    author = await repo.get_comment_author(project_id, task_id, comment_id)
    is_admin = await repo_proj.is_user_admin_or_curator(project_id, current_user_id)
    if not (is_admin or author == current_user_id):
        raise PermissionDeniedException('Не админ и не создатель комментария не может его удалить!')
    try:
        await repo.delete_comment(comment_id)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось удалить комментарий.')
    return {'message': 'Комментарий удален!'}


async def update_comment(db: AsyncSession, project_id: int, task_id: int, comment_id: int,
                        message: str, current_user_id: int) -> dict:
    """Обновить комментарий."""
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo_proj.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    author = await repo.get_comment_author(project_id, task_id, comment_id)
    if author is None:
        raise NotFoundException('Комментарий не найден!')
    is_admin = await repo_proj.is_user_admin_or_curator(project_id, current_user_id)
    if not (is_admin or author == current_user_id):
        raise PermissionDeniedException('Только админ или автор может изменить комментарий!')
    if len(message) > 1000:
        raise LackOfInformationException('Длина комментария не может быть больше 1000 символов!')
    comment_old = await repo.get_comment_by_id(comment_id)
    if message == comment_old.comment_text:
        return {'message': 'Комментарий не изменился!'}
    try:
        await repo.update_comment(comment_id, message)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось обновить комментарий.')
    return {'message': 'Комментарий обновлен!'}