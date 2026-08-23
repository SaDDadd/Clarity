import pytest
import uuid
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from repositories.task_repository import TaskRepository
from repositories.project_repository import ProjectRepository
from models.task import TaskModel
from schemas.task import TaskCreate
from repositories.project_repository import ProjectRepository
from models.user import UserModel


class TestTaskRepository:

    @pytest.mark.asyncio
    async def test_create_task_success(self, db_session: AsyncSession, test_project):
        repo = TaskRepository(db_session)
        task_data = TaskCreate(
            title='Test Task',
            task_description='Description',
            task_status='pending',
            assigned_to=None,
            deadline=None
        )
        task = await repo.create_task(test_project.project_id, task_data)
        assert isinstance(task, TaskModel)
        assert task.title == 'Test Task'
        assert task.task_description == 'Description'
        assert task.task_status == 'pending'
        assert task.project_id == test_project.project_id
        assert task.assigned_to is None
        assert task.deadline is None

    @pytest.mark.asyncio
    async def test_create_task_with_deadline_and_assigned(self, db_session: AsyncSession, test_project, test_users):
        repo = TaskRepository(db_session)
        member = test_users['member']
        deadline = datetime.date.today() + datetime.timedelta(days=7)
        task_data = TaskCreate(
            title='Task with deadline',
            task_description=None,
            task_status='in_progress',
            assigned_to=member.user_id,
            deadline=deadline
        )
        task = await repo.create_task(test_project.project_id, task_data)
        assert task.assigned_to == member.user_id
        assert task.deadline == deadline
        assert task.task_status == 'in_progress'

    @pytest.mark.asyncio
    async def test_get_tasks_by_user_success(self, db_session: AsyncSession, test_project, test_users):
        repo = TaskRepository(db_session)
        member = test_users['member']
        task_data = TaskCreate(title='Task for member', assigned_to=member.user_id)
        await repo.create_task(test_project.project_id, task_data)
        tasks = await repo.get_tasks_by_user(member.user_id)
        assert isinstance(tasks, list)
        assert len(tasks) >= 1
        assert any(t.assigned_to == member.user_id for t in tasks)

    @pytest.mark.asyncio
    async def test_get_tasks_by_user_empty(self, db_session: AsyncSession, test_users):
        repo = TaskRepository(db_session)
        outsider = test_users['outsider']
        tasks = await repo.get_tasks_by_user(outsider.user_id)
        assert isinstance(tasks, list)
        assert len(tasks) == 0

    @pytest.mark.asyncio
    async def test_get_task_by_id_success(self, db_session: AsyncSession, test_task):
        repo = TaskRepository(db_session)
        task_id = test_task.task_id
        task = await repo.get_task_by_id(task_id)
        assert task is not None
        assert task.task_id == task_id

    @pytest.mark.asyncio
    async def test_get_task_by_id_not_found(self, db_session: AsyncSession):
        repo = TaskRepository(db_session)
        task = await repo.get_task_by_id(99999)
        assert task is None

    @pytest.mark.asyncio
    async def test_get_project_tasks_success(self, db_session: AsyncSession, test_project, test_task):
        repo = TaskRepository(db_session)
        tasks = await repo.get_project_tasks(test_project.project_id)
        assert isinstance(tasks, list)
        assert len(tasks) >= 1
        assert any(t.task_id == test_task.task_id for t in tasks)

    @pytest.mark.asyncio
    async def test_get_project_tasks_empty(self, db_session: AsyncSession, test_project):
        repo = TaskRepository(db_session)
        pass

    @pytest.mark.asyncio
    async def test_get_project_tasks_empty_with_users(self, db_session: AsyncSession, test_users):
        repo_proj = ProjectRepository(db_session)
        admin = test_users['admin']
        project = await repo_proj.create_project_with_admin(
            name=f'EmptyProject_{uuid.uuid4().hex[:8]}',
            description=None,
            admin_id=admin.user_id
        )
        repo = TaskRepository(db_session)
        tasks = await repo.get_project_tasks(project.project_id)
        assert isinstance(tasks, list)
        assert len(tasks) == 0

    @pytest.mark.asyncio
    async def test_is_task_in_project_true(self, db_session: AsyncSession, test_project, test_task):
        repo = TaskRepository(db_session)
        result = await repo.is_task_in_project(test_project.project_id, test_task.task_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_is_task_in_project_false_wrong_task(self, db_session: AsyncSession, test_project):
        repo = TaskRepository(db_session)
        result = await repo.is_task_in_project(test_project.project_id, 99999)
        assert result is False

    @pytest.mark.asyncio
    async def test_is_task_in_project_false_wrong_project(self, db_session: AsyncSession, test_task):
        repo = TaskRepository(db_session)
        result = await repo.is_task_in_project(99999, test_task.task_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_assign_task_success(self, db_session: AsyncSession, test_task, test_users):
        repo = TaskRepository(db_session)
        member = test_users['member']
        result = await repo.assign_task(member.user_id, test_task.task_id)
        assert result is True
        updated_task = await repo.get_task_by_id(test_task.task_id)
        assert updated_task.assigned_to == member.user_id

    @pytest.mark.asyncio
    async def test_assign_task_task_not_found(self, db_session: AsyncSession, test_users):
        repo = TaskRepository(db_session)
        member = test_users['member']
        result = await repo.assign_task(member.user_id, 99999)
        assert result is False

    @pytest.mark.asyncio
    async def test_update_task_by_id_success(self, db_session: AsyncSession, test_project, test_task):
        repo = TaskRepository(db_session)
        new_title = 'Updated Title'
        new_description = 'New description'
        update_dict = {
            'title': new_title,
            'task_description': new_description
        }
        result = await repo.update_task_by_id(test_project.project_id, test_task.task_id, update_dict)
        assert result is True
        updated = await repo.get_task_by_id(test_task.task_id)
        assert updated.title == new_title
        assert updated.task_description == new_description

    @pytest.mark.asyncio
    async def test_update_task_by_id_not_found(self, db_session: AsyncSession, test_project):
        repo = TaskRepository(db_session)
        result = await repo.update_task_by_id(test_project.project_id, 99999, {'title': 'new'})
        assert result is False

    @pytest.mark.asyncio
    async def test_update_task_status_success(self, db_session: AsyncSession, test_project, test_task):
        repo = TaskRepository(db_session)
        new_status = 'in_progress'
        result = await repo.update_task_status(test_project.project_id, test_task.task_id, new_status)
        assert result is True
        updated = await repo.get_task_by_id(test_task.task_id)
        assert updated.task_status == new_status

    @pytest.mark.asyncio
    async def test_update_task_status_not_found(self, db_session: AsyncSession, test_project):
        repo = TaskRepository(db_session)
        result = await repo.update_task_status(test_project.project_id, 99999, 'completed')
        assert result is False

    @pytest.mark.asyncio
    async def test_update_task_status_no_change(self, db_session: AsyncSession, test_project, test_task):
        repo = TaskRepository(db_session)
        result = await repo.update_task_status(test_project.project_id, test_task.task_id, 'pending')
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_task_success(self, db_session: AsyncSession, test_task):
        repo = TaskRepository(db_session)
        task_id = test_task.task_id
        result = await repo.delete_task(task_id)
        assert result is True
        deleted = await repo.get_task_by_id(task_id)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, db_session: AsyncSession):
        repo = TaskRepository(db_session)
        result = await repo.delete_task(99999)
        assert result is False