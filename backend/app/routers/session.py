import uuid
import secrets
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.session import SessionModel
from app.schemas.session import SessionStartRequest, SessionEndRequest, SessionResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/session", tags=["Session Tracking"])

@router.post("/start", response_model=SessionResponse, status_code=201)
def start_session(
    payload: SessionStartRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initializes a new active protection session for an extension or dashboard client."""
    client_ip = payload.ip_address or (request.client.host if request.client else None)
    ua = payload.user_agent or request.headers.get("user-agent")
    token = f"sess_{secrets.token_urlsafe(32)}"

    new_session = SessionModel(
        user_id=current_user.id,
        session_token=token,
        client_type=payload.client_type,
        ip_address=client_ip,
        user_agent=ua[:500] if ua else None,
        is_active=True
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    AuditService.log(
        db=db,
        action="SESSION_STARTED",
        resource_type="SESSION",
        resource_id=str(new_session.id),
        user_id=current_user.id,
        details={"client_type": payload.client_type},
        ip_address=client_ip
    )

    return new_session

@router.post("/end", response_model=SessionResponse)
def end_session(
    payload: SessionEndRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Terminates an active protection session."""
    session_obj = db.query(SessionModel).filter(
        SessionModel.session_token == payload.session_token,
        SessionModel.user_id == current_user.id
    ).first()

    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or does not belong to current user."
        )

    session_obj.is_active = False
    session_obj.ended_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session_obj)

    AuditService.log(
        db=db,
        action="SESSION_ENDED",
        resource_type="SESSION",
        resource_id=str(session_obj.id),
        user_id=current_user.id,
        details={"session_token_prefix": payload.session_token[:10]}
    )

    return session_obj
