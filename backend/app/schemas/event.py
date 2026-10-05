from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class TelemetryEventCreate(BaseModel):
    session_id: Optional[UUID] = None
    domain: str = Field(..., max_length=255)
    event_type: str = Field(..., description="FINGERPRINT_PROBE, ATTRIBUTE_DETECTED, MASK_APPLIED, etc.")
    signal_type: Optional[str] = Field(None, description="CANVAS, WEBGL, NAVIGATOR, SCREEN, TIMEZONE, FONTS, MEDIA_DEVICES, AUDIO, HARDWARE")
    probe_method: Optional[str] = None
    action: Optional[str] = Field(None, description="DETECTED, MASKED, NOISE_INJECTED, NORMALIZED, BLOCKED")
    risk_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    risk_before: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    risk_after: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    consistency_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    source: str = Field(default="EXTENSION", description="EXTENSION, DASHBOARD, DEMO")
    privacy_safe_metadata: Optional[Dict[str, Any]] = None

class TelemetryEventResponse(BaseModel):
    id: UUID
    domain: str
    event_type: str
    signal_type: Optional[str]
    action: Optional[str]
    risk_score: float
    risk_before: Optional[float]
    risk_after: Optional[float]
    consistency_score: float
    source: str
    timestamp: datetime

    model_config = {"from_attributes": True}

class ExtensionRegisterRequest(BaseModel):
    client_version: str = Field(..., max_length=20)
    browser_type: str = Field(..., max_length=50)

class ExtensionRegisterResponse(BaseModel):
    extension_id: str
    status: str
    sync_interval_seconds: int

class ExtensionSitePolicy(BaseModel):
    domain: str
    enabled: bool
    policy: Dict[str, Any]

class ExtensionConfigResponse(BaseModel):
    sync_interval: int
    global_enabled: bool
    sites: List[ExtensionSitePolicy]
