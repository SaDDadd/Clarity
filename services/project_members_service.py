from core.exceptions import (AppException, NotFoundException,
                             PermissionDeniedException, LackOfInformationException)
from repositories.project_repository import ProjectRepository
from sqlalchemy.ext.asyncio import AsyncSession
from cache.cache_keys import project_key, user_projects_pattern
from cache.cache_service import delete_cache, delete_cache_by_pattern


async def update_member_role(db: AsyncSession, user_id: int, project_id: int, 
                             current_user_id: int, role_project: str) -> dict:
    """Обновление роли участника."""
    repo = ProjectRepository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await repo.is_user_in_project(project_id, user_id):
        raise NotFoundException('Пользователь не состоит в проекте!')
    if not await repo.is_user_admin_or_curator(project_id, current_user_id):
        raise PermissionDeniedException('Только администратор или куратор может менять роли!')
    if role_project == 'admin':
        raise LackOfInformationException('Нельзя изменить передать роль админа!')
    if current_user_id == user_id:
        raise PermissionDeniedException('Нельзя изменить свою роль!')
    current_role = await repo.get_user_role_in_project(project_id, user_id)
    if current_role == 'admin':
        raise PermissionDeniedException('Нельзя изменить роль администратора. Передайте роль другому участнику!')
    if current_role == role_project:
        return {'message': 'Роль уже установлена!'}
    if role_project not in ('curator', 'member'):
        raise LackOfInformationException('Недопустимая роль!')
    try:
        await repo.update_user_role(project_id, user_id, role_project)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось обновить роль участника!')
    await delete_cache(project_key(project_id))
    project_info = await repo.get_project_all_info(project_id)
    for member in project_info['members']:
        await delete_cache_by_pattern(user_projects_pattern(member.user_id))
    return {'message': 'Роль обновлена!'}


async def transfer_admin(db: AsyncSession, project_id: int, current_user_id: int, 
                         new_admin_id: int) -> dict:
    """Передача админа: старый админ становится куратором."""
    repo = ProjectRepository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await repo.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('Только администратор может передать роль администратора!')
    if current_user_id == new_admin_id:
        raise LackOfInformationException('Вы уже администратор проекта!')
    if not await repo.is_user_in_project(project_id, new_admin_id):
        raise NotFoundException('Новый администратор не состоит в проекте!')
    try:
        result = await repo.reassign_admin(project_id, new_admin_id)
        if not result:
            raise AppException(500, 'Не удалось передать роль администратора!')
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось передать роль администратора!')
    await delete_cache(project_key(project_id))
    project_info = await repo.get_project_all_info(project_id)
    for member in project_info['members']:
        await delete_cache_by_pattern(user_projects_pattern(member.user_id))
    return {'message': 'Роль администратора передана! Старый администратор стал куратором.'}