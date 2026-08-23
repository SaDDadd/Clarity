import pytest
import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DataError
from repositories.project_repository import ProjectRepository
from models.project import ProjectModel
from models.project_members import ProjectMemberModel
from models.task import TaskModel
from models.project_invitations import ProjectInvitationModel
from repositories.task_repository import TaskRepository
from repositories.project_invitation_repository import ProjectInvitationRepository
from schemas.task import TaskCreate


class TestProjectRepository:

    @pytest.mark.asyncio
    async def test_create_project_with_admin_success(self, db_session: AsyncSession, test_users):
        repo = ProjectRepository(db_session)
        name = f'Test_project_{uuid.uuid4().hex[:8]}'
        response = await repo.create_project_with_admin(
            name=name,
            description='Test_description',
            admin_id=test_users['admin'].user_id
        )
        get_member = await repo.is_user_in_project(response.project_id, test_users['admin'].user_id)
        assert isinstance(response, ProjectModel)
        assert response.project_name == name
        assert response.project_description == 'Test_description'
        assert response.admin_id == test_users['admin'].user_id
        assert get_member is True

    @pytest.mark.asyncio
    async def test_create_project_with_admin_missing_fields(self, db_session: AsyncSession, test_users):
        repo = ProjectRepository(db_session)
        with pytest.raises(IntegrityError):
            await repo.create_project_with_admin(
                name=None,
                description='Test_description',
                admin_id=test_users['admin'].user_id
            )

    @pytest.mark.asyncio
    async def test_add_user_success(self, db_session: AsyncSession, test_users, test_project):
        repo = ProjectRepository(db_session)
        response = await repo.add_user(test_project.project_id, test_users['member'].user_id)
        get_member = await repo.is_user_in_project(test_project.project_id, test_users['member'].user_id)
        assert response is True
        assert get_member is True

    @pytest.mark.asyncio
    async def test_add_user_already_in_project(self, db_session: AsyncSession, test_users, test_project_with_member):
        repo = ProjectRepository(db_session)
        with pytest.raises(IntegrityError):
            await repo.add_user(
                test_project_with_member['project'].project_id,
                test_users['member'].user_id
            )

    @pytest.mark.asyncio
    async def test_add_user_non_existent_user(self, db_session: AsyncSession, test_project):
        repo = ProjectRepository(db_session)
        with pytest.raises(IntegrityError):
            await repo.add_user(test_project.project_id, 99999)

    @pytest.mark.asyncio
    async def test_get_projects_by_admin_success(self, db_session: AsyncSession, test_users, test_project):
        repo = ProjectRepository(db_session)
        projects = await repo.get_projects_by_admin(test_users['admin'].user_id)
        assert isinstance(projects, list)
        assert len(projects) >= 1
        assert any(p.project_id == test_project.project_id for p in projects)

    @pytest.mark.asyncio
    async def test_get_projects_by_admin_empty(self, db_session: AsyncSession, test_users):
        repo = ProjectRepository(db_session)
        projects = await repo.get_projects_by_admin(test_users['outsider'].user_id)
        assert isinstance(projects, list)
        assert len(projects) == 0

    @pytest.mark.asyncio
    async def test_get_projects_by_admin_user_not_found(self, db_session: AsyncSession):
        repo = ProjectRepository(db_session)
        projects = await repo.get_projects_by_admin(99999)
        assert isinstance(projects, list)
        assert len(projects) == 0

    @pytest.mark.asyncio
    async def test_is_user_in_project_true(self, db_session: AsyncSession, test_project_with_member, test_users):
        repo = ProjectRepository(db_session)
        project = test_project_with_member['project']
        member = test_users['member']
        result = await repo.is_user_in_project(project.project_id, member.user_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_is_user_in_project_false(self, db_session: AsyncSession, test_project, test_users):
        repo = ProjectRepository(db_session)
        outsider = test_users['outsider']
        result = await repo.is_user_in_project(test_project.project_id, outsider.user_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_is_user_in_project_project_not_found(self, db_session: AsyncSession, test_users):
        repo = ProjectRepository(db_session)
        admin = test_users['admin']
        result = await repo.is_user_in_project(99999, admin.user_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_is_user_in_project_user_not_found(self, db_session: AsyncSession, test_project):
        repo = ProjectRepository(db_session)
        result = await repo.is_user_in_project(test_project.project_id, 99999)
        assert result is False

    @pytest.mark.asyncio
    async def test_get_user_role_in_project_admin(self, db_session: AsyncSession, test_project, test_users):
        repo = ProjectRepository(db_session)
        admin = test_users['admin']
        role = await repo.get_user_role_in_project(test_project.project_id, admin.user_id)
        assert role == 'admin'

    @pytest.mark.asyncio
    async def test_get_user_role_in_project_member(self, db_session: AsyncSession, test_project_with_member, test_users):
        repo = ProjectRepository(db_session)
        project = test_project_with_member['project']
        member = test_users['member']
        role = await repo.get_user_role_in_project(project.project_id, member.user_id)
        assert role == 'member'

    @pytest.mark.asyncio
    async def test_get_user_role_in_project_not_member(self, db_session: AsyncSession, test_project, test_users):
        repo = ProjectRepository(db_session)
        outsider = test_users['outsider']
        role = await repo.get_user_role_in_project(test_project.project_id, outsider.user_id)
        assert role is None

    @pytest.mark.asyncio
    async def test_get_project_all_info_success(self, db_session: AsyncSession, test_project_with_member, test_users):
        repo = ProjectRepository(db_session)
        project = test_project_with_member['project']
        info = await repo.get_project_all_info(project.project_id)
        assert isinstance(info, dict)
        assert 'project' in info
        assert 'members' in info
        assert info['project'].project_id == project.project_id
        assert len(info['members']) >= 2
        member_ids = [m.user_id for m in info['members']]
        assert test_users['admin'].user_id in member_ids
        assert test_users['member'].user_id in member_ids

    @pytest.mark.asyncio
    async def test_get_project_all_info_project_not_found(self, db_session: AsyncSession):
        repo = ProjectRepository(db_session)
        info = await repo.get_project_all_info(99999)
        assert info['project'] is None
        assert info['members'] == []

    @pytest.mark.asyncio
    async def test_reassign_admin_success(self, db_session: AsyncSession, test_project_with_member, test_users):
        repo = ProjectRepository(db_session)
        project = test_project_with_member['project']
        member = test_users['member']
        await repo.update_user_role(project.project_id, member.user_id, 'admin')
        admins_before = await repo.get_admins_list(project.project_id)
        assert len(admins_before) == 2

        result = await repo.reassign_admin(project.project_id, member.user_id)
        assert result is True
        updated_project = await repo.get_project_by_id(project.project_id)
        assert updated_project.admin_id == member.user_id

    @pytest.mark.asyncio
    async def test_reassign_admin_project_not_found(self, db_session: AsyncSession, test_users):
        repo = ProjectRepository(db_session)
        result = await repo.reassign_admin(99999, test_users['admin'].user_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_reassign_admin_new_admin_not_in_project(self, db_session: AsyncSession, test_project, test_users):
        repo = ProjectRepository(db_session)
        outsider = test_users['outsider']
        result = await repo.reassign_admin(test_project.project_id, outsider.user_id)
        assert result is True
        updated = await repo.get_project_by_id(test_project.project_id)
        assert updated.admin_id == outsider.user_id

    @pytest.mark.asyncio
    async def test_get_admins_list_success(self, db_session: AsyncSession, test_project, test_users):
        repo = ProjectRepository(db_session)
        admins = await repo.get_admins_list(test_project.project_id)
        assert isinstance(admins, list)
        assert len(admins) == 1
        assert admins[0].user_id == test_users['admin'].user_id
        assert admins[0].role_project == 'admin'

    @pytest.mark.asyncio
    async def test_get_admins_list_no_admins(self, db_session: AsyncSession, test_project):
        repo = ProjectRepository(db_session)
        from sqlalchemy import delete
        await db_session.execute(
            delete(ProjectMemberModel).where(
                ProjectMemberModel.project_id == test_project.project_id,
                ProjectMemberModel.role_project == 'admin'
            )
        )
        await db_session.commit()
        admins = await repo.get_admins_list(test_project.project_id)
        assert isinstance(admins, list)
        assert len(admins) == 0

    @pytest.mark.asyncio
    async def test_is_user_admin_true(self, db_session: AsyncSession, test_project, test_users):
        repo = ProjectRepository(db_session)
        admin = test_users['admin']
        result = await repo.is_user_admin(test_project.project_id, admin.user_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_is_user_admin_false_for_member(self, db_session: AsyncSession, test_project_with_member, test_users):
        repo = ProjectRepository(db_session)
        project = test_project_with_member['project']
        member = test_users['member']
        result = await repo.is_user_admin(project.project_id, member.user_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_is_user_admin_false_for_non_member(self, db_session: AsyncSession, test_project, test_users):
        repo = ProjectRepository(db_session)
        outsider = test_users['outsider']
        result = await repo.is_user_admin(test_project.project_id, outsider.user_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_get_user_projects_success(self, db_session: AsyncSession, test_project_with_member, test_users):
        repo = ProjectRepository(db_session)
        admin_projects = await repo.get_user_projects(test_users['admin'].user_id)
        member_projects = await repo.get_user_projects(test_users['member'].user_id)
        assert isinstance(admin_projects, list)
        assert len(admin_projects) >= 1
        assert isinstance(member_projects, list)
        assert len(member_projects) >= 1
        project_ids_admin = [p.project_id for p in admin_projects]
        project_ids_member = [p.project_id for p in member_projects]
        common = set(project_ids_admin) & set(project_ids_member)
        assert len(common) >= 1

    @pytest.mark.asyncio
    async def test_get_user_projects_empty(self, db_session: AsyncSession, test_users):
        repo = ProjectRepository(db_session)
        outsider = test_users['outsider']
        projects = await repo.get_user_projects(outsider.user_id)
        assert isinstance(projects, list)
        assert len(projects) == 0

    @pytest.mark.asyncio
    async def test_update_project_description_success(self, db_session: AsyncSession, test_project):
        repo = ProjectRepository(db_session)
        new_desc = f'Updated_description_{uuid.uuid4().hex[:8]}'
        result = await repo.update_project_description(new_desc, test_project.project_id)
        assert result is True
        updated = await repo.get_project_by_id(test_project.project_id)
        assert updated.project_description == new_desc

    @pytest.mark.asyncio
    async def test_update_project_description_project_not_found(self, db_session: AsyncSession):
        repo = ProjectRepository(db_session)
        result = await repo.update_project_description('test', 99999)
        assert result is False

    @pytest.mark.asyncio
    async def test_update_project_name_success(self, db_session: AsyncSession, test_project):
        repo = ProjectRepository(db_session)
        new_name = f'Updated_name_{uuid.uuid4().hex[:8]}'
        result = await repo.update_project_name(new_name, test_project.project_id)
        assert result is True
        updated = await repo.get_project_by_id(test_project.project_id)
        assert updated.project_name == new_name

    @pytest.mark.asyncio
    async def test_update_project_name_project_not_found(self, db_session: AsyncSession):
        repo = ProjectRepository(db_session)
        result = await repo.update_project_name('test', 99999)
        assert result is False

    @pytest.mark.asyncio
    async def test_update_user_role_success(self, db_session: AsyncSession, test_project_with_member, test_users):
        repo = ProjectRepository(db_session)
        project = test_project_with_member['project']
        member = test_users['member']
        result = await repo.update_user_role(project.project_id, member.user_id, 'admin')
        assert result is True
        role = await repo.get_user_role_in_project(project.project_id, member.user_id)
        assert role == 'admin'
        result = await repo.update_user_role(project.project_id, member.user_id, 'member')
        assert result is True
        role = await repo.get_user_role_in_project(project.project_id, member.user_id)
        assert role == 'member'

    @pytest.mark.asyncio
    async def test_update_user_role_user_not_in_project(self, db_session: AsyncSession, test_project, test_users):
        repo = ProjectRepository(db_session)
        outsider = test_users['outsider']
        result = await repo.update_user_role(test_project.project_id, outsider.user_id, 'member')
        assert result is False

    @pytest.mark.asyncio
    async def test_update_user_role_invalid_role(self, db_session: AsyncSession, test_project_with_member, test_users):
        repo = ProjectRepository(db_session)
        project = test_project_with_member['project']
        member = test_users['member']
        with pytest.raises(DataError):
            await repo.update_user_role(project.project_id, member.user_id, 'superadmin')

    @pytest.mark.asyncio
    async def test_delete_project_member_success(self, db_session: AsyncSession, test_project_with_member, test_users):
        repo = ProjectRepository(db_session)
        project = test_project_with_member['project']
        member = test_users['member']
        result = await repo.delete_project_member(project.project_id, member.user_id)
        assert result is True
        in_project = await repo.is_user_in_project(project.project_id, member.user_id)
        assert in_project is False

    @pytest.mark.asyncio
    async def test_delete_project_member_not_found(self, db_session: AsyncSession, test_project, test_users):
        repo = ProjectRepository(db_session)
        outsider = test_users['outsider']
        result = await repo.delete_project_member(test_project.project_id, outsider.user_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_project_success(self, db_session: AsyncSession, test_project):
        repo = ProjectRepository(db_session)
        project_id = test_project.project_id
        result = await repo.delete_project(project_id)
        assert result is True
        project = await repo.get_project_by_id(project_id)
        assert project is None
        members = await db_session.execute(
            select(ProjectMemberModel).where(ProjectMemberModel.project_id == project_id)
        )
        assert len(members.scalars().all()) == 0
        tasks = await db_session.execute(
            select(TaskModel).where(TaskModel.project_id == project_id)
        )
        assert len(tasks.scalars().all()) == 0
        invitations = await db_session.execute(
            select(ProjectInvitationModel).where(ProjectInvitationModel.project_id == project_id)
        )
        assert len(invitations.scalars().all()) == 0

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, db_session: AsyncSession):
        repo = ProjectRepository(db_session)
        result = await repo.delete_project(99999)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_project_cascades(self, db_session: AsyncSession, test_project, test_users):
        repo = ProjectRepository(db_session)
        project = test_project
        task_repo = TaskRepository(db_session)
        task_create = TaskCreate(title='test task')
        task = await task_repo.create_task(project.project_id, task_create)
        inv_repo = ProjectInvitationRepository(db_session)
        await inv_repo.create_invitation(
            project_id=project.project_id,
            inviter_id=test_users['admin'].user_id,
            invitee_id=test_users['outsider'].user_id,
            message='test'
        )
        result = await repo.delete_project(project.project_id)
        assert result is True
        task_exists = await task_repo.get_task_by_id(task.task_id)
        assert task_exists is None
        inv_list = await inv_repo.get_invitation_for_project(project.project_id)
        assert inv_list == []

    @pytest.mark.asyncio
    async def test_get_number_admins_success(self, db_session: AsyncSession, test_project, test_users):
        repo = ProjectRepository(db_session)
        count = await repo.get_number_admins(test_project.project_id)
        assert count == 1
        member = test_users['member']
        await repo.add_user(test_project.project_id, member.user_id)
        await repo.update_user_role(test_project.project_id, member.user_id, 'admin')
        count = await repo.get_number_admins(test_project.project_id)
        assert count == 2

    @pytest.mark.asyncio
    async def test_get_number_admins_no_admins(self, db_session: AsyncSession, test_project):
        repo = ProjectRepository(db_session)
        await db_session.execute(
            delete(ProjectMemberModel).where(
                ProjectMemberModel.project_id == test_project.project_id,
                ProjectMemberModel.role_project == 'admin'
            )
        )
        await db_session.commit()
        count = await repo.get_number_admins(test_project.project_id)
        assert count == 0