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