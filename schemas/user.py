# Схемы для пользователей (публичные данные)
from pydantic import BaseModel, EmailStr, Field
import datetime

class UserBase(BaseModel):
    username : str = Field(max_length=50)
    email : EmailStr = Field(max_length=100)

class UserResponse(UserBase):
    created_date : datetime.datetime

class UpdateUsernameRequest(BaseModel):
    username : str = Field(max_length=50)

class UpdateEmailRequest(BaseModel):
    email : EmailStr = Field(max_length=100)