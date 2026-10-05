import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import GUID

if TYPE_CHECKING:
    from app.models.user import User

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False) # LOGIN, LOGOUT, REGISTER, SITE_PROTECTED, etc.
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False) # USER, SITE, POLICY, EXTENSION
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True) # Privacy-safe details only
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
