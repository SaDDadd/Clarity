from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base
from sqlalchemy import Text, Enum, ForeignKey, func
import datetime

class ProjectInvitationModel(Base):
    __tablename__ = 'project_invitations'

    invitation_id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)
    inviter_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    invitee_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    status_invited: Mapped[str] = mapped_column(Enum('pending', 'accepted', 'declined'), nullable=False, server_default='pending')
    created_date: Mapped[datetime.datetime] = mapped_column(nullable=False, server_default=func.now())
    update_date: Mapped[datetime.datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())
    message: Mapped[str | None] = mapped_column(Text, nullable=True)