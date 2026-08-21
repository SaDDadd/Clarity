from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import current_user, get_db
from models.user import UserModel
from schemas.common import ProjectRole
from schemas.project import AddMemberRequest, ProjectCreate, ProjectUpdate, UserProjectResponse
from services.project_members_service import update_member_role
from services.project_service import (add_user, create_project, delete_project,
                                      delete_project_user, get_admin_projects,
                                      get_project_info, get_user_projects, update_project)

router = APIRouter()


@router.post('/projects', tags=['Проекты'],
             summary='Создание проекта', status_code=201)
async def create_project_endpoint(project: ProjectCreate,
                                  user: UserModel = Depends(current_user),
                                  db: AsyncSession = Depends(get_db)):
    """Создаёт новый проект и назначает текущего пользователя администратором."""
    return await create_project(db, project, user.user_id)


@router.post('/projects/{project_id}/members', tags=['Проекты'],
             summary='Добавить участника в проект', status_code=201)
async def add_member_endpoint(project_id: int, request: AddMemberRequest,
                              current_user: UserModel = Depends(current_user),
                              db: AsyncSession = Depends(get_db)):
    """Добавляет пользователя в проект (только администратор)."""
    return await add_user(db, project_id, current_user.user_id, request.user_id)


@router.patch('/projects/{project_id}/members/{user_id}/role', tags=['Проекты'],
              summary='Изменение роли участника')
async def update_member_role_endpoint(project_id: int, user_id: int, role: ProjectRole,
                                      current_user: UserModel = Depends(current_user),
                                      db: AsyncSession = Depends(get_db)):
    """Изменяет роль участника проекта (только администратор)."""
    return await update_member_role(db, user_id, project_id, current_user.user_id, role)


@router.get('/projects/all', response_model=list[UserProjectResponse], tags=['Проекты'],
            summary='Вывод проектов, где пользователь участвует (как админ и участник)')
async def get_member_projects_endpoint(current_user: UserModel = Depends(current_user),
                                       db: AsyncSession = Depends(get_db)):
    """Возвращает все проекты, в которых состоит текущий пользователь."""
    return await get_user_projects(db, current_user.user_id)


@router.get('/projects', tags=['Проекты'],
            summary='Вывод проектов пользователя, где он админ')
async def get_projects_admin_endpoint(user: UserModel = Depends(current_user),
                                      db: AsyncSession = Depends(get_db)):
    """Возвращает проекты, где пользователь является администратором."""
    return await get_admin_projects(db, user.user_id)


@router.get('/projects/{projects_id}', tags=['Проекты'],
            summary='Получить информацию о проекте')
async def get_project_info_endpoint(projects_id: int,
                                    user: UserModel = Depends(current_user),
                                    db: AsyncSession = Depends(get_db)):
    """Возвращает полную информацию о проекте (включая список участников)."""
    return await get_project_info(db, projects_id, user.user_id)


@router.put('/projects/{projects_id}', tags=['Проекты'],
            summary='Обновить описание проекта')
async def update_project_description_endpoint(projects_id: int, project: ProjectUpdate,
                                              user: UserModel = Depends(current_user),
                                              db: AsyncSession = Depends(get_db)):
    """Обновляет название и/или описание проекта (только администратор)."""
    return await update_project(db, projects_id, user.user_id, project)


@router.delete('/projects/{project_id}', tags=['Проекты'],
               summary='Удалить проект')
async def delete_project_endpoint(project_id: int,
                                  user: UserModel = Depends(current_user),
                                  db: AsyncSession = Depends(get_db)):
    """Удаляет проект (только администратор)."""
    return await delete_project(db, project_id, user.user_id)


@router.delete('/projects/{project_id}/members/{user_id}', tags=['Проекты'],
               summary='Удалить участника из проекта')
async def delete_project_member_endpoint(project_id: int, user_id: int,
                                         current_user: UserModel = Depends(current_user),
                                         db: AsyncSession = Depends(get_db)):
    """Удаляет участника из проекта (только администратор)."""
    return await delete_project_user(db, project_id, current_user.user_id, user_id)