from pydantic import Field, BaseModel, ConfigDict
import datetime


class TaskCommentCreate(BaseModel):
    comment_text: str = Field(min_length=1, max_length=1000)

class TaskCommentResponse(BaseModel):
    comment_id: int
    task_id: int
    author_id: int | None
    comment_text: str = Field(min_length=1, max_length=1000)
    created_date: datetime.datetime
    update_date: datetime.datetime
    model_config = ConfigDict(from_attributes=True)