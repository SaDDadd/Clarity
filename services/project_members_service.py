from core.exceptions import (AppException, NotFoundException,
                             PermissionDeniedException)
from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.common import ProjectRole
from cache.cache_keys import project_key, user_projects_key
from cache.cache_service import delete_cache


async def update_member_role(db: AsyncSession, user_id: int, project_id: int, 
                             current_user_id: int, role_project) -> dict:
    """Обновление роли участника. Владельца менять нельзя."""
    if isinstance(role_project, ProjectRole):
        role_project = role_project.value
    repo = ProjectRepository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден')
    if not await repo.is_user_in_project(project_id, user_id):
        raise PermissionDeniedException('Пользователь не состоит в проекте')
    if not await repo.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('Текущий пользователь не администратор проекта')
    if current_user_id == user_id:
        raise PermissionDeniedException('Нельзя изменить свою собственную роль')
    current_role = await repo.get_user_role_in_project(project_id, user_id)
    if current_role == 'owner':
        raise PermissionDeniedException('Нельзя изменить роль владельца проекта')
    if role_project == 'owner':
        raise PermissionDeniedException('Передача владения выполняется отдельным сценарием')
    if current_role == role_project:
        return {'message': 'Роль уже установлена'}
    updated = await repo.update_user_role(project_id, user_id, role_project)
    if not updated:
        raise AppException(500, 'Не удалось обновить роль')
    await delete_cache(project_key(project_id))
    await delete_cache(user_projects_key(user_id, 'all'))
    await delete_cache(user_projects_key(user_id, 'admin'))
    return {'message': 'Роль обновлена'}