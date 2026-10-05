from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class PolicyBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    enabled: bool = True
    masking_strength: str = Field(default="BALANCED", description="LOW, BALANCED, AGGRESSIVE, STEALTH")
    protected_signals: List[str] = Field(
        default=["CANVAS", "WEBGL", "NAVIGATOR", "SCREEN", "TIMEZONE", "FONTS", "MEDIA_DEVICES", "AUDIO", "HARDWARE"]
    )
    strategy: str = Field(default="DISTRIBUTION_SAMPLED", description="STATIC, DISTRIBUTION_SAMPLED, AI_GENERATED")
    session_persistence: bool = True
    rules_json: Dict[str, Any] = Field(
        default_factory=lambda: {
            "mask_canvas": True,
            "mask_webgl": True,
            "mask_navigator": True,
            "mask_screen": True,
            "mask_timezone": True,
            "mask_audio": True,
            "noise_level": 0.05
        }
    )

class PolicyCreate(PolicyBase):
    pass

class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    enabled: Optional[bool] = None
    masking_strength: Optional[str] = None
    protected_signals: Optional[List[str]] = None
    strategy: Optional[str] = None
    session_persistence: Optional[bool] = None
    rules_json: Optional[Dict[str, Any]] = None

class PolicyResponse(PolicyBase):
    id: UUID
    user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
