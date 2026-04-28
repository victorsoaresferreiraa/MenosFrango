from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid

# O QUE O ROUTER PEDIU AGORA!
class UpdateClientNotesRequest(BaseModel):
    notes: str

class PersonalDashboardResponse(BaseModel):
    total_clients: int
    pending_invites: int
    active_plans: int

class InviteClientRequest(BaseModel):
    email: EmailStr
    full_name: str

class AcceptInviteResponse(BaseModel):
    message: str
    user_id: uuid.UUID

class PersonalClientResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    personal_id: uuid.UUID
    status: str
    invited_at: datetime
    accepted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PersonalClientDetailResponse(PersonalClientResponse):
    full_name: str
    email: EmailStr

class PersonalBase(BaseModel):
    full_name: str
    email: EmailStr

class PersonalCreate(PersonalBase):
    password: str