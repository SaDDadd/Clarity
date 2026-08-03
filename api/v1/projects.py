from fastapi import APIRouter 
from services.project_service import create_project, get_project

router = APIRouter()

@router.get('/projects', tags=['Проекты'], \
            summary='Вывод проектов, в которых участвует пользователь') # Получение проектов пользователя
async def get_projects():


@router.post('/projects', tags=['Проекты'], \
             summary='Создание проекта') # Создание проекта
async def create_project():

@router.get('/projects/{projects_id}', tags=['Проекты'], \
            summary='Получить информацию о проекте') # Получить информацию о проекте 
async def get_project_info():

@router.put('/projects/{projects_id}', tags=['Проекты'], \
            summary='Обновить описание проекта') # Обновить описание проекта
async def update_project_description():

@router.delete('/projects/{project_id}', tags=['Проекты'], \
               summary='Удалить проект') # Удалить проект
async def delete_project():

@router.delete('/projects/{project_id}/members/{user_id}', tags=['Проекты'], \
               summary='Удалить участника из проекта') # Удалить участника из проекта
async def delete_project_user():

@router.post('/projects/{project_id}/members', tags=['Проекты'], \
             summary='Добавить участника в проект') # Добавление участника в проект (только админ)