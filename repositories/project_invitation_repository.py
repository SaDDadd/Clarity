from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.project import ProjectModel
from models.project_invitations import ProjectInvitationModel


class ProjectInvitationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_invitation(self, project_id: int, inviter_id: int, 
                                invitee_id: int, message: str | None) -> ProjectInvitationModel:
        """Создать приглашение."""
        invitation = ProjectInvitationModel(
            project_id=project_id,
            inviter_id=inviter_id,
            invitee_id=invitee_id,
            status_invited="pending",
            message=message
        )
        self.session.add(invitation)
        await self.session.flush()
        return invitation

    async def get_invitation_by_id(self, invitation_id: int) -> ProjectInvitationModel | None:
        """Получить приглашение по ID."""
        task = await self.session.execute(
            select(ProjectInvitationModel)
            .where(
                ProjectInvitationModel.invitation_id == invitation_id
            )
        )
        result = task.scalar_one_or_none()
        return result

    async def get_invitation_by_user(self, user_id: int) -> list[ProjectInvitationModel]:
        """Список, где пользователь приглашённый."""
        task = await self.session.execute(
            select(ProjectInvitationModel)
            .where(
                ProjectInvitationModel.invitee_id == user_id,
                ProjectInvitationModel.status_invited == "pending"
            )
        )
        result = task.scalars().all()
        return result

    async def get_invitation_for_project(self, project_id: int) -> list[ProjectInvitationModel]:
        """Список приглашённых у проекта."""
        task = await self.session.execute(
            select(ProjectInvitationModel)
            .where(
                ProjectInvitationModel.project_id == project_id,
                ProjectInvitationModel.status_invited == "pending"
            )
        )
        result = task.scalars().all()
        return result

    async def update_invitation_status(self, invitation_id: int, status_invited: str) -> bool:
        """Обновление статуса."""
        task = await self.get_invitation_by_id(invitation_id)
        if task:
            await self.session.execute(
                update(ProjectInvitationModel)
                .values(status_invited=status_invited, update_date=func.now())
                .where(
                    ProjectInvitationModel.invitation_id == invitation_id
                )
            )
            await self.session.flush()
            return True
        else:
            return False

    async def delete_invitation(self, invitation_id: int) -> bool:
        """Удаление приглашения."""
        task = await self.get_invitation_by_id(invitation_id)
        if task:
            await self.session.execute(
                delete(ProjectInvitationModel)
                .where(
                    ProjectInvitationModel.invitation_id == invitation_id
                )
            )
            await self.session.flush()
            return True
        else:
            return False

    async def get_pending_invitation(self, project_id: int, invitee_id: int) -> bool:
        """Проверка на существование приглашения."""
        task = await self.session.execute(
            select(ProjectInvitationModel)
            .where(
                ProjectInvitationModel.project_id == project_id,
                ProjectInvitationModel.invitee_id == invitee_id,
                ProjectInvitationModel.status_invited == "pending"
            )
        )
        result = task.scalar_one_or_none()
        if result:
            return True
        else:
            return False

    async def get_pending_invitations_by_inviter(self, inviter_id: int) -> list[ProjectInvitationModel]:
        """Все pending-приглашения, отправленные пользователем."""
        result = await self.session.execute(
            select(ProjectInvitationModel)
            .where(
                ProjectInvitationModel.inviter_id == inviter_id,
                ProjectInvitationModel.status_invited == 'pending'
            )
        )
        return result.scalars().all()

    async def get_invitation_by_user_with_project(self, user_id: int) -> list[tuple[ProjectInvitationModel, str]]:
        """Входящие приглашения + имя проекта."""
        result = await self.session.execute(
            select(ProjectInvitationModel, ProjectModel.project_name)
            .join(ProjectModel,
                  ProjectModel.project_id == ProjectInvitationModel.project_id
            )
            .where(
                ProjectInvitationModel.invitee_id == user_id,
                ProjectInvitationModel.status_invited == "pending"
            )
        )
        return result.all()