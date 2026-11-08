from core.exceptions import (ConflictException,
                             InvalidInvitationStateException,
                             NotFoundException, PermissionDeniedException,
                             LackOfInformationException)
from schemas.project import ProjectCreate, ProjectMemberCheck, ProjectUpdate, UserProjectResponse
from core.uow import UnitOfWork
from cache.cache_keys import (project_key, user_projects_key, project_tasks_key,
                              TTL_PROJECT, TTL_PROJECT_LIST, project_all_pattern,
                              user_projects_pattern, user_tasks_pattern,
                              user_invitations_pattern, project_task_items_pattern,
                              project_invitations_pattern)
from cache.cache_service import (get_cache, set_cache, delete_cache,
                                 delete_cache_by_pattern)


async def create_project(uow: UnitOfWork, project_data: ProjectCreate, admin_id: int) -> dict:
    """Создание проекта."""
    result = await uow.project.create_project_with_admin(
        project_data.project_name,
        project_data.project_description, admin_id
    )
    await delete_cache_by_pattern(user_projects_pattern(admin_id))
    return {
        'project_id': result.project_id,
        'project_name': result.project_name,
        'project_description': result.project_description,
        'admin_id': result.admin_id,
    }


async def add_user(uow: UnitOfWork, project_id: int, current_user_id: int, user_id_to_add: int) -> dict:
    """Добавить пользователя в проект."""
    project = await uow.project.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await uow.project.is_user_admin_or_curator(project_id, current_user_id):
        raise PermissionDeniedException('Нельзя добавить пользователя: вы не админ и не куратор проекта!')
    if current_user_id == user_id_to_add:
        raise InvalidInvitationStateException('Нельзя добавить самого себя!')
    if not await uow.user.check_user_exists(user_id_to_add):
        raise NotFoundException('Нельзя добавить пользователя: его не существует!')
    if await uow.project.is_user_in_project(project_id, user_id_to_add):
        raise ConflictException('Пользователь уже состоит в проекте')
    await uow.project.add_user(project_id, user_id_to_add)
    project_info = await uow.project.get_project_all_info(project_id)
    member_ids = [i.user_id for i in project_info['members']]
    await delete_cache(project_key(project_id))
    for i in member_ids:
        await delete_cache_by_pattern(user_projects_pattern(i))
    return {'message': 'Пользователь добавлен в проект!'}


async def get_admin_projects(uow: UnitOfWork, admin_id: int) -> list[UserProjectResponse]:
    """Проекты, где пользователь admin."""
    key = user_projects_key(admin_id, 'admin')
    cached = await get_cache(key)
    if cached is not None:
        return cached
    projects = await uow.project.get_projects_by_creator(admin_id)
    result: list[UserProjectResponse] = []
    for project in projects:
        role = await uow.project.get_user_role_in_project(project.project_id, admin_id)
        result.append(UserProjectResponse(
            project_id=project.project_id,
            project_name=project.project_name,
            project_description=project.project_description or '',
            admin_id=project.admin_id,
            role=role
        ))
    data = [UserProjectResponse.model_validate(project).model_dump(mode='json') for project in result]
    await set_cache(key, data, TTL_PROJECT_LIST)
    return data


async def checking_rights_project(uow: UnitOfWork, project_data: ProjectMemberCheck) -> str:
    """Проверка прав проекта."""
    result = await uow.project.get_user_role_in_project(project_data.project_id, project_data.user_id)
    if result is None:
        raise PermissionDeniedException('Пользователь не состоит в проекте!')
    return result


async def get_project_info(uow: UnitOfWork, project_id: int, user_id: int) -> dict:
    """Получить всю информацию о проекте."""
    project = await uow.project.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await uow.project.is_user_in_project(project_id, user_id):
        raise PermissionDeniedException('Пользователь не является участником проекта!')
    user_role = await uow.project.get_user_role_in_project(project_id, user_id)
    key = project_key(project_id)
    cached = await get_cache(key)
    if cached is not None:
        cached['role'] = user_role
        return cached
    project_info = await uow.project.get_project_all_info(project_id)
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


async def get_user_projects(uow: UnitOfWork, current_user_id: int) -> list[UserProjectResponse]:
    """Получить проекты пользователя."""
    key = user_projects_key(current_user_id, 'all')
    cached = await get_cache(key)
    if cached is not None:
        return cached
    projects = await uow.project.get_user_projects(current_user_id)
    result = []
    for project in projects:
        role = await uow.project.get_user_role_in_project(project.project_id, current_user_id)
        if role is None:
            role = 'member'
        result.append(UserProjectResponse(
            project_id=project.project_id,
            project_name=project.project_name,
            project_description=project.project_description or '',
            admin_id=project.admin_id,
            role=role
        ))
    data = [UserProjectResponse.model_validate(project).model_dump(mode='json') for project in result]
    await set_cache(key, data, TTL_PROJECT_LIST)
    return data


async def update_project(uow: UnitOfWork, project_id: int, user_id: int, project_data: ProjectUpdate) -> dict:
    """Обновление проекта."""
    project = await uow.project.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await uow.project.is_user_admin_or_curator(project_id, user_id):
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
    project_info = await uow.project.get_project_all_info(project_id)
    member_ids = [i.user_id for i in project_info['members']]
    pending_invitations = await uow.invitation.get_invitation_for_project(project_id)
    invitee_ids = {inv.invitee_id for inv in pending_invitations}
    if 'project_name' in changes:
        await uow.project.update_project_name(changes['project_name'], project_id)
    if 'project_description' in changes:
        await uow.project.update_project_description(changes['project_description'], project_id)
    await delete_cache(project_key(project_id))
    await delete_cache_by_pattern(project_invitations_pattern(project_id))
    for invitee_id in invitee_ids:
        await delete_cache_by_pattern(user_invitations_pattern(invitee_id))
    for member_id in member_ids:
        await delete_cache_by_pattern(user_projects_pattern(member_id))
    return {'message': 'Проект обновлен!'}


