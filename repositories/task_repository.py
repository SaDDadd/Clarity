from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.task import TaskModel
from models.task_comments import TaskCommentsModel
from schemas.task import TaskCreate


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


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


    async def get_tasks_by_user(self, assigned_to: int) -> list[TaskModel]:
        """Получить все задачи пользователя."""
        result = await self.session.execute(
            select(TaskModel)
            .where(
                TaskModel.assigned_to == assigned_to
            )
        )
        tasks = result.scalars().all()
        return tasks


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


    async def get_project_tasks(self, project_id: int) -> list[TaskModel]:
        """Получить все задачи проекта."""
        result = await self.session.execute(
            select(TaskModel)
            .where(
                TaskModel.project_id == project_id
            )
        )
        tasks = result.scalars().all()
        return tasks


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


    async def delete_task(self, task_id: int) -> bool:
        """Удалить задачу."""
        result = await self.get_task_by_id(task_id)
        if result:
            await self.session.delete(result)
            await self.session.flush()
            return True
        return False


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


    async def create_comment(self, project_id: int, task_id: int, user_id: int, message: str) -> TaskCommentsModel:
        """Создание комментария для задачи в проекте."""
        comment = TaskCommentsModel(
            task_id=task_id,
            project_id=project_id,
            author_id=user_id,
            comment_text=message
        )
        self.session.add(comment)
        await self.session.flush()
        return comment


    async def get_comment_author(self, project_id: int, task_id: int, comment_id: int) -> int | None:
        """Получить автора комментария у задачи."""
        result = await self.session.execute(
            select(TaskCommentsModel.author_id)
            .where(
                TaskCommentsModel.project_id == project_id,
                TaskCommentsModel.task_id == task_id,
                TaskCommentsModel.comment_id == comment_id
            )
        )
        comment = result.scalar_one_or_none()
        return comment


    async def get_comment_by_id(self, comment_id: int) -> TaskCommentsModel | None:
        """Получить комментарий по ID."""
        result = await self.session.execute(
            select(TaskCommentsModel)
            .where(
                TaskCommentsModel.comment_id == comment_id
            )
        )
        comment = result.scalar_one_or_none()
        return comment


    async def delete_comment(self, comment_id: int) -> bool:
        """Удалить комментарий."""
        comment = await self.get_comment_by_id(comment_id)
        if comment:
            await self.session.delete(comment)
            await self.session.flush()
            return True
        return False


    async def update_comment(self, comment_id: int, message: str) -> bool:
        """Обновить комментарий."""
        result = await self.session.execute(
            update(TaskCommentsModel)
            .where(
                TaskCommentsModel.comment_id == comment_id
            )
            .values(comment_text=message, update_date=func.now())
        )
        await self.session.flush()
        return result.rowcount > 0


    async def get_task_comments(self, project_id: int, task_id: int) -> list[TaskCommentsModel]:
        """Получить комментарии задачи."""
        result = await self.session.execute(
            select(TaskCommentsModel)
            .where(
                TaskCommentsModel.project_id == project_id,
                TaskCommentsModel.task_id == task_id
            )
            .order_by(TaskCommentsModel.created_date)
        )
        return result.scalars().all()