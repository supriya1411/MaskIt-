from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class SessionStartRequest(BaseModel):
    client_type: str = Field(default="EXTENSION", description="EXTENSION or DASHBOARD")
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

class SessionEndRequest(BaseModel):
    session_token: str

class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    session_token: str
    client_type: str
    is_active: bool
    started_at: datetime
    ended_at: Optional[datetime]
    last_seen_at: datetime

    model_config = {"from_attributes": True}
