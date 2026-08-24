import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from core.exceptions import (
    NotFoundException, PermissionDeniedException, LastAdminDeletionException
)
from services.project_members_service import update_member_role
from repositories.project_repository import ProjectRepository


class TestProjectMemberService:
    @pytest.mark.asyncio
    async def test_update_member_role_success_to_admin(self, db_session: AsyncSession, test_project_with_member, test_users):
        project = test_project_with_member['project']
        admin = test_users['admin']
        member = test_users['member']
        result = await update_member_role(db_session, member.user_id, project.project_id, admin.user_id, 'admin')
        assert result == {'message': 'Роль обновлена'}
        repo = ProjectRepository(db_session)
        role = await repo.get_user_role_in_project(project.project_id, member.user_id)
        assert role == 'admin'

    @pytest.mark.asyncio
    async def test_update_member_role_success_to_member(self, db_session: AsyncSession, test_project_with_member, test_users):
        project = test_project_with_member['project']
        admin = test_users['admin']
        repo = ProjectRepository(db_session)
        # повышаем до admin
        await repo.update_user_role(project.project_id, test_users['member'].user_id, 'admin')
        # теперь понижаем до member
        result = await update_member_role(db_session, test_users['member'].user_id, project.project_id, admin.user_id, 'member')
        assert result == {'message': 'Роль обновлена'}
        role = await repo.get_user_role_in_project(project.project_id, test_users['member'].user_id)
        assert role == 'member'

    @pytest.mark.asyncio
    async def test_update_member_role_same_role(self, db_session: AsyncSession, test_project_with_member, test_users):
        project = test_project_with_member['project']
        admin = test_users['admin']
        member = test_users['member']
        # пытаемся обновить на ту же роль 'member'
        result = await update_member_role(db_session, member.user_id, project.project_id, admin.user_id, 'member')
        assert result == {'message': 'Роль уже установлена'}

    @pytest.mark.asyncio
    async def test_update_member_role_project_not_found(self, db_session: AsyncSession, test_users):
        admin = test_users['admin']
        with pytest.raises(NotFoundException) as exc:
            await update_member_role(db_session, admin.user_id, 99999, admin.user_id, 'member')
        assert exc.value.detail == 'Проект не найден'

    @pytest.mark.asyncio
    async def test_update_member_role_user_not_in_project(self, db_session: AsyncSession, test_project, test_users):
        admin = test_users['admin']
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await update_member_role(db_session, outsider.user_id, test_project.project_id, admin.user_id, 'member')
        assert exc.value.detail == 'Пользователь не состоит в проекте'

    @pytest.mark.asyncio
    async def test_update_member_role_not_admin(self, db_session: AsyncSession, test_project_with_member, test_users):
        project = test_project_with_member['project']
        # добавляем outsider в проект как участника (не админа)
        repo = ProjectRepository(db_session)
        outsider = test_users['outsider']
        await repo.add_user(project.project_id, outsider.user_id)

        member = test_users['member']
        # теперь пытаемся изменить роль member, будучи outsider (не админом)
        with pytest.raises(PermissionDeniedException) as exc:
            await update_member_role(db_session, member.user_id, project.project_id, outsider.user_id, 'admin')
        assert exc.value.detail == 'Текущий пользователь не администратор проекта'

    @pytest.mark.asyncio
    async def test_update_member_role_self(self, db_session: AsyncSession, test_project_with_member, test_users):
        project = test_project_with_member['project']
        admin = test_users['admin']
        with pytest.raises(PermissionDeniedException) as exc:
            await update_member_role(db_session, admin.user_id, project.project_id, admin.user_id, 'member')
        assert exc.value.detail == 'Нельзя изменить свою собственную роль'

    @pytest.mark.asyncio
    async def test_update_member_role_last_admin(self, db_session: AsyncSession, test_project, test_users):
        admin = test_users['admin']
        pass