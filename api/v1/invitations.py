from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import current_user, get_db
from models.user import UserModel
from schemas.invitation import InvitationCreate, InvitationStatusUpdate
from services.invitation_service import (cancel_invitation, get_project_invitations,
                                         get_user_invitations, response_to_invitation,
                                         send_invitation)

router = APIRouter()


@router.post('/projects/{project_id}/invitations', tags=['Приглашение в проект'],
             summary='Отправка приглашения в проект пользователю')
async def sending_invitations_endpoint(invitation_data: InvitationCreate, project_id: int,
                                       current_user: UserModel = Depends(current_user),
                                       db: AsyncSession = Depends(get_db)):
    """Отправляет приглашение в проект от администратора."""
    return await send_invitation(db, project_id, invitation_data.user_id,
                                 current_user.user_id, invitation_data.message)


@router.patch('/invitations/{invitation_id}', tags=['Приглашение в проект'],
              summary='Ответ от пользователя на приглашение в проект')
async def response_to_invitation_endpoint(invitation_id: int,
                                          invitation_date: InvitationStatusUpdate,
                                          current_user: UserModel = Depends(current_user),
                                          db: AsyncSession = Depends(get_db)):
    """Принимает или отклоняет приглашение."""
    return await response_to_invitation(db, invitation_id, invitation_date.action,
                                        current_user.user_id)


@router.get('/invitations', tags=['Приглашение в проект'],
            summary='Список проектов, в которые приглашают пользователя')
async def user_invitations_endpoint(current_user: UserModel = Depends(current_user),
                                    db: AsyncSession = Depends(get_db)):
    """Возвращает все входящие приглашения для текущего пользователя."""
    return await get_user_invitations(db, current_user.user_id)


@router.get('/invitations/project/{project_id}', tags=['Приглашение в проект'],
            summary='Список приглашений в проект')
async def project_invitations_endpoint(project_id: int,
                                       current_user: UserModel = Depends(current_user),
                                       db: AsyncSession = Depends(get_db)):
    """Возвращает все приглашения для указанного проекта (доступно только администратору)."""
    return await get_project_invitations(db, project_id, current_user.user_id)


@router.delete('/invitations/{invitation_id}', tags=['Приглашение в проект'],
               summary='Удаление приглашения')
async def delete_invitation_endpoint(invitation_id: int,
                                     current_user: UserModel = Depends(current_user),
                                     db: AsyncSession = Depends(get_db)):
    """Отменяет (удаляет) приглашение. Доступно администратору проекта или отправителю."""
    return await cancel_invitation(db, invitation_id, current_user.user_id)