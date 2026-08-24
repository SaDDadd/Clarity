import pytest
import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from core.exceptions import PermissionDeniedException, InvalidDeadlineException, NotFoundException
from services.task_service import (
    create_task, get_project_tasks, get_task_info, get_tasks_user,
    update_task, change_status, delete_task
)
from schemas.task import TaskCreate, TaskUpdate
from schemas.common import TaskStatus
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository

class TestTaskService:
    @pytest.mark.asyncio
    async def test_create_task_success(self, db_session: AsyncSession, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        task_data = TaskCreate(
            title='Test Task',
            task_description='Desc',
            task_status='pending',
            assigned_to=member.user_id,
            deadline=datetime.date.today() + datetime.timedelta(days=1)
        )
        result = await create_task(db_session, project.project_id, member.user_id, task_data)
        assert result.title == 'Test Task'
        assert result.project_id == project.project_id

    @pytest.mark.asyncio
    async def test_create_task_user_not_in_project(self, db_session: AsyncSession, test_project, test_users):
        outsider = test_users['outsider']
        task_data = TaskCreate(title='Test')
        with pytest.raises(PermissionDeniedException) as exc:
            await create_task(db_session, test_project.project_id, outsider.user_id, task_data)
        assert exc.value.detail == 'Текущего пользователя нет в проекте!'

    @pytest.mark.asyncio
    async def test_create_task_deadline_in_past(self, db_session: AsyncSession, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        task_data = TaskCreate(
            title='Test',
            deadline=datetime.date.today() - datetime.timedelta(days=1)
        )
        with pytest.raises(InvalidDeadlineException) as exc:
            await create_task(db_session, project.project_id, member.user_id, task_data)
        assert exc.value.detail == 'Время дэдлайна не может быть меньше сегодняшнего дня!'

    @pytest.mark.asyncio
    async def test_create_task_assigned_to_not_in_project(self, db_session: AsyncSession, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        outsider = test_users['outsider']
        task_data = TaskCreate(
            title='Test',
            assigned_to=outsider.user_id
        )
        with pytest.raises(PermissionDeniedException) as exc:
            await create_task(db_session, project.project_id, member.user_id, task_data)
        assert exc.value.detail == 'Добавляемого пользователя нет в проекте!'

    @pytest.mark.asyncio
    async def test_get_project_tasks_success(self, db_session: AsyncSession, test_project_with_member, test_task, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        tasks = await get_project_tasks(db_session, project.project_id, member.user_id)
        assert isinstance(tasks, list)
        assert len(tasks) >= 1

    @pytest.mark.asyncio
    async def test_get_project_tasks_user_not_in_project(self, db_session: AsyncSession, test_project, test_users):
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await get_project_tasks(db_session, test_project.project_id, outsider.user_id)
        assert exc.value.detail == 'Пользователя нет в проекте!'

    @pytest.mark.asyncio
    async def test_get_task_info_success(self, db_session: AsyncSession, test_project_with_member, test_task, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        result = await get_task_info(db_session, project.project_id, member.user_id, test_task.task_id)
        assert result.task_id == test_task.task_id

    @pytest.mark.asyncio
    async def test_get_task_info_project_not_exists(self, db_session: AsyncSession, test_task, test_users):
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await get_task_info(db_session, 99999, outsider.user_id, test_task.task_id)
        assert exc.value.detail == 'Данного проекта не существует!'

    @pytest.mark.asyncio
    async def test_get_task_info_user_not_in_project(self, db_session: AsyncSession, test_project, test_task, test_users):
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await get_task_info(db_session, test_project.project_id, outsider.user_id, test_task.task_id)
        assert exc.value.detail == 'Текущего пользователя нет в проекте!'

    @pytest.mark.asyncio
    async def test_get_task_info_task_not_in_project(self, db_session: AsyncSession, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        repo_proj = ProjectRepository(db_session)
        second_project = await repo_proj.create_project_with_admin(
            name=f'Second_{uuid.uuid4().hex[:8]}',
            description=None,
            admin_id=test_users['admin'].user_id
        )
        repo_task = TaskRepository(db_session)
        task_data = TaskCreate(title='Task in second')
        task_second = await repo_task.create_task(second_project.project_id, task_data)
        with pytest.raises(NotFoundException) as exc:
            await get_task_info(db_session, project.project_id, member.user_id, task_second.task_id)
        assert exc.value.detail == 'Задачи нет в проекте!'

    @pytest.mark.asyncio
    async def test_get_task_info_task_not_found(self, db_session: AsyncSession, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        with pytest.raises(NotFoundException) as exc:
            await get_task_info(db_session, project.project_id, member.user_id, 99999)
        assert exc.value.detail == 'Задачи нет в проекте!'

    @pytest.mark.asyncio
    async def test_get_tasks_user_success(self, db_session: AsyncSession, test_users, test_project_with_member):
        member = test_users['member']
        project = test_project_with_member['project']
        repo_task = TaskRepository(db_session)
        task_data = TaskCreate(title='Task for member', assigned_to=member.user_id)
        await repo_task.create_task(project.project_id, task_data)
        tasks = await get_tasks_user(db_session, member.user_id)
        assert isinstance(tasks, list)
        assert len(tasks) >= 1

    @pytest.mark.asyncio
    async def test_update_task_success(self, db_session: AsyncSession, test_project_with_member, test_task, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        update_data = TaskUpdate(title='Updated Title', task_description='New Desc')
        result = await update_task(db_session, project.project_id, test_task.task_id, member.user_id, update_data)
        assert result == {'message': 'Задача обновилась!'}
        repo_task = TaskRepository(db_session)
        updated = await repo_task.get_task_by_id(test_task.task_id)
        assert updated.title == 'Updated Title'
        assert updated.task_description == 'New Desc'

    @pytest.mark.asyncio
    async def test_update_task_no_data(self, db_session: AsyncSession, test_project_with_member, test_task, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        update_data = TaskUpdate()
        result = await update_task(db_session, project.project_id, test_task.task_id, member.user_id, update_data)
        assert result == {'message': 'Нет данных для обновления!'}

    @pytest.mark.asyncio
    async def test_update_task_not_in_project(self, db_session: AsyncSession, test_project_with_member, test_task, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        repo_proj = ProjectRepository(db_session)
        second_project = await repo_proj.create_project_with_admin(
            name=f'Second_{uuid.uuid4().hex[:8]}',
            description=None,
            admin_id=test_users['admin'].user_id
        )
        repo_task = TaskRepository(db_session)
        task_second = await repo_task.create_task(second_project.project_id, TaskCreate(title='Second Task'))
        with pytest.raises(NotFoundException) as exc:
            await update_task(db_session, project.project_id, task_second.task_id, member.user_id, TaskUpdate(title='new'))
        assert exc.value.detail == 'Задачи нет в проекте!'

    @pytest.mark.asyncio
    async def test_update_task_user_not_in_project(self, db_session: AsyncSession, test_project, test_task, test_users):
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await update_task(db_session, test_project.project_id, test_task.task_id, outsider.user_id, TaskUpdate(title='new'))
        assert exc.value.detail == 'Текущего пользователя нет в проекте!'

    @pytest.mark.asyncio
    async def test_update_task_deadline_in_past(self, db_session: AsyncSession, test_project_with_member, test_task, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        update_data = TaskUpdate(deadline=datetime.date.today() - datetime.timedelta(days=1))
        with pytest.raises(InvalidDeadlineException) as exc:
            await update_task(db_session, project.project_id, test_task.task_id, member.user_id, update_data)
        assert exc.value.detail == 'Время дэдлайна не может быть меньше сегодняшнего дня!'

    @pytest.mark.asyncio
    async def test_update_task_assigned_to_not_exist(self, db_session: AsyncSession, test_project_with_member, test_task, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        update_data = TaskUpdate(assigned_to=99999)
        with pytest.raises(NotFoundException) as exc:
            await update_task(db_session, project.project_id, test_task.task_id, member.user_id, update_data)
        assert exc.value.detail == 'Такого пользователя не существует!'

    @pytest.mark.asyncio
    async def test_update_task_assigned_to_not_in_project(self, db_session: AsyncSession, test_project_with_member, test_task, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        outsider = test_users['outsider']
        update_data = TaskUpdate(assigned_to=outsider.user_id)
        with pytest.raises(PermissionDeniedException) as exc:
            await update_task(db_session, project.project_id, test_task.task_id, member.user_id, update_data)
        assert exc.value.detail == 'Добавляемого пользователя нет в проекте!'

    @pytest.mark.asyncio
    async def test_change_status_success(self, db_session: AsyncSession, test_project_with_member, test_task, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        result = await change_status(db_session, project.project_id, test_task.task_id, member.user_id, TaskStatus.IN_PROGRESS)
        assert result == {'message': 'Статус обновлен!'}

    @pytest.mark.asyncio
    async def test_change_status_already_set(self, db_session: AsyncSession, test_project_with_member, test_task, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        result = await change_status(db_session, project.project_id, test_task.task_id, member.user_id, TaskStatus.PENDING)
        assert result == {'message': 'Статус уже установлен'}

    @pytest.mark.asyncio
    async def test_change_status_project_not_exists(self, db_session: AsyncSession, test_task, test_users):
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await change_status(db_session, 99999, test_task.task_id, outsider.user_id, TaskStatus.IN_PROGRESS)
        assert exc.value.detail == 'Данного проекта не существует!'

    @pytest.mark.asyncio
    async def test_change_status_user_not_in_project(self, db_session: AsyncSession, test_project, test_task, test_users):
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await change_status(db_session, test_project.project_id, test_task.task_id, outsider.user_id, TaskStatus.IN_PROGRESS)
        assert exc.value.detail == 'Текущего пользователя нет в проекте!'

    @pytest.mark.asyncio
    async def test_change_status_task_not_in_project(self, db_session: AsyncSession, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        with pytest.raises(NotFoundException) as exc:
            await change_status(db_session, project.project_id, 99999, member.user_id, TaskStatus.IN_PROGRESS)
        assert exc.value.detail == 'Задачи нет в проекте!'

    @pytest.mark.asyncio
    async def test_delete_task_success(self, db_session: AsyncSession, test_project_with_member, test_task, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        result = await delete_task(db_session, project.project_id, test_task.task_id, member.user_id)
        assert result == {'message': 'Задача удалена из проекта!'}

    @pytest.mark.asyncio
    async def test_delete_task_project_not_exists(self, db_session: AsyncSession, test_task, test_users):
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await delete_task(db_session, 99999, test_task.task_id, outsider.user_id)
        assert exc.value.detail == 'Данного проекта не существует!'

    @pytest.mark.asyncio
    async def test_delete_task_user_not_in_project(self, db_session: AsyncSession, test_project, test_task, test_users):
        outsider = test_users['outsider']
        with pytest.raises(PermissionDeniedException) as exc:
            await delete_task(db_session, test_project.project_id, test_task.task_id, outsider.user_id)
        assert exc.value.detail == 'Текущего пользователя нет в проекте!'

    @pytest.mark.asyncio
    async def test_delete_task_task_not_in_project(self, db_session: AsyncSession, test_project_with_member, test_users):
        project = test_project_with_member['project']
        member = test_users['member']
        with pytest.raises(NotFoundException) as exc:
            await delete_task(db_session, project.project_id, 99999, member.user_id)
        assert exc.value.detail == 'Задачи нет в проекте!'