from uuid import UUID
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.utils.privacy import sanitize_privacy_metadata

class AuditService:
    @staticmethod
    def log(
        db: Session,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Creates an immutable audit record ensuring zero raw fingerprint or sensitive PII is logged.
        """
        clean_details = sanitize_privacy_metadata(details) if details else None
        
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            details=clean_details,
            ip_address=ip_address
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry
