from sqlalchemy.ext.asyncio import AsyncSession 
from repositories.user_repository import UserRepository
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository
from repositories.project_invitation_repository import ProjectInvitationRepository


class UnitOfWork():
    def __init__(self, session: AsyncSession):
        self.session = session 
        self._committed = False 
        self._rollback = False
        self.user = UserRepository(session)
        self.project = ProjectRepository(session)
        self.task = TaskRepository(session)
        self.project_inv = ProjectInvitationRepository(session)


    async def __aenter__(self) -> "UnitOfWork":
        """Вход в контекстный менеджер."""
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Выход из контекстного менеджера."""
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()


    async def commit(self) -> None:
        """Commit транзакции."""
        if self._committed:
            return
        elif self._rollback:
            raise RuntimeError('Нельзя совершить commit после rollback!')
        await self.session.commit()
        self._committed = True


    async def rollback(self) -> None:
        """Rollback транзакции."""
        if self._rollback:
            return 
        elif self._committed:
            raise RuntimeError('Нельзя совершить rollback после commit!')
        await self.session.rollback()
        self._rollback = True


    async def flush(self) -> None:
        """Проброс изменений без commit."""
        await self.session.flush()