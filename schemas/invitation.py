from pydantic import BaseModel, Field
from schemas.common import InvitationRole
from datetime import datetime
from pydantic import ConfigDict

class InvitationBase(BaseModel):
    invitee_id : int
    message : str | None = Field(default=None, max_length=1000)

class InvitationStatusUpdate(BaseModel):
    action : InvitationRole

class InvitationResponse(InvitationBase):
    invitation_id: int 
    project_id : int
    inviter_id : int
    invitee_id: int
    status_invited : InvitationRole | None
    message: str | None = Field(default=None, max_length=1000)
    created_date: datetime | None
    update_date: datetime | None
    model_config = ConfigDict(from_attributes=True)

class InvitationCreate(BaseModel):
    user_id : int
    message : str | None = Field(default=None, max_length=1000)