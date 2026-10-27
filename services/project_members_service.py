from core.exceptions import (AppException, NotFoundException,
                             PermissionDeniedException, ConflictException)
from repositories.project_repository import ProjectRepository
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.common import ProjectRole
from cache.cache_keys import project_key, user_projects_key
from cache.cache_service import delete_cache


async def update_member_role(db: AsyncSession, user_id: int, project_id: int, 
                             current_user_id: int, role_project: str) -> dict:
    """Обновление роли участника. Владельца менять нельзя."""
    repo = ProjectRepository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await repo.is_user_in_project(project_id, user_id):
        raise NotFoundException('Пользователь не состоит в проекте!')
    is_admin = await repo.is_user_admin(project_id, current_user_id)
    is_admin_or_curator = await repo.is_user_admin_or_curator(project_id, current_user_id)
    if not is_admin_or_curator:
        raise PermissionDeniedException('Только администратор или куратор может менять роли!')
    current_role = await repo.get_user_role_in_project(project_id, user_id)
    if role_project == 'admin':
        if not is_admin:
            raise PermissionDeniedException('Только действующий администратор может передать роль администратора!')
        if current_user_id == user_id:
            raise PermissionDeniedException('Вы уже администратор проекта!')
        try:
            result = await repo.reassign_admin(project_id, user_id)
            if not result:
                raise AppException(500, 'Не удалось передать роль администратора!')
            await db.commit()
        except Exception:
            await db.rollback()
            raise AppException(500, 'Не удалось передать роль администратора!')
        await delete_cache(project_key(project_id))
        project_info = await repo.get_project_all_info(project_id)
        for mid in (m.user_id for m in project_info['members']):
            await delete_cache(user_projects_key(mid, 'all'))
            await delete_cache(user_projects_key(mid, 'admin'))
        return {'message': 'Роль администратора передана!'}
    if current_user_id == user_id:
        raise PermissionDeniedException('Нельзя изменить свою собственную роль!')
    if current_role == 'admin':
        raise PermissionDeniedException('Нельзя изменить роль администратора. Сначала передайте роль другому участнику!')
    if current_role == role_project:
        return {'message': 'Роль уже установлена!'}
    if role_project not in ('curator', 'member'):
        raise PermissionDeniedException('Недопустимая роль!')
    try:
        await repo.update_user_role(project_id, user_id, role_project)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось обновить роль участника!')
    await delete_cache(project_key(project_id))
    await delete_cache(user_projects_key(user_id, 'all'))
    await delete_cache(user_projects_key(user_id, 'admin'))
    project_info = await repo.get_project_all_info(project_id)
    member_ids = [m.user_id for m in project_info['members']]
    for mid in member_ids:
        await delete_cache(user_projects_key(mid, 'all'))
        await delete_cache(user_projects_key(mid, 'admin'))
    return {'message': 'Роль обновлена'}