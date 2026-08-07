from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db, current_user
from models.user import UserModel
from schemas.task import TaskCreate, TaskStatusUpdate, TaskUpdate
from services.task_service import change_status, create_task, delete_task,\
    get_project_tasks, get_task_info, get_tasks_user, update_task

router = APIRouter()

# POST
@router.post('/projects/{project_id}/tasks', tags=['Задачи'],\
             summary='Создать задачу') # Создать задачу
async def create_task_endpoint(project_id: int, task: TaskCreate,\
                                    current_user: UserModel = Depends(current_user),\
                                    db: AsyncSession = Depends(get_db)):
    return await create_task(db, project_id, current_user.user_id, task)

# PATCH
@router.patch('/projects/{project_id}/tasks/{task_id}/status', tags=['Задачи'], \
              summary='Изменить статус задачи') # Изменить статус задачи
async def change_status_endpoint(task: TaskStatusUpdate, project_id: int, task_id: int,\
                                    current_user: UserModel = Depends(current_user),\
                                    db: AsyncSession = Depends(get_db)):
    return await change_status(db, project_id, task_id, current_user.user_id, task.task_status)

# GET
@router.get('/tasks', tags=['Задачи'], \
            summary='Получить задачи пользователя') # Получить задачи пользователя
async def get_tasks_user_endpoint(current_user: UserModel = Depends(current_user),\
                                    db: AsyncSession = Depends(get_db)):
    return await get_tasks_user(db, current_user.user_id)

@router.get('/projects/{project_id}/tasks', tags=['Задачи'], \
            summary='Получить задачи проекта') # Получить задачи проекта
async def get_project_tasks_endpoint(project_id: int, current_user: UserModel = Depends(current_user),\
                                        db: AsyncSession = Depends(get_db)):
    return await get_project_tasks(db, project_id, current_user.user_id)

@router.get('/projects/{project_id}/tasks/{task_id}', tags=['Задачи'], \
            summary='Получить инфорациюю о задаче') # Получить информацию о задаче
async def get_task_info_endpoint(project_id: int, task_id: int,\
                                    current_user: UserModel = Depends(current_user),\
                                    db: AsyncSession = Depends(get_db)):
    return await get_task_info(db, project_id, current_user.user_id, task_id)

# PUT
@router.put('/projects/{project_id}/tasks/{task_id}', tags=['Задачи'], \
            summary='Обновить задачу') # Обновить задачу
async def update_task_endpoint(project_id: int, task_id: int, task: TaskUpdate,\
                                    current_user: UserModel = Depends(current_user),\
                                    db: AsyncSession = Depends(get_db)):
    return await update_task(db, project_id, task_id, current_user.user_id, task)

# DELETE
@router.delete('/projects/{project_id}/tasks/{task_id}', tags=['Задачи'], \
               summary='Удалить задачу') # Удалить задачу
async def delete_task_endpoint(project_id: int, task_id: int,\
                                    current_user: UserModel = Depends(current_user),\
                                    db: AsyncSession = Depends(get_db)):
    return await delete_task(db, project_id, task_id, current_user.user_id)