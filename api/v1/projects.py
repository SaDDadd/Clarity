from fastapi import APIRouter , Depends
from services.project_service import create_project, update_project, get_admin_projects
from schemas.project import ProjectCreate, ProjectUpdate, ProjectsGet
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_db

router = APIRouter()

@router.get('/projects', tags=['Проекты'], \
            summary='Вывод проектов, в которых участвует пользователь') # Получение проектов админа
async def get_projects_admin(project: ProjectsGet, db: AsyncSession = Depends(get_db)):
    return await get_admin_projects(db, project)

@router.post('/projects', tags=['Проекты'], \
             summary='Создание проекта') # Создание проекта
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_db)):
    return await create_project(db, project)

@router.get('/projects/{projects_id}', tags=['Проекты'], \
            summary='Получить информацию о проекте') # Получить информацию о проекте 
async def get_project_info():
    pass

@router.put('/projects/{projects_id}', tags=['Проекты'], \
            summary='Обновить описание проекта') # Обновить описание проекта
async def update_project_description(project: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    return await update_project(db, project)

@router.delete('/projects/{project_id}', tags=['Проекты'], \
               summary='Удалить проект') # Удалить проект
async def delete_project():
    pass

@router.delete('/projects/{project_id}/members/{user_id}', tags=['Проекты'], \
               summary='Удалить участника из проекта') # Удалить участника из проекта
async def delete_project_user():
    pass

@router.post('/projects/{project_id}/members', tags=['Проекты'], \
             summary='Добавить участника в проект') # Добавление участника в проект (только админ)
async def add_user():
    pass