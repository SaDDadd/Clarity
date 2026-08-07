from repositories.project_invitation_repository import ProjectInvitationRepository

async def send_invitation(): # Отправка приглашения

async def get_user_invitations(): # Возращаем список приглашений пользователя

async def get_project_invitations(): #  Возращает список приглашений проекта (только админ)

async def respond_to_invitation(): # Возращает информацию о принятии/отклонении приглашения в проект

async def cancel_invitation(): # Удалить приглашение