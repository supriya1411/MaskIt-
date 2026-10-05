import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import GUID

class FingerprintEvent(Base):
    __tablename__ = "fingerprint_events"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    domain: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    signal_type: Mapped[str] = mapped_column(String(50), nullable=False) # CANVAS, WEBGL, NAVIGATOR, SCREEN, etc.
    probe_method: Mapped[str] = mapped_column(String(100), nullable=False) # toDataURL, getParameter, etc.
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    consistency_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    entropy_estimate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    privacy_safe_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
