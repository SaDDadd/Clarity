from repositories.project_invitation_repository import ProjectInvitationRepository
from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository
from core.exceptions import NotFoundException, PermissionDeniedException, ConflictException, MemberAlreadyInProjectException, InvalidInvitationStateException, InvitationAlreadyProcessedException
from schemas.invitation import InvitationRole

async def send_invitation(db, project_id: int, user_id: int, current_user_id: int, message: str): # Отправка приглашения
    repo = ProjectInvitationRepository(db)
    repo_proj = ProjectRepository(db)
    repo_user = UserRepository(db)
    if not await repo_proj.get_project_by_id(project_id):
        raise NotFoundException('Проект не найден!')
    if not await repo_user.get_by_id(user_id):
        raise NotFoundException('Пользователь не найден!')
    if not await repo_proj.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('Только администратор может приглашать!')
    if await repo_proj.is_user_in_project(project_id, user_id):
        raise MemberAlreadyInProjectException('Пользователь уже является участником проекта!')
    if await repo.get_pending_invitation(project_id, user_id):
        raise ConflictException('Приглашение уже отправлено!')
    if current_user_id == user_id: 
        raise InvalidInvitationStateException('Нельзя пригласить самого себя!')
    return await repo.create_invitation(project_id, current_user_id, user_id, message)

async def get_user_invitations(db, current_user_id: int): # Возращаем список приглашений пользователя
    repo = ProjectInvitationRepository(db)
    return await repo.get_invitation_by_user(current_user_id)

async def get_project_invitations(db, project_id: int, current_user_id: int): # Возращает список приглашений проекта 
    repo = ProjectInvitationRepository(db)
    repo_proj = ProjectRepository(db)
    if not await repo_proj.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('Только администратор может просматривать приглашения проекта!')
    if not await repo_proj.get_project_by_id(project_id):
        raise NotFoundException('Проект не найден!')
    return await repo.get_invitation_for_project(project_id)

async def response_to_invitation(db, invitation_id: int, action: InvitationRole, current_user_id: int): # Возращает информацию о принятии/отклонении приглашения в проект
    repo = ProjectInvitationRepository(db)
    repo_proj = ProjectRepository(db)
    if action != 'accepted':
        raise
    if not await repo.get_invitation_by_id(invitation_id):
        raise NotFoundException()
    if current_user_id != invitee_id:
        raise PermissionDeniedException()
    if
        raise InvitationAlreadyProcessedException()
    repo.update_invitation_status()
    if action == InvitationRole.ACCEPTED:
        repo_proj.add_user(project_id, invitee_id)
    return {'message': ''}

async def cancel_invitation(db, invitation_id: int, current_user_id: int): # Удалить приглашение
    repo = ProjectInvitationRepository(db)
    repo_proj = ProjectRepository(db)
    if await repo.get_invitation_by_id(invitation_id) is None:
        raise NotFoundException()
    project_id = 
    inviter_id = 
    if not await repo_proj.is_user_admin(project_id, current_user_id) or inviter_id == current_user_id:
        raise PermissionDeniedException()
    return await repo.delete_invitation(invitation_id)