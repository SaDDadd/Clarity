from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository
from models.project_members import ProjectMemberModel
from core.exceptions import NotFoundException, PermissionDeniedException, AppException

async def update_member_role(db, user_id: int, project_id: int, current_user_id: int, role_project: str):
    repo = ProjectRepository(db)
    repo_user = UserRepository(db)
    if await repo.get_project_by_id(project_id) is None:
        raise NotFoundException('Проект не найден')
    if await repo_user.get_by_id(user_id) is None:
        raise NotFoundException('Пользователь не найден')
    if not await repo.is_user_in_project(project_id, user_id):
        raise PermissionDeniedException('Пользователь не состоит в проекте')
    if not await repo.is_user_admin(project_id, user_id):
        raise PermissionDeniedException('Пользователь не является администратором')
    if not await repo.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('Текущий пользователь не администратор проекта')
    if await repo.delete_project_member(project_id, user_id):
        if await repo.update_user_role(project_id, user_id, role_project):
            return {'message': ''}
        else:
            raise AppException(500, 'Не удалось обновить роль')
    else:
        raise AppException(500, 'Не удалось обновить роль')