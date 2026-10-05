import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import GUID

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    domain: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False) # FINGERPRINT_PROBE, ATTRIBUTE_DETECTED, MASK_APPLIED, etc.
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="EXTENSION", nullable=False) # EXTENSION, DASHBOARD, DEMO
    privacy_safe_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
