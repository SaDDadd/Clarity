from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, func, select
from models.task_comments import TaskCommentsModel
from fastapi_pagination.ext.sqlalchemy import apaginate
from core.filters import CommentFilter
from fastapi_pagination import Page, Params


class CommentRepository():
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

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


    async def get_task_comments(self, project_id: int, task_id: int, filter: CommentFilter | None = None, 
                                params: Params | None = None) -> Page[TaskCommentsModel]: 
        """Получить комментарии задачи."""
        query = select(TaskCommentsModel).where(
                TaskCommentsModel.project_id == project_id,
                TaskCommentsModel.task_id == task_id
            ).order_by(TaskCommentsModel.created_date)
        if filter:
            query = filter.filter(query)
        return await apaginate(self.session, query, params=params)


    async def get_task_comment_locations_by_author(self, user_id: int) -> list[tuple[int, int]]:
        """Возврат id проекта и комментария автора"""
        result = await self.session.execute(
                select(TaskCommentsModel.project_id, TaskCommentsModel.task_id)
                .where(TaskCommentsModel.author_id == user_id)
                .distinct()
        )
        return result.all()


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


    async def delete_comment(self, comment_id: int) -> bool:
        """Удалить комментарий."""
        comment = await self.get_comment_by_id(comment_id)
        if comment:
            await self.session.delete(comment)
            await self.session.flush()
            return True
        return False