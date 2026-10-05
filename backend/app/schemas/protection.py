from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SiteProtectRequest(BaseModel):
    domain: str = Field(..., min_length=3, max_length=255, description="Domain to protect e.g. youtube.com")
    policy_id: Optional[UUID] = None

class SiteUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    policy_id: Optional[UUID] = None

class SiteResponse(BaseModel):
    id: UUID
    domain: str
    enabled: bool
    status: str
    policy_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    last_activity_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class ProtectionSummary(BaseModel):
    protected_sites: int
    active_sites: int
    protection_events: int
    signals_protected: int
    high_risk_probes: int
    average_risk_before: float
    average_risk_after: float
    protection_rate: float # percentage 0-100

class SiteAnalytics(BaseModel):
    site_id: UUID
    domain: str
    enabled: bool
    events: int
    fingerprint_probes: int
    canvas_events: int
    webgl_events: int
    navigator_events: int
    screen_events: int
    timezone_events: int
    media_devices_events: int
    audio_events: int
    signals_masked: int
    risk_before: float
    risk_after: float
    consistency_score: float
    last_activity: Optional[datetime] = None
