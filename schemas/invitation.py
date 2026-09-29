from pydantic import BaseModel
from schemas.common import InvitationRole
from datetime import datetime
from pydantic import ConfigDict

class InvitationBase(BaseModel):
    invitee_id : int
    message : str

class InvitationStatusUpdate(BaseModel):
    action : InvitationRole

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
    message : str