async def delete_project(uow: UnitOfWork, project_id: int, user_id: int) -> dict:
    """Удаление проекта."""
    project = await uow.project.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await uow.project.is_user_admin(project_id, user_id):
        raise PermissionDeniedException('Вы не админ этого проекта!')
    project_info = await uow.project.get_project_all_info(project_id)
    member_ids = [i.user_id for i in project_info['members']]
    pending_invitations = await uow.invitation.get_invitation_for_project(project_id)
    invitee_ids = list({inv.invitee_id for inv in pending_invitations})
    await uow.project.delete_project(project_id)
    """Автоматический каскад по проекту: детали, tasks, task items, comments, invitations."""
    await delete_cache_by_pattern(project_all_pattern(project_id))
    for i in member_ids:
        await delete_cache_by_pattern(user_projects_pattern(i))
        await delete_cache_by_pattern(user_tasks_pattern(i))
    for iid in invitee_ids:
        await delete_cache_by_pattern(user_invitations_pattern(iid))
    return {'message': 'Проект успешно удален!'}


async def delete_project_user(uow: UnitOfWork, project_id: int, current_user_id: int, user_id_to_del: int) -> dict:
    """Удаляет участника из проекта."""
    if await uow.project.get_project_by_id(project_id) is None:
        raise NotFoundException('Проект не найден!')
    if not await uow.user.check_user_exists(user_id_to_del):
        raise NotFoundException('Нельзя удалить пользователя: его не существует!')
    if not await uow.project.is_user_admin_or_curator(project_id, current_user_id):
        raise PermissionDeniedException('Нельзя удалить пользователя: вы не админ/куратор проекта!')
    if not await uow.project.is_user_in_project(project_id, user_id_to_del):
        raise ConflictException('Пользователь не состоит в проекте!')
    if current_user_id == user_id_to_del:
        raise PermissionDeniedException('Нельзя удалить самого себя!')
    if await uow.project.is_user_admin(project_id, user_id_to_del):
        raise PermissionDeniedException('Нельзя удалить создателя проекта. Сначала передайте роль!')
    await uow.project.unassign_user_tasks_in_project(project_id, user_id_to_del)
    await uow.project.delete_user_from_project(project_id, user_id_to_del)
    await delete_cache(project_key(project_id))
    await delete_cache(project_tasks_key(project_id))
    await delete_cache_by_pattern(project_task_items_pattern(project_id))
    await delete_cache_by_pattern(user_projects_pattern(user_id_to_del))
    await delete_cache_by_pattern(user_tasks_pattern(user_id_to_del))
    return {'message': 'Пользователь удален из проекта!'}


async def leave_from_project(uow: UnitOfWork, project_id: int, current_user_id: int) -> dict:
    """Выйти из проекта."""
    if await uow.project.get_project_by_id(project_id) is None:
        raise NotFoundException('Проект не найден!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise ConflictException('Пользователь не состоит в проекте!')
    project_info = await uow.project.get_project_all_info(project_id)
    member_ids = [i.user_id for i in project_info['members']]
    is_admin = await uow.project.is_user_admin(project_id, current_user_id)
    new_admin_id = None
    invitee_ids: list[int] = []
    if is_admin:
        """Назначаем нового администратора или удаляем проект."""
        new_admin_id = await uow.project.automatically_assign_admin(project_id, current_user_id)
        if new_admin_id is None:
            """Если участников не осталось, удаляем проект."""
            pending = await uow.invitation.get_invitation_for_project(project_id)
            invitee_ids = list({inv.invitee_id for inv in pending})
            await uow.project.delete_project(project_id)
        else:
            """Снимаем задачи и удаляем администратора из проекта."""
            await uow.project.unassign_user_tasks_in_project(project_id, current_user_id)
            await uow.project.delete_user_from_project(project_id, current_user_id)
    else:
        """Снимаем задачи и удаляем участника из проекта."""
        await uow.project.unassign_user_tasks_in_project(project_id, current_user_id)
        await uow.project.delete_user_from_project(project_id, current_user_id)
    if is_admin and new_admin_id is None:
        """Проект удалён — автоматический каскад по всем ключам проекта."""
        await delete_cache_by_pattern(project_all_pattern(project_id))
    else:
        await delete_cache(project_key(project_id))
        await delete_cache(project_tasks_key(project_id))
        await delete_cache_by_pattern(project_task_items_pattern(project_id))
    await delete_cache_by_pattern(user_projects_pattern(current_user_id))
    await delete_cache_by_pattern(user_tasks_pattern(current_user_id))
    for member_id in member_ids:
        if member_id == current_user_id:
            continue
        await delete_cache_by_pattern(user_projects_pattern(member_id))
        if is_admin and new_admin_id is None:
            """Если проект удалён, у участников тоже меняются задачи."""
            await delete_cache_by_pattern(user_tasks_pattern(member_id))
    for iid in invitee_ids:
        await delete_cache_by_pattern(user_invitations_pattern(iid))
    return {'message': 'Вы вышли из проекта!'}