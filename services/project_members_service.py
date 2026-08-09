from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository
from models.project_members import ProjectMemberModel

async def update_member_role(db, user_id: int, project_id: int, current_user_id: int, role_project: str):
    repo = ProjectRepository(db)
    repo_user = UserRepository(db)
    if await repo.get_project_by_id(project_id) is None:
        raise
    if await repo_user.get_by_id(user_id) is None:
        raise
    if not await repo.is_user_in_project(project_id, user_id):
        raise
    if not await repo.is_user_admin(project_id, user_id):
        raise
    if not await repo.is_user_admin(project_id, current_user_id):
        raise
    if await repo.delete_project_member(project_id, user_id):
        if await repo.add_user_role(project_id, user_id, role_project):
            return {'message': ''}
        else:
            raise
    else:
        raise