from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import current_user, get_db
from models.user import UserModel
from schemas.common import ProjectRole
from schemas.project import AddMemberRequest, ProjectCreate, ProjectUpdate, UserProjectResponse
from services.project_members_service import update_member_role
from services.project_service import (add_user, create_project, delete_project,
                                      delete_project_user, get_admin_projects,
                                      get_project_info, get_user_projects, update_project, 
                                      leave_from_project)
from cache.cache_keys import user_projects_key, TTL_PROJECT_LIST
from cache.cache_service import get_cache, set_cache

router = APIRouter()


@router.post('/projects', tags=['Проекты'],
             summary='Создание проекта', status_code=201)
async def create_project_endpoint(project: ProjectCreate,
                                  user: UserModel = Depends(current_user),
                                  db: AsyncSession = Depends(get_db)):
    """Создание проекта."""
    return await create_project(db, project, user.user_id)


@router.post('/projects/{project_id}/members', tags=['Проекты'],
             summary='Добавить участника в проект')
async def add_member_endpoint(project_id: int, request: AddMemberRequest,
                              current_user: UserModel = Depends(current_user),
                              db: AsyncSession = Depends(get_db)):
    """Добавление пользователя в проект."""
    return await add_user(db, project_id, current_user.user_id, request.user_id)


@router.patch('/projects/{project_id}/members/{user_id}/role', tags=['Проекты'],
              summary='Изменение роли участника')
async def update_member_role_endpoint(project_id: int, user_id: int, role: ProjectRole,
                                      current_user: UserModel = Depends(current_user),
                                      db: AsyncSession = Depends(get_db)):
    """Обновление роли пользователя в проекте."""
    return await update_member_role(db, user_id, project_id, current_user.user_id, role.value)


@router.get('/projects/all', tags=['Проекты'], summary='Проекты, где пользователь участвует (owner/admin/member)')
async def get_member_projects_endpoint(current_user: UserModel = Depends(current_user),
                                       db: AsyncSession = Depends(get_db)):
    """Получить всех участников проекта."""
    key = user_projects_key(current_user.user_id)
    cached = await get_cache(key)
    if cached is not None:
        return cached
    projects = await get_user_projects(db, current_user.user_id)
    data = [UserProjectResponse.model_validate(project).model_dump(mode='json') for project in projects]
    await set_cache(key, data, TTL_PROJECT_LIST)
    return data


@router.get('/projects', tags=['Проекты'], summary='Проекты пользователя, где он admin.')
async def get_projects_admin_endpoint(user: UserModel = Depends(current_user),
                                      db: AsyncSession = Depends(get_db)):
    """Получить проекты пользователя, где он admin."""
    key = user_projects_key(user.user_id, 'admin')
    cached = await get_cache(key)
    if cached is not None:
        return cached
    projects = await get_admin_projects(db, user.user_id)
    data = [UserProjectResponse.model_validate(project).model_dump(mode='json') for project in projects]
    await set_cache(key, data, TTL_PROJECT_LIST)
    return data


@router.get('/projects/{project_id}', tags=['Проекты'], summary='Получить информацию о проекте')
async def get_project_info_endpoint(project_id: int,
                                    user: UserModel = Depends(current_user),
                                    db: AsyncSession = Depends(get_db)):
    """Получить всю информацию про проект."""
    return await get_project_info(db, project_id, user.user_id)


@router.put('/projects/{project_id}', tags=['Проекты'], summary='Обновить проект')
async def update_project_description_endpoint(project_id: int, project: ProjectUpdate,
                                              user: UserModel = Depends(current_user),
                                              db: AsyncSession = Depends(get_db)):
    """Обновление проекта."""
    return await update_project(db, project_id, user.user_id, project)


@router.delete('/projects/{project_id}', tags=['Проекты'], summary='Удалить проект')
async def delete_project_endpoint(project_id: int,
                                  user: UserModel = Depends(current_user),
                                  db: AsyncSession = Depends(get_db)):
    """Удаление проекта."""
    return await delete_project(db, project_id, user.user_id)


@router.delete('/projects/{project_id}/members/{user_id}', tags=['Проекты'], summary='Удалить участника из проекта')
async def delete_project_member_endpoint(project_id: int, user_id: int,
                                         current_user: UserModel = Depends(current_user),
                                         db: AsyncSession = Depends(get_db)):
    """Удалить участника проекта."""
    return await delete_project_user(db, project_id, current_user.user_id, user_id)

@router.delete('/projects/{project_id}/leave', tags=['Проекты'], 
               summary='Выйти из проекта')
async def leave_from_project_endpoint(project_id: int, 
                                      user: UserModel = Depends(current_user), 
                                      db: AsyncSession = Depends(get_db)):
    """Выход из проекта."""
    return await leave_from_project(db, project_id, user.user_id)