from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession 
from services.task_service import get_project_tasks, create_task, update_task
from schemas.task import TaskCreate, TaskUpdate
from models.user import UserModel
from core.dependencies import get_db, current_user

router = APIRouter()

@router.get('/projects/{project_id}/tasks', tags=['Задачи'], \
            summary='Получить задачи проекта') # Получить задачи проекта
async def get_project_tasks(project_id: int, current_user: UserModel = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return await get_project_tasks(db, project_id, current_user.user_id)

@router.post('/projects/{project_id}/tasks', tags=['Задачи'], \
             summary='Создать задачу') # Создать задачу
async def create_task(project_id: int, task: TaskCreate, current_user: UserModel = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return await create_task(db, project_id, current_user.user_id, task)

@router.get('/projects/{project_id}/tasks/{task_id}', tags=['Задачи'], \
            summary='Получить инфорациюю о задаче') # Получить информацию о задаче
async def get_task_info():
    pass

@router.put('/projects/{project_id}/tasks/{task_id}', tags=['Задачи'], \
            summary='Обновить задачу') # Обновить задачу
async def update_task(project_id: int, task_id: int, task: TaskUpdate, current_user: UserModel = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return await update_task(db, project_id, task_id, current_user.user_id, task)

@router.patch('/tasks/{task_id}/status', tags=['Задачи'], \
              summary='Изменить статус задачи') # Изменить статус задачи
async def change_status():
    pass

@router.delete('/tasks/{task_id}', tags=['Задачи'], \
               summary='Удалить задачу') # Удалить задачу
async def delete_task():
    pass

@router.get('/tasks', tags=['Задачи'], \
            summary='Получить задачи пользователя') # Получить задачи пользователя
async def get_tasks_user():
    pass