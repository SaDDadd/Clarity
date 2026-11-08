from fastapi import APIRouter, Depends

from core.dependencies import current_user, get_uow
from core.uow import UnitOfWork
from models.user import UserModel
from schemas.common import ProjectRole
from schemas.project import AddMemberRequest, ProjectCreate, ProjectUpdate, TransferAdminRequest
from services.project_members_service import update_member_role, transfer_admin
from services.project_service import (add_user, create_project, delete_project,
                                      delete_project_user, get_admin_projects,
                                      get_project_info, get_user_projects, update_project,
                                      leave_from_project)


router = APIRouter()


@router.post('/projects', tags=['Проекты'],
             summary='Создание проекта', status_code=201)
async def create_project_endpoint(project: ProjectCreate,
                                  user: UserModel = Depends(current_user),
                                  uow: UnitOfWork = Depends(get_uow)):
    """Создание проекта."""
    return await create_project(uow, project, user.user_id)


@router.post('/projects/{project_id}/members', tags=['Проекты'],
             summary='Добавить участника в проект')
async def add_member_endpoint(project_id: int, request: AddMemberRequest,
                              current_user: UserModel = Depends(current_user),
                              uow: UnitOfWork = Depends(get_uow)):
    """Добавление пользователя в проект."""
    return await add_user(uow, project_id, current_user.user_id, request.user_id)


@router.patch('/projects/{project_id}/members/{user_id}/role', tags=['Проекты'],
              summary='Изменение роли участника')
async def update_member_role_endpoint(project_id: int, user_id: int, role: ProjectRole,
                                      current_user: UserModel = Depends(current_user),
                                      uow: UnitOfWork = Depends(get_uow)):
    """Обновление роли пользователя в проекте."""
    return await update_member_role(uow, user_id, project_id, current_user.user_id, role.value)


@router.get('/projects/all', tags=['Проекты'], summary='Проекты, где пользователь участвует (owner/admin/member)')
async def get_member_projects_endpoint(current_user: UserModel = Depends(current_user),
                                       uow: UnitOfWork = Depends(get_uow)):
    """Получить проекты пользователя, где он участвует."""
    # добавить фильтраию и пагинацию
    return await get_user_projects(uow, current_user.user_id)


@router.get('/projects', tags=['Проекты'], summary='Проекты пользователя, где он admin.')
async def get_projects_admin_endpoint(user: UserModel = Depends(current_user),
                                      uow: UnitOfWork = Depends(get_uow)):
    """Получить проекты пользователя, где он admin."""
    # добавить фильтраию и пагинацию
    return await get_admin_projects(uow, user.user_id)


@router.get('/projects/{project_id}', tags=['Проекты'], summary='Получить информацию о проекте')
async def get_project_info_endpoint(project_id: int,
                                    user: UserModel = Depends(current_user),
                                    uow: UnitOfWork = Depends(get_uow)):
    """Получить всю информацию про проект."""
    return await get_project_info(uow, project_id, user.user_id)


@router.put('/projects/{project_id}', tags=['Проекты'], summary='Обновить проект')
async def update_project_description_endpoint(project_id: int, project: ProjectUpdate,
                                              user: UserModel = Depends(current_user),
                                              uow: UnitOfWork = Depends(get_uow)):
    """Обновление проекта."""
    return await update_project(uow, project_id, user.user_id, project)


@router.delete('/projects/{project_id}', tags=['Проекты'], summary='Удалить проект')
async def delete_project_endpoint(project_id: int,
                                  user: UserModel = Depends(current_user),
                                  uow: UnitOfWork = Depends(get_uow)):
    """Удаление проекта."""
    return await delete_project(uow, project_id, user.user_id)


@router.delete('/projects/{project_id}/members/{user_id}', tags=['Проекты'], summary='Удалить участника из проекта')
async def delete_project_member_endpoint(project_id: int, user_id: int,
                                         current_user: UserModel = Depends(current_user),
                                         uow: UnitOfWork = Depends(get_uow)):
    """Удалить участника проекта."""
    return await delete_project_user(uow, project_id, current_user.user_id, user_id)


@router.delete('/projects/{project_id}/leave', tags=['Проекты'],
               summary='Выйти из проекта')
async def leave_from_project_endpoint(project_id: int,
                                      user: UserModel = Depends(current_user),
                                      uow: UnitOfWork = Depends(get_uow)):
    """Выход из проекта."""
    return await leave_from_project(uow, project_id, user.user_id)


@router.patch('/projects/{project_id}/admin', tags=['Проекты'],
              summary='Передать роль администратора')
async def transfer_admin_endpoint(project_id: int, 
                                  data: TransferAdminRequest, 
                                  current_user: UserModel = Depends(current_user),
                                  uow: UnitOfWork = Depends(get_uow)):
    """Админ выбирает нового админа."""
    return await transfer_admin(uow, project_id, current_user.user_id, data.new_admin_id)