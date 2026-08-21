from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import current_user, get_db
from models.user import UserModel
from schemas.user import UpdateEmailRequest, UpdateUsernameRequest, UserResponse
from services.user_service import update_user_email, update_user_username

router = APIRouter()


@router.put('/profile/username', tags=['Изменения профиля'],
            summary='Обновить имя пользователя')
async def update_username_endpoint(request: UpdateUsernameRequest,
                                   current_user: UserModel = Depends(current_user),
                                   db: AsyncSession = Depends(get_db)):
    """Обновляет имя пользователя."""
    return await update_user_username(db, request.username, current_user.user_id)


@router.put('/profile/email', tags=['Изменения профиля'],
            summary='Обновить email пользователя')
async def update_email_endpoint(request: UpdateEmailRequest,
                                current_user: UserModel = Depends(current_user),
                                db: AsyncSession = Depends(get_db)):
    """Обновляет email пользователя."""
    return await update_user_email(db, request.email, current_user.user_id)


@router.get('/profile', tags=['Изменения профиля'],
            summary='Получить информацию о пользователе')
async def get_profile_endpoint(current_user: UserModel = Depends(current_user)) -> UserResponse:
    """Возвращает данные текущего пользователя."""
    return UserResponse.model_validate(current_user)