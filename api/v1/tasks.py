from fastapi import APIRouter, Depends

from core.dependencies import current_user, get_uow
from core.uow import UnitOfWork
from models.user import UserModel
from schemas.task import TaskCreate, TaskStatusUpdate, TaskUpdate, TaskCommentCreate
from services.task_service import (change_status, create_task, delete_task,
                                   get_project_tasks, get_task_info, get_tasks_user,
                                   update_task, create_task_comment, delete_task_comment,
                                   update_comment, get_task_comments)
from core.filters import TaskFilter, CommentFilter
from fastapi_filter import FilterDepends

router = APIRouter()


@router.put('/projects/{project_id}/tasks/{task_id}', tags=['Задачи'],
            summary='Обновить задачу')
async def update_task_endpoint(project_id: int, task_id: int, task: TaskUpdate,
                               current_user: UserModel = Depends(current_user),
                               uow: UnitOfWork = Depends(get_uow)):
    """Обновляет задачу. Доступно участникам проекта."""
    return await update_task(uow, project_id, task_id, current_user.user_id, task)


@router.put('/projects/{project_id}/tasks/{task_id}/comments/{comment_id}', tags=['Комментарии'],
            summary='Обновление комментария задачи.')
async def update_comment_endpoint(message: TaskCommentCreate, project_id: int, task_id: int,
                                  comment_id: int, current_user: UserModel = Depends(current_user),
                                  uow: UnitOfWork = Depends(get_uow)):
    """Обновление комментария."""
    return await update_comment(uow, project_id, task_id, comment_id, message.comment_text, current_user.user_id)


@router.get('/tasks', tags=['Задачи'],
            summary='Получить задачи пользователя')
async def get_tasks_user_endpoint(current_user: UserModel = Depends(current_user),
                                  task_filter: TaskFilter = FilterDepends(TaskFilter),
                                  uow: UnitOfWork = Depends(get_uow)):
    """Возвращает все задачи, назначенные на текущего пользователя."""
    # добавить фильтраию и пагинацию
    return await get_tasks_user(uow, current_user.user_id, task_filter)


@router.get('/projects/{project_id}/tasks', tags=['Задачи'],
            summary='Получить задачи проекта')
async def get_project_tasks_endpoint(project_id: int,
                                     current_user: UserModel = Depends(current_user),
                                     task_filter: TaskFilter = FilterDepends(TaskFilter),
                                     uow: UnitOfWork = Depends(get_uow)):
    """Возвращает все задачи указанного проекта. Доступно участникам проекта."""
    # добавить фильтраию и пагинацию
    return await get_project_tasks(uow, project_id, current_user.user_id, task_filter)


@router.get('/projects/{project_id}/tasks/{task_id}', tags=['Задачи'],
            summary='Получить информацию о задаче')
async def get_task_info_endpoint(project_id: int, task_id: int,
                                 current_user: UserModel = Depends(current_user),
                                 uow: UnitOfWork = Depends(get_uow)):
    """Возвращает детальную информацию о задаче. Доступно участникам проекта."""
    return await get_task_info(uow, project_id, current_user.user_id, task_id)


@router.get('/projects/{project_id}/tasks/{task_id}/comments', tags=['Комментарии'],
            summary='Получить комментарии задачи')
async def get_task_comments_endpoint(project_id: int, task_id: int,
                                     current_user: UserModel = Depends(current_user),
                                     comment_filter: CommentFilter = FilterDepends(CommentFilter),
                                     uow: UnitOfWork = Depends(get_uow)):
    """Возвращает комментарии задачи."""
    # добавить фильтраию и пагинацию
    return await get_task_comments(uow, project_id, task_id, current_user.user_id, comment_filter)


@router.patch('/projects/{project_id}/tasks/{task_id}/status', tags=['Задачи'],
              summary='Изменить статус задачи')
async def change_status_endpoint(task: TaskStatusUpdate, project_id: int, task_id: int,
                                 current_user: UserModel = Depends(current_user),
                                 uow: UnitOfWork = Depends(get_uow)):
    """Изменяет статус задачи. Доступно участникам проекта."""
    return await change_status(uow, project_id, task_id, current_user.user_id,
                               task.task_status)


@router.post('/projects/{project_id}/tasks', status_code=201, tags=['Задачи'],
             summary='Создать задачу')
async def create_task_endpoint(project_id: int, task: TaskCreate,
                               current_user: UserModel = Depends(current_user),
                               uow: UnitOfWork = Depends(get_uow)):
    """Создаёт новую задачу в проекте. Доступно участникам проекта."""
    return await create_task(uow, project_id, current_user.user_id, task)


@router.post('/projects/{project_id}/tasks/{task_id}/comments', tags=['Комментарии'],
             summary='Написать комментарий к задаче.')
async def create_task_comment_endpoint(message: TaskCommentCreate, project_id: int, task_id: int,
                                       current_user: UserModel = Depends(current_user),
                                       uow: UnitOfWork = Depends(get_uow)):
    """Написать комментарий к задаче проекта."""
    return await create_task_comment(uow, project_id, task_id, message.comment_text, current_user.user_id)


@router.delete('/projects/{project_id}/tasks/{task_id}', tags=['Задачи'],
               summary='Удалить задачу')
async def delete_task_endpoint(project_id: int, task_id: int,
                               current_user: UserModel = Depends(current_user),
                               uow: UnitOfWork = Depends(get_uow)):
    """Удаляет задачу. Доступно участникам проекта."""
    return await delete_task(uow, project_id, task_id, current_user.user_id)


@router.delete('/projects/{project_id}/tasks/{task_id}/comments/{comment_id}', tags=['Комментарии'],
               summary='Удалить комментарий к задаче.')
async def delete_task_comment_endpoint(project_id: int, task_id: int, comment_id: int,
                                      current_user: UserModel = Depends(current_user),
                                      uow: UnitOfWork = Depends(get_uow)):
    """Удаление комментария задачи."""
    return await delete_task_comment(uow, project_id, task_id, comment_id, current_user.user_id)