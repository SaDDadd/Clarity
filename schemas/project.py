# Схемы для проектов (создание, обновление, вывод)
from pydantic import BaseModel, Field
from schemas.common import ProjectRole
from schemas.user import UserResponse

class ProjectBase(BaseModel):
    project_name : str = Field(min_length=1, max_length=100)
    project_description : str | None

class ProjectCreate(ProjectBase):
    pass
    
class ProjectUpdate(ProjectBase):
    project_name : str | None
    project_description : str | None

class ProjectMember(BaseModel):
    user_id : int
    role : ProjectRole

class ProjectResponse(ProjectBase):
    members : list[UserResponse]