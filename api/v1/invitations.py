from fastapi import APIRouter, Depends

from core.dependencies import current_user, get_uow
from core.uow import UnitOfWork
from models.user import UserModel
from schemas.invitation import InvitationCreate, InvitationStatusUpdate
from services.invitation_service import (delete_invitation, get_project_invitations,
                                         get_user_invitations, response_to_invitation,
                                         send_invitation)
from core.filters import InvitationFilter
from fastapi_filter import FilterDepends

router = APIRouter()


@router.get('/invitations', tags=['Приглашение в проект'],
            summary='Список проектов, в которые приглашают пользователя')
async def user_invitations_endpoint(current_user: UserModel = Depends(current_user),
                                    invitation_filter: InvitationFilter = FilterDepends(InvitationFilter),
                                    uow: UnitOfWork = Depends(get_uow)):
    """Возвращает все входящие приглашения для текущего пользователя."""
    # добавить фильтраию и пагинацию
    return await get_user_invitations(uow, current_user.user_id, invitation_filter)


@router.get('/invitations/project/{project_id}', tags=['Приглашение в проект'],
            summary='Список приглашений в проект')
async def project_invitations_endpoint(project_id: int,
                                       current_user: UserModel = Depends(current_user),
                                       invitation_filter: InvitationFilter = FilterDepends(InvitationFilter),
                                       uow: UnitOfWork = Depends(get_uow)):
    """Возвращает все приглашения для указанного проекта (доступно только администратору)."""
    # добавить фильтраию и пагинацию
    return await get_project_invitations(uow, project_id, current_user.user_id, invitation_filter)


@router.patch('/invitations/{invitation_id}', tags=['Приглашение в проект'],
              summary='Ответ от пользователя на приглашение в проект')
async def response_to_invitation_endpoint(invitation_id: int,
                                          invitation_date: InvitationStatusUpdate,
                                          current_user: UserModel = Depends(current_user),
                                          uow: UnitOfWork = Depends(get_uow)):
    """Принимает или отклоняет приглашение."""
    return await response_to_invitation(uow, invitation_id, invitation_date.action,
                                        current_user.user_id)


@router.post('/projects/{project_id}/invitations', tags=['Приглашение в проект'],
             summary='Отправка приглашения в проект пользователю')
async def sending_invitations_endpoint(invitation_data: InvitationCreate, project_id: int,
                                       current_user: UserModel = Depends(current_user),
                                       uow: UnitOfWork = Depends(get_uow)):
    """Отправляет приглашение в проект от администратора."""
    return await send_invitation(uow, project_id, invitation_data.user_id,
                                 current_user.user_id, invitation_data.message)


@router.delete('/invitations/{invitation_id}', tags=['Приглашение в проект'],
               summary='Удаление приглашения')
async def delete_invitation_endpoint(invitation_id: int,
                                     current_user: UserModel = Depends(current_user),
                                     uow: UnitOfWork = Depends(get_uow)):
    """Удаляет приглашение. Доступно администратору проекта или отправителю."""
    return await delete_invitation(uow, invitation_id, current_user.user_id)