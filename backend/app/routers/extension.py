import uuid
import secrets
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_optional_current_user
from app.models.user import User
from app.models.protected_site import ProtectedSite
from app.models.policy import Policy
from app.models.fingerprint_event import FingerprintEvent
from app.models.masking_event import MaskingEvent
from app.models.analytics_event import AnalyticsEvent
from app.schemas.event import (
    ExtensionRegisterRequest, ExtensionRegisterResponse,
    ExtensionConfigResponse, ExtensionSitePolicy, TelemetryEventCreate, TelemetryEventResponse
)
from app.services.audit_service import AuditService
from app.services.risk_engine import RiskEngine
from app.routers.websocket import broadcast_dashboard_event

router = APIRouter(prefix="/extension", tags=["Extension Synchronization"])

@router.post("/register", response_model=ExtensionRegisterResponse, status_code=201)
def register_extension(
    payload: ExtensionRegisterRequest,
    request: Request,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Registers a new MaskIt browser extension instance and provisions synchronization credentials.
    """
    ext_id = f"ext_{secrets.token_hex(16)}"

    AuditService.log(
        db=db,
        action="EXTENSION_REGISTERED",
        resource_type="EXTENSION",
        resource_id=ext_id,
        user_id=current_user.id if current_user else None,
        details={"client_version": payload.client_version, "browser_type": payload.browser_type},
        ip_address=request.client.host if request.client else None
    )

    return ExtensionRegisterResponse(
        extension_id=ext_id,
        status="REGISTERED",
        sync_interval_seconds=30
    )

@router.get("/protected-sites", response_model=Dict[str, List[ExtensionSitePolicy]])
def get_extension_protected_sites(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns active protected domains and compiled masking policies for the extension.
    If no user token is passed, returns active public/system protected domains.
    """
    site_query = db.query(ProtectedSite)
    if current_user:
        site_query = site_query.filter(ProtectedSite.user_id == current_user.id)
    
    sites = site_query.all()
    results: List[ExtensionSitePolicy] = []

    for s in sites:
        policy_rules = {
            "mask_canvas": True,
            "mask_webgl": True,
            "mask_navigator": True,
            "mask_screen": True,
            "mask_timezone": True,
            "mask_audio": True
        }
        if s.policy and s.policy.rules_json:
            policy_rules.update(s.policy.rules_json)

        results.append(ExtensionSitePolicy(
            domain=s.domain,
            enabled=s.enabled,
            policy=policy_rules
        ))

    return {"sites": results}

@router.get("/config", response_model=ExtensionConfigResponse)
def get_extension_config(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the comprehensive runtime configuration, sync interval, and domain rules
    intended to be locally cached by the browser extension.
    """
    sites_dict = get_extension_protected_sites(current_user=current_user, db=db)
    return ExtensionConfigResponse(
        sync_interval=30,
        global_enabled=True,
        sites=sites_dict["sites"]
    )

@router.post("/event", response_model=TelemetryEventResponse, status_code=201)
async def ingest_extension_event(
    event_in: TelemetryEventCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Ingests privacy-safe telemetry from the local browser extension masking engine.
    Calculates deterministic risk reduction, persists to PostgreSQL, and broadcasts via WebSocket.
    """
    user_id = current_user.id if current_user else None
    sig = event_in.signal_type or "GENERIC"
    conf = RiskEngine.SIGNAL_CLASSIFICATION.get(sig.upper(), {"max_impact": 15.0})

    risk_before = event_in.risk_before if event_in.risk_before is not None else float(conf["max_impact"] * 4.0)
    risk_after = event_in.risk_after if event_in.risk_after is not None else max(10.0, risk_before * 0.25)
    consistency_score = event_in.consistency_score if event_in.consistency_score is not None else 98.0
    action = event_in.action or "MASKED"

    # 1. Update last_activity on ProtectedSite if matching domain exists
    site = db.query(ProtectedSite).filter(ProtectedSite.domain == event_in.domain.lower()).first()
    if site:
        site.last_activity_at = datetime.now(timezone.utc)

    # 2. Store FingerprintEvent (probe record)
    fp_event = FingerprintEvent(
        user_id=user_id,
        session_id=event_in.session_id,
        domain=event_in.domain.lower(),
        signal_type=sig,
        probe_method=event_in.probe_method or "API_INTERCEPT",
        risk_score=risk_before,
        consistency_score=consistency_score,
        entropy_estimate=round(conf["max_impact"] * 0.6, 2)
    )
    db.add(fp_event)

    # 3. Store MaskingEvent (action record)
    mask_event = MaskingEvent(
        user_id=user_id,
        session_id=event_in.session_id,
        domain=event_in.domain.lower(),
        signal_type=sig,
        action=action,
        risk_before=risk_before,
        risk_after=risk_after,
        consistency_before=consistency_score,
        consistency_after=consistency_score,
        policy_id=site.policy_id if site else None
    )
    db.add(mask_event)

    # 4. Store AnalyticsEvent
    analytics_ev = AnalyticsEvent(
        user_id=user_id,
        domain=event_in.domain.lower(),
        event_type=event_in.event_type or "FINGERPRINT_PROBE",
        risk_score=risk_after,
        source=event_in.source,
        privacy_safe_metadata=event_in.privacy_safe_metadata
    )
    db.add(analytics_ev)
    db.commit()
    db.refresh(analytics_ev)

    # 5. Broadcast real-time event to WebSocket subscribers
    broadcast_payload = {
        "event": event_in.event_type or "FINGERPRINT_PROBE",
        "domain": event_in.domain.lower(),
        "signal": sig,
        "action": action,
        "risk_before": risk_before,
        "risk_after": risk_after,
        "consistency": consistency_score,
        "timestamp": analytics_ev.timestamp.isoformat()
    }
    await broadcast_dashboard_event(broadcast_payload)

    return TelemetryEventResponse(
        id=analytics_ev.id,
        domain=event_in.domain.lower(),
        event_type=event_in.event_type,
        signal_type=sig,
        action=action,
        risk_score=risk_after,
        risk_before=risk_before,
        risk_after=risk_after,
        consistency_score=consistency_score,
        source=event_in.source,
        timestamp=analytics_ev.timestamp
    )
