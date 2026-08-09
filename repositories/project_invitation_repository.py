from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from models.project_invitations import ProjectInvitationModel
import datetime

class ProjectInvitationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Создать приглашение
    async def create_invitation(self, project_id: int, inviter_id: int, invitee_id: int, message: str) -> ProjectInvitationModel:
        task = ProjectInvitationModel(
            project_id=project_id, 
            inviter_id=inviter_id, 
            invitee_id=invitee_id, 
            status_invited='pending',
            message=message
        )
        self.session.add(task)
        await self.session.commit()
        return task

    # Получить приглашение по ID
    async def get_invitation_by_id(self, invitation_id: int) -> ProjectInvitationModel | None:
        task = await self.session.execute(select(ProjectInvitationModel).where(ProjectInvitationModel.invitation_id == invitation_id))
        result = task.scalar_one_or_none()
        return result

    # Список, где пользователь приглашенный
    async def get_invitation_by_user(self, user_id: int) -> list[ProjectInvitationModel] | None:
        task = await self.session.execute(select(ProjectInvitationModel).where(ProjectInvitationModel.invitee_id == user_id, ProjectInvitationModel.status_invited == 'pending'))
        result = task.scalars().all()
        return result
    
    # Список приглашенных у проекта
    async def get_invitation_for_project(self, project_id) -> list[ProjectInvitationModel] | None:
        task = await self.session.execute(select(ProjectInvitationModel).where(ProjectInvitationModel.project_id == project_id, ProjectInvitationModel.status_invited == 'pending'))
        result = task.scalars().all()
        return result

    # Обновление статуса
    async def update_invitation_status(self, invitation_id: int, status_invited: str) -> bool:
        task = await self.get_invitation_by_id(invitation_id)
        if task:
            result = await self.session.execute(update(ProjectInvitationModel).values(status_invited=status_invited, update_date=func.now()).where(ProjectInvitationModel.invitation_id == invitation_id))
            await self.session.commit()
            return True
        else:
            return False
        
    # Удаление приглашения
    async def delete_invitation(self, invitation_id: int) -> bool:
        task = await self.get_invitation_by_id(invitation_id)
        if task:
            result = await self.session.execute(delete(ProjectInvitationModel).where(ProjectInvitationModel.invitation_id == invitation_id))
            await self.session.commit()
            return True
        else:
            return False

    # Проверка на существование приглашения 
    async def get_pending_invitation(self, project_id: int, invitee_id: int) -> bool:
        task = await self.session.execute(select(ProjectInvitationModel).where(ProjectInvitationModel.project_id == project_id, ProjectInvitationModel.invitee_id == invitee_id, ProjectInvitationModel.status_invited == 'pending'))
        result = task.scalar_one_or_none()
        if result:
            return True
        else:
            return False