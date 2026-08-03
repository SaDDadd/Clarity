# Схемы для проектов (создание, обновление, вывод)
from pydantic import BaseModel, Field
from schemas.common import ProjectRole
from schemas.user import UserResponse

class ProjectBase(BaseModel):
    project_id : int
    project_name : str = Field(max_length=100)
    project_description : str | None

class ProjectCreate(ProjectBase):
    admin_id : int
    
class ProjectUpdate(ProjectBase):
    project_name : str | None
    project_description : str | None

class ProjectMember(ProjectBase):
    user_id : int
    role : ProjectRole

class ProjectsGet(BaseModel):
    project_id : int
    admin_id : int

class ProjectResponse(ProjectBase):
    members : list[UserResponse]