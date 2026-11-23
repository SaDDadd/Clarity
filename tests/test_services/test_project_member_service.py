import pytest
from core.uow import UnitOfWork
from core.exceptions import (
    NotFoundException, PermissionDeniedException
)
from services.project_members_service import update_member_role


class TestProjectMemberService:
    @pytest.mark.asyncio
    async def test_update_member_role_same_role(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        admin = test_users['admin']
        member = test_users['member']
        result = await update_member_role(uow, member.user_id, project.project_id, admin.user_id, 'member')
        assert result == {'message': 'Роль уже установлена!'}


    @pytest.mark.asyncio
    async def test_update_member_role_project_not_found(self, uow: UnitOfWork, test_users):
        admin = test_users['admin']
        with pytest.raises(NotFoundException) as exc:
            await update_member_role(uow, admin.user_id, 99999, admin.user_id, 'member')
        assert exc.value.detail == 'Проект не найден!'


    @pytest.mark.asyncio
    async def test_update_member_role_not_admin(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        outsider = test_users['outsider']
        await uow.project.add_user(project.project_id, outsider.user_id)
        member = test_users['member']
        with pytest.raises(PermissionDeniedException) as exc:
            await update_member_role(uow, member.user_id, project.project_id, outsider.user_id, 'admin')
        assert exc.value.detail == 'Только администратор или куратор может менять роли!'


    @pytest.mark.asyncio
    async def test_update_member_role_self(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        admin = test_users['admin']
        with pytest.raises(PermissionDeniedException) as exc:
            await update_member_role(uow, admin.user_id, project.project_id, admin.user_id, 'member')
        assert exc.value.detail == 'Нельзя изменить свою роль!'