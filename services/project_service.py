from core.exceptions import (AppException, ConflictException,
                             InvalidInvitationStateException,
                             NotFoundException, PermissionDeniedException, 
                             LackOfInformationException)
from models.project import ProjectModel
from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository
from repositories.project_invitation_repository import ProjectInvitationRepository
from schemas.project import ProjectCreate, ProjectMemberCheck, ProjectUpdate, UserProjectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from cache.cache_keys import (project_key, user_tasks_key, user_projects_key, project_tasks_key,
                              project_invitations_key, user_invitations_key, TTL_PROJECT, PROJECT_PREFIX,
                              project_comments_pattern)
from cache.cache_service import (get_cache, set_cache, delete_cache,
                                 delete_cache_by_pattern)


async def create_project(db: AsyncSession, project_data: ProjectCreate, admin_id: int) -> dict:
    """Создание проекта."""
    repo = ProjectRepository(db)
    try:
        result = await repo.create_project_with_admin(
            project_data.project_name, 
            project_data.project_description, admin_id
        )
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось создать проект!')
    await delete_cache(user_projects_key(admin_id, 'all'))
    await delete_cache(user_projects_key(admin_id, 'admin'))
    return {
        'project_id': result.project_id,
        'project_name': result.project_name,
        'project_description': result.project_description,
        'admin_id': result.admin_id,
    }


async def add_user(db: AsyncSession, project_id: int, current_user_id: int, user_id_to_add: int) -> dict:
    """Добавить пользователя в проект."""
    repo = ProjectRepository(db)
    repo_user = UserRepository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await repo.is_user_admin_or_curator(project_id, current_user_id):
        raise PermissionDeniedException('Нельзя добавить пользователя: вы не админ и не куратор проекта!')
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
    """Проекты, где пользователь admin."""
    repo = ProjectRepository(db)
    projects = await repo.get_projects_by_creator(admin_id)
    result: list[UserProjectResponse] = []
    for project in projects:
        role = await repo.get_user_role_in_project(project.project_id, admin_id)
        result.append(UserProjectResponse(
            project_id=project.project_id,
            project_name=project.project_name,
            project_description=project.project_description or '',
            admin_id=project.admin_id,
            role=role
        ))
    return result


async def checking_rights_project(db: AsyncSession, project_data: ProjectMemberCheck) -> str:
    """Проверка прав проекта."""
    repo = ProjectRepository(db)
    result = await repo.get_user_role_in_project(project_data.project_id, project_data.user_id)
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
    user_role = await repo.get_user_role_in_project(project_id, user_id)
    key = project_key(project_id)
    cached = await get_cache(key)
    if cached is not None:
        cached['role'] = user_role
        return cached
    project_info = await repo.get_project_all_info(project_id)
    info = project_info['project']
    members = project_info['members']
    answer = {
        'project_id': info.project_id,
        'project_name': info.project_name,
        'project_description': info.project_description,
        'admin_id': info.admin_id,
        'members': [
            {
                'user_id': m.user_id,
                'role': m.role_project,
                'joined_date': m.joined_date.isoformat() if m.joined_date else None
            }
            for m in members
        ]
    }
    await set_cache(key, answer, TTL_PROJECT)   
    answer['role'] = user_role                  
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
            admin_id=project.admin_id,
            role=role
        ))
    return result


async def update_project(db: AsyncSession, project_id: int, 
                         user_id: int, project_data: ProjectUpdate) -> dict:
    """Обновление проекта."""
    repo = ProjectRepository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await repo.is_user_admin_or_curator(project_id, user_id):
        raise PermissionDeniedException('Пользователь не может менять проект, он не админ/куратор!')
    update_data = project_data.model_dump(exclude_unset=True)
    if 'project_name' in update_data and update_data['project_name'] is None:
        raise LackOfInformationException('Название проекта не может быть null!')
    changes: dict = {}
    if 'project_name' in update_data and update_data['project_name'] != project.project_name:
        changes['project_name'] = update_data['project_name']
    if 'project_description' in update_data and update_data['project_description'] != project.project_description:
        changes['project_description'] = update_data['project_description']
    if not changes:
        return {'message': 'Ничего не изменилось!'}
    project_info = await repo.get_project_all_info(project_id)
    member_ids = [i.user_id for i in project_info['members']]
    try:
        if 'project_name' in changes:
            await repo.update_project_name(changes['project_name'], project_id)
        if 'project_description' in changes:
            await repo.update_project_description(changes['project_description'], project_id)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось обновить проект!')
    await delete_cache(project_key(project_id))
    for i in member_ids:
        await delete_cache(user_projects_key(i, 'all'))
        await delete_cache(user_projects_key(i, 'admin'))
    return {'message': 'Проект обновлен!'}


