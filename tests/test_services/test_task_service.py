import pytest
import uuid
from core.uow import UnitOfWork
from core.exceptions import PermissionDeniedException, NotFoundException
from services.task_service import (
    create_task, get_project_tasks, get_task_info,
    update_task, change_status, delete_task
)
from schemas.task import TaskCreate, TaskUpdate
from schemas.common import TaskStatus


class TestTaskService:
    @pytest.mark.asyncio
    async def test_create_task_user_not_in_project(self, uow: UnitOfWork, test_project, test_users):
        outsider = test_users['outsider']
        task_data = TaskCreate(title='Test')
        with pytest.raises(PermissionDeniedException) as exc:
            await create_task(uow, test_project.project_id, outsider.user_id, task_data)
        assert exc.value.detail == 'Текущего пользователя нет в проекте!'


    @pytest.mark.asyncio
    async def test_get_project_tasks_user_not_in_project(self, uow: UnitOfWork, test_project, test_users):
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await get_project_tasks(uow, test_project.project_id, outsider.user_id)
        assert exc.value.detail == 'Пользователя нет в проекте!'


    @pytest.mark.asyncio
    async def test_get_task_info_success(self, uow: UnitOfWork, test_project_with_member, test_task, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        result = await get_task_info(uow, project.project_id, member.user_id, test_task.task_id)
        assert result['task_id'] == test_task.task_id


    @pytest.mark.asyncio
    async def test_get_task_info_project_not_exists(self, uow: UnitOfWork, test_task, test_users):
        outsider = test_users['outsider']
        with pytest.raises(NotFoundException) as exc:
            await get_task_info(uow, 99999, outsider.user_id, test_task.task_id)
        assert exc.value.detail == 'Данного проекта не существует!'


    @pytest.mark.asyncio
    async def test_get_task_info_user_not_in_project(self, uow: UnitOfWork, test_project, test_task, test_users):
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await get_task_info(uow, test_project.project_id, outsider.user_id, test_task.task_id)
        assert exc.value.detail == 'Текущего пользователя нет в проекте!'


    @pytest.mark.asyncio
    async def test_get_task_info_task_not_in_project(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        second_project = await uow.project.create_project_with_admin(
            name=f'Second_{uuid.uuid4().hex[:8]}',
            description=None,
            admin_id=test_users['admin'].user_id
        )
        task_data = TaskCreate(title='Task in second')
        task_second = await uow.task.create_task(second_project.project_id, task_data)
        with pytest.raises(NotFoundException) as exc:
            await get_task_info(uow, project.project_id, member.user_id, task_second.task_id)
        assert exc.value.detail == 'Задачи нет в проекте!'


    @pytest.mark.asyncio
    async def test_get_task_info_task_not_found(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        with pytest.raises(NotFoundException) as exc:
            await get_task_info(uow, project.project_id, member.user_id, 99999)
        assert exc.value.detail == 'Задачи нет в проекте!'


    @pytest.mark.asyncio
    async def test_update_task_no_data(self, uow: UnitOfWork, test_project_with_member, test_task, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        update_data = TaskUpdate()
        result = await update_task(uow, project.project_id, test_task.task_id, member.user_id, update_data)
        assert result == {'message': 'Нет данных для обновления!'}


    @pytest.mark.asyncio
    async def test_update_task_not_in_project(self, uow: UnitOfWork, test_project_with_member, test_task, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        second_project = await uow.project.create_project_with_admin(
            name=f'Second_{uuid.uuid4().hex[:8]}',
            description=None,
            admin_id=test_users['admin'].user_id
        )
        task_second = await uow.task.create_task(second_project.project_id, TaskCreate(title='Second Task'))
        with pytest.raises(NotFoundException) as exc:
            await update_task(uow, project.project_id, task_second.task_id, member.user_id, TaskUpdate(title='new'))
        assert exc.value.detail == 'Задачи нет в проекте!'


    @pytest.mark.asyncio
    async def test_update_task_user_not_in_project(self, uow: UnitOfWork, test_project, test_task, test_users):
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await update_task(uow, test_project.project_id, test_task.task_id, outsider.user_id, TaskUpdate(title='new'))
        assert exc.value.detail == 'Текущего пользователя нет в проекте!'


    @pytest.mark.asyncio
    async def test_update_task_assigned_to_not_in_project(self, uow: UnitOfWork, test_project_with_member, test_task, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        outsider = test_users['outsider']
        update_data = TaskUpdate(assigned_to=outsider.user_id)
        with pytest.raises(PermissionDeniedException) as exc:
            await update_task(uow, project.project_id, test_task.task_id, member.user_id, update_data)
        assert exc.value.detail == 'Задачу могут обновлять только админ, куратор или назначенный исполнитель!'


    @pytest.mark.asyncio
    async def test_change_status_project_not_exists(self, uow: UnitOfWork, test_task, test_users):
        outsider = test_users['outsider']
        with pytest.raises(NotFoundException) as exc:
            await change_status(uow, 99999, test_task.task_id, outsider.user_id, TaskStatus.IN_PROGRESS)
        assert exc.value.detail == 'Данного проекта не существует!'


    @pytest.mark.asyncio
    async def test_change_status_user_not_in_project(self, uow: UnitOfWork, test_project, test_task, test_users):
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await change_status(uow, test_project.project_id, test_task.task_id, outsider.user_id, TaskStatus.IN_PROGRESS)
        assert exc.value.detail == 'Текущего пользователя нет в проекте!'


    @pytest.mark.asyncio
    async def test_change_status_task_not_in_project(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        with pytest.raises(NotFoundException) as exc:
            await change_status(uow, project.project_id, 99999, member.user_id, TaskStatus.IN_PROGRESS)
        assert exc.value.detail == 'Задачи нет в проекте!'


    @pytest.mark.asyncio
    async def test_delete_task_project_not_exists(self, uow: UnitOfWork, test_task, test_users):
        outsider = test_users['outsider']
        with pytest.raises(NotFoundException) as exc:
            await delete_task(uow, 99999, test_task.task_id, outsider.user_id)
        assert exc.value.detail == 'Данного проекта не существует!'


    @pytest.mark.asyncio
    async def test_delete_task_user_not_in_project(self, uow: UnitOfWork, test_project, test_task, test_users):
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await delete_task(uow, test_project.project_id, test_task.task_id, outsider.user_id)
        assert exc.value.detail == 'Текущего пользователя нет в проекте!'


    @pytest.mark.asyncio
    async def test_delete_task_task_not_in_project(self, uow: UnitOfWork, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        with pytest.raises(NotFoundException) as exc:
            await delete_task(uow, project.project_id, 99999, member.user_id)
        assert exc.value.detail == 'Задачи нет в проекте!'