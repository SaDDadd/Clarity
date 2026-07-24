from fastapi import APIRouter 

router = APIRouter()

@router.get('/projects', tags=('Проекты'), \
            description='Вывод проектов, в которых участвует пользователь') # Получение проектов пользователя
async def get_projects():

@router.post('/projects', tags=('Проекты'), \
             description='Создание проекта') # Создание проекта
async def create_project():

@router.get('/projects/{projects_id}', tags=('Проекты'), \
            description='Получить информацию о проекте') # Получить информацию о проекте 
async def get_project_info():

@router.put('/projects/{projects_id}', tags=('Проекты'), \
            description='Обновить описание проекта') # Обновить описание проекта
async def update_project_description():

@router.delete('/projects/{project_id}', tags=('Проекты'), \
               description='Удалить проект') # Удалить проект
async def delete_project():

@router.delete('/projects/{project_id}/members/{user_id}', tags=('Проекты'), \
               description='Удалить участника из проекта') # Удалить участника из проекта
async def delete_project_user():

@router.post('/projects/{project_id}/members', tags=('Проекты'), \
             description='Добавить участника в проект') # Добавление участника в проект (только админ)