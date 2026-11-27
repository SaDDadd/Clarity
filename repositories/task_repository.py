from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.task import TaskModel
from models.task_comments import TaskCommentsModel
from models.project_members import ProjectMemberModel
from schemas.task import TaskCreate
from core.filters import TaskFilter, CommentFilter
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import apaginate


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def assign_task(self, user_id: int, task_id: int) -> bool:
        """Назначить задачу пользователю."""
        task = await self.get_task_by_id(task_id)
        if task:
            await self.session.execute(
                update(TaskModel)
                .values(assigned_to=user_id)
                .where(
                    TaskModel.task_id == task_id
                )
            )
            await self.session.flush()
            return True
        return False


    async def update_task_by_id(self, project_id: int, task_id: int, data: dict) -> bool:
        """Обновить задачу по ID."""
        result = await self.session.execute(
            update(TaskModel)
            .values(data)
            .where(
                TaskModel.project_id == project_id,
                TaskModel.task_id == task_id
            )
        )
        await self.session.flush()
        return result.rowcount > 0 


    async def update_task_status(self, project_id: int, task_id: int, task_status: str) -> bool:
        """Обновить статус задачи."""
        result = await self.session.execute(
            update(TaskModel)
            .values(task_status=task_status)
            .where(
                TaskModel.project_id == project_id,
                TaskModel.task_id == task_id,
                TaskModel.task_status != task_status
            )
        )
        await self.session.flush()
        return result.rowcount > 0


    async def get_tasks_by_user(self, assigned_to: int, filter: TaskFilter | None = None, 
                                params: Params | None = None) -> Page[TaskModel]:
        """Получить все задачи пользователя."""
        query = select(TaskModel).where(
                TaskModel.assigned_to == assigned_to
            ).order_by(
                TaskModel.task_id
            )
        if filter:
            query = filter.filter(query)
        return await apaginate(self.session, query, params=params)


    async def get_all_tasks_for_user(self, user_id: int, filter: TaskFilter | None = None, 
                                     params: Params | None = None) -> Page[TaskModel]:
        """Получить все задачи пользователя."""
        query = (
            select(TaskModel)
            .join(ProjectMemberModel, ProjectMemberModel.project_id == TaskModel.project_id)
            .where(ProjectMemberModel.user_id == user_id)
            .order_by(TaskModel.task_id)
        )
        if filter:
            query = filter.filter(query)
        return await apaginate(self.session, query, params=params)


    async def get_favorite_tasks_for_user(self, user_id: int, filter: TaskFilter | None,
                                          params: Params | None = None) -> Page[TaskModel]:
        """Получить избранные задачи."""
        query = select(TaskModel).join(
            ProjectMemberModel, ProjectMemberModel.project_id == TaskModel.project_id
        ).where(
            ProjectMemberModel.user_id == user_id,
            TaskModel.task_favorite.is_(True)
        ).order_by(
            TaskModel.task_id
        )
        if filter: 
            query = filter.filter(query)
        return await apaginate(self.session, query, params=params)


    async def get_task_by_id(self, task_id: int) -> TaskModel | None:
        """Получить задачу по ID."""
        result = await self.session.execute(
            select(TaskModel)
            .where(
                TaskModel.task_id == task_id
            )
        )
        task = result.scalar_one_or_none()
        return task


    async def get_project_tasks(self, project_id: int, filter: TaskFilter | None = None, 
                                params: Params | None = None) -> Page[TaskModel]:
        """Получить все задачи проекта."""
        query = select(TaskModel).where(
                TaskModel.project_id == project_id
            ).order_by(
                TaskModel.task_id
            )
        if filter:
            query = filter.filter(query)
        return await apaginate(self.session, query, params=params)


    async def create_task(self, project_id: int, task: TaskCreate) -> TaskModel:
        """Создать задачу."""
        result = TaskModel(
            title=task.title,
            task_description=task.task_description,
            task_status=task.task_status.value,
            task_priority=task.task_priority.value,
            task_favorite=task.task_favorite,
            project_id=project_id,
            assigned_to=task.assigned_to,
            deadline=task.deadline
        )
        self.session.add(result)
        await self.session.flush()
        return result


    async def delete_task(self, task_id: int) -> bool:
        """Удалить задачу."""
        result = await self.get_task_by_id(task_id)
        if result:
            await self.session.delete(result)
            await self.session.flush()
            return True
        return False


    async def is_task_in_project(self, project_id: int, task_id: int) -> bool:
        """Проверить, принадлежит ли задача проекту."""
        result = await self.session.execute(
            select(TaskModel)
            .where(
                TaskModel.project_id == project_id,
                TaskModel.task_id == task_id
            )
        )
        task = result.scalar_one_or_none()
        if task is None:
            return False
        else:
            return True


    async def is_user_task_performer(self, task_id: int, user_id: int) -> bool:
        """Проверка является ли пользователь исполнителем задачи."""
        result = await self.session.execute(
            select(TaskModel.assigned_to)
            .where(
                TaskModel.task_id == task_id
            )
        )
        assigned_to = result.scalar_one_or_none()
        return assigned_to == user_id