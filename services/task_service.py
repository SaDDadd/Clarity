import datetime

from core.exceptions import (InvalidDeadlineException, NotFoundException, 
    PermissionDeniedException, LackOfInformationException, AppException, 
    ConflictException)
from schemas.task import TaskResponse, TaskCreate, TaskUpdate, TaskCommentResponse
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from schemas.common import TaskStatus
from sqlalchemy.ext.asyncio import AsyncSession 
from cache.cache_keys import (project_tasks_key, user_tasks_key, task_key, 
    task_comments_list_key, task_comments_pattern, TTL_TASK, TTL_TASK_LIST, TTL_TASK_COMMENT_LIST)
from cache.cache_service import get_cache, delete_cache, set_cache, delete_cache_by_pattern

async def create_task(db: AsyncSession, project_id: int, current_user_id: int, task: TaskCreate) -> dict:
    """Создаёт задачу. Паттерн как в create_project."""
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo_proj.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует! ')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if task.deadline is not None and task.deadline < datetime.date.today():
        raise InvalidDeadlineException(
            'Время дэдлайна не может быть меньше сегодняшнего дня!')
    if task.assigned_to is not None:
        if not await repo_proj.is_user_in_project(project_id, task.assigned_to):
            raise PermissionDeniedException('Добавляемого пользователя нет в проекте!')
    try:
        result = await repo.create_task(project_id, task)
        await db.refresh(result)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось создать задачу!')
    answer = TaskResponse.model_validate(result).model_dump(mode='json')
    await delete_cache(project_tasks_key(project_id))
    if task.assigned_to is not None:
        await delete_cache(user_tasks_key(task.assigned_to))
    return answer


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


async def get_task_info(db: AsyncSession, project_id: int, current_user_id: int, task_id: int) -> dict:
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
    update_data = task.model_dump(exclude_unset=True)
    if 'task_favorite' in update_data and update_data['task_favorite'] is None:
        """Проверяем, что флаг избранного не равен null."""
        raise LackOfInformationException('Флаг избранного не может быть null!')
    if 'task_status' in update_data:
        """Преобразуем статус задачи в строковое значение."""
        if update_data['task_status'] is None:
            raise LackOfInformationException('Статус задачи не может быть null!')
        update_data['task_status'] = task.task_status.value
    if 'task_priority' in update_data:
        """Преобразуем приоритет задачи в строковое значение."""
        if update_data['task_priority'] is None:
            raise LackOfInformationException('Приоритет не может быть null!')
        update_data['task_priority'] = task.task_priority.value
    if not update_data:
        return {'message': 'Нет данных для обновления!'}
    if 'title' in update_data and update_data['title'] is None:
        raise LackOfInformationException('Название задачи не может быть пустым!')
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    is_performer = await repo.is_user_task_performer(task_id, current_user_id)
    is_admin_or_curator = await repo_proj.is_user_admin_or_curator(project_id, current_user_id)
    if not (is_performer or is_admin_or_curator):
        raise PermissionDeniedException('Задачу могут обновлять только админ, куратор или назначенный исполнитель!')
    if not is_admin_or_curator:
        """Ограничиваем поля, доступные исполнителю без прав администратора."""
        restricted = {'deadline', 'assigned_to', 'task_priority'} & set(update_data.keys())
        if restricted:
            raise PermissionDeniedException('Только администратор или куратор может менять дедлайн, исполнителя и приоритет задачи!')
    if 'deadline' in update_data and update_data['deadline'] is not None:
        """Проверяем, что новый дедлайн не в прошлом."""
        if update_data['deadline'] < datetime.date.today():
            raise InvalidDeadlineException('Время дэдлайна не может быть меньше сегодняшнего дня!')
    if 'assigned_to' in update_data and update_data['assigned_to'] is not None:
        """Проверяем существование и участие нового исполнителя."""
        if not await repo_user.check_user_exists(update_data['assigned_to']):
            raise NotFoundException('Такого пользователя не существует!')
        if not await repo_proj.is_user_in_project(project_id, update_data['assigned_to']):
            raise PermissionDeniedException('Добавляемого пользователя нет в проекте!')
    old_info = await repo.get_task_by_id(task_id)
    previous_performer = old_info.assigned_to if old_info else None
    try:
        await repo.update_task_by_id(project_id, task_id, update_data)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось обновить задачу!')
    await delete_cache(task_key(project_id, task_id))
    await delete_cache(project_tasks_key(project_id))
    if previous_performer is not None:
        """Инвалидируем кэш задач предыдущего исполнителя."""
        await delete_cache(user_tasks_key(previous_performer, 'all'))
    if 'assigned_to' in update_data:
        """Инвалидируем кэш задач нового исполнителя при необходимости."""
        new_performer = update_data['assigned_to']
        if new_performer is not None and new_performer != previous_performer:
            """Инвалидируем кэш, если исполнитель изменился."""
            await delete_cache(user_tasks_key(new_performer, 'all'))
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
        raise AppException(500, 'Не удалось изменить статус задачи!')
    if not changed:
        return {'message': 'Статус уже установлен!'}
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
        raise AppException(500, 'Не удалось удалить задачу!')
    await delete_cache(task_key(project_id, task_id))
    await delete_cache(project_tasks_key(project_id))
    if assignee:
        await delete_cache(user_tasks_key(assignee, 'all'))
    await delete_cache_by_pattern(task_comments_pattern(project_id, task_id))
    return {'message': 'Задача удалена из проекта!'}


