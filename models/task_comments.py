from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base
from sqlalchemy import Text, ForeignKey, func
import datetime

class TaskCommentsModel(Base):
    __tablename__ = 'task_comments' 

    comment_id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.project_id', ondelete='CASCADE'))
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.task_id', ondelete='CASCADE'), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'), nullable=False)
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_date: Mapped[datetime.datetime] = mapped_column(nullable=False, server_default=func.now())
    update_date: Mapped[datetime.datetime] = mapped_column(nullable=False, server_default=func.now())