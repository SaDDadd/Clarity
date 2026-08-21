from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base
from sqlalchemy import Text, Enum, ForeignKey, func
import datetime

class ProjectInvitationModel(Base):
    __tablename__ = 'project_invitations'

    invitation_id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)
    inviter_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'), nullable=False)
    invitee_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'), nullable=False)
    status_invited: Mapped[str] = mapped_column(Enum('pending', 'accepted', 'declined'), nullable=True)
    created_date: Mapped[datetime.datetime] = mapped_column(nullable=True, server_default=func.now())
    update_date: Mapped[datetime.datetime] = mapped_column(nullable=True, server_default=func.now())
    message: Mapped[str] = mapped_column(Text, nullable=True)