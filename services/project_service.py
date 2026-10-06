from core.exceptions import (AppException, ConflictException,
                             InvalidInvitationStateException,
                             LastAdminDeletionException, NotFoundException,
                             PermissionDeniedException)
from models.project import ProjectModel
from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository
from schemas.project import ProjectCreate, ProjectMemberCheck, ProjectUpdate, UserProjectResponse, ProjectResponse
from sqlalchemy.ext.asyncio import AsyncSession 
from cache.cache_keys import project_key, user_projects_key, TTL_PROJECT
from cache.cache_service import get_cache, set_cache, delete_cache


async def create_project(db: AsyncSession, project_data: ProjectCreate, admin_id: int) -> ProjectModel:
    """Создаёт новый проект и добавляет администратора."""
    repo = ProjectRepository(db)
    result = await repo.create_project_with_admin(
        project_data.project_name,
        project_data.project_description,
        admin_id
    )
    await delete_cache(user_projects_key(admin_id, 'all'))
    await delete_cache(user_projects_key(admin_id, 'admin'))
    return result


async def add_user(db: AsyncSession, project_id: int, current_user_id: int, user_id_to_add: int) -> dict:
    """Добавляет пользователя в проект (только администратор)."""
    repo = ProjectRepository(db)
    repo_user = UserRepository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await repo.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('Нельзя добавить пользователя: вы не админ проекта!')
    if current_user_id == user_id_to_add:
        raise InvalidInvitationStateException('Нельзя добавить самого себя!')
    if not await repo_user.check_user_exists(user_id_to_add):
        raise NotFoundException('Нельзя добавить пользователя: его не существует!')
    if await repo.is_user_in_project(project_id, user_id_to_add):
        raise ConflictException('Пользователь уже состоит в проекте')
    if await repo.add_user(project_id, user_id_to_add):
        project_info = await repo.get_project_all_info(project_id)
        member_ids = [i.user_id for i in project_info['members']]
        await delete_cache(project_key(project_id))
        for i in member_ids:
            await delete_cache(user_projects_key(i, 'all'))
            await delete_cache(user_projects_key(i, 'admin'))
        return {'message': 'Пользователь добавлен в проект!'}
    raise AppException(500, 'Неизвестная ошибка при добавлении пользователя в проект!')


async def get_admin_projects(db: AsyncSession, admin_id: int) -> list[ProjectModel]:
    """Возвращает проекты, где пользователь является администратором."""
    repo = ProjectRepository(db)
    numb_projects = await repo.get_projects_by_admin(admin_id)
    if not numb_projects:
        return []
    else:
        return numb_projects


async def checking_rights_project(db: AsyncSession, project_date: ProjectMemberCheck) -> str:
    """Проверяет права пользователя в проекте (возвращает роль)."""
    repo = ProjectRepository(db)
    result = await repo.get_user_role_in_project(project_date.project_id, project_date.user_id)
    if result is None:
        raise PermissionDeniedException('Пользователь не состоит в проекте!')
    else:
        return result


async def get_project_info(db: AsyncSession, project_id: int, user_id: int) -> dict:
    """Возвращает полную информацию о проекте."""
    repo = ProjectRepository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await repo.is_user_in_project(project_id, user_id):
        raise PermissionDeniedException('Пользователь не является участником проекта!')
    key = project_key(project_id)
    cached = await get_cache(key)
    if cached is not None:
        return cached
    project_info = await repo.get_project_all_info(project_id)
    info = project_info['project']
    members = project_info['members']
    answer = {'project_id':info.project_id, 
              'project_name':info.project_name, 
              'project_description':info.project_description,
              'admin_id':info.admin_id, 
              'members': [
                {
                    'user_id': member.user_id,
                    'role': member.role_project,
                    'joined_date': member.joined_date.isoformat() if member.joined_date else None,
                }
                for member in members
                ],
            }
    await set_cache(key, answer, TTL_PROJECT)
    return answer


