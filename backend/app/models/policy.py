import uuid
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import GUID, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.protected_site import ProtectedSite
    from app.models.masking_event import MaskingEvent

class Policy(Base, TimestampMixin):
    __tablename__ = "policies"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    masking_strength: Mapped[str] = mapped_column(String(50), default="BALANCED", nullable=False) # LOW, BALANCED, AGGRESSIVE, STEALTH
    protected_signals: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False) # ["CANVAS", "WEBGL", "NAVIGATOR", "SCREEN", "TIMEZONE", "FONTS", "MEDIA_DEVICES", "AUDIO", "HARDWARE"]
    strategy: Mapped[str] = mapped_column(String(50), default="DISTRIBUTION_SAMPLED", nullable=False) # STATIC, DISTRIBUTION_SAMPLED, AI_GENERATED
    session_persistence: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rules_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="policies")
    protected_sites: Mapped[List["ProtectedSite"]] = relationship("ProtectedSite", back_populates="policy")
    masking_events: Mapped[List["MaskingEvent"]] = relationship("MaskingEvent", back_populates="policy")
