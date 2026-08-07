from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class ProjectInvitationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Создать приглашение
    async def create_invitation(project_id: int, inviter_id: int, invitee_id: int, message: str) -> bool:
        pass

    # Получить приглашение по ID
    async def get_invitation_by_id():
        pass

    # Список приглашени, где пользователь приглашонный
    async def get_invitation_by_user():
        pass

    # Список приглашенных у проекта
    async def get_invitation_for_project():
        pass

    # Проверка на активное приглашение
    async def get_pending_invitation():
        pass

    # Обновление статуса
    async def update_invitation_status():
        pass

    # Удаление приглашения
    async def delete_invitation():
        pass