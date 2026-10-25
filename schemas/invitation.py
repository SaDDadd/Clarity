from pydantic import BaseModel, Field
from schemas.common import InvitationRole, InvitationAction
from datetime import datetime
from pydantic import ConfigDict

class InvitationBase(BaseModel):
    invitee_id : int
    message : str | None = Field(default=None, max_length=1000)

class InvitationStatusUpdate(BaseModel):
    action : InvitationAction

class InvitationResponse(InvitationBase):
    invitation_id: int 
    project_id : int
    inviter_id : int
    status_invited : InvitationRole | None
    created_date: datetime | None
    update_date: datetime | None
    model_config = ConfigDict(from_attributes=True)

class InvitationCreate(BaseModel):
    user_id : int
    message : str | None = Field(default=None, max_length=1000)