async def get_user_projects(db: AsyncSession, current_user_id: int) -> list[UserProjectResponse]:
    """Возвращает все проекты, в которых участвует пользователь."""
    repo = ProjectRepository(db)
    projects = await repo.get_user_projects(current_user_id)
    result = []
    for project in projects:
        role = await repo.get_user_role_in_project(project.project_id, current_user_id)
        if role is None:
            role = 'member'
        result.append(UserProjectResponse(
            project_id=project.project_id,
            project_name=project.project_name,
            project_description=project.project_description or '',
            role=role
        ))
    return result


async def update_project(db: AsyncSession, project_id: int, user_id: int, project_date: ProjectUpdate) -> dict:
    """Обновляет название и/или описание проекта (только администратор)."""
    repo = ProjectRepository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await repo.is_user_in_project(project_id, user_id):
        raise PermissionDeniedException('Пользователь не является участником проекта!')
    if await repo.get_user_role_in_project(project_id, user_id) != 'admin':
        raise PermissionDeniedException('Пользователь не может менять проект, он не админ!')
    if project_date.project_description is None and project_date.project_name is None:
        return {'message': 'Ничего не изменилось!'}
    project_info = repo.get_project_all_info(project_id)
    member_ids = [i.user_id for i in project_info['members']]
    if project_date.project_description is None:
        await repo.update_project_name(project_date.project_name, project_id)
    elif project_date.project_name is None:
        await repo.update_project_description(project_date.project_description, project_id)
    else:
        await repo.update_project_description(project_date.project_description, project_id)
        await repo.update_project_name(project_date.project_name, project_id)
    await delete_cache(project_key(project_id))
    for i in member_ids:
        await delete_cache(user_projects_key(i, 'all'))
        await delete_cache(user_projects_key(i, 'admin'))
    return {'message': 'Проект обновлен!'}


async def delete_project(db: AsyncSession, project_id: int, user_id: int) -> dict:
    """Удаляет проект (только администратор)."""
    repo = ProjectRepository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await repo.is_user_admin(project_id, user_id):
        raise PermissionDeniedException('Вы не админ этого проекта!')
    project_info = await repo.get_project_all_info(project_id)
    if not await repo.delete_project(project_id):
        raise AppException(500, 'Не удалось удалить проект')
    await delete_cache(project_key(project_id))
    member_ids = [i.user_id for i in project_info['members']]
    for i in member_ids:
        await delete_cache(user_projects_key(i, 'all'))
        await delete_cache(user_projects_key(i, 'admin'))
    return {'message': 'Проект успешно удален!'}


async def delete_project_user(db: AsyncSession, project_id: int, current_user_id: int,
                              user_id_to_del: int) -> dict:
    """Удаляет участника из проекта (только администратор)."""
    repo = ProjectRepository(db)
    repo_user = UserRepository(db)
    if not await repo_user.check_user_exists(user_id_to_del):
        raise NotFoundException('Нельзя удалить пользователя: его не существует!')
    if not await repo.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('Нельзя удалить пользователя: вы не админ проекта!')
    if not await repo.is_user_in_project(project_id, user_id_to_del):
        raise ConflictException('Пользователь не состоит в проекте!')
    if await repo.is_user_admin(project_id, user_id_to_del):
        admins_count = await repo.get_number_admins(project_id)
        if admins_count == 1:
            raise LastAdminDeletionException('Нельзя удалить единственного администратора проекта!')
        project = await repo.get_project_by_id(project_id)
        if project.admin_id == user_id_to_del:
            admins = await repo.get_admins_list(project_id)
            other_admin = next((a for a in admins if a.user_id != user_id_to_del), None)
            if other_admin:
                await repo.reassign_admin(project_id, other_admin.user_id)
            else:
                raise AppException(500, 'Не удалось переназначить администратора')
    deleted = await repo.delete_user(project_id, user_id_to_del)
    if not deleted:
        raise AppException(500, 'Неизвестная ошибка при удалении пользователя из проекта!')
    await delete_cache(project_key(project_id))
    await delete_cache(user_projects_key(current_user_id, 'admin'))
    await delete_cache(user_projects_key(user_id_to_del, 'all'))
    return {'message': 'Пользователь удален из проекта!'}