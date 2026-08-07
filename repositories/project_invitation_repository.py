# Репозиторий приглашений в проект
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from 

class ProjectInvitationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_invitation(project_id: int, inviter_id: int, invitee_id: int, message: str) -> bool: # Создать приглашение

    async def get_invitation_by_id(): # Получить приглашение по ID

    async def get_invitation_by_user(): # Список приглашени, где пользователь приглашонный

    async def get_invitation_for_project(): # Список приглашенных у проекта

    async def get_pending_invitation(): # Проверка на активное приглашение

    async def update_invitation_status(): # Обновление статуса

    async def delete_invitation(): # Удаление приглашения
