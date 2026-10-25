from core.exceptions import (AppException, ConflictException,
                             InvalidInvitationStateException,
                             InvitationAlreadyProcessedException,
                             MemberAlreadyInProjectException, NotFoundException,
                             PermissionDeniedException)
from models.project_invitations import ProjectInvitationModel
from repositories.project_invitation_repository import ProjectInvitationRepository
from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository
from schemas.invitation import InvitationResponse
from schemas.common import InvitationAction
from sqlalchemy.ext.asyncio import AsyncSession
from cache.cache_keys import user_invitations_key, project_invitations_key,project_key, \
                                user_projects_key, TTL_INVITATION_LIST
from cache.cache_service import get_cache, delete_cache, set_cache


async def send_invitation(db: AsyncSession, project_id: int, user_id: int, current_user_id: int,
                          message: str | None) -> ProjectInvitationModel:
    """Отправляет приглашение в проект."""
    repo = ProjectInvitationRepository(db)
    repo_proj = ProjectRepository(db)
    repo_user = UserRepository(db)
    if not await repo_proj.get_project_by_id(project_id):
        raise NotFoundException('Проект не найден!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Вы не состоите в проекте!')
    if not await repo_user.get_by_id(user_id):
        raise NotFoundException('Пользователь не найден!')
    if current_user_id == user_id:
        raise InvalidInvitationStateException('Нельзя пригласить самого себя!')
    if await repo_proj.is_user_in_project(project_id, user_id):
        raise MemberAlreadyInProjectException('Пользователь уже является участником проекта!')
    if await repo.get_pending_invitation(project_id, user_id):
        raise ConflictException('Приглашение уже отправлено!')
    try:
        result = await repo.create_invitation(project_id, current_user_id, user_id, message)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось отправить приглашение.')
    if result:
        await delete_cache(user_invitations_key(user_id, 'all'))
        await delete_cache(project_invitations_key(project_id, 'admin'))
    return result


async def get_user_invitations(db: AsyncSession, current_user_id: int) -> list[ProjectInvitationModel]:
    """Возвращает список приглашений для пользователя."""
    repo = ProjectInvitationRepository(db)
    return await repo.get_invitation_by_user(current_user_id)


async def get_project_invitations(db: AsyncSession, project_id: int,
                                  current_user_id: int) -> list[ProjectInvitationModel]:
    """Возвращает список приглашений проекта."""
    repo = ProjectInvitationRepository(db)
    repo_proj = ProjectRepository(db)
    if not await repo_proj.get_project_by_id(project_id):
        raise NotFoundException('Проект не найден!')
    if not await repo_proj.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Данного пользователя нет в проекте!')
    key = project_invitations_key(project_id, 'all')
    cached = await get_cache(key)
    if cached is not None:
        return cached
    data = await repo.get_invitation_for_project(project_id)
    serialized = [InvitationResponse.model_validate(i).model_dump(mode='json') for i in data]
    await set_cache(key, serialized, TTL_INVITATION_LIST)
    return serialized


async def response_to_invitation(db: AsyncSession, invitation_id: int, action: InvitationAction,
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
    if await repo_proj.is_user_in_project(project_id, invitee_id):
        raise MemberAlreadyInProjectException('Пользователь уже является участником проекта')
    try:
        await repo.update_invitation_status(invitation_id, action.value)
        if action == InvitationAction.ACCEPTED:
            await repo_proj.add_user(project_id, invitee_id)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось получить ответ на приглашение в проект.')
    await delete_cache(user_invitations_key(invitee_id, 'all'))
    await delete_cache(project_key(project_id))
    await delete_cache(project_invitations_key(project_id, 'admin'))
    await delete_cache(user_projects_key(invitee_id, 'all'))
    await delete_cache(user_projects_key(invitee_id, 'admin'))
    return {'message': f'Приглашение {action.value}'}


async def cancel_invitation(db: AsyncSession, invitation_id: int, current_user_id: int) -> dict:
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
    is_admin = await repo_proj.is_user_admin_or_curator(project_id, current_user_id)
    if not (is_admin or inviter_id == current_user_id):
        raise PermissionDeniedException('Только администратор проекта или отправитель может отменить приглашение')
    try:
        await repo.delete_invitation(invitation_id)
        await db.commit()
    except Exception:
        await db.rollback()
        raise AppException(500, 'Не удалось отменить приглашение в проект.')
    await delete_cache(user_invitations_key(invitation.invitee_id, 'all'))
    await delete_cache(project_invitations_key(project_id, 'admin'))
    return {'message': 'Приглашение отменено'}