import pytest
import uuid
from core.uow import UnitOfWork
from sqlalchemy.exc import IntegrityError, DataError
from models.project import ProjectModel
from schemas.task import TaskCreate


class TestProjectRepository:
    @pytest.mark.asyncio
    async def test_create_project_with_admin_success(self, uow: UnitOfWork, test_users):
        """Проверяет успешное создание проекта с администратором."""
        name = f'Test_project_{uuid.uuid4().hex[:8]}'
        response = await uow.project.create_project_with_admin(
            name=name,
            description='Test_description',
            admin_id=test_users['admin'].user_id
        )
        get_member = await uow.project.is_user_in_project(response.project_id, test_users['admin'].user_id)
        assert isinstance(response, ProjectModel)
        assert response.project_name == name
        assert response.project_description == 'Test_description'
        assert response.admin_id == test_users['admin'].user_id
        assert get_member is True


    @pytest.mark.asyncio
    async def test_create_project_with_admin_missing_fields(self, uow: UnitOfWork, test_users):
        """Проверяет, что при отсутствии обязательного поля выбрасывается IntegrityError."""
        with pytest.raises(IntegrityError):
            await uow.project.create_project_with_admin(
                name=None,
                description='Test_description',
                admin_id=test_users['admin'].user_id
            )


    @pytest.mark.asyncio
    async def test_add_user_success(self, uow: UnitOfWork, test_users, test_project):
        """Проверяет успешное добавление пользователя в проект."""
        response = await uow.project.add_user(test_project.project_id, test_users['member'].user_id)
        get_member = await uow.project.is_user_in_project(test_project.project_id, test_users['member'].user_id)
        assert response is True
        assert get_member is True


    @pytest.mark.asyncio
    async def test_add_user_already_in_project(self, uow: UnitOfWork, test_users, test_project_with_member):
        """Проверяет, что повторное добавление участника вызывает IntegrityError."""
        with pytest.raises(IntegrityError):
            await uow.project.add_user(
                test_project_with_member['project'].project_id,
                test_users['member'].user_id
            )


    @pytest.mark.asyncio
    async def test_add_user_non_existent_user(self, uow: UnitOfWork, test_project):
        """Проверяет, что добавление несуществующего пользователя вызывает IntegrityError."""
        with pytest.raises(IntegrityError):
            await uow.project.add_user(test_project.project_id, 99999)


    @pytest.mark.asyncio
    async def test_is_user_in_project_true(self, uow: UnitOfWork, test_project_with_member, test_users):
        """Проверяет, что для участника проекта возвращается True."""
        project = test_project_with_member['project']
        member = test_users['member']
        result = await uow.project.is_user_in_project(project.project_id, member.user_id)
        assert result is True


    @pytest.mark.asyncio
    async def test_is_user_in_project_false(self, uow: UnitOfWork, test_project, test_users):
        """Проверяет, что для неучастника возвращается False."""
        outsider = test_users['outsider']
        result = await uow.project.is_user_in_project(test_project.project_id, outsider.user_id)
        assert result is False


    @pytest.mark.asyncio
    async def test_is_user_in_project_project_not_found(self, uow: UnitOfWork, test_users):
        """Проверяет, что для несуществующего проекта возвращается False."""
        admin = test_users['admin']
        result = await uow.project.is_user_in_project(99999, admin.user_id)
        assert result is False


    @pytest.mark.asyncio
    async def test_is_user_in_project_user_not_found(self, uow: UnitOfWork, test_project):
        """Проверяет, что для несуществующего пользователя возвращается False."""
        result = await uow.project.is_user_in_project(test_project.project_id, 99999)
        assert result is False


    @pytest.mark.asyncio
    async def test_get_user_role_in_project_admin(self, uow: UnitOfWork, test_project, test_users):
        """Проверяет, что для администратора возвращается роль 'admin'."""
        admin = test_users['admin']
        role = await uow.project.get_user_role_in_project(test_project.project_id, admin.user_id)
        assert role == 'admin'


    @pytest.mark.asyncio
    async def test_get_user_role_in_project_member(self, uow: UnitOfWork, test_project_with_member, test_users):
        """Проверяет, что для участника возвращается роль 'member'."""
        project = test_project_with_member['project']
        member = test_users['member']
        role = await uow.project.get_user_role_in_project(project.project_id, member.user_id)
        assert role == 'member'


    @pytest.mark.asyncio
    async def test_get_user_role_in_project_not_member(self, uow: UnitOfWork, test_project, test_users):
        """Проверяет, что для неучастника возвращается None."""
        outsider = test_users['outsider']
        role = await uow.project.get_user_role_in_project(test_project.project_id, outsider.user_id)
        assert role is None


    @pytest.mark.asyncio
    async def test_get_project_all_info_success(self, uow: UnitOfWork, test_project_with_member, test_users):
        """Проверяет получение полной информации о проекте (проект + участники)."""
        project = test_project_with_member['project']
        info = await uow.project.get_project_all_info(project.project_id)
        assert isinstance(info, dict)
        assert 'project' in info
        assert 'members' in info
        assert info['project'].project_id == project.project_id
        assert len(info['members']) >= 2
        member_ids = [m.user_id for m in info['members']]
        assert test_users['admin'].user_id in member_ids
        assert test_users['member'].user_id in member_ids


    @pytest.mark.asyncio
    async def test_get_project_all_info_project_not_found(self, uow: UnitOfWork):
        """Проверяет, что для несуществующего проекта возвращается словарь с None и пустым списком."""
        info = await uow.project.get_project_all_info(99999)
        assert info['project'] is None
        assert info['members'] == []


    @pytest.mark.asyncio
    async def test_reassign_admin_project_not_found(self, uow: UnitOfWork, test_users):
        """Проверяет, что при несуществующем проекте возвращается False."""
        result = await uow.project.reassign_admin(99999, test_users['admin'].user_id)
        assert result is False


    @pytest.mark.asyncio
    async def test_is_user_admin_true(self, uow: UnitOfWork, test_project, test_users):
        """Проверяет, что для администратора возвращается True."""
        admin = test_users['admin']
        result = await uow.project.is_user_admin(test_project.project_id, admin.user_id)
        assert result is True


    @pytest.mark.asyncio
    async def test_is_user_admin_false_for_member(self, uow: UnitOfWork, test_project_with_member, test_users):
        """Проверяет, что для обычного участника возвращается False."""
        project = test_project_with_member['project']
        member = test_users['member']
        result = await uow.project.is_user_admin(project.project_id, member.user_id)
        assert result is False


    @pytest.mark.asyncio
    async def test_is_user_admin_false_for_non_member(self, uow: UnitOfWork, test_project, test_users):
        """Проверяет, что для неучастника возвращается False."""
        outsider = test_users['outsider']
        result = await uow.project.is_user_admin(test_project.project_id, outsider.user_id)
        assert result is False


    @pytest.mark.asyncio
    async def test_get_user_projects_empty(self, uow: UnitOfWork, test_users):
        """Проверяет, что для пользователя без проектов возвращается пустой список."""
        outsider = test_users['outsider']
        projects = await uow.project.get_user_projects(outsider.user_id)
        assert isinstance(projects, list)
        assert len(projects) == 0


    @pytest.mark.asyncio
    async def test_update_project_description_success(self, uow: UnitOfWork, test_project):
        """Проверяет успешное обновление описания проекта."""
        new_desc = f'Updated_description_{uuid.uuid4().hex[:8]}'
        result = await uow.project.update_project_description(new_desc, test_project.project_id)
        assert result is True
        updated = await uow.project.get_project_by_id(test_project.project_id)
        assert updated.project_description == new_desc


    @pytest.mark.asyncio
    async def test_update_project_description_project_not_found(self, uow: UnitOfWork):
        """Проверяет, что при несуществующем проекте возвращается False."""
        result = await uow.project.update_project_description('test', 99999)
        assert result is False


    @pytest.mark.asyncio
    async def test_update_project_name_success(self, uow: UnitOfWork, test_project):
        """Проверяет успешное обновление названия проекта."""
        new_name = f'Updated_name_{uuid.uuid4().hex[:8]}'
        result = await uow.project.update_project_name(new_name, test_project.project_id)
        assert result is True
        updated = await uow.project.get_project_by_id(test_project.project_id)
        assert updated.project_name == new_name


    @pytest.mark.asyncio
    async def test_update_project_name_project_not_found(self, uow: UnitOfWork):
        """Проверяет, что при несуществующем проекте возвращается False."""
        result = await uow.project.update_project_name('test', 99999)
        assert result is False


    @pytest.mark.asyncio
    async def test_update_user_role_success(self, uow: UnitOfWork, test_project_with_member, test_users):
        """Проверяет успешное изменение роли пользователя в проекте."""
        project = test_project_with_member['project']
        member = test_users['member']
        result = await uow.project.update_user_role(project.project_id, member.user_id, 'admin')
        assert result is True
        role = await uow.project.get_user_role_in_project(project.project_id, member.user_id)
        assert role == 'admin'
        result = await uow.project.update_user_role(project.project_id, member.user_id, 'member')
        assert result is True
        role = await uow.project.get_user_role_in_project(project.project_id, member.user_id)
        assert role == 'member'


    @pytest.mark.asyncio
    async def test_update_user_role_user_not_in_project(self, uow: UnitOfWork, test_project, test_users):
        """Проверяет, что при попытке изменить роль неучастника возвращается False."""
        outsider = test_users['outsider']
        result = await uow.project.update_user_role(test_project.project_id, outsider.user_id, 'member')
        assert result is False


    @pytest.mark.asyncio
    async def test_update_user_role_invalid_role(self, uow: UnitOfWork, test_project_with_member, test_users):
        """Проверяет, что при передаче недопустимой роли выбрасывается DataError."""
        project = test_project_with_member['project']
        member = test_users['member']
        with pytest.raises(DataError):
            await uow.project.update_user_role(project.project_id, member.user_id, 'superadmin')


    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, uow: UnitOfWork):
        """Проверяет, что при удалении несуществующего проекта возвращается False."""
        result = await uow.project.delete_project(99999)
        assert result is False


    @pytest.mark.asyncio
    async def test_delete_project_cascades(self, uow: UnitOfWork, test_project, test_users):
        """Проверяет каскадное удаление: задачи и приглашения удаляются вместе с проектом."""
        project = test_project
        task_create = TaskCreate(title='test task')
        task = await uow.task.create_task(project.project_id, task_create)
        await uow.invitation.create_invitation(
            project_id=project.project_id,
            inviter_id=test_users['admin'].user_id,
            invitee_id=test_users['outsider'].user_id,
            message='test'
        )
        result = await uow.project.delete_project(project.project_id)
        assert result is True
        task_exists = await uow.task.get_task_by_id(task.task_id)
        assert task_exists is None
        inv_list = await uow.invitation.get_invitation_for_project(project.project_id)
        assert inv_list == []


    @pytest.mark.asyncio
    async def test_delete_user_success(self, uow: UnitOfWork, test_project_with_member, test_users):
        """Проверяет успешное удаление пользователя из проекта (метод delete_user)."""
        project = test_project_with_member['project']
        member = test_users['member']
        assert await uow.project.is_user_in_project(project.project_id, member.user_id) is True
        result = await uow.project.delete_user_from_project(project.project_id, member.user_id)
        assert result is True
        assert await uow.project.is_user_in_project(project.project_id, member.user_id) is False


    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, uow: UnitOfWork, test_project, test_users):
        """Проверяет, что при удалении несуществующего пользователя возвращается False."""
        outsider = test_users['outsider']
        result = await uow.project.delete_user_from_project(test_project.project_id, outsider.user_id)
        assert result is False


    @pytest.mark.asyncio
    async def test_get_project_by_id_success(self, uow: UnitOfWork, test_project):
        """Проверяет получение проекта по существующему ID."""
        project = await uow.project.get_project_by_id(test_project.project_id)
        assert project is not None
        assert project.project_id == test_project.project_id


    @pytest.mark.asyncio
    async def test_get_project_by_id_not_found(self, uow: UnitOfWork):
        """Проверяет, что при несуществующем ID возвращается None."""
        project = await uow.project.get_project_by_id(99999)
        assert project is None