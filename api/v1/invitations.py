from fastapi import APIRouter
from fastapi import Depends
from core.dependencies import get_db, current_user
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import UserModel
from services.invitation_service import send_invitation, get_project_invitations, get_user_invitations, cancel_invitation, response_to_invitation
from schemas.invitation import InvitationCreate 

router = APIRouter()

# POST
@router.post('/projects/{project_id}/invitations', tags=['Приглашение в проект'], summary='Отправка приглашения в проект пользователю')
async def sending_invitations(user_id: int, project_id: int, message: str, current_user: UserModel = Depends(current_user), db: AsyncSession = Depends(get_db)): # Отправка приглашений
    return await send_invitation(db, project_id, user_id, current_user.user_id, message)

# PATCH
@router.patch('/invitations/{invitation_id}', tags=['Приглашение в проект'], summary='Ответ от пользователя на приглашение в проект')
async def response_to_invitation(invitation_id: int, action: str, current_user: UserModel = Depends(current_user), db: AsyncSession = Depends(get_db)): # Ответ на приглашение
    return await response_to_invitation(db, invitation_id, action, current_user.user_id)

# GET
@router.get('/invitations/{invitation_id}', tags=['Приглашение в проект'], summary='Список проектов, в которые приглашают пользователя')
async def user_invitations(invitation_id: int, current_user: UserModel = Depends(current_user), db: AsyncSession = Depends(get_db)): # Список приглашений для текущего пользователя
    return await get_user_invitations(db, current_user.user_id, invitation_id)

@router.get('/invitations/project/{project_id}', tags=['Приглашение в проект'], summary='Список приглашений в проект')
async def project_invitations(project_id: int, current_user: UserModel = Depends(current_user), db: AsyncSession = Depends(get_db)): # Список приглашений для текущего проекта
    return await get_project_invitations(db, project_id, current_user.user_id)

# DELETE
@router.delete('/invitations/{invitation_id}', tags=['Приглашение в проект'], summary='Удаление приглашения')
async def delete_invitation(invitation_id: int, current_user: UserModel = Depends(current_user), db: AsyncSession = Depends(get_db)): # Удаление приглашения (только админ)
    return await cancel_invitation(db, invitation_id, current_user.user_id)