import pytest
from core.uow import UnitOfWork
from core.exceptions import (
    NotFoundException, PermissionDeniedException
)
from services.project_members_service import update_member_role


class TestProjectMemberService:
    @pytest.mark.asyncio
    async def test_update_member_role_success_to_admin(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        admin = test_users['admin']
        member = test_users['member']
        result = await update_member_role(uow, member.user_id, project.project_id, admin.user_id, 'admin')
        assert result == {'message': 'Роль обновлена'}
        role = await uow.project.get_user_role_in_project(project.project_id, member.user_id)
        assert role == 'admin'

    @pytest.mark.asyncio
    async def test_update_member_role_success_to_member(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        admin = test_users['admin']
        await uow.project.update_user_role(project.project_id, test_users['member'].user_id, 'admin')
        result = await update_member_role(uow, test_users['member'].user_id, project.project_id, admin.user_id, 'member')
        assert result == {'message': 'Роль обновлена'}
        role = await uow.project.get_user_role_in_project(project.project_id, test_users['member'].user_id)
        assert role == 'member'

    @pytest.mark.asyncio
    async def test_update_member_role_same_role(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        admin = test_users['admin']
        member = test_users['member']
        result = await update_member_role(uow, member.user_id, project.project_id, admin.user_id, 'member')
        assert result == {'message': 'Роль уже установлена'}

    @pytest.mark.asyncio
    async def test_update_member_role_project_not_found(self, uow: UnitOfWork, test_users):
        admin = test_users['admin']
        with pytest.raises(NotFoundException) as exc:
            await update_member_role(uow, admin.user_id, 99999, admin.user_id, 'member')
        assert exc.value.detail == 'Проект не найден!'

    @pytest.mark.asyncio
    async def test_update_member_role_user_not_in_project(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await update_member_role(uow, outsider.user_id, test_project.project_id, admin.user_id, 'member')
        assert exc.value.detail == 'Пользователь не состоит в проекте'

    @pytest.mark.asyncio
    async def test_update_member_role_not_admin(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        outsider = test_users['outsider']
        await uow.project.add_user(project.project_id, outsider.user_id)
        member = test_users['member']
        with pytest.raises(PermissionDeniedException) as exc:
            await update_member_role(uow, member.user_id, project.project_id, outsider.user_id, 'admin')
        assert exc.value.detail == 'Текущий пользователь не администратор проекта!'

    @pytest.mark.asyncio
    async def test_update_member_role_self(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        admin = test_users['admin']
        with pytest.raises(PermissionDeniedException) as exc:
            await update_member_role(uow, admin.user_id, project.project_id, admin.user_id, 'member')
        assert exc.value.detail == 'Нельзя изменить свою собственную роль!'

    @pytest.mark.asyncio
    async def test_update_member_role_last_admin(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        pass