from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.dashboard import AuditLogResponse

router = APIRouter(prefix="/audit", tags=["Audit Log"])

@router.get("", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns immutable audit logs tracking logins, logouts, policy changes,
    and site protection events. Strictly privacy-safe.
    """
    logs = db.query(AuditLog).filter(
        (AuditLog.user_id == current_user.id) | (AuditLog.user_id == None)
    ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return logs
