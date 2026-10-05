from uuid import UUID
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class DashboardOverviewResponse(BaseModel):
    protected_sites: int
    active_sites: int
    scans_today: int
    fingerprint_probes: int
    signals_detected: int
    signals_masked: int
    high_risk_events: int
    average_risk_before: float
    average_risk_after: float
    average_consistency: float
    protection_rate: float

class TimelinePoint(BaseModel):
    timestamp: datetime
    probes_count: int
    masked_count: int
    avg_risk: float

class SignalStat(BaseModel):
    signal: str
    count: int
    masked_count: int
    risk_level: str
    impact_weight: float

class RiskDistribution(BaseModel):
    low_count: int
    medium_count: int
    high_count: int
    critical_count: int
    average_score: float

class AuditLogResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True}
