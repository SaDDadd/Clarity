# Схемы для задач
from pydantic import BaseModel, Field
import datetime
from schemas.common import TaskStatus

class TaskBase(BaseModel):
    title : str = Field(max_length=150)
    task_description : str | None
    task_status : TaskStatus = Field(default=TaskStatus.PENDING)
    deadline : datetime.date | None = Field()

class TaskCreate(TaskBase):
    assigned_to : int | None

class TaskUpdate(BaseModel):
    title : str | None = None
    task_description : str | None = None
    task_status : TaskStatus | None = None
    assigned_to: int | None = None
    deadline : datetime.date | None = None

class TaskStatusUpdate(BaseModel):
    task_status : TaskStatus

class TaskResponse(TaskBase):
    task_id : int
    project_id : int
    assigned_to : int | None
    created_date : datetime.datetime