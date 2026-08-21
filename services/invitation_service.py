from core.exceptions import (AppException, ConflictException,
                             InvalidInvitationStateException,
                             InvitationAlreadyProcessedException,
                             MemberAlreadyInProjectException, NotFoundException,
                             PermissionDeniedException)
from models.project_invitations import ProjectInvitationModel
from repositories.project_invitation_repository import ProjectInvitationRepository
from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository
from schemas.invitation import InvitationRole


async def send_invitation(db, project_id: int, user_id: int, current_user_id: int,
                          message: str) -> ProjectInvitationModel:
    """Отправляет приглашение в проект."""
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


async def get_user_invitations(db, current_user_id: int) -> list[ProjectInvitationModel]:
    """Возвращает список приглашений для пользователя."""
    repo = ProjectInvitationRepository(db)
    return await repo.get_invitation_by_user(current_user_id)


async def get_project_invitations(db, project_id: int,
                                  current_user_id: int) -> list[ProjectInvitationModel]:
    """Возвращает список приглашений проекта (только для администратора)."""
    repo = ProjectInvitationRepository(db)
    repo_proj = ProjectRepository(db)
    if not await repo_proj.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('Только администратор может просматривать приглашения проекта!')
    if not await repo_proj.get_project_by_id(project_id):
        raise NotFoundException('Проект не найден!')
    return await repo.get_invitation_for_project(project_id)


async def response_to_invitation(db, invitation_id: int, action: InvitationRole,
                                 current_user_id: int) -> dict:
    """Обрабатывает ответ на приглашение (принять/отклонить)."""
    repo = ProjectInvitationRepository(db)
    repo_proj = ProjectRepository(db)

    invitation = await repo.get_invitation_by_id(invitation_id)
    if not invitation:
        raise NotFoundException('Приглашение не найдено')

    invitee_id = invitation.invitee_id
    project_id = invitation.project_id
    status_invited = invitation.status_invited

    if current_user_id != invitee_id:
        raise PermissionDeniedException('Вы не являетесь получателем этого приглашения')
    if status_invited != 'pending':
        raise InvitationAlreadyProcessedException('Приглашение уже было принято или отклонено')

    new_status = action.value
    updated = await repo.update_invitation_status(invitation_id, new_status)
    if not updated:
        raise AppException(500, 'Не удалось обновить статус приглашения')
    if action == InvitationRole.ACCEPTED:
        if await repo_proj.is_user_in_project(project_id, invitee_id):
            raise MemberAlreadyInProjectException('Пользователь уже является участником проекта')
        await repo_proj.add_user(project_id, invitee_id)
    return {'message': f'Приглашение {new_status}'}


async def cancel_invitation(db, invitation_id: int, current_user_id: int) -> dict:
    """Отменяет (удаляет) приглашение."""
    repo = ProjectInvitationRepository(db)
    repo_proj = ProjectRepository(db)

    invitation = await repo.get_invitation_by_id(invitation_id)
    if not invitation:
        raise NotFoundException('Приглашение не найдено')

    if invitation.status_invited != 'pending':
        raise InvitationAlreadyProcessedException('Приглашение уже обработано')

    project_id = invitation.project_id
    inviter_id = invitation.inviter_id

    is_admin = await repo_proj.is_user_admin(project_id, current_user_id)
    if not (is_admin or inviter_id == current_user_id):
        raise PermissionDeniedException('Только администратор проекта или отправитель может отменить приглашение')

    deleted = await repo.delete_invitation(invitation_id)
    if not deleted:
        raise NotFoundException('Не удалось удалить приглашение (возможно, оно уже удалено)')
    return {'message': 'Приглашение отменено'}