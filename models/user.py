from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base
from sqlalchemy import String, func
import datetime

class UserModel(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_date: Mapped[datetime.datetime] = mapped_column(nullable=False, server_default=func.now())