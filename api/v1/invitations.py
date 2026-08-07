from fastapi import APIRouter

router = APIRouter()

# POST
@router.post()
async def sending_invitations(): # Отправка приглашений
    return await 

# PATCH
@router.patch()
async def response_to_invitation(): # Ответ на приглашение
    return await 

# GET
@router.get()
async def user_invitations(): # Список приглашений для текущего пользователя
    return await 

@router.get()
async def project_invitations(): # Список приглашений для текущего проекта (только админ) 
    return await

# DELETE
@router.delete()
async def delete_invitation(): # Удаление приглашения (только админ)
    return await