import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_optional_current_user
from app.models.user import User
from app.models.analytics_event import AnalyticsEvent
from app.models.fingerprint_event import FingerprintEvent
from app.models.masking_event import MaskingEvent
from app.schemas.event import TelemetryEventCreate, TelemetryEventResponse
from app.utils.privacy import sanitize_privacy_metadata
from app.routers.websocket import broadcast_dashboard_event
from app.utils.query_scope import apply_user_scope
from app.services.risk_engine import RiskEngine

router = APIRouter(prefix="/events", tags=["Telemetry & Events"])

@router.post("", response_model=TelemetryEventResponse, status_code=201)
async def record_event(
    event_in: TelemetryEventCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Ingests and validates privacy-safe telemetry events.
    Applies privacy filter to sanitize any accidental PII, cookies, or raw byte payloads.
    Broadcasts real-time notification to active WebSocket dashboard listeners.
    """
    clean_meta = sanitize_privacy_metadata(event_in.privacy_safe_metadata) or {}
    user_id = current_user.id if current_user else None

    risk_before = event_in.risk_before if event_in.risk_before is not None else (event_in.risk_score or 50.0)
    risk_after = event_in.risk_after if event_in.risk_after is not None else max(10.0, risk_before * 0.3)
    consistency_score = event_in.consistency_score if event_in.consistency_score is not None else 98.0
    action = event_in.action or ("MASKED" if event_in.event_type == "MASK_APPLIED" else "DETECTED")
    signal_type = RiskEngine.canonicalize_signal(event_in.signal_type)

    clean_meta.update({
        "signal_type": signal_type,
        "action": action,
        "risk_before": risk_before,
        "risk_after": risk_after,
        "consistency_score": consistency_score,
    })

    # Ingest into AnalyticsEvent
    analytics_ev = AnalyticsEvent(
        user_id=user_id,
        domain=event_in.domain.lower(),
        event_type=event_in.event_type,
        risk_score=risk_after,
        source=event_in.source,
        privacy_safe_metadata=clean_meta
    )
    db.add(analytics_ev)

    # Ingest to FingerprintEvent or MaskingEvent depending on type
    if signal_type:
        fp_ev = FingerprintEvent(
            user_id=user_id,
            session_id=event_in.session_id,
            domain=event_in.domain.lower(),
            signal_type=signal_type,
            probe_method=event_in.probe_method or "JS_API_PROBE",
            risk_score=risk_before,
            consistency_score=consistency_score
        )
        db.add(fp_ev)

        if action in ("MASKED", "NOISE_INJECTED", "NORMALIZED", "BLOCKED"):
            mask_ev = MaskingEvent(
                user_id=user_id,
                session_id=event_in.session_id,
                domain=event_in.domain.lower(),
                signal_type=signal_type,
                action=action,
                risk_before=risk_before,
                risk_after=risk_after,
                consistency_before=consistency_score,
                consistency_after=consistency_score
            )
            db.add(mask_ev)

    db.commit()
    db.refresh(analytics_ev)

    # Real-time WebSocket emission
    await broadcast_dashboard_event({
        "event": event_in.event_type,
        "domain": event_in.domain.lower(),
        "signal": signal_type,
        "action": action,
        "risk_before": risk_before,
        "risk_after": risk_after,
        "consistency": consistency_score,
        "timestamp": analytics_ev.timestamp.isoformat()
    })

    return TelemetryEventResponse(
        id=analytics_ev.id,
        domain=analytics_ev.domain,
        event_type=analytics_ev.event_type,
        signal_type=signal_type,
        action=action,
        risk_score=risk_after,
        risk_before=risk_before,
        risk_after=risk_after,
        consistency_score=consistency_score,
        source=analytics_ev.source,
        timestamp=analytics_ev.timestamp
    )

@router.get("", response_model=List[TelemetryEventResponse])
def get_recent_events(
    limit: int = 50,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves recent telemetry events stored in PostgreSQL."""
    query = db.query(AnalyticsEvent)
    if current_user:
        query = apply_user_scope(query, AnalyticsEvent.user_id, current_user.id)
    
    events = query.order_by(AnalyticsEvent.timestamp.desc()).limit(limit).all()
    
    res = []
    for ev in events:
        meta = ev.privacy_safe_metadata or {}
        risk_after = meta.get("risk_after", ev.risk_score)
        risk_before = meta.get("risk_before")
        res.append(TelemetryEventResponse(
            id=ev.id,
            domain=ev.domain,
            event_type=ev.event_type,
            signal_type=meta.get("signal_type"),
            action=meta.get("action") or ("MASKED" if "MASK" in ev.event_type else "LOGGED"),
            risk_score=ev.risk_score,
            risk_before=risk_before,
            risk_after=risk_after,
            consistency_score=meta.get("consistency_score", 98.0),
            source=ev.source,
            timestamp=ev.timestamp
        ))
    return res
