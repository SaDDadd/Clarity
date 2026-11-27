from fastapi import APIRouter, Depends

from core.dependencies import current_user, get_uow
from core.uow import UnitOfWork
from models.user import UserModel
from schemas.task import TaskCreate, TaskStatusUpdate, TaskUpdate, TaskResponse
from services.task_service import (change_status, create_task, delete_task,
                                   get_project_tasks, get_task_info, get_tasks_user,
                                   update_task, get_favorite_tasks, get_all_user_tasks)
from core.filters import TaskFilter
from fastapi_filter import FilterDepends
from fastapi_pagination import Params, Page


router = APIRouter()


@router.put('/projects/{project_id}/tasks/{task_id}', response_model=dict, tags=['Задачи'],
            summary='Обновить задачу')
async def update_task_endpoint(project_id: int, task_id: int, task: TaskUpdate,
                               current_user: UserModel = Depends(current_user),
                               uow: UnitOfWork = Depends(get_uow)):
    """Обновляет задачу. Доступно участникам проекта."""
    return await update_task(uow, project_id, task_id, current_user.user_id, task)


@router.get('/tasks', response_model=Page[TaskResponse], tags=['Задачи'],
            summary='Получить задачи пользователя')
async def get_tasks_user_endpoint(current_user: UserModel = Depends(current_user),
                                  task_filter: TaskFilter = FilterDepends(TaskFilter),
                                  params: Params = Depends(),
                                  uow: UnitOfWork = Depends(get_uow)):
    """Возвращает все задачи, назначенные на текущего пользователя."""
    # добавить фильтраию и пагинацию
    return await get_tasks_user(uow, current_user.user_id, task_filter, params)


@router.get('/tasks/all', response_model=Page[TaskResponse], tags=['Задачи'], summary='Все задачи из доступных проектов')
async def get_all_user_tasks_endpoint(current_user: UserModel = Depends(current_user),
                                      task_filter: TaskFilter = FilterDepends(TaskFilter),
                                      params: Params = Depends(),
                                      uow: UnitOfWork = Depends(get_uow)):
    """Получить все задачи пользователя."""
    # добавить фильтрацию и пагинацию
    return await get_all_user_tasks(uow, current_user.user_id, task_filter, params)


@router.get('/tasks/favorites', response_model=Page[TaskResponse], tags=['Задачи'], summary='Получить избранные задачи.')
async def get_favorite_tasks_endpoint(current_user: UserModel = Depends(current_user),
                                      task_filter: TaskFilter = FilterDepends(TaskFilter),
                                      params: Params = Depends(),
                                      uow: UnitOfWork = Depends(get_uow)):
    """Получить все избранные задачи пользователя."""
    # добавить фильтрацию и пагинацию
    return await get_favorite_tasks(uow, current_user.user_id, task_filter, params)


@router.get('/projects/{project_id}/tasks', response_model=Page[TaskResponse], tags=['Задачи'],
            summary='Получить задачи проекта')
async def get_project_tasks_endpoint(project_id: int,
                                     current_user: UserModel = Depends(current_user),
                                     task_filter: TaskFilter = FilterDepends(TaskFilter),
                                     params: Params = Depends(),
                                     uow: UnitOfWork = Depends(get_uow)):
    """Возвращает все задачи указанного проекта. Доступно участникам проекта."""
    # добавить фильтраию и пагинацию
    return await get_project_tasks(uow, project_id, current_user.user_id, task_filter, params)


@router.get('/projects/{project_id}/tasks/{task_id}', response_model=TaskResponse, tags=['Задачи'],
            summary='Получить информацию о задаче')
async def get_task_info_endpoint(project_id: int, task_id: int,
                                 current_user: UserModel = Depends(current_user),
                                 uow: UnitOfWork = Depends(get_uow)):
    """Возвращает детальную информацию о задаче. Доступно участникам проекта."""
    return await get_task_info(uow, project_id, current_user.user_id, task_id)


@router.patch('/projects/{project_id}/tasks/{task_id}/status', response_model=dict, tags=['Задачи'],
              summary='Изменить статус задачи')
async def change_status_endpoint(task: TaskStatusUpdate, project_id: int, task_id: int,
                                 current_user: UserModel = Depends(current_user),
                                 uow: UnitOfWork = Depends(get_uow)):
    """Изменяет статус задачи. Доступно участникам проекта."""
    return await change_status(uow, project_id, task_id, current_user.user_id,
                               task.task_status)


@router.post('/projects/{project_id}/tasks', status_code=201, response_model=TaskResponse, tags=['Задачи'],
             summary='Создать задачу')
async def create_task_endpoint(project_id: int, task: TaskCreate,
                               current_user: UserModel = Depends(current_user),
                               uow: UnitOfWork = Depends(get_uow)):
    """Создаёт новую задачу в проекте. Доступно участникам проекта."""
    return await create_task(uow, project_id, current_user.user_id, task)


@router.delete('/projects/{project_id}/tasks/{task_id}', response_model=dict, tags=['Задачи'],
               summary='Удалить задачу')
async def delete_task_endpoint(project_id: int, task_id: int,
                               current_user: UserModel = Depends(current_user),
                               uow: UnitOfWork = Depends(get_uow)):
    """Удаляет задачу. Доступно участникам проекта."""
    return await delete_task(uow, project_id, task_id, current_user.user_id)