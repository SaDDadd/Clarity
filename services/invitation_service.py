from repositories.project_invitation_repository import ProjectInvitationRepository
from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository
from core.exceptions import NotFoundException, PermissionDeniedException, ConflictException, MemberAlreadyInProjectException, InvalidInvitationStateException

async def send_invitation(db, project_id: int, user_id: int, current_user_id: int, message: str): # Отправка приглашения
    repo = ProjectInvitationRepository(db)
    repo_proj = ProjectRepository(db)
    repo_user = UserRepository(db)
    if not await repo_proj.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('Только администратор может приглашать')
    if not await repo_user.get_by_id(user_id):
        raise NotFoundException('Пользователь не найден')
    if await repo_proj.is_user_in_project(project_id, user_id):
        raise MemberAlreadyInProjectException('')
    if not await repo_proj.get_project_by_id(project_id):
        raise NotFoundException('Проект не найден')
    if await repo.get_pending_invitation(project_id, user_id):
        raise ConflictException('Приглашение уже отправлено')
    if current_user_id == user_id: 
        raise InvalidInvitationStateException('Нельзя пригласить самого себя')
    return await repo.create_invitation(project_id, current_user_id, user_id, message)

async def get_user_invitations(db, current_user_id: int): # Возращаем список приглашений пользователя
    repo = ProjectInvitationRepository(db)
    return await repo.get_invitation_by_user(current_user_id)

async def get_project_invitations(db, project_id: int, current_user_id: int): # Возращает список приглашений проекта 
    repo = ProjectInvitationRepository(db)
    repo_proj = ProjectRepository(db)
    if not await repo_proj.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('')
    if not await repo_proj.get_project_by_id(project_id):
        raise
    return await repo.get_invitation_for_project(project_id)

async def response_to_invitation(db, invitation_id: int, action: str): # Возращает информацию о принятии/отклонении приглашения в проект
    repo = ProjectInvitationRepository(db)
    if action != 'accepted':
        raise

async def cancel_invitation(db, current_user_id: int, invitation_id: int): # Удалить приглашение
    repo = ProjectInvitationRepository(db)
    repo_proj = ProjectRepository(db)
    return await repo.delete_invitation(invitation_id)