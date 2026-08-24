from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.task import TaskModel


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Создать задачу
    async def create_task(self, project_id: int, task) -> TaskModel:
        result = TaskModel(
            title=task.title,
            task_description=task.task_description,
            task_status=task.task_status,
            project_id=project_id,
            assigned_to=task.assigned_to,
            deadline=task.deadline
        )
        self.session.add(result)
        await self.session.commit()
        return result

    # Получить все задачи пользователя
    async def get_tasks_by_user(self, assigned_to: int) -> list[TaskModel]:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.assigned_to == assigned_to)
        )
        tasks = result.scalars().all()
        return tasks

    # Получить задачу по ID
    async def get_task_by_id(self, task_id: int) -> TaskModel | None:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.task_id == task_id)
        )
        task = result.scalar_one_or_none()
        return task

    # Получить все задачи проекта
    async def get_project_tasks(self, project_id: int) -> list[TaskModel] | None:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.project_id == project_id)
        )
        tasks = result.scalars().all()
        return tasks

    # Проверить, принадлежит ли задача проекту
    async def is_task_in_project(self, project_id: int, task_id: int) -> bool:
        result = await self.session.execute(
            select(TaskModel).where(
                TaskModel.project_id == project_id,
                TaskModel.task_id == task_id
            )
        )
        task = result.scalar_one_or_none()
        if task is None:
            return False
        else:
            return True

    # Назначить задачу пользователю
    async def assign_task(self, user_id: int, task_id: int) -> bool:
        task = await self.get_task_by_id(task_id)
        if task:
            await self.session.execute(
                update(TaskModel)
                .values(assigned_to=user_id)
                .where(TaskModel.task_id == task_id)
            )
            await self.session.commit()
            return True
        return False

    # Обновить задачу по ID
    async def update_task_by_id(self, project_id: int, task_id: int, slov: dict) -> bool:
        result = await self.get_task_by_id(task_id)
        if result:
            await self.session.execute(
                update(TaskModel)
                .values(slov)
                .where(TaskModel.project_id == project_id, TaskModel.task_id == task_id)
            )
            await self.session.commit()
            return True
        else:
            return False

    # Обновить статус задачи
    async def update_task_status(self, project_id: int, task_id: int, task_status: str) -> bool:
        result = await self.session.execute(
            update(TaskModel)
            .values(task_status=task_status)
            .where(
                TaskModel.project_id == project_id,
                TaskModel.task_id == task_id,
                TaskModel.task_status != task_status
            )
        )
        await self.session.commit()
        return result.rowcount > 0

    # Удалить задачу
    async def delete_task(self, task_id: int) -> bool:
        result = await self.get_task_by_id(task_id)
        if result:
            await self.session.delete(result)
            await self.session.commit()
            return True
        return False