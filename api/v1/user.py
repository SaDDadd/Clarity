from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import current_user, get_db
from models.user import UserModel
from services.user_service import update_user_username, update_user_email
from schemas.user import UpdateEmailRequest, UpdateUsernameRequest

router = APIRouter()

# PUT
@router.put('/profile', tags=['Изменения профиля'], summary='Обновить имя пользователя') # Обновление имени профиля
async def update_username(username: str, current_user: UserModel = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return await update_user_username(db, username, current_user.user_id)

@router.put('/profile', tags=['Изменения профиля'], summary='Обновить email пользователя') # Обновление email профиля
async def update_email(email: str, current_user: UserModel = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return await update_user_email(db, email, current_user.user_id)