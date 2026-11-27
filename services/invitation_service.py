from core.exceptions import (ConflictException,
                             InvalidInvitationStateException,
                             InvitationAlreadyProcessedException,
                             MemberAlreadyInProjectException, NotFoundException,
                             PermissionDeniedException)
from schemas.invitation import InvitationResponse
from schemas.common import InvitationAction
from core.uow import UnitOfWork
from cache.cache_keys import project_key, user_projects_key, user_invitations_pattern
from cache.cache_service import delete_cache, delete_cache_by_pattern
from core.filters import InvitationFilter
from fastapi_pagination import Page, Params


async def get_user_invitations(uow: UnitOfWork, current_user_id: int,
                    invitation_filter: InvitationFilter | None = None, params: Params | None = None) -> Page[InvitationResponse]:
    """Приглашения пользователя с project_name."""
    rows = await uow.invitation.get_invitation_by_user_with_project(current_user_id, invitation_filter, params)
    result = []
    for invitation, project_name in rows.items:
        data = InvitationResponse.model_validate(
            {
                "invitation_id": invitation.invitation_id,
                "project_id": invitation.project_id,
                "project_name": project_name,
                "inviter_id": invitation.inviter_id,
                "invitee_id": invitation.invitee_id,
                "status_invited": invitation.status_invited,
                "created_date": invitation.created_date,
                "update_date": invitation.update_date,
                "message": invitation.message,
            }
        )
        result.append(data)
    return Page[InvitationResponse](
        items=result,
        total=rows.total,
        page=rows.page,
        size=rows.size,
        pages=rows.pages
    )


async def get_project_invitations(uow: UnitOfWork, project_id: int, current_user_id: int,
                                  invitation_filter: InvitationFilter | None = None, params: Params | None = None) -> Page[InvitationResponse]:
    """Возвращает приглашения проекта с учётом прав доступа."""
    if not await uow.project.get_project_by_id(project_id):
        raise NotFoundException('Проект не найден!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Данного пользователя нет в проекте!')
    if not await uow.project.is_user_admin_or_curator(project_id, current_user_id):
        raise PermissionDeniedException('Не админ и не куратор не может смотреть приглашения в проект!')
    rows = await uow.invitation.get_invitation_for_project_pagination(project_id, invitation_filter, params)
    serialized = []
    for invitation, username in rows.items:
        data = InvitationResponse.model_validate(
            {
                "invitation_id": invitation.invitation_id,
                "project_id": invitation.project_id,
                "inviter_id": invitation.inviter_id,
                "invitee_id": invitation.invitee_id,
                "invitee_username": username,
                "status_invited": invitation.status_invited,
                "created_date": invitation.created_date,
                "update_date": invitation.update_date,
                "message": invitation.message,
            }
        )
        serialized.append(data)
    return Page[InvitationResponse](
        items=serialized,
        total=rows.total,
        page=rows.page,
        size=rows.size,
        pages=rows.pages
    )


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
    if action == InvitationAction.ACCEPTED:
        """Инвалидируем кэш проекта и списков проектов пользователя."""
        await delete_cache(project_key(project_id))
        await delete_cache(user_projects_key(invitee_id, 'all'))
        await delete_cache(user_projects_key(invitee_id, 'admin'))
        await delete_cache_by_pattern(user_invitations_pattern(invitee_id))
    return {'message': f'Приглашение {action.value}!'}


async def send_invitation(uow: UnitOfWork, project_id: int, user_id: int, current_user_id: int, message: str) -> dict:
    """Отправляет приглашение."""
    project = await uow.project.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Вы не состоите в проекте!')
    if not await uow.user.get_by_id(user_id):
        raise NotFoundException('Пользователь не найден!')
    if not await uow.project.is_user_admin_or_curator(project_id, current_user_id):
        raise PermissionDeniedException('Только администратор или куратор может приглашать пользователей!')
    if current_user_id == user_id:
        raise InvalidInvitationStateException('Нельзя пригласить самого себя!')
    if await uow.project.is_user_in_project(project_id, user_id):
        raise MemberAlreadyInProjectException('Пользователь уже является участником проекта!')
    if await uow.invitation.get_pending_invitation(project_id, user_id):
        raise ConflictException('Приглашение уже отправлено!')
    result = await uow.invitation.create_invitation(project_id, current_user_id, user_id, message)
    await uow.session.refresh(result)
    answer = InvitationResponse.model_validate(result).model_dump(mode='json')
    answer['project_name'] = project.project_name
    await delete_cache(user_invitations_pattern(user_id))
    return answer


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
    return {'message': 'Приглашение удалено!'}