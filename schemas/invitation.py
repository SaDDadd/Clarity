from pydantic import BaseModel
from schemas.common import InvitationRole

class InvitationBase(BaseModel):
    invitee_id : int
    message : str

class InvitationStatusUpdate(BaseModel):
    action : InvitationRole

class InvitationResponse(InvitationBase):
    project_id : int
    inviter_id : int
    status_invited : InvitationRole