async def create_task_comment(db: AsyncSession, project_id: int, task_id: int,
                              message: str, current_user_id: int) -> dict:
    """Создаёт комментарий."""
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
        await db.refresh(result)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось создать комментарий!')
    answer = TaskCommentResponse.model_validate(result).model_dump(mode='json')
    await delete_cache(task_comments_list_key(project_id, task_id))
    return answer

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
    comment_info = await repo.get_comment_by_id(comment_id)
    if comment_info is None:
        raise NotFoundException('Комментарий не найден!')
    if comment_info.project_id != project_id or comment_info.task_id != task_id:
        raise ConflictException('Данные не подходят!')
    author_id = comment_info.author_id
    is_admin_or_curator = await repo_proj.is_user_admin_or_curator(project_id, current_user_id)
    if not (is_admin_or_curator or (author_id is not None and author_id == current_user_id)):
        raise PermissionDeniedException('Не админ и не создатель комментария не может его удалить!')
    try:
        await repo.delete_comment(comment_id)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось удалить комментарий!')
    await delete_cache(task_comments_list_key(project_id, task_id))
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
    comment = await repo.get_comment_by_id(comment_id)
    if comment is None:
        raise NotFoundException('Комментарий не найден!')
    if comment.project_id != project_id or comment.task_id != task_id:
        raise ConflictException('Данные не подходят!')
    is_admin_or_curator = await repo_proj.is_user_admin_or_curator(project_id, current_user_id)
    if not (is_admin_or_curator or comment.author_id == current_user_id):
        raise PermissionDeniedException('Только админ, куратор или автор комментария могут изменить комментарий!')
    if len(message) > 1000:
        raise LackOfInformationException('Длина комментария не может быть больше 1000 символов!')
    if message == comment.comment_text:
        return {'message': 'Комментарий не изменился!'}
    try:
        await repo.update_comment(comment_id, message)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось обновить комментарий!')
    await delete_cache(task_comments_list_key(project_id, task_id))
    return {'message': 'Комментарий обновлен!'}


async def get_task_comments(db: AsyncSession, project_id: int, task_id: int,
                            current_user_id: int) -> list[dict]:
    """Список комментариев задачи."""
    repo = TaskRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo_proj.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await repo.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    key = task_comments_list_key(project_id, task_id)
    cached = await get_cache(key)
    if cached is not None:
        return cached
    data = await repo.get_task_comments(project_id, task_id)
    answer = [TaskCommentResponse.model_validate(c).model_dump(mode='json') for c in data]
    await set_cache(key, answer, TTL_TASK_COMMENT_LIST)
    return answer