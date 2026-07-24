from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base
from sqlalchemy import Enum, ForeignKey, func, PrimaryKeyConstraint
import datetime

class ProjectMemberModel(Base):
    __tablename__ = 'project_members'
    __table_args__ = (PrimaryKeyConstraint('project_id', 'user_id'),) # Так как в таблице нет первичного ключа

    project_id: Mapped[int] = mapped_column(ForeignKey('projects.project_id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'), nullable=False)
    role_project: Mapped[str] = mapped_column(Enum('admin', 'member'), nullable=False, server_default='member')
    joined_date: Mapped[datetime.datetime] = mapped_column(nullable=False, server_default=func.now())