import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import GUID, TimestampMixin

if TYPE_CHECKING:
    from app.models.session import SessionModel
    from app.models.protected_site import ProtectedSite
    from app.models.policy import Policy
    from app.models.audit_log import AuditLog

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    sessions: Mapped[List["SessionModel"]] = relationship("SessionModel", back_populates="user", cascade="all, delete-orphan")
    protected_sites: Mapped[List["ProtectedSite"]] = relationship("ProtectedSite", back_populates="user", cascade="all, delete-orphan")
    policies: Mapped[List["Policy"]] = relationship("Policy", back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")
