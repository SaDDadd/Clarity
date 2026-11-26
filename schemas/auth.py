from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    username: str = Field(min_length=2, max_length=30)
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=8, max_length=50)

class UserLogin(BaseModel):
    username_or_email: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=50)

class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = 'Bearer'

class UserDataForToken(BaseModel):
    user_id: int
    username: str = Field(min_length=2, max_length=30)