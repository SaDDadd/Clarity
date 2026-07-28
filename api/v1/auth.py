from fastapi import APIRouter 
from core.security import hash_password
from schemas.auth import UserRegister, UserLogin
from core.dependencies import AsyncSession
from core.dependencies import get_db
from core.dependencies import current_user
from core.exceptions import NotFoundException, ConflictException

router = APIRouter()
session = get_db()

@router.post('/auth/register', tags=('Аутентификация'), \
             description='Принимает значения пользователя при регистрации') # Регистрация нового пользователя
async def user_registration(user: UserRegister):

@router.post('/auth/login', tags=('Аутентификация'), \
             description='Регистрация пользователя') # Вход в систему
async def user_log(user: UserLogin):

@router.get('/auth/me', tags=('Аутентификация'), \
            description='Получение информации о пользователе') # Получить информацию о пользователе
async def get_user_info(user: UserRegister):

