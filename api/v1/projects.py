from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db, current_user
from models.user import UserModel
from schemas.project import UserProjectResponse
from schemas.project import AddMemberRequest, DeleteMemberRequest, ProjectCreate, ProjectUpdate
from services.project_service import add_user, create_project, delete_project, delete_project_user,\
    get_admin_projects, get_project_info, get_user_projects, update_project
from services.project_members_service import update_member_role
from schemas.common import ProjectRole 
router = APIRouter()

# POST
@router.post('/projects', tags=['Проекты'], \
             summary='Создание проекта', status_code=201) # Создание проекта
async def create_project_endpoint(project: ProjectCreate, user: UserModel = Depends(current_user),\
                                    db: AsyncSession = Depends(get_db)):
    return await create_project(db, project, user.user_id)

@router.post('/projects/{project_id}/members', tags=['Проекты'], \
             summary='Добавить участника в проект', status_code=201) # Добавление участника в проект (только админ)
async def add_member(project_id: int, request: AddMemberRequest, current_user: UserModel = Depends(current_user),\
                        db: AsyncSession = Depends(get_db)):
    return await add_user(db, project_id, current_user.user_id, request.user_id)

# PATCH
@router.patch('/projects/{project_id}/members/{user_id}/role', tags=['Проекты'],\
              summary='Изменение роли участника')
async def update_member_role_endpoint(project_id: int, user_id: int, role: ProjectRole, current_user: UserModel = Depends(current_user),\
                             db: AsyncSession = Depends(get_db)):
    return await update_member_role(db, user_id, project_id, current_user.user_id, role)

# GET
@router.get('/projects', tags=['Проекты'], \
            summary='Вывод проектов пользователя, где он админ') # Получение проектов админа
async def get_projects_admin(user: UserModel = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return await get_admin_projects(db, user.user_id)

@router.get('/projects/{projects_id}', tags=['Проекты'], \
            summary='Получить информацию о проекте') # Получить информацию о проекте 
async def get_project_info_endpoint(projects_id: int, user: UserModel = Depends(current_user),\
                                        db: AsyncSession = Depends(get_db)):
    return await get_project_info(db, projects_id, user.user_id)

@router.get('/projects/all', response_model=list[UserProjectResponse], tags=['Проекты'], summary='Вывод проектов, где пользователь участвует(как админ и участник)')
async def get_member_projects(current_user: UserModel = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return await get_user_projects(db, current_user.user_id)

# PUT
@router.put('/projects/{projects_id}', tags=['Проекты'], \
            summary='Обновить описание проекта') # Обновить описание проекта
async def update_project_description(projects_id: int, project: ProjectUpdate, user: UserModel = Depends(current_user),\
                                        db: AsyncSession = Depends(get_db)):
    return await update_project(db, projects_id, user.user_id, project)

# DELETE
@router.delete('/projects/{project_id}', tags=['Проекты'], \
               summary='Удалить проект') # Удалить проект
async def delete_project_endpoint(project_id: int, user: UserModel = Depends(current_user),\
                                    db: AsyncSession = Depends(get_db) ):
    return await delete_project(db, project_id, user.user_id)

@router.delete('/projects/{project_id}/members/{user_id}', tags=['Проекты'], summary='Удалить участника из проекта')
async def delete_project_member(project_id: int, user_id: int,
                                current_user: UserModel = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return await delete_project_user(db, project_id, current_user.user_id, user_id)