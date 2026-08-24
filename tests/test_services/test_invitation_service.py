import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from core.exceptions import (
    NotFoundException, PermissionDeniedException, MemberAlreadyInProjectException,
    ConflictException, InvalidInvitationStateException, InvitationAlreadyProcessedException
)
from services.invitation_service import (
    send_invitation, get_user_invitations, get_project_invitations,
    response_to_invitation, cancel_invitation
)
from schemas.common import InvitationRole
from repositories.project_invitation_repository import ProjectInvitationRepository
from repositories.project_repository import ProjectRepository

class TestInvitationService:
    @pytest.mark.asyncio
    async def test_send_invitation_success(self, db_session: AsyncSession, test_project, test_users):
        project = test_project
        admin = test_users['admin']
        outsider = test_users['outsider']
        message = "Join us!"
        result = await send_invitation(db_session, project.project_id, outsider.user_id, admin.user_id, message)
        assert result.project_id == project.project_id
        assert result.invitee_id == outsider.user_id
        assert result.status_invited == 'pending'

    @pytest.mark.asyncio
    async def test_send_invitation_project_not_found(self, db_session: AsyncSession, test_users):
        admin = test_users['admin']
        outsider = test_users['outsider']
        with pytest.raises(NotFoundException) as exc:
            await send_invitation(db_session, 99999, outsider.user_id, admin.user_id, "msg")
        assert exc.value.detail == 'Проект не найден!'

    @pytest.mark.asyncio
    async def test_send_invitation_user_not_found(self, db_session: AsyncSession, test_project, test_users):
        admin = test_users['admin']
        with pytest.raises(NotFoundException) as exc:
            await send_invitation(db_session, test_project.project_id, 99999, admin.user_id, "msg")
        assert exc.value.detail == 'Пользователь не найден!'

    @pytest.mark.asyncio
    async def test_send_invitation_not_admin(self, db_session: AsyncSession, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await send_invitation(db_session, project.project_id, outsider.user_id, member.user_id, "msg")
        assert exc.value.detail == 'Только администратор может приглашать!'

    @pytest.mark.asyncio
    async def test_send_invitation_user_already_member(self, db_session: AsyncSession, test_project_with_member, test_users):
        project = test_project_with_member['project']
        admin = test_users['admin']
        member = test_users['member']
        with pytest.raises(MemberAlreadyInProjectException) as exc:
            await send_invitation(db_session, project.project_id, member.user_id, admin.user_id, "msg")
        assert exc.value.detail == 'Пользователь уже является участником проекта!'

    @pytest.mark.asyncio
    async def test_send_invitation_pending_already_exists(self, db_session: AsyncSession, test_project, test_users):
        project = test_project
        admin = test_users['admin']
        outsider = test_users['outsider']
        await send_invitation(db_session, project.project_id, outsider.user_id, admin.user_id, "msg1")
        with pytest.raises(ConflictException) as exc:
            await send_invitation(db_session, project.project_id, outsider.user_id, admin.user_id, "msg2")
        assert exc.value.detail == 'Приглашение уже отправлено!'

    @pytest.mark.asyncio
    async def test_send_invitation_self(self, db_session: AsyncSession, test_project, test_users):
        admin = test_users['admin']
        with pytest.raises(InvalidInvitationStateException) as exc:
            await send_invitation(db_session, test_project.project_id, admin.user_id, admin.user_id, "msg")
        assert exc.value.detail == 'Нельзя пригласить самого себя!'

    @pytest.mark.asyncio
    async def test_get_user_invitations_success(self, db_session: AsyncSession, test_invitation, test_users):
        outsider = test_users['outsider']
        invitations = await get_user_invitations(db_session, outsider.user_id)
        assert isinstance(invitations, list)
        assert len(invitations) >= 1
        assert invitations[0].invitee_id == outsider.user_id

    @pytest.mark.asyncio
    async def test_get_user_invitations_empty(self, db_session: AsyncSession, test_users):
        member = test_users['member']
        invitations = await get_user_invitations(db_session, member.user_id)
        assert isinstance(invitations, list)
        assert len(invitations) == 0

    @pytest.mark.asyncio
    async def test_get_project_invitations_success(self, db_session: AsyncSession, test_invitation, test_users):
        invitation = test_invitation
        project_id = invitation.project_id
        admin = test_users['admin']
        invitations = await get_project_invitations(db_session, project_id, admin.user_id)
        assert isinstance(invitations, list)
        assert len(invitations) >= 1
        assert invitations[0].invitation_id == invitation.invitation_id

    @pytest.mark.asyncio
    async def test_get_project_invitations_not_admin(self, db_session: AsyncSession, test_invitation, test_users):
        project_id = test_invitation.project_id
        member = test_users['member']
        with pytest.raises(PermissionDeniedException) as exc:
            await get_project_invitations(db_session, project_id, member.user_id)
        assert exc.value.detail == 'Только администратор может просматривать приглашения проекта!'

    @pytest.mark.asyncio
    async def test_get_project_invitations_project_not_found(self, db_session: AsyncSession, test_users):
        admin = test_users['admin']
        with pytest.raises(NotFoundException) as exc:
            await get_project_invitations(db_session, 99999, admin.user_id)
        assert exc.value.detail == 'Проект не найден!'

    @pytest.mark.asyncio
    async def test_response_to_invitation_accept_success(self, db_session: AsyncSession, test_invitation, test_users):
        invitation = test_invitation
        invitee = test_users['outsider']
        result = await response_to_invitation(db_session, invitation.invitation_id, InvitationRole.ACCEPTED, invitee.user_id)
        assert result == {'message': 'Приглашение accepted'}
        repo_inv = ProjectInvitationRepository(db_session)
        updated_inv = await repo_inv.get_invitation_by_id(invitation.invitation_id)
        assert updated_inv.status_invited == 'accepted'
        repo_proj = ProjectRepository(db_session)
        assert await repo_proj.is_user_in_project(invitation.project_id, invitee.user_id) is True

    @pytest.mark.asyncio
    async def test_response_to_invitation_decline_success(self, db_session: AsyncSession, test_invitation, test_users):
        invitation = test_invitation
        invitee = test_users['outsider']
        result = await response_to_invitation(db_session, invitation.invitation_id, InvitationRole.DECLINED, invitee.user_id)
        assert result == {'message': 'Приглашение declined'}
        repo_inv = ProjectInvitationRepository(db_session)
        updated_inv = await repo_inv.get_invitation_by_id(invitation.invitation_id)
        assert updated_inv.status_invited == 'declined'
        repo_proj = ProjectRepository(db_session)
        assert await repo_proj.is_user_in_project(invitation.project_id, invitee.user_id) is False

    @pytest.mark.asyncio
    async def test_response_to_invitation_not_found(self, db_session: AsyncSession, test_users):
        outsider = test_users['outsider']
        with pytest.raises(NotFoundException) as exc:
            await response_to_invitation(db_session, 99999, InvitationRole.ACCEPTED, outsider.user_id)
        assert exc.value.detail == 'Приглашение не найдено'

    @pytest.mark.asyncio
    async def test_response_to_invitation_not_invitee(self, db_session: AsyncSession, test_invitation, test_users):
        invitation = test_invitation
        other_user = test_users['member']
        with pytest.raises(PermissionDeniedException) as exc:
            await response_to_invitation(db_session, invitation.invitation_id, InvitationRole.ACCEPTED, other_user.user_id)
        assert exc.value.detail == 'Вы не являетесь получателем этого приглашения'

    @pytest.mark.asyncio
    async def test_response_to_invitation_already_processed(self, db_session: AsyncSession, test_invitation, test_users):
        invitation = test_invitation
        invitee = test_users['outsider']
        await response_to_invitation(db_session, invitation.invitation_id, InvitationRole.ACCEPTED, invitee.user_id)
        with pytest.raises(InvitationAlreadyProcessedException) as exc:
            await response_to_invitation(db_session, invitation.invitation_id, InvitationRole.DECLINED, invitee.user_id)
        assert exc.value.detail == 'Приглашение уже было принято или отклонено'

    @pytest.mark.asyncio
    async def test_response_to_invitation_accept_already_member(self, db_session: AsyncSession, test_invitation, test_users):
        invitation = test_invitation
        invitee = test_users['outsider']
        repo_proj = ProjectRepository(db_session)
        await repo_proj.add_user(invitation.project_id, invitee.user_id)
        with pytest.raises(MemberAlreadyInProjectException) as exc:
            await response_to_invitation(db_session, invitation.invitation_id, InvitationRole.ACCEPTED, invitee.user_id)
        assert exc.value.detail == 'Пользователь уже является участником проекта'

    @pytest.mark.asyncio
    async def test_cancel_invitation_success(self, db_session: AsyncSession, test_invitation, test_users):
        invitation = test_invitation
        admin = test_users['admin']
        result = await cancel_invitation(db_session, invitation.invitation_id, admin.user_id)
        assert result == {'message': 'Приглашение отменено'}
        repo_inv = ProjectInvitationRepository(db_session)
        deleted = await repo_inv.get_invitation_by_id(invitation.invitation_id)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_cancel_invitation_not_found(self, db_session: AsyncSession, test_users):
        admin = test_users['admin']
        with pytest.raises(NotFoundException) as exc:
            await cancel_invitation(db_session, 99999, admin.user_id)
        assert exc.value.detail == 'Приглашение не найдено'

    @pytest.mark.asyncio
    async def test_cancel_invitation_already_processed(self, db_session: AsyncSession, test_invitation, test_users):
        invitation = test_invitation
        admin = test_users['admin']
        invitee = test_users['outsider']
        await response_to_invitation(db_session, invitation.invitation_id, InvitationRole.ACCEPTED, invitee.user_id)
        with pytest.raises(InvitationAlreadyProcessedException) as exc:
            await cancel_invitation(db_session, invitation.invitation_id, admin.user_id)
        assert exc.value.detail == 'Приглашение уже обработано'

    @pytest.mark.asyncio
    async def test_cancel_invitation_not_allowed(self, db_session: AsyncSession, test_invitation, test_users):
        invitation = test_invitation
        member = test_users['member']
        with pytest.raises(PermissionDeniedException) as exc:
            await cancel_invitation(db_session, invitation.invitation_id, member.user_id)
        assert exc.value.detail == 'Только администратор проекта или отправитель может отменить приглашение'