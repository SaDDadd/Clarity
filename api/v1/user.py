from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import current_user, get_db
from models.user import UserModel
from schemas.user import UpdateEmailRequest, UpdateUsernameRequest, UpdatePasswordRequest, UserResponse
from services.user_service import (update_user_email, update_user_username, update_user_password, 
                                   search_by_username, delete_profile, get_profile_info)

router = APIRouter()


@router.put('/profile/username', tags=['Изменения профиля'],
            summary='Обновить имя пользователя')
async def update_username_endpoint(request: UpdateUsernameRequest,
                                   current_user: UserModel = Depends(current_user),
                                   db: AsyncSession = Depends(get_db)):
    """Обновляет имя текущего пользователя."""
    return await update_user_username(db, request, current_user.user_id)


@router.put('/profile/email', tags=['Изменения профиля'],
            summary='Обновить email пользователя')
async def update_email_endpoint(request: UpdateEmailRequest,
                                current_user: UserModel = Depends(current_user),
                                db: AsyncSession = Depends(get_db)):
    """Обновляет email текущего пользователя."""
    return await update_user_email(db, request, current_user.user_id)


@router.get('/profile', tags=['Изменения профиля'],
            summary='Получить информацию о пользователе')
async def get_profile_endpoint(current_user: UserModel = Depends(current_user)) -> UserResponse:
    """Возвращает данные текущего пользователя."""
    return await get_profile_info(current_user)


@router.patch('/profile/password', tags=['Изменения профиля'],
              summary='Обновить пароль пользователя')
async def update_password_endpoint(request: UpdatePasswordRequest,
                                   current_user: UserModel = Depends(current_user),
                                   db: AsyncSession = Depends(get_db)):
    """Обновляет пароль текущего пользователя."""
    return await update_user_password(db, request, current_user.user_id)


@router.get('/users/search', tags=['Пользователи'], summary='Поиск пользователя по нику')
async def search_users(search_user: str, current_user: UserModel = Depends(current_user), 
                       db: AsyncSession = Depends(get_db)):
    """Поиск пользователей."""
    return await search_by_username(db, search_user, current_user.username)


@router.delete('/profile', tags=['Изменения профиля'], summary='Удаление профиля')
async def delete_profile_endpoint(current_user: UserModel = Depends(current_user), 
                                  db: AsyncSession = Depends(get_db)):
    """Удаление провиля пользователя."""
    return await delete_profile(db, current_user.user_id)