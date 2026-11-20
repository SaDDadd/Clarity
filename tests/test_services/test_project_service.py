import pytest
import uuid
from core.uow import UnitOfWork
from core.exceptions import (
    NotFoundException, PermissionDeniedException, InvalidInvitationStateException,
    ConflictException, LastAdminDeletionException
)
from services.project_service import (
    create_project, add_user, get_admin_projects, checking_rights_project,
    get_project_info, get_user_projects, update_project, delete_project, delete_project_user
)
from schemas.project import ProjectCreate, ProjectUpdate, ProjectMemberCheck
from repositories.project_repository import ProjectRepository

class TestProjectService:

    @pytest.mark.asyncio
    async def test_create_project_success(self, uow: UnitOfWork, test_users):
        admin = test_users['admin']
        project_data = ProjectCreate(
            project_name=f'New Project {uuid.uuid4().hex[:8]}',
            project_description='Description'
        )
        result = await create_project(uow, project_data, admin.user_id)
        assert result['project_name'] == project_data.project_name
        assert result['admin_id'] == admin.user_id


    @pytest.mark.asyncio
    async def test_add_user_success(self, uow: UnitOfWork, test_project, test_users):
        project = test_project
        admin = test_users['admin']
        outsider = test_users['outsider']
        result = await add_user(uow, project.project_id, admin.user_id, outsider.user_id)
        assert result == {'message': 'Пользователь добавлен в проект!'}
        repo = ProjectRepository(uow)
        assert await repo.is_user_in_project(project.project_id, outsider.user_id) is True


    @pytest.mark.asyncio
    async def test_add_user_project_not_found(self, uow: UnitOfWork, test_users):
        admin = test_users['admin']
        with pytest.raises(NotFoundException) as exc:
            await add_user(uow, 99999, admin.user_id, admin.user_id)
        assert exc.value.detail == 'Проект не найден!'


    @pytest.mark.asyncio
    async def test_add_user_not_admin(self, uow: UnitOfWork, test_project, test_users):
        project = test_project
        member = test_users['member']
        repo = ProjectRepository(uow)
        await repo.add_user(project.project_id, member.user_id)
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await add_user(uow, project.project_id, member.user_id, outsider.user_id)
        assert exc.value.detail == 'Нельзя добавить пользователя: вы не админ проекта!'


    @pytest.mark.asyncio
    async def test_add_user_self(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        with pytest.raises(InvalidInvitationStateException) as exc:
            await add_user(uow, test_project.project_id, admin.user_id, admin.user_id)
        assert exc.value.detail == 'Нельзя добавить самого себя!'


    @pytest.mark.asyncio
    async def test_add_user_not_exist(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        with pytest.raises(NotFoundException) as exc:
            await add_user(uow, test_project.project_id, admin.user_id, 99999)
        assert exc.value.detail == 'Нельзя добавить пользователя: его не существует!'


    @pytest.mark.asyncio
    async def test_add_user_already_in_project(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        admin = test_users['admin']
        member = test_users['member']
        with pytest.raises(ConflictException) as exc:
            await add_user(uow, project.project_id, admin.user_id, member.user_id)
        assert exc.value.detail == 'Пользователь уже состоит в проекте'


    @pytest.mark.asyncio
    async def test_get_admin_projects_success(self, uow: UnitOfWork, test_users, test_project):
        admin = test_users['admin']
        projects = await get_admin_projects(uow, admin.user_id)
        assert isinstance(projects, list)
        assert len(projects) >= 1
        assert any(p.project_id == test_project.project_id for p in projects)


    @pytest.mark.asyncio
    async def test_get_admin_projects_empty(self, uow: UnitOfWork, test_users):
        outsider = test_users['outsider']
        projects = await get_admin_projects(uow, outsider.user_id)
        assert projects == []


    @pytest.mark.asyncio
    async def test_checking_rights_project_success(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        check = ProjectMemberCheck(project_id=project.project_id, user_id=member.user_id)
        role = await checking_rights_project(uow, check)
        assert role == 'member'


    @pytest.mark.asyncio
    async def test_checking_rights_project_not_in_project(self, uow: UnitOfWork, test_project, test_users):
        outsider = test_users['outsider']
        check = ProjectMemberCheck(project_id=test_project.project_id, user_id=outsider.user_id)
        with pytest.raises(PermissionDeniedException) as exc:
            await checking_rights_project(uow, check)
        assert exc.value.detail == 'Пользователь не состоит в проекте!'


    @pytest.mark.asyncio
    async def test_get_project_info_success(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        info = await get_project_info(uow, project.project_id, member.user_id)
        assert info['project_id'] == project.project_id
        assert 'members' in info
        assert len(info['members']) >= 2


    @pytest.mark.asyncio
    async def test_get_project_info_project_not_found(self, uow: UnitOfWork, test_users):
        admin = test_users['admin']
        with pytest.raises(NotFoundException) as exc:
            await get_project_info(uow, 99999, admin.user_id)
        assert exc.value.detail == 'Проект не найден!'


    @pytest.mark.asyncio
    async def test_get_project_info_user_not_in_project(self, uow: UnitOfWork, test_project, test_users):
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await get_project_info(uow, test_project.project_id, outsider.user_id)
        assert exc.value.detail == 'Пользователь не является участником проекта!'


    @pytest.mark.asyncio
    async def test_get_user_projects_success(self, uow: UnitOfWork, test_users, test_project_with_member):
        admin = test_users['admin']
        projects = await get_user_projects(uow, admin.user_id)
        assert isinstance(projects, list)
        assert len(projects) >= 1
        assert projects[0].project_id == test_project_with_member['project'].project_id


    @pytest.mark.asyncio
    async def test_update_project_success_name(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        update_data = ProjectUpdate(project_name='Updated Name', project_description=None)
        result = await update_project(uow, test_project.project_id, admin.user_id, update_data)
        assert result == {'message': 'Проект обновлен!'}
        repo = ProjectRepository(uow)
        project = await repo.get_project_by_id(test_project.project_id)
        assert project.project_name == 'Updated Name'


    @pytest.mark.asyncio
    async def test_update_project_success_description(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        update_data = ProjectUpdate(project_name=None, project_description='New Desc')
        result = await update_project(uow, test_project.project_id, admin.user_id, update_data)
        assert result == {'message': 'Проект обновлен!'}
        repo = ProjectRepository(uow)
        project = await repo.get_project_by_id(test_project.project_id)
        assert project.project_description == 'New Desc'


    @pytest.mark.asyncio
    async def test_update_project_success_both(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        update_data = ProjectUpdate(project_name='Both Name', project_description='Both Desc')
        result = await update_project(uow, test_project.project_id, admin.user_id, update_data)
        assert result == {'message': 'Проект обновлен!'}
        repo = ProjectRepository(uow)
        project = await repo.get_project_by_id(test_project.project_id)
        assert project.project_name == 'Both Name'
        assert project.project_description == 'Both Desc'


    @pytest.mark.asyncio
    async def test_update_project_no_changes(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        update_data = ProjectUpdate(project_name=None, project_description=None)
        result = await update_project(uow, test_project.project_id, admin.user_id, update_data)
        assert result == {'message': 'Ничего не изменилось!'}


    @pytest.mark.asyncio
    async def test_update_project_not_found(self, uow: UnitOfWork, test_users):
        admin = test_users['admin']
        update_data = ProjectUpdate(project_name='new')
        with pytest.raises(NotFoundException) as exc:
            await update_project(uow, 99999, admin.user_id, update_data)
        assert exc.value.detail == 'Проект не найден!'


    @pytest.mark.asyncio
    async def test_update_project_user_not_in_project(self, uow: UnitOfWork, test_project, test_users):
        outsider = test_users['outsider']
        update_data = ProjectUpdate(project_name='new')
        with pytest.raises(PermissionDeniedException) as exc:
            await update_project(uow, test_project.project_id, outsider.user_id, update_data)
        assert exc.value.detail == 'Пользователь не является участником проекта!'


    @pytest.mark.asyncio
    async def test_update_project_not_admin(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        update_data = ProjectUpdate(project_name='new')
        with pytest.raises(PermissionDeniedException) as exc:
            await update_project(uow, project.project_id, member.user_id, update_data)
        assert exc.value.detail == 'Пользователь не может менять проект, он не админ!'


    @pytest.mark.asyncio
    async def test_delete_project_success(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        result = await delete_project(uow, test_project.project_id, admin.user_id)
        assert result == {'message': 'Проект успешно удален!'}


    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, uow: UnitOfWork, test_users):
        admin = test_users['admin']
        with pytest.raises(NotFoundException) as exc:
            await delete_project(uow, 99999, admin.user_id)
        assert exc.value.detail == 'Проект не найден!'


    @pytest.mark.asyncio
    async def test_delete_project_not_admin(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        with pytest.raises(PermissionDeniedException) as exc:
            await delete_project(uow, project.project_id, member.user_id)
        assert exc.value.detail == 'Вы не админ этого проекта!'


    @pytest.mark.asyncio
    async def test_delete_project_user_success(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        admin = test_users['admin']
        member = test_users['member']
        result = await delete_project_user(uow, project.project_id, admin.user_id, member.user_id)
        assert result == {'message': 'Пользователь удален из проекта!'}
        repo = ProjectRepository(uow)
        assert await repo.is_user_in_project(project.project_id, member.user_id) is False


    @pytest.mark.asyncio
    async def test_delete_project_user_not_exist(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        with pytest.raises(NotFoundException) as exc:
            await delete_project_user(uow, test_project.project_id, admin.user_id, 99999)
        assert exc.value.detail == 'Нельзя удалить пользователя: его не существует!'


    @pytest.mark.asyncio
    async def test_delete_project_user_not_admin(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await delete_project_user(uow, project.project_id, member.user_id, outsider.user_id)
        assert exc.value.detail == 'Нельзя удалить пользователя: вы не админ проекта!'


    @pytest.mark.asyncio
    async def test_delete_project_user_not_in_project(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        outsider = test_users['outsider']
        with pytest.raises(ConflictException) as exc:
            await delete_project_user(uow, test_project.project_id, admin.user_id, outsider.user_id)
        assert exc.value.detail == 'Пользователь не состоит в проекте!'


    @pytest.mark.asyncio
    async def test_delete_project_user_last_admin(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        with pytest.raises(LastAdminDeletionException) as exc:
            await delete_project_user(uow, test_project.project_id, admin.user_id, admin.user_id)
        assert exc.value.detail == 'Нельзя удалить единственного администратора проекта!'


    @pytest.mark.asyncio
    async def test_delete_project_user_admin_not_last(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        member = test_users['member']
        await uow.project.add_user(test_project.project_id, member.user_id)
        await uow.project.update_user_role(test_project.project_id, member.user_id, 'admin')
        result = await delete_project_user(uow, test_project.project_id, admin.user_id, member.user_id)
        assert result == {'message': 'Пользователь удален из проекта!'}
        assert await uow.project.is_user_in_project(test_project.project_id, admin.user_id) is True
        assert await uow.project.is_user_in_project(test_project.project_id, member.user_id) is False
        project = await uow.project.get_project_by_id(test_project.project_id)
        assert project.admin_id == admin.user_id