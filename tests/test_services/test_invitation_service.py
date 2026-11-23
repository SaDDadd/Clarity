import pytest
from core.uow import UnitOfWork
from core.exceptions import (
    NotFoundException, PermissionDeniedException, MemberAlreadyInProjectException,
    InvalidInvitationStateException, InvitationAlreadyProcessedException
)
from services.invitation_service import (
    send_invitation, get_project_invitations,
    response_to_invitation)
from schemas.common import InvitationRole


class TestInvitationService:
    @pytest.mark.asyncio
    async def test_send_invitation_project_not_found(self, uow: UnitOfWork, test_users):
        admin = test_users['admin']
        outsider = test_users['outsider']
        with pytest.raises(NotFoundException) as exc:
            await send_invitation(uow, 99999, outsider.user_id, admin.user_id, "msg")
        assert exc.value.detail == 'Проект не найден!'


    @pytest.mark.asyncio
    async def test_send_invitation_user_not_found(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        with pytest.raises(NotFoundException) as exc:
            await send_invitation(uow, test_project.project_id, 99999, admin.user_id, "msg")
        assert exc.value.detail == 'Пользователь не найден!'


    @pytest.mark.asyncio
    async def test_send_invitation_user_already_member(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        admin = test_users['admin']
        member = test_users['member']
        with pytest.raises(MemberAlreadyInProjectException) as exc:
            await send_invitation(uow, project.project_id, member.user_id, admin.user_id, "msg")
        assert exc.value.detail == 'Пользователь уже является участником проекта!'


    @pytest.mark.asyncio
    async def test_send_invitation_self(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        with pytest.raises(InvalidInvitationStateException) as exc:
            await send_invitation(uow, test_project.project_id, admin.user_id, admin.user_id, "msg")
        assert exc.value.detail == 'Нельзя пригласить самого себя!'


    @pytest.mark.asyncio
    async def test_get_project_invitations_project_not_found(self, uow: UnitOfWork, test_users):
        admin = test_users['admin']
        with pytest.raises(NotFoundException) as exc:
            await get_project_invitations(uow, 99999, admin.user_id)
        assert exc.value.detail == 'Проект не найден!'


    @pytest.mark.asyncio
    async def test_response_to_invitation_accept_success(self, uow: UnitOfWork, test_invitation, test_users):
        invitation = test_invitation
        invitee = test_users['outsider']
        result = await response_to_invitation(uow, invitation.invitation_id, InvitationRole.ACCEPTED, invitee.user_id)
        assert result == {'message': 'Приглашение accepted!'}
        updated_inv = await uow.invitation.get_invitation_by_id(invitation.invitation_id)
        assert updated_inv.status_invited == 'accepted'
        assert await uow.project.is_user_in_project(invitation.project_id, invitee.user_id) is True


    @pytest.mark.asyncio
    async def test_response_to_invitation_decline_success(self, uow: UnitOfWork, test_invitation, test_users):
        invitation = test_invitation
        invitee = test_users['outsider']
        result = await response_to_invitation(uow, invitation.invitation_id, InvitationRole.DECLINED, invitee.user_id)
        assert result == {'message': 'Приглашение declined!'}
        updated_inv = await uow.invitation.get_invitation_by_id(invitation.invitation_id)
        assert updated_inv.status_invited == 'declined'
        assert await uow.project.is_user_in_project(invitation.project_id, invitee.user_id) is False


    @pytest.mark.asyncio
    async def test_response_to_invitation_not_found(self, uow: UnitOfWork, test_users):
        outsider = test_users['outsider']
        with pytest.raises(NotFoundException) as exc:
            await response_to_invitation(uow, 99999, InvitationRole.ACCEPTED, outsider.user_id)
        assert exc.value.detail == 'Приглашение не найдено!'


    @pytest.mark.asyncio
    async def test_response_to_invitation_not_invitee(self, uow: UnitOfWork, test_invitation, test_users):
        invitation = test_invitation
        other_user = test_users['member']
        with pytest.raises(PermissionDeniedException) as exc:
            await response_to_invitation(uow, invitation.invitation_id, InvitationRole.ACCEPTED, other_user.user_id)
        assert exc.value.detail == 'Вы не являетесь получателем этого приглашения!'


    @pytest.mark.asyncio
    async def test_response_to_invitation_already_processed(self, uow: UnitOfWork, test_invitation, test_users):
        invitation = test_invitation
        invitee = test_users['outsider']
        await response_to_invitation(uow, invitation.invitation_id, InvitationRole.ACCEPTED, invitee.user_id)
        with pytest.raises(InvitationAlreadyProcessedException) as exc:
            await response_to_invitation(uow, invitation.invitation_id, InvitationRole.DECLINED, invitee.user_id)
        assert exc.value.detail == 'Приглашение уже было принято или отклонено!'


    @pytest.mark.asyncio
    async def test_response_to_invitation_accept_already_member(self, uow: UnitOfWork, test_invitation, test_users):
        invitation = test_invitation
        invitee = test_users['outsider']
        await uow.project.add_user(invitation.project_id, invitee.user_id)
        with pytest.raises(MemberAlreadyInProjectException) as exc:
            await response_to_invitation(uow, invitation.invitation_id, InvitationRole.ACCEPTED, invitee.user_id)
        assert exc.value.detail == 'Пользователь уже является участником проекта!'