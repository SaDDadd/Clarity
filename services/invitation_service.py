from core.exceptions import (ConflictException,
                             InvalidInvitationStateException,
                             InvitationAlreadyProcessedException,
                             MemberAlreadyInProjectException, NotFoundException,
                             PermissionDeniedException)
from schemas.invitation import InvitationResponse
from schemas.common import InvitationAction
from core.uow import UnitOfWork
from cache.cache_keys import (user_invitations_key, project_invitations_key,
                              project_key, user_projects_key, TTL_INVITATION_LIST)
from cache.cache_service import get_cache, delete_cache, set_cache
from core.filters import InvitationFilter


async def send_invitation(uow: UnitOfWork, project_id: int, user_id: int, current_user_id: int, message: str) -> dict:
    """Отправляет приглашение. Паттерн как в create_project."""
    project = await uow.project.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Вы не состоите в проекте!')
    if not await uow.user.get_by_id(user_id):
        raise NotFoundException('Пользователь не найден!')
    if current_user_id == user_id:
        raise InvalidInvitationStateException('Нельзя пригласить самого себя!')
    if await uow.project.is_user_in_project(project_id, user_id):
        raise MemberAlreadyInProjectException('Пользователь уже является участником проекта!')
    if await uow.invitation.get_pending_invitation(project_id, user_id):
        raise ConflictException('Приглашение уже отправлено!')
    result = await uow.invitation.create_invitation(project_id, current_user_id, user_id, message)
    answer = InvitationResponse.model_validate(result).model_dump(mode='json')
    answer['project_name'] = project.project_name
    await delete_cache(user_invitations_key(user_id, 'all'))
    await delete_cache(project_invitations_key(project_id, 'all'))
    return answer


async def get_user_invitations(uow: UnitOfWork, current_user_id: int, invitation_filter: InvitationFilter | None = None) -> list[dict]:
    """Приглашения пользователя с project_name."""
    key = user_invitations_key(current_user_id, 'all')
    cached = await get_cache(key)
    if cached is not None:
        return cached
    rows = await uow.invitation.get_invitation_by_user_with_project(current_user_id, invitation_filter)
    result = []
    for invitation, project_name in rows:
        data = InvitationResponse.model_validate(invitation).model_dump(mode='json')
        data['project_name'] = project_name
        result.append(data)
    await set_cache(key, result, TTL_INVITATION_LIST)
    return result


async def get_project_invitations(uow: UnitOfWork, project_id: int, current_user_id: int, invitation_filter: InvitationFilter | None = None) -> list[dict]:
    """Возвращает приглашения проекта с учётом прав доступа."""
    if not await uow.project.get_project_by_id(project_id):
        raise NotFoundException('Проект не найден!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Данного пользователя нет в проекте!')
    if not await uow.project.is_user_admin_or_curator(project_id, current_user_id):
        raise PermissionDeniedException('Не админ и не куратор не может смотреть приглашения в проект!')
    key = project_invitations_key(project_id, 'all')
    cached = await get_cache(key)
    if cached is not None:
        return cached
    data = await uow.invitation.get_invitation_for_project(project_id, invitation_filter)
    serialized = [InvitationResponse.model_validate(i).model_dump(mode='json') for i in data]
    await set_cache(key, serialized, TTL_INVITATION_LIST)
    return serialized


async def response_to_invitation(uow: UnitOfWork, invitation_id: int, action: InvitationAction, current_user_id: int) -> dict:
    """Обрабатывает ответ на приглашение."""
    invitation = await uow.invitation.get_invitation_by_id(invitation_id)
    if not invitation:
        raise NotFoundException('Приглашение не найдено!')
    invitee_id = invitation.invitee_id
    project_id = invitation.project_id
    if current_user_id != invitee_id:
        raise PermissionDeniedException('Вы не являетесь получателем этого приглашения!')
    if invitation.status_invited != 'pending':
        raise InvitationAlreadyProcessedException('Приглашение уже было принято или отклонено!')
    if await uow.project.is_user_in_project(project_id, invitee_id):
        raise MemberAlreadyInProjectException('Пользователь уже является участником проекта!')
    await uow.invitation.update_invitation_status(invitation_id, action.value)
    if action == InvitationAction.ACCEPTED:
        await uow.project.add_user(project_id, invitee_id)
    await delete_cache(user_invitations_key(invitee_id, 'all'))
    await delete_cache(project_invitations_key(project_id, 'all'))
    if action == InvitationAction.ACCEPTED:
        await delete_cache(project_key(project_id))
        await delete_cache(user_projects_key(invitee_id, 'all'))
        await delete_cache(user_projects_key(invitee_id, 'admin'))
    return {'message': f'Приглашение {action.value}!'}


async def delete_invitation(uow: UnitOfWork, invitation_id: int, current_user_id: int) -> dict:
    """Удаляем приглашение."""
    invitation = await uow.invitation.get_invitation_by_id(invitation_id)
    if not invitation:
        raise NotFoundException('Приглашение не найдено!')
    if invitation.status_invited != 'pending':
        raise InvitationAlreadyProcessedException('Приглашение уже обработано!')
    project_id = invitation.project_id
    inviter_id = invitation.inviter_id
    is_sender = current_user_id == inviter_id
    is_admin = await uow.project.is_user_admin_or_curator(project_id, current_user_id)
    if not (is_admin or is_sender):
        raise PermissionDeniedException('Только администратор проекта или отправитель может удалить приглашение!')
    await uow.invitation.delete_invitation(invitation_id)
    await delete_cache(user_invitations_key(invitation.invitee_id, 'all'))
    await delete_cache(project_invitations_key(project_id, 'all'))
    return {'message': 'Приглашение удалено!'}