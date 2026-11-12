import datetime

from core.exceptions import (InvalidDeadlineException, NotFoundException,
    PermissionDeniedException, LackOfInformationException, ConflictException)
from schemas.task import TaskResponse, TaskCreate, TaskUpdate, TaskCommentResponse
from schemas.common import TaskStatus
from core.uow import UnitOfWork
from cache.cache_keys import (project_tasks_key, user_tasks_key, task_key,
            task_comments_list_key, TTL_TASK, TTL_TASK_LIST, TTL_TASK_COMMENT_LIST)
from cache.cache_service import get_cache, delete_cache, set_cache, has_filter
from core.filters import TaskFilter, CommentFilter


async def update_task(uow: UnitOfWork, project_id: int, task_id: int, current_user_id: int,
                      task: TaskUpdate) -> dict:
    """Обновляет задачу."""
    update_data = task.model_dump(exclude_unset=True)
    if 'task_favorite' in update_data and update_data['task_favorite'] is None:
        raise LackOfInformationException('Флаг избранного не может быть null!')
    if 'task_status' in update_data:
        if update_data['task_status'] is None:
            raise LackOfInformationException('Статус задачи не может быть null!')
        update_data['task_status'] = task.task_status.value
    if 'task_priority' in update_data:
        if update_data['task_priority'] is None:
            raise LackOfInformationException('Приоритет не может быть null!')
        update_data['task_priority'] = task.task_priority.value
    if not update_data:
        return {'message': 'Нет данных для обновления!'}
    if 'title' in update_data and update_data['title'] is None:
        raise LackOfInformationException('Название задачи не может быть пустым!')
    if not await uow.task.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    is_performer = await uow.task.is_user_task_performer(task_id, current_user_id)
    is_admin_or_curator = await uow.project.is_user_admin_or_curator(project_id, current_user_id)
    if not (is_performer or is_admin_or_curator):
        raise PermissionDeniedException('Задачу могут обновлять только админ, куратор или назначенный исполнитель!')
    if not is_admin_or_curator:
        """Ограничиваем поля, доступные исполнителю без прав администратора."""
        restricted = {'deadline', 'assigned_to', 'task_priority'} & set(update_data.keys())
        if restricted:
            raise PermissionDeniedException('Только администратор или куратор может менять дедлайн, исполнителя и приоритет задачи!')
    if 'deadline' in update_data and update_data['deadline'] is not None:
        if update_data['deadline'] < datetime.date.today():
            raise InvalidDeadlineException('Время дэдлайна не может быть меньше сегодняшнего дня!')
    if 'assigned_to' in update_data and update_data['assigned_to'] is not None:
        if not await uow.user.check_user_exists(update_data['assigned_to']):
            raise NotFoundException('Такого пользователя не существует!')
        if not await uow.project.is_user_in_project(project_id, update_data['assigned_to']):
            raise PermissionDeniedException('Добавляемого пользователя нет в проекте!')
    old_info = await uow.task.get_task_by_id(task_id)
    previous_performer = old_info.assigned_to if old_info else None
    await uow.task.update_task_by_id(project_id, task_id, update_data)
    await delete_cache(task_key(project_id, task_id))
    await delete_cache(project_tasks_key(project_id))
    if previous_performer is not None:
        """Инвалидируем кэш задач предыдущего исполнителя."""
        await delete_cache(user_tasks_key(previous_performer, 'all'))
    if 'assigned_to' in update_data:
        """Инвалидируем кэш задач нового исполнителя."""
        new_performer = update_data['assigned_to']
        if new_performer is not None and new_performer != previous_performer:
            """Инвалидируем кэш, если исполнитель изменился."""
            await delete_cache(user_tasks_key(new_performer, 'all'))
    return {'message': 'Задача обновилась!'}


