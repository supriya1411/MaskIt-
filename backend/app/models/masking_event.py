import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import GUID

if TYPE_CHECKING:
    from app.models.policy import Policy

class MaskingEvent(Base):
    __tablename__ = "masking_events"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    domain: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    signal_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), default="MASKED", nullable=False) # MASKED, NOISE_INJECTED, NORMALIZED, BLOCKED
    risk_before: Mapped[float] = mapped_column(Float, nullable=False)
    risk_after: Mapped[float] = mapped_column(Float, nullable=False)
    consistency_before: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    consistency_after: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    policy_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("policies.id", ondelete="SET NULL"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False)

    policy: Mapped[Optional["Policy"]] = relationship("Policy", back_populates="masking_events")
