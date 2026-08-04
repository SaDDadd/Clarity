# Схемы для проектов (создание, обновление, вывод)
from pydantic import BaseModel, Field
from schemas.common import ProjectRole
from schemas.user import UserResponse

class ProjectBase(BaseModel):
    project_name : str = Field(max_length=100)
    project_description : str | None

class ProjectCreate(ProjectBase):
    admin_id : int
    
class ProjectUpdate(ProjectBase):
    project_name : str | None = None
    project_description : str | None = None

class ProjectMember(ProjectBase):
    user_id : int
    role : ProjectRole

class ProjectMemberCheck(BaseModel):
    project_id : int
    user_id : int

class ProjectResponse(ProjectBase):
    project_id : int
    members : list[UserResponse]