async def update_comment(uow: UnitOfWork, project_id: int, task_id: int, comment_id: int,
                        message: str, current_user_id: int) -> dict:
    """Обновить комментарий."""
    if await uow.project.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await uow.task.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    comment = await uow.task.get_comment_by_id(comment_id)
    if comment is None:
        raise NotFoundException('Комментарий не найден!')
    if comment.project_id != project_id or comment.task_id != task_id:
        raise ConflictException('Данные не подходят!')
    is_admin_or_curator = await uow.project.is_user_admin_or_curator(project_id, current_user_id)
    if not (is_admin_or_curator or comment.author_id == current_user_id):
        raise PermissionDeniedException('Только админ, куратор или автор комментария могут изменить комментарий!')
    if len(message) > 1000:
        raise LackOfInformationException('Длина комментария не может быть больше 1000 символов!')
    if message == comment.comment_text:
        return {'message': 'Комментарий не изменился!'}
    await uow.task.update_comment(comment_id, message)
    await delete_cache(task_comments_list_key(project_id, task_id))
    return {'message': 'Комментарий обновлен!'}


async def get_project_tasks(uow: UnitOfWork, project_id: int, current_user_id: int,
                                task_filter: TaskFilter | None = None) -> list[dict]:
    """Возвращает все задачи проекта."""
    if await uow.project.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Пользователя нет в проекте!')
    use_cache = not await has_filter(task_filter)
    key = project_tasks_key(project_id)
    if use_cache:
        cached = await get_cache(key)
        if cached is not None:
            return cached
    data = await uow.task.get_project_tasks(project_id, task_filter)
    answer = [TaskResponse.model_validate(i).model_dump(mode='json') for i in data]
    if use_cache:
        await set_cache(key, answer, TTL_TASK_LIST)
    return answer


async def get_task_info(uow: UnitOfWork, project_id: int, current_user_id: int, task_id: int) -> dict:
    """Возвращает информацию о задаче."""
    if await uow.project.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await uow.task.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    key = task_key(project_id, task_id)
    cached = await get_cache(key)
    if cached is not None:
        return cached
    data = await uow.task.get_task_by_id(task_id)
    answer = TaskResponse.model_validate(data).model_dump(mode='json')
    await set_cache(key, answer, TTL_TASK)
    return answer


async def get_tasks_user(uow: UnitOfWork, current_user_id: int, task_filter: TaskFilter | None = None) -> list[dict]:
    """Возвращает все задачи, назначенные на пользователя."""
    use_cache = not await has_filter(task_filter)
    key = user_tasks_key(current_user_id, 'all')
    if use_cache:
        cached = await get_cache(key)
        if cached is not None:
            return cached
    data = await uow.task.get_tasks_by_user(current_user_id, task_filter)
    answer = [TaskResponse.model_validate(i).model_dump(mode='json') for i in data]
    if use_cache:
        await set_cache(key, answer, TTL_TASK_LIST)
    return answer


async def get_task_comments(uow: UnitOfWork, project_id: int, task_id: int, current_user_id: int,
                                comment_filter: CommentFilter | None = None) -> list[dict]:
    """Список комментариев задачи."""
    if await uow.project.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await uow.task.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    use_cache = not await has_filter(comment_filter)
    key = task_comments_list_key(project_id, task_id)
    if use_cache:
        cached = await get_cache(key)
        if cached is not None:
            return cached
    result = await uow.task.get_task_comments(project_id, task_id, comment_filter)
    answer = [TaskCommentResponse.model_validate(com).model_dump(mode='json') for com in result]
    if use_cache:
        await set_cache(key, answer, TTL_TASK_COMMENT_LIST)
    return answer


