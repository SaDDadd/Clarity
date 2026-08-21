# schemas/user.py
from pydantic import BaseModel, ConfigDict, EmailStr, Field
import datetime

class UserBase(BaseModel):
    username: str = Field(max_length=50)
    email: EmailStr = Field(max_length=100)

class UserResponse(UserBase):
    user_id: int
    created_date: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class UpdateUsernameRequest(BaseModel):
    username: str = Field(max_length=50)

class UpdateEmailRequest(BaseModel):
    email: EmailStr = Field(max_length=100)