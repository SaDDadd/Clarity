import pytest 
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.project_repository import ProjectRepository
from models.project_members import ProjectMemberModel
from models.project import ProjectModel
from sqlalchemy.exc import IntegrityError

class TestProjectRepository:
    @pytest.mark.asyncio
    async def test_create_project_with_admin_success(self, db_session: AsyncSession, test_users):
        repo = ProjectRepository(db_session)
        name = f'Test_project{uuid.uuid4().hex[:8]}'
        response = await repo.create_project_with_admin(name=name, description='Test_description', \
                                                        admin_id=test_users['admin'].user_id)
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
            await repo.create_project_with_admin(name=None, description='Test_description', \
                                                 admin_id=test_users['admin'].user_id)

    @pytest.mark.asyncio
    async def test_add_user_success(self, db_session, test_users, test_project):
        repo = ProjectRepository(db_session)
        response = await repo.add_user(test_project.project_id, test_users['member'].user_id)
        get_member = await repo.is_user_in_project(test_project.project_id, test_users['member'].user_id)
        assert response is True
        assert get_member is True

    @pytest.mark.asyncio
    async def test_add_user_already_in_project(self, db_session, test_users, test_project_with_member):
        repo = ProjectRepository(db_session)
        with pytest.raises(IntegrityError):
            await repo.add_user(test_project_with_member['project'].project_id, test_users['member'].user_id)

    @pytest.mark.asyncio
    async def test_add_user_non_existent_user(self, db_session, test_project):
        repo = ProjectRepository(db_session)
        with pytest.raises(IntegrityError):
            await repo.add_user(test_project.project_id, 99999)

    @pytest.mark.asyncio
    async def test_get_projects_by_admin_success(self, db_session):

    @pytest.mark.asyncio
    async def test_get_projects_by_admin_empty():

    @pytest.mark.asyncio
    async def test_get_projects_by_admin_user_not_found():

    @pytest.mark.asyncio
    async def test_is_user_in_project_true():

    @pytest.mark.asyncio
    async def test_is_user_in_project_false():

    @pytest.mark.asyncio
    async def test_is_user_in_project_project_not_found():

    @pytest.mark.asyncio
    async def test_is_user_in_project_user_not_found():

    @pytest.mark.asyncio
    async def test_get_user_role_in_project_admin():

    @pytest.mark.asyncio
    async def test_get_user_role_in_project_member():

    @pytest.mark.asyncio
    async def test_get_user_role_in_project_not_member():

    @pytest.mark.asyncio
    async def test_get_project_all_info_success():

    @pytest.mark.asyncio
    async def test_get_project_all_info_project_not_found():

    @pytest.mark.asyncio
    async def test_reassign_admin_success():

    @pytest.mark.asyncio
    async def test_reassign_admin_project_not_found():

    @pytest.mark.asyncio
    async def test_reassign_admin_new_admin_not_in_project():

    @pytest.mark.asyncio
    async def test_get_admins_list_success():

    @pytest.mark.asyncio
    async def test_get_admins_list_no_admins():

    @pytest.mark.asyncio
    async def test_is_user_admin_true():

    @pytest.mark.asyncio
    async def test_is_user_admin_false_for_member():

    @pytest.mark.asyncio
    async def test_is_user_admin_false_for_non_member():

    @pytest.mark.asyncio
    async def test_get_user_projects_success():

    @pytest.mark.asyncio
    async def test_get_user_projects_empty():

    @pytest.mark.asyncio
    async def test_update_project_description_success():

    @pytest.mark.asyncio
    async def test_update_project_description_project_not_found():

    @pytest.mark.asyncio
    async def test_update_project_name_success():

    @pytest.mark.asyncio
    async def test_update_project_name_project_not_found():

    @pytest.mark.asyncio
    async def test_update_user_role_success():

    @pytest.mark.asyncio 
    async def test_update_user_role_user_not_in_project():

    @pytest.mark.asyncio 
    async def test_update_user_role_invalid_role():

    @pytest.mark.asyncio 
    async def test_delete_project_member_success():

    @pytest.mark.asyncio 
    async def test_delete_project_member_not_found():

    @pytest.mark.asyncio 
    async def test_delete_project_success():

    @pytest.mark.asyncio
    async def test_delete_project_not_found():

    @pytest.mark.asyncio 
    async def test_delete_project_cascades():

    @pytest.mark.asyncio
    async def test_get_number_admins_success():

    @pytest.mark.asyncio
    async def test_get_number_admins_no_admins():