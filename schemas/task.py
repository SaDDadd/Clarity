# schemas/task.py
from pydantic import BaseModel, Field
import datetime
from schemas.common import TaskStatus, TaskPriority
from pydantic import ConfigDict

class TaskBase(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=150)
    task_description: str | None = Field(default=None, max_length=1000)
    task_status: TaskStatus = Field(default=TaskStatus.PENDING)
    task_priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    task_favorite: bool = Field(default=False)
    deadline: datetime.date | None = Field(default=None)

class TaskCreate(TaskBase):
    title: str = Field(min_length=1, max_length=150)
    assigned_to: int | None = None

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=150)
    task_description: str | None = Field(default=None, max_length=1000)
    task_status: TaskStatus | None = None
    task_priority: TaskPriority | None = None
    task_favorite: bool | None = None
    assigned_to: int | None = None
    deadline: datetime.date | None = None

class TaskStatusUpdate(BaseModel):
    task_status: TaskStatus

class TaskResponse(TaskBase):
    task_id: int
    project_id: int
    assigned_to: int | None
    created_date: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class TaskCommentCreate(BaseModel):
    comment_text: str = Field(min_length=1, max_length=1000)

class TaskCommentResponse(BaseModel):
    comment_id: int
    task_id: int
    author_id: int
    comment_text: str
    created_date: datetime.datetime
    update_date: datetime.datetime
    model_config = ConfigDict(from_attributes=True)