async def delete_project(db: AsyncSession, project_id: int, user_id: int) -> dict:
    """Удаление проекта."""
    repo = ProjectRepository(db)
    repo_inv = ProjectInvitationRepository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await repo.is_user_admin(project_id, user_id):
        raise PermissionDeniedException('Вы не админ этого проекта!')
    project_info = await repo.get_project_all_info(project_id)
    member_ids = [i.user_id for i in project_info['members']]
    pending_invitations = await repo_inv.get_invitation_for_project(project_id)
    invitee_ids = list({inv.invitee_id for inv in pending_invitations})
    try:
        await repo.delete_project(project_id)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось удалить проект!')
    await delete_cache(project_key(project_id))
    await delete_cache(project_tasks_key(project_id))
    await delete_cache(project_invitations_key(project_id, 'admin'))
    await delete_cache_by_pattern(project_comments_pattern(project_id))
    await delete_cache_by_pattern(f"{PROJECT_PREFIX}:{project_id}:task*")
    for i in member_ids:
        await delete_cache(user_projects_key(i, 'all'))
        await delete_cache(user_projects_key(i, 'admin'))
        await delete_cache(user_tasks_key(i, 'all'))
    for iid in invitee_ids:
        await delete_cache(user_invitations_key(iid, 'all'))
    return {'message': 'Проект успешно удален!'}


async def delete_project_user(db: AsyncSession, project_id: int, current_user_id: int, user_id_to_del: int) -> dict:
    """Удаляет участника из проекта."""
    repo = ProjectRepository(db)
    repo_user = UserRepository(db)
    if await repo.get_project_by_id(project_id) is None:
        raise NotFoundException('Проект не найден!')
    if not await repo_user.check_user_exists(user_id_to_del):
        raise NotFoundException('Нельзя удалить пользователя: его не существует!')
    if not await repo.is_user_admin_or_curator(project_id, current_user_id):
        raise PermissionDeniedException('Нельзя удалить пользователя: вы не админ/куратор проекта!')
    if not await repo.is_user_in_project(project_id, user_id_to_del):
        raise ConflictException('Пользователь не состоит в проекте!')
    if current_user_id == user_id_to_del:
        raise PermissionDeniedException('Нельзя удалить самого себя!')
    if await repo.is_user_admin(project_id, user_id_to_del):
        raise PermissionDeniedException('Нельзя удалить создателя проекта. Сначала передайте роль!')
    try:
        await repo.unassign_user_tasks_in_project(project_id, user_id_to_del)
        await repo.delete_user_from_project(project_id, user_id_to_del)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось удалить участника из проекта!')
    await delete_cache(project_key(project_id))
    await delete_cache(project_tasks_key(project_id))
    await delete_cache(project_invitations_key(project_id, 'admin'))
    await delete_cache(user_projects_key(user_id_to_del, 'all'))
    await delete_cache(user_projects_key(user_id_to_del, 'admin'))
    await delete_cache(user_projects_key(current_user_id, 'admin'))
    await delete_cache(user_tasks_key(user_id_to_del, 'all'))
    await delete_cache_by_pattern(f"{PROJECT_PREFIX}:{project_id}:task*")
    return {'message': 'Пользователь удален из проекта!'}


async def leave_from_project(db: AsyncSession, project_id: int, current_user_id: int) -> dict:
    """Выйти из проекта."""
    repo = ProjectRepository(db)
    repo_inv = ProjectInvitationRepository(db)
    if await repo.get_project_by_id(project_id) is None:
        raise NotFoundException('Проект не найден!')
    if not await repo.is_user_in_project(project_id, current_user_id):
        raise ConflictException('Пользователь не состоит в проекте!')
    project_info = await repo.get_project_all_info(project_id)
    member_ids = [i.user_id for i in project_info['members']]
    is_admin = await repo.is_user_admin(project_id, current_user_id)
    new_admin_id = None
    invitee_ids: list[int] = []
    try:
        if is_admin:
            """"""
            new_admin_id = await repo.automatically_assign_admin(project_id, current_user_id)
            if new_admin_id is None:
                pending = await repo_inv.get_invitation_for_project(project_id)
                invitee_ids = list({inv.invitee_id for inv in pending})
                await repo.delete_project(project_id)
            else:
                await repo.unassign_user_tasks_in_project(project_id, current_user_id)
                await repo.delete_user_from_project(project_id, current_user_id)
        else:
            """"""
            await repo.unassign_user_tasks_in_project(project_id, current_user_id)
            await repo.delete_user_from_project(project_id, current_user_id)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось выйти из проекта!')
    await delete_cache(project_key(project_id))
    await delete_cache(project_tasks_key(project_id))
    await delete_cache(project_invitations_key(project_id, 'admin'))
    await delete_cache_by_pattern(f"{PROJECT_PREFIX}:{project_id}:task*")
    await delete_cache(user_projects_key(current_user_id, 'all'))
    await delete_cache(user_projects_key(current_user_id, 'admin'))
    await delete_cache(user_tasks_key(current_user_id, 'all'))
    for member_id in member_ids:
        if member_id == current_user_id:
            continue
        await delete_cache(user_projects_key(member_id, 'all'))
        await delete_cache(user_projects_key(member_id, 'admin'))
        if is_admin and new_admin_id is None:
            await delete_cache(user_tasks_key(member_id, 'all'))
    for iid in invitee_ids:
        await delete_cache(user_invitations_key(iid, 'all'))
    return {'message': 'Вы вышли из проекта!'}