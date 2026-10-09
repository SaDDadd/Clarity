from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import current_user, get_db
from models.user import UserModel
from schemas.user import UpdateEmailRequest, UpdateUsernameRequest, UpdatePasswordRequest, UserResponse
from services.user_service import update_user_email, update_user_username, update_user_password, search_by_username, \
                                    delete_profile
from cache.cache_keys import user_key, TTL_USER
from cache.cache_service import get_cache, set_cache

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
    key = user_key(current_user.user_id)
    cached = await get_cache(key)

    if cached is not None:
        return cached 
    
    data = UserResponse.model_validate(current_user).model_dump(mode='json')
    await set_cache(key, data, TTL_USER)
    return data

@router.patch('/profile/password', tags=['Изменения профиля'], 
            summary='Обновить пароль пользователя')
async def update_password_endpoint(request: UpdatePasswordRequest, 
                                   current_user: UserModel = Depends(current_user),
                                   db: AsyncSession = Depends(get_db)):
    """Обновление пароля пользователя."""
    return await update_user_password(db, request.password, current_user.user_id)

@router.get('/users/search', tags=['Пользователи'], summary='Поиск пользователя по нику')
async def search_users(search_user: str, current_user: UserModel = Depends(current_user), 
                       db: AsyncSession = Depends(get_db)):
    return await search_by_username(db, search_user, current_user.username)

@router.delete('/profile', tags=['Именения профиля'], summary='Удаление профиля')
async def delete_profile_endpoint(current_user: UserModel = Depends(current_user), 
                                  db: AsyncSession = Depends(get_db)):
    return await delete_profile(db, current_user.user_id)