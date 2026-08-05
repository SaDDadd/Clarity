from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession 
from services.task_service import get_task_by_id
from core.dependencies import get_db

router = APIRouter()

@router.get('/projects/{project_id}/tasks', tags=['Задачи'], \
            summary='Получить задачи проекта') # Получить задачи проекта
async def get_tasks_project(project_id: int, task_id: int, db: AsyncSession = Depends(get_db)):
    return await get_task_by_id(db, project_id, task_id)

@router.post('/projects/{project_id}/tasks', tags=['Задачи'], \
             summary='Создать задачу') # Создать задачу
async def create_task():

@router.get('/tasks/{task_id}', tags=['Задачи'], \
            summary='Получить инфорациюю о задаче') # Получить информацию о задаче
async def get_task_info():

@router.put('/tasks/{task_id}', tags=['Задачи'], \
            summary='Обновить задачу') # Обновить задачу
async def update_task():

@router.patch('/tasks/{task_id}/status', tags=['Задачи'], \
              summary='Изменить статус задачи') # Изменить статус задачи
async def change_status():

@router.delete('/tasks/{task_id}', tags=['Задачи'], \
               summary='Удалить задачу') # Удалить задачу
async def delete_task():

@router.get('/tasks', tags=['Задачи'], \
            summary='Получить задачи пользователя') # Получить задачи пользователя
async def get_tasks_user():