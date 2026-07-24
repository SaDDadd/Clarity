from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base
from sqlalchemy import String, Text

class ProjectModel(Base):
    __tablename__ = 'projects'

    project_id: Mapped[int] = mapped_column(primary_key=True)
    project_name: Mapped[str] = mapped_column(String(100), nullable=False)
    project_description: Mapped[str] = mapped_column(Text, nullable=True)
    admin_id: Mapped[int] = mapped_column(nullable=False)