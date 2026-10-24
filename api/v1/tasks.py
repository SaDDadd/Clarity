from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import current_user, get_db
from models.user import UserModel
from schemas.task import TaskCreate, TaskStatusUpdate, TaskUpdate, TaskCommentCreate
from services.task_service import (change_status, create_task, delete_task,
                                   get_project_tasks, get_task_info, get_tasks_user,
                                   update_task, create_task_comment, delete_task_comment,
                                   update_comment)
router = APIRouter()


@router.post('/projects/{project_id}/tasks', status_code=201, tags=['Задачи'],
             summary='Создать задачу')
async def create_task_endpoint(project_id: int, task: TaskCreate,
                               current_user: UserModel = Depends(current_user),
                               db: AsyncSession = Depends(get_db)):
    """Создаёт новую задачу в проекте. Доступно участникам проекта."""
    return await create_task(db, project_id, current_user.user_id, task)


@router.patch('/projects/{project_id}/tasks/{task_id}/status', tags=['Задачи'],
              summary='Изменить статус задачи')
async def change_status_endpoint(task: TaskStatusUpdate, project_id: int, task_id: int,
                                 current_user: UserModel = Depends(current_user),
                                 db: AsyncSession = Depends(get_db)):
    """Изменяет статус задачи. Доступно участникам проекта."""
    return await change_status(db, project_id, task_id, current_user.user_id,
                               task.task_status)


@router.get('/tasks', tags=['Задачи'],
            summary='Получить задачи пользователя')
async def get_tasks_user_endpoint(current_user: UserModel = Depends(current_user),
                                  db: AsyncSession = Depends(get_db)):
    """Возвращает все задачи, назначенные на текущего пользователя."""
    return await get_tasks_user(db, current_user.user_id)


@router.get('/projects/{project_id}/tasks', tags=['Задачи'],
            summary='Получить задачи проекта')
async def get_project_tasks_endpoint(project_id: int,
                                     current_user: UserModel = Depends(current_user),
                                     db: AsyncSession = Depends(get_db)):
    """Возвращает все задачи указанного проекта. Доступно участникам проекта."""
    return await get_project_tasks(db, project_id, current_user.user_id)


@router.get('/projects/{project_id}/tasks/{task_id}', tags=['Задачи'],
            summary='Получить информацию о задаче')
async def get_task_info_endpoint(project_id: int, task_id: int,
                                 current_user: UserModel = Depends(current_user),
                                 db: AsyncSession = Depends(get_db)):
    """Возвращает детальную информацию о задаче. Доступно участникам проекта."""
    return await get_task_info(db, project_id, current_user.user_id, task_id)


@router.put('/projects/{project_id}/tasks/{task_id}', tags=['Задачи'],
            summary='Обновить задачу')
async def update_task_endpoint(project_id: int, task_id: int, task: TaskUpdate,
                               current_user: UserModel = Depends(current_user),
                               db: AsyncSession = Depends(get_db)):
    """Обновляет задачу. Доступно участникам проекта."""
    return await update_task(db, project_id, task_id, current_user.user_id, task)


@router.delete('/projects/{project_id}/tasks/{task_id}', tags=['Задачи'],
               summary='Удалить задачу')
async def delete_task_endpoint(project_id: int, task_id: int,
                               current_user: UserModel = Depends(current_user),
                               db: AsyncSession = Depends(get_db)):
    """Удаляет задачу. Доступно участникам проекта."""
    return await delete_task(db, project_id, task_id, current_user.user_id)

@router.post('/projects/{project_id}/tasks/{task_id}/comments', tags=['Комментарии'],
             summary='Написать комментарий к задаче.')
async def create_task_comment_endpoint(message: TaskCommentCreate, project_id: int, task_id: int, 
                                       current_user: UserModel = Depends(current_user), 
                                       db: AsyncSession = Depends(get_db)):
    """Написать комментарий к задаче проекта."""
    return await create_task_comment(db, project_id, task_id, message.comment_text, current_user.user_id)

@router.delete('/projects/{project_id}/tasks/{task_id}/comments/{comment_id}', tags=['Комментарии'],
               summary='Удалить комментарий к задаче.')
async def delete_task_comment_endpoint(project_id: int, task_id: int, comment_id: int,  
                                      current_user: UserModel = Depends(current_user), 
                                      db: AsyncSession = Depends(get_db)):
    """Удаление комментария задачи."""
    return await delete_task_comment(db, project_id, task_id, comment_id, current_user.user_id)

@router.put('/projects/{project_id}/tasks/{task_id}/comments/{comment_id}', tags=['Комментарии'], 
            summary='Обновление комментария задачи.')
async def update_comment_endpoint(message: TaskCommentCreate, project_id: int, task_id: int, 
                                  comment_id: int, current_user: UserModel = Depends(current_user),
                                  db: AsyncSession = Depends(get_db)):
    """Обновление комментария."""
    return await update_comment(db, project_id, task_id, comment_id, message.comment_text, current_user.user_id)