async def change_status(uow: UnitOfWork, project_id: int, task_id: int, current_user_id: int,
                        task_status: TaskStatus) -> dict:
    """Изменяет статус задачи."""
    if await uow.project.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await uow.task.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    task = await uow.task.get_task_by_id(task_id)
    assignee = task.assigned_to if task else None
    is_admin = await uow.project.is_user_admin_or_curator(project_id, current_user_id)
    is_assignee = current_user_id == assignee
    if not (is_admin or is_assignee):
        raise PermissionDeniedException('Не админ и не назначенный на задачу не может менять статус задачи!')
    changed = await uow.task.update_task_status(project_id, task_id, task_status.value)
    if not changed:
        return {'message': 'Статус уже установлен!'}
    await delete_cache(task_key(project_id, task_id))
    await delete_cache(project_tasks_key(project_id))
    if assignee:
        await delete_cache(user_tasks_key(assignee, 'all'))
    return {'message': 'Статус обновлен!'}


async def create_task(uow: UnitOfWork, project_id: int, current_user_id: int, task: TaskCreate) -> dict:
    """Создаёт задачу."""
    if await uow.project.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует! ')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await uow.project.is_user_admin_or_curator(project_id, current_user_id):
        raise PermissionDeniedException('Не админ и не куратор не может создавать задачи!')
    if task.deadline is not None and task.deadline < datetime.date.today():
        raise InvalidDeadlineException('Время дэдлайна не может быть меньше сегодняшнего дня!')
    if task.assigned_to is not None:
        if not await uow.project.is_user_in_project(project_id, task.assigned_to):
            raise PermissionDeniedException('Добавляемого пользователя нет в проекте!')
    result = await uow.task.create_task(project_id, task)
    answer = TaskResponse.model_validate(result).model_dump(mode='json')
    await delete_cache(project_tasks_key(project_id))
    if task.assigned_to is not None:
        """Инвалидируем кэш задач назначенного пользователя."""
        await delete_cache(user_tasks_key(task.assigned_to, 'all'))
    return answer


async def create_task_comment(uow: UnitOfWork, project_id: int, task_id: int,
                              message: str, current_user_id: int) -> dict:
    """Создаёт комментарий."""
    if await uow.project.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await uow.task.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    result = await uow.task.create_comment(project_id, task_id, current_user_id, message)
    answer = TaskCommentResponse.model_validate(result).model_dump(mode='json')
    await delete_cache(task_comments_list_key(project_id, task_id))
    return answer


async def delete_task(uow: UnitOfWork, project_id: int, task_id: int, current_user_id: int) -> dict:
    """Удаляет задачу."""
    if await uow.project.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await uow.task.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    if not await uow.project.is_user_admin_or_curator(project_id, current_user_id):
        raise PermissionDeniedException('Только создатель или куратор может удалить задачу.')
    task = await uow.task.get_task_by_id(task_id)
    assignee = task.assigned_to if task else None
    await uow.task.delete_task(task_id)
    await delete_cache(task_key(project_id, task_id))
    await delete_cache(project_tasks_key(project_id))
    if assignee:
        await delete_cache(user_tasks_key(assignee, 'all'))
    await delete_cache(task_comments_list_key(project_id, task_id))
    return {'message': 'Задача удалена из проекта!'}


async def delete_task_comment(uow: UnitOfWork, project_id: int, task_id: int, comment_id: int,
                              current_user_id: int) -> dict:
    """Удалить комментарий у задачи."""
    if await uow.project.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await uow.task.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    comment_info = await uow.task.get_comment_by_id(comment_id)
    if comment_info is None:
        raise NotFoundException('Комментарий не найден!')
    if comment_info.project_id != project_id or comment_info.task_id != task_id:
        raise ConflictException('Данные не подходят!')
    author_id = comment_info.author_id
    is_admin_or_curator = await uow.project.is_user_admin_or_curator(project_id, current_user_id)
    if not (is_admin_or_curator or (author_id is not None and author_id == current_user_id)):
        raise PermissionDeniedException('Не админ и не создатель комментария не может его удалить!')
    await uow.task.delete_comment(comment_id)
    await delete_cache(task_comments_list_key(project_id, task_id))
    return {'message': 'Комментарий удален!'}