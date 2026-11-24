import pytest
import uuid
from core.uow import UnitOfWork
from fastapi_pagination import Page
from core.exceptions import (
    NotFoundException, PermissionDeniedException, InvalidInvitationStateException,
    ConflictException
)
from services.project_service import (
    create_project, add_user, get_admin_projects, checking_rights_project,
    get_project_info, get_user_projects, update_project, delete_project, delete_project_user
)
from schemas.project import ProjectCreate, ProjectUpdate, ProjectMemberCheck


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
        assert await uow.project.is_user_in_project(project.project_id, outsider.user_id) is True


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
        await uow.project.add_user(project.project_id, member.user_id)
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await add_user(uow, project.project_id, member.user_id, outsider.user_id)
        assert exc.value.detail == 'Нельзя добавить пользователя: вы не админ и не куратор проекта!'


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
    async def test_get_admin_projects_empty(self, uow: UnitOfWork, test_users):
        outsider = test_users['outsider']
        projects = await get_admin_projects(uow, outsider.user_id)
        assert isinstance(projects, Page)


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
        with pytest.raises(NotFoundException) as exc:
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
    async def test_update_project_success_name(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        update_data = ProjectUpdate(project_name='Updated Name', project_description=None)
        result = await update_project(uow, test_project.project_id, admin.user_id, update_data)
        assert result == {'message': 'Проект обновлен!'}
        project = await uow.project.get_project_by_id(test_project.project_id)
        assert project.project_name == 'Updated Name'


    @pytest.mark.asyncio
    async def test_update_project_success_both(self, uow: UnitOfWork, test_project, test_users):
        admin = test_users['admin']
        update_data = ProjectUpdate(project_name='Both Name', project_description='Both Desc')
        result = await update_project(uow, test_project.project_id, admin.user_id, update_data)
        assert result == {'message': 'Проект обновлен!'}
        project = await uow.project.get_project_by_id(test_project.project_id)
        assert project.project_name == 'Both Name'
        assert project.project_description == 'Both Desc'


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
        assert exc.value.detail == 'Пользователь не может менять проект, он не админ/куратор!'


    @pytest.mark.asyncio
    async def test_update_project_not_admin(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        update_data = ProjectUpdate(project_name='new')
        with pytest.raises(PermissionDeniedException) as exc:
            await update_project(uow, project.project_id, member.user_id, update_data)
        assert exc.value.detail == 'Пользователь не может менять проект, он не админ/куратор!'


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
        assert await uow.project.is_user_in_project(project.project_id, member.user_id) is False


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
        assert exc.value.detail == 'Нельзя удалить пользователя: вы не админ/куратор проекта!'


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
        with pytest.raises(PermissionDeniedException) as exc:
            await delete_project_user(uow, test_project.project_id, admin.user_id, admin.user_id)
        assert exc.value.detail == 'Нельзя удалить самого себя!'