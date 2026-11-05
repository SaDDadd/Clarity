from sqlalchemy.ext.asyncio import AsyncSession 
from repositories.user_repository import UserRepository
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository
from repositories.project_invitation_repository import ProjectInvitationRepository


class UnitOfWork():
    def __init__(self, session: AsyncSession, read_only: bool = False):
        self.session = session 
        self._read_only = read_only
        self._commited = False 
        self._rollback = False
        self.user = UserRepository(session)
        self.project = ProjectRepository(session)
        self.task = TaskRepository(session)
        self.project_inv = ProjectInvitationRepository(session)


    async def __aenter__(self) -> "UnitOfWork":
        """"""
        pass 


    async def __aexit__(self, exc_type, exc) -> None:
        """"""
        if (exc_type is not None) and (exc_type is not self._commited) \
                and (exc_type is not self._rollback):
            await self.session.rollback()
        elif (exc_type is None) and (exc_type is not self._commited) \
                and (exc_type is not self._rollback):
            await self.session.rollback()
        elif exc_type is self._commited:
            pass
        elif exc_type is self._rollback:
            pass


    async def commit(self) -> None:
        """"""
        if self._rollback is True:
            raise RuntimeError('Нельзя совершать commit после отката!')
        elif self._commited is True:
            pass
        elif self._read_only is True:
            raise RuntimeError('Не соввершаем commit при получении данных из БД!')
        else:
            await self.session.commit()


    async def rollback(self) -> None:
        """"""
        if self._commited is True:
            raise RuntimeError('Нельзя откатить то, что commit!')
        elif self._rollback is True:
            pass
        else:
            await self.session.rollback()


    async def flush(self) -> None:
        """"""
        await self.session.flush()
