# schemas/task.py
from pydantic import BaseModel, Field
import datetime
from schemas.common import TaskStatus, TaskPriority

class TaskBase(BaseModel):
    title: str = Field(max_length=150)
    task_description: str | None = None
    task_status: TaskStatus = Field(default=TaskStatus.PENDING)
    task_priority: TaskPriority = TaskPriority.LOW
    favorite: bool = False
    deadline: datetime.date | None = Field(default=None)

class TaskCreate(TaskBase):
    assigned_to: int | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    task_description: str | None = None
    task_status: TaskStatus | None = None
    task_priority: TaskPriority | None = None
    favorite: bool | None = None
    assigned_to: int | None = None
    deadline: datetime.date | None = None

class TaskStatusUpdate(BaseModel):
    task_status: TaskStatus

class TaskResponse(TaskBase):
    task_id: int
    project_id: int
    assigned_to: int | None
    task_priority: TaskPriority | None = None
    favorite: bool
    created_date: datetime.datetime