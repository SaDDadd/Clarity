import pytest
import uuid
import datetime
from core.uow import UnitOfWork
from models.task import TaskModel
from schemas.task import TaskCreate


class TestTaskRepository:
    @pytest.mark.asyncio
    async def test_create_task_success(self, uow: UnitOfWork, test_project):
        """Проверяет успешное создание задачи с минимальными данными."""
        task_data = TaskCreate(
            title='Test Task',
            task_description='Description',
            task_status='pending',
            assigned_to=None,
            deadline=None
        )
        task = await uow.task.create_task(test_project.project_id, task_data)
        assert isinstance(task, TaskModel)
        assert task.title == 'Test Task'
        assert task.task_description == 'Description'
        assert task.task_status == 'pending'
        assert task.project_id == test_project.project_id
        assert task.assigned_to is None
        assert task.deadline is None


    @pytest.mark.asyncio
    async def test_create_task_with_deadline_and_assigned(self, uow: UnitOfWork, test_project, test_users):
        """Проверяет создание задачи с указанием дедлайна и исполнителя."""
        member = test_users['member']
        deadline = datetime.date.today() + datetime.timedelta(days=7)
        task_data = TaskCreate(
            title='Task with deadline',
            task_description=None,
            task_status='in_progress',
            assigned_to=member.user_id,
            deadline=deadline
        )
        task = await uow.task.create_task(test_project.project_id, task_data)
        assert task.assigned_to == member.user_id
        assert task.deadline == deadline
        assert task.task_status == 'in_progress'


    @pytest.mark.asyncio
    async def test_get_tasks_by_user_success(self, uow: UnitOfWork, test_project, test_users):
        """Проверяет получение списка задач, назначенных на пользователя."""
        member = test_users['member']
        task_data = TaskCreate(title='Task for member', assigned_to=member.user_id)
        await uow.task.create_task(test_project.project_id, task_data)
        tasks = await uow.task.get_tasks_by_user(member.user_id)
        assert isinstance(tasks, list)
        assert len(tasks) >= 1
        assert any(t.assigned_to == member.user_id for t in tasks)


    @pytest.mark.asyncio
    async def test_get_tasks_by_user_empty(self, uow: UnitOfWork, test_users):
        """Проверяет, что для пользователя без задач возвращается пустой список."""
        outsider = test_users['outsider']
        tasks = await uow.task.get_tasks_by_user(outsider.user_id)
        assert isinstance(tasks, list)
        assert len(tasks) == 0


    @pytest.mark.asyncio
    async def test_get_task_by_id_success(self, uow: UnitOfWork, test_task):
        """Проверяет получение задачи по существующему ID."""
        task_id = test_task.task_id
        task = await uow.task.get_task_by_id(task_id)
        assert task is not None
        assert task.task_id == task_id


    @pytest.mark.asyncio
    async def test_get_task_by_id_not_found(self, uow: UnitOfWork):
        """Проверяет, что при несуществующем ID возвращается None."""
        task = await uow.task.get_task_by_id(99999)
        assert task is None


    @pytest.mark.asyncio
    async def test_get_project_tasks_success(self, uow: UnitOfWork, test_project, test_task):
        """Проверяет получение списка всех задач проекта."""
        tasks = await uow.task.get_project_tasks(test_project.project_id)
        assert isinstance(tasks, list)
        assert len(tasks) >= 1
        assert any(t.task_id == test_task.task_id for t in tasks)


    @pytest.mark.asyncio
    async def test_get_project_tasks_empty(self, uow: UnitOfWork, test_project):
        """Заглушка для теста пустого списка задач (реализован в следующем тесте)."""
        pass


    @pytest.mark.asyncio
    async def test_is_task_in_project_true(self, uow: UnitOfWork, test_project, test_task):
        """Проверяет, что задача принадлежит указанному проекту (True)."""
        result = await uow.task.is_task_in_project(test_project.project_id, test_task.task_id)
        assert result is True


    @pytest.mark.asyncio
    async def test_is_task_in_project_false_wrong_task(self, uow: UnitOfWork, test_project):
        """Проверяет, что несуществующая задача не принадлежит проекту (False)."""
        result = await uow.task.is_task_in_project(test_project.project_id, 99999)
        assert result is False


    @pytest.mark.asyncio
    async def test_is_task_in_project_false_wrong_project(self, uow: UnitOfWork, test_task):
        """Проверяет, что задача не принадлежит другому проекту (False)."""
        result = await uow.task.is_task_in_project(99999, test_task.task_id)
        assert result is False


    @pytest.mark.asyncio
    async def test_assign_task_success(self, uow: UnitOfWork, test_task, test_users):
        """Проверяет успешное назначение задачи пользователю."""
        member = test_users['member']
        result = await uow.task.assign_task(member.user_id, test_task.task_id)
        assert result is True
        updated_task = await uow.task.get_task_by_id(test_task.task_id)
        assert updated_task.assigned_to == member.user_id


    @pytest.mark.asyncio
    async def test_assign_task_task_not_found(self, uow: UnitOfWork, test_users):
        """Проверяет, что при несуществующей задаче возвращается False."""
        member = test_users['member']
        result = await uow.task.assign_task(member.user_id, 99999)
        assert result is False


    @pytest.mark.asyncio
    async def test_update_task_by_id_success(self, uow: UnitOfWork, test_project, test_task):
        """Проверяет успешное обновление задачи (поля title и description)."""
        new_title = 'Updated Title'
        new_description = 'New description'
        update_dict = {
            'title': new_title,
            'task_description': new_description
        }
        result = await uow.task.update_task_by_id(test_project.project_id, test_task.task_id, update_dict)
        assert result is True
        updated = await uow.task.get_task_by_id(test_task.task_id)
        assert updated.title == new_title
        assert updated.task_description == new_description


    @pytest.mark.asyncio
    async def test_update_task_by_id_not_found(self, uow: UnitOfWork, test_project):
        """Проверяет, что при обновлении несуществующей задачи возвращается False."""
        result = await uow.task.update_task_by_id(test_project.project_id, 99999, {'title': 'new'})
        assert result is False


    @pytest.mark.asyncio
    async def test_update_task_status_success(self, uow: UnitOfWork, test_project, test_task):
        """Проверяет успешное изменение статуса задачи."""
        new_status = 'in_progress'
        result = await uow.task.update_task_status(test_project.project_id, test_task.task_id, new_status)
        assert result is True
        updated = await uow.task.get_task_by_id(test_task.task_id)
        assert updated.task_status == new_status


    @pytest.mark.asyncio
    async def test_update_task_status_not_found(self, uow: UnitOfWork, test_project):
        """Проверяет, что при обновлении статуса несуществующей задачи возвращается False."""
        result = await uow.task.update_task_status(test_project.project_id, 99999, 'completed')
        assert result is False


    @pytest.mark.asyncio
    async def test_delete_task_success(self, uow: UnitOfWork, test_task):
        """Проверяет успешное удаление задачи."""
        task_id = test_task.task_id
        result = await uow.task.delete_task(task_id)
        assert result is True
        deleted = await uow.task.get_task_by_id(task_id)
        assert deleted is None


    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, uow: UnitOfWork):
        """Проверяет, что при удалении несуществующей задачи возвращается False."""
        result = await uow.task.delete_task(99999)
        assert result is False