from core.exceptions import (AppException, ConflictException,
                             InvalidInvitationStateException,
                             NotFoundException, PermissionDeniedException)
from models.project import ProjectModel
from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository
from schemas.project import ProjectCreate, ProjectMemberCheck, ProjectUpdate, UserProjectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from cache.cache_keys import (project_key, user_projects_key, project_tasks_key,
                              project_invitations_key, TTL_PROJECT, PROJECT_PREFIX)
from cache.cache_service import (get_cache, set_cache, delete_cache,
                                 delete_cache_by_pattern)


async def create_project(db: AsyncSession, project_data: ProjectCreate, admin_id: int) -> ProjectModel:
    """Создание проекта."""
    repo = ProjectRepository(db)
    try:
        result = await repo.create_project_with_admin(
            project_data.project_name,
            project_data.project_description,
            admin_id
        )
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось создать проект.')
    await delete_cache(user_projects_key(admin_id, 'all'))
    await delete_cache(user_projects_key(admin_id, 'admin'))
    return result


async def add_user(db: AsyncSession, project_id: int, current_user_id: int, user_id_to_add: int) -> dict:
    """Добавить пользователя в проект."""
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
    try:
        await repo.add_user(project_id, user_id_to_add)
        project_info = await repo.get_project_all_info(project_id)
        member_ids = [i.user_id for i in project_info['members']]
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось добавить пользователя в проект.')
    await delete_cache(project_key(project_id))
    for i in member_ids:
        await delete_cache(user_projects_key(i, 'all'))
    return {'message': 'Пользователь добавлен в проект!'}


async def get_admin_projects(db: AsyncSession, admin_id: int) -> list[UserProjectResponse]:
    """Проекты, где пользователь owner или admin."""
    repo = ProjectRepository(db)
    projects = await repo.get_projects_by_admin(admin_id)
    result: list[UserProjectResponse] = []
    try:
        for project in projects:
            role = await repo.get_user_role_in_project(project.project_id, admin_id)
            result.append(UserProjectResponse(
                project_id=project.project_id,
                project_name=project.project_name,
                project_description=project.project_description or '',
                owner_id=project.owner_id,
                role=role
            ))
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось получить проекты.')
    return result


async def checking_rights_project(db: AsyncSession, project_date: ProjectMemberCheck) -> str:
    """Проверка прав проекта."""
    repo = ProjectRepository(db)
    result = await repo.get_user_role_in_project(project_date.project_id, project_date.user_id)
    if result is None:
        raise PermissionDeniedException('Пользователь не состоит в проекте!')
    return result


async def get_project_info(db: AsyncSession, project_id: int, user_id: int) -> dict:
    """Получить всю информацию о проекте."""
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
    answer = {
        'project_id': info.project_id,
        'project_name': info.project_name,
        'project_description': info.project_description,
        'owner_id': info.owner_id,
        'members': [
            {
                'user_id': member.user_id,
                'role': member.role_project,
                'joined_date': member.joined_date.isoformat() if member.joined_date else None
            }
            for member in members
        ]
    }
    await set_cache(key, answer, TTL_PROJECT)
    return answer


async def get_user_projects(db: AsyncSession, current_user_id: int) -> list[UserProjectResponse]:
    """Получить участников проекта."""
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
            owner_id=project.owner_id,
            role=role
        ))
    return result


async def update_project(db: AsyncSession, project_id: int, user_id: int, project_date: ProjectUpdate) -> dict:
    """Обновление проекта."""
    repo = ProjectRepository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await repo.is_user_admin(project_id, user_id):
        raise PermissionDeniedException('Пользователь не может менять проект, он не админ/владелец!')
    if project_date.project_description is None and project_date.project_name is None:
        return {'message': 'Ничего не изменилось!'}
    project_info = await repo.get_project_all_info(project_id)
    member_ids = [i.user_id for i in project_info['members']]
    if project_date.project_description is None:
        try:
            await repo.update_project_name(project_date.project_name, project_id)
            await db.commit()
        except Exception:
            await db.rollback()
            raise AppException(500, 'Не удалось обновить проект.')
    elif project_date.project_name is None:
        try:
            await repo.update_project_description(project_date.project_description, project_id)
            await db.commit()
        except Exception:
            await db.rollback()
            raise AppException(500, 'Не удалось обновить проект.')
    else:
        try:
            await repo.update_project_description(project_date.project_description, project_id)
            await repo.update_project_name(project_date.project_name, project_id)
            await db.commit()
        except Exception:
            await db.rollback()
            raise AppException(500, 'Не удалось обновить проект.')
    await delete_cache(project_key(project_id))
    for i in member_ids:
        await delete_cache(user_projects_key(i, 'all'))
        await delete_cache(user_projects_key(i, 'admin'))
    return {'message': 'Проект обновлен!'}


async def delete_project(db: AsyncSession, project_id: int, user_id: int) -> dict:
    """Удаление проекта."""
    repo = ProjectRepository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await repo.is_user_admin(project_id, user_id):
        raise PermissionDeniedException('Вы не админ этого проекта!')
    project_info = await repo.get_project_all_info(project_id)
    try:
        await repo.delete_project(project_id)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось удалить проект.')
    await delete_cache(project_key(project_id))
    await delete_cache(project_tasks_key(project_id))
    member_ids = [i.user_id for i in project_info['members']]
    await delete_cache(project_invitations_key(project_id, 'admin'))
    for i in member_ids:
        await delete_cache(user_projects_key(i, 'all'))
        await delete_cache(user_projects_key(i, 'admin'))
    await delete_cache_by_pattern(f"{PROJECT_PREFIX}:{project_id}:task*")
    return {'message': 'Проект успешно удален!'}


async def delete_project_user(db: AsyncSession, project_id: int, current_user_id: int, user_id_to_del: int) -> dict:
    """Удаляет участника из проекта."""
    repo = ProjectRepository(db)
    repo_user = UserRepository(db)
    if not await repo_user.check_user_exists(user_id_to_del):
        raise NotFoundException('Нельзя удалить пользователя: его не существует!')
    if not await repo.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('Нельзя удалить пользователя: вы не админ проекта!')
    if not await repo.is_user_in_project(project_id, user_id_to_del):
        raise ConflictException('Пользователь не состоит в проекте!')
    if await repo.is_user_owner(project_id, user_id_to_del):
        raise PermissionDeniedException('Нельзя удалить владельца проекта. Сначала передайте владение.')
    try:
        await repo.unassign_user_tasks_in_project(project_id, user_id_to_del)
        await repo.delete_user_from_project(project_id, user_id_to_del)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось удалить участника из проекта.')
    await delete_cache(project_key(project_id))
    await delete_cache(project_tasks_key(project_id))
    await delete_cache(project_invitations_key(project_id, 'admin'))
    await delete_cache(user_projects_key(user_id_to_del, 'all'))
    await delete_cache(user_projects_key(user_id_to_del, 'admin'))
    await delete_cache(user_projects_key(current_user_id, 'admin'))
    await delete_cache_by_pattern(f"{PROJECT_PREFIX}:{project_id}:task*")
    return {'message': 'Пользователь удален из проекта!'}