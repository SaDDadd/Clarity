# schemas/project.py
from pydantic import BaseModel, ConfigDict, Field
from schemas.common import ProjectRole
from schemas.user import UserResponse

class ProjectBase(BaseModel):
    project_name: str = Field(min_length=1, max_length=100)
    project_description: str | None = Field(min_length=1, max_length=1000)

class ProjectCreate(ProjectBase):
    project_name: str = Field(min_length=1, max_length=100)
    project_description: str | None = Field(default=None, max_length=1000)

class ProjectUpdate(BaseModel):
    project_name: str | None = Field(min_length=1, max_length=100)
    project_description: str | None = Field(default=None, max_length=1000)

class ProjectMemberCheck(BaseModel):
    project_id: int
    user_id: int

class AddMemberRequest(BaseModel):
    user_id: int

class UserProjectResponse(BaseModel):
    project_id: int
    project_name: str
    project_description: str | None
    role: ProjectRole | None = None
    model_config = ConfigDict(from_attributes=True, extra='ignore')