# Схемы для регистрации, логина, токена
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    username : str = Field(min_length=1, max_length=50)
    email : EmailStr = Field(max_length=100)
    password : str = Field(min_length=8, max_length=255)

class UserLogin(BaseModel):
    username_or_email : str
    password : str = Field(max_length=255)

class Token(BaseModel):
    access_token : str
    token_type : str
    expires_in : int

class RefreshToken(BaseModel):
    refresh_token : str
    token_type : str