from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base 
from sqlalchemy import String, Enum, Text, ForeignKey, func
import datetime

class TaskModel(Base):
    __tablename__ = 'tasks'

    task_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    task_description: Mapped[str] = mapped_column(Text, nullable=True)
    task_status: Mapped[str] = mapped_column(Enum('pending', 'in_progress', 'completed'), \
                                     nullable=True, server_default='pending')
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.project_id'), ondelete='CASCADE', nullable=False)
    assigned_to: Mapped[int] = mapped_column(ForeignKey('users.user_id'), nullable=True)
    deadline: Mapped[datetime.date] = mapped_column(nullable=True)
    created_date: Mapped[datetime.datetime] = mapped_column(nullable=False, server_default=func.now())