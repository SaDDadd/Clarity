from core.exceptions import NotFoundException, PermissionDeniedException, LackOfInformationException
from core.uow import UnitOfWork
from cache.cache_keys import project_key, user_projects_pattern
from cache.cache_service import delete_cache, delete_cache_by_pattern


async def update_member_role(uow: UnitOfWork, user_id: int, project_id: int, 
                             current_user_id: int, role_project: str) -> dict:
    """Обновление роли участника."""
    project = await uow.project.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await uow.project.is_user_in_project(project_id, user_id):
        raise NotFoundException('Пользователь не состоит в проекте!')
    if not await uow.project.is_user_admin_or_curator(project_id, current_user_id):
        raise PermissionDeniedException('Только администратор или куратор может менять роли!')
    if role_project == 'admin':
        raise LackOfInformationException('Нельзя изменить передать роль админа!')
    if current_user_id == user_id:
        raise PermissionDeniedException('Нельзя изменить свою роль!')
    current_role = await uow.project.get_user_role_in_project(project_id, user_id)
    if current_role == 'admin':
        raise PermissionDeniedException('Нельзя изменить роль администратора. Передайте роль другому участнику!')
    if current_role == role_project:
        return {'message': 'Роль уже установлена!'}
    if role_project not in ('curator', 'member'):
        raise LackOfInformationException('Недопустимая роль!')
    await uow.project.update_user_role(project_id, user_id, role_project)
    await delete_cache(project_key(project_id))
    project_info = await uow.project.get_project_all_info(project_id)
    for member in project_info['members']:
        """Инвалидируем кэш проектов для каждого участника."""
        await delete_cache_by_pattern(user_projects_pattern(member.user_id))
    return {'message': 'Роль обновлена!'}


async def transfer_admin(uow: UnitOfWork, project_id: int, current_user_id: int, 
                         new_admin_id: int) -> dict:
    """Передача админа: старый админ становится куратором."""
    project = await uow.project.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await uow.project.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('Только администратор может передать роль администратора!')
    if current_user_id == new_admin_id:
        raise LackOfInformationException('Вы уже администратор проекта!')
    if not await uow.project.is_user_in_project(project_id, new_admin_id):
        raise NotFoundException('Новый администратор не состоит в проекте!')
    await uow.project.reassign_admin(project_id, new_admin_id)
    await delete_cache(project_key(project_id))
    project_info = await uow.project.get_project_all_info(project_id)
    for member in project_info['members']:
        """Инвалидируем кэш проектов для каждого участника."""
        await delete_cache_by_pattern(user_projects_pattern(member.user_id))
    return {'message': 'Роль администратора передана! Старый администратор стал куратором.'}