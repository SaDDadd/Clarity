import pytest
import uuid
from core.uow import UnitOfWork
from models.project_invitations import ProjectInvitationModel


class TestProjectInvitationRepository:
    @pytest.mark.asyncio
    async def test_create_invitation_success(self, uow: UnitOfWork, test_project, test_users):
        """Проверяет успешное создание приглашения."""
        project = test_project
        inviter = test_users['admin']
        invitee = test_users['outsider']
        message = "Приглашение для теста"
        invitation = await uow.invitation.create_invitation(
            project_id=project.project_id,
            inviter_id=inviter.user_id,
            invitee_id=invitee.user_id,
            message=message
        )
        assert isinstance(invitation, ProjectInvitationModel)
        assert invitation.project_id == project.project_id
        assert invitation.inviter_id == inviter.user_id
        assert invitation.invitee_id == invitee.user_id
        assert invitation.status_invited == 'pending'
        assert invitation.message == message


    @pytest.mark.asyncio
    async def test_get_invitation_by_id_success(self, uow: UnitOfWork, test_invitation):
        """Проверяет получение приглашения по существующему ID."""
        invitation_id = test_invitation.invitation_id
        result = await uow.invitation.get_invitation_by_id(invitation_id)
        assert result is not None
        assert result.invitation_id == invitation_id


    @pytest.mark.asyncio
    async def test_get_invitation_by_id_not_found(self, uow: UnitOfWork):
        """Проверяет возврат None при запросе несуществующего ID."""
        result = await uow.invitation.get_invitation_by_id(99999)
        assert result is None


    @pytest.mark.asyncio
    async def test_get_invitation_by_user_success(self, uow: UnitOfWork, test_invitation):
        """Проверяет получение списка приглашений для пользователя, у которого они есть."""
        invitee_id = test_invitation.invitee_id
        result = await uow.invitation.get_invitation_by_user(invitee_id)
        assert isinstance(result, list)
        assert len(result) >= 1
        assert any(inv.invitee_id == invitee_id for inv in result)


    @pytest.mark.asyncio
    async def test_get_invitation_by_user_empty(self, uow: UnitOfWork, test_users):
        """Проверяет, что для пользователя без приглашений возвращается пустой список."""
        member = test_users['member']
        result = await uow.invitation.get_invitation_by_user(member.user_id)
        assert isinstance(result, list)


    @pytest.mark.asyncio
    async def test_get_invitation_for_project_success(self, uow: UnitOfWork, test_invitation):
        """Проверяет получение списка приглашений для проекта с активными приглашениями."""
        project_id = test_invitation.project_id
        result = await uow.invitation.get_invitation_for_project(project_id)
        assert isinstance(result, list)
        assert len(result) >= 1
        assert any(inv.project_id == project_id for inv in result)


    @pytest.mark.asyncio
    async def test_get_invitation_for_project_empty_with_users(self, uow: UnitOfWork, test_users):
        """Проверяет, что для проекта без приглашений возвращается пустой список."""
        admin = test_users['admin']
        project = await uow.project.create_project_with_admin(
            name=f'EmptyProject_{uuid.uuid4().hex[:8]}',
            description=None,
            admin_id=admin.user_id
        )
        result = await uow.invitation.get_invitation_for_project(project.project_id)
        assert isinstance(result, list)
        assert len(result) == 0


    @pytest.mark.asyncio
    async def test_update_invitation_status_success(self, uow: UnitOfWork, test_invitation):
        """Проверяет успешное обновление статуса приглашения."""
        invitation_id = test_invitation.invitation_id
        new_status = 'accepted'
        result = await uow.invitation.update_invitation_status(invitation_id, new_status)
        assert result is True
        updated = await uow.invitation.get_invitation_by_id(invitation_id)
        assert updated.status_invited == new_status


    @pytest.mark.asyncio
    async def test_update_invitation_status_not_found(self, uow: UnitOfWork):
        """Проверяет, что обновление статуса для несуществующего приглашения возвращает False."""
        result = await uow.invitation.update_invitation_status(99999, 'accepted')
        assert result is False


    @pytest.mark.asyncio
    async def test_delete_invitation_success(self, uow: UnitOfWork, test_invitation):
        """Проверяет успешное удаление приглашения."""
        invitation_id = test_invitation.invitation_id
        result = await uow.invitation.delete_invitation(invitation_id)
        assert result is True
        deleted = await uow.invitation.get_invitation_by_id(invitation_id)
        assert deleted is None


    @pytest.mark.asyncio
    async def test_delete_invitation_not_found(self, uow: UnitOfWork):
        """Проверяет, что удаление несуществующего приглашения возвращает False."""
        result = await uow.invitation.delete_invitation(99999)
        assert result is False


    @pytest.mark.asyncio
    async def test_get_pending_invitation_true(self, uow: UnitOfWork, test_invitation):
        """Проверяет, что для существующего ожидающего приглашения возвращается True."""
        project_id = test_invitation.project_id
        invitee_id = test_invitation.invitee_id
        result = await uow.invitation.get_pending_invitation(project_id, invitee_id)
        assert result is True


    @pytest.mark.asyncio
    async def test_get_pending_invitation_false(self, uow: UnitOfWork, test_project, test_users):
        """Проверяет, что для пользователя без приглашения возвращается False."""
        project_id = test_project.project_id
        member = test_users['member']
        result = await uow.invitation.get_pending_invitation(project_id, member.user_id)
        assert result is False