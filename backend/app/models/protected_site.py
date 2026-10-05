import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import GUID, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.policy import Policy

class ProtectedSite(Base, TimestampMixin):
    __tablename__ = "protected_sites"
    __table_args__ = (
        UniqueConstraint("user_id", "domain", name="uq_user_domain"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    policy_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("policies.id", ondelete="SET NULL"), nullable=True)
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="protected_sites")
    policy: Mapped[Optional["Policy"]] = relationship("Policy", back_populates="protected_sites")
