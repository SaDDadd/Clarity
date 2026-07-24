from fastapi import APIRouter

router = APIRouter()

@router.get('/projects/{project_id}/tasks', tags=('Задачи'), \
            description='Получить задачи проекта') # Получить задачи проекта
async def get_tasks_project():

@router.post('/projects/{project_id}/tasks', tags=('Задачи'), \
             description='Создать задачу') # Создать задачу
async def create_task():

@router.get('/tasks/{task_id}', tags=('Задачи'), \
            descriptiom='Получить инфорациюю о задаче') # Получить информацию о задаче
async def get_task_info():

@router.put('/tasks/{task_id}', tags=('Задачи'), \
            description='Обновить задачу') # Обновить задачу
async def update_task():

@router.patch('/tasks/{task_id}/status', tags=('Задачи'), \
              description='Изменить статус задачи') # Изменить статус задачи
async def change_status():

@router.delete('/tasks/{task_id}', tags=('Задачи'), \
               description='Удалить задачу') # Удалить задачу
async def delete_task():

@router.get('/tasks', tags=('Задачи'), \
            description='Получить задачи пользователя') # Получить задачи пользователя
async def get_tasks_user():