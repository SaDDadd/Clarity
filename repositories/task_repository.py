from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.task import TaskModel
import datetime

# Переписать под SQLAlchemy

class TaskRepository:
    def __init__(self, session: AsyncSession) -> None: # Инициализация с подключением к БД
        self.session = session

    async def create_task(self, title: str, description: str | None, status: str,
                    proj_id: int, assigned_to: int | None, 
                    deadline: datetime.date | None) -> TaskModel: # Создать задачу
        task = TaskModel(title=title, task_description=description, task_status=status, \
                         project_id=proj_id, assigned_to=assigned_to, deadline=deadline)
        self.session.add(task)
        await self.session.commit()
        return task

    async def get_tasks_by_user(self, assigned_to: int) -> list[TaskModel]: # Получить все задачи 
        # пользователя
        result = await self.session.execute(select(TaskModel).where(TaskModel.assigned_to == assigned_to))
        tasks = result.scalars().all()
        return tasks

    async def assign_task(self, user_id: int, task_id: int) -> bool: # Назначить задачу 
        # пользователю
        task = await self.get_task_by_id(task_id)
        if task:
            task = await self.session.execute(update(TaskModel).values(assigned_to=user_id).where(TaskModel.task_id == task_id))
            await self.session.commit()
            return True
        return False

    async def delete_task(self, task_id: int) -> TaskModel | None: # Удалить задачу
        result = await self.session.execute(select(TaskModel).where(TaskModel.task_id == task_id))
        task = result.scalar_one_or_none()
        if task:
            await self.session.delete(task)
            await self.session.commit()
            return task
        return None

    async def get_task_by_id(self, project_id: int, task_id: int) -> TaskModel | None: # Получить задачу по ID
        result = await self.session.execute(select(TaskModel).where(TaskModel.project_id == project_id, TaskModel.task_id == task_id))
        task = result.scalar_one_or_none()
        return task

    async def update_task_by_id(self, task_id: int, status: str) -> TaskModel | None: # Обновить статус 
        # задачи
        result = await self.session.execute(select(TaskModel).where(TaskModel.task_id == task_id))
        task = result.scalar_one_or_none()
        if task:
            task.task_status = status
            await self.session.commit()
            return task
        return None