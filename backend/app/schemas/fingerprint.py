from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ScreenSignal(BaseModel):
    width: Optional[int] = Field(None, ge=1, le=16384)
    height: Optional[int] = Field(None, ge=1, le=16384)
    color_depth: Optional[int] = Field(None, ge=1, le=64)
    pixel_ratio: Optional[float] = Field(None, ge=0.1, le=10.0)

class BrowserSignal(BaseModel):
    user_agent: Optional[str] = Field(None, max_length=1000)
    language: Optional[str] = Field(None, max_length=50)
    languages: Optional[List[str]] = Field(default=None)
    platform: Optional[str] = Field(None, max_length=100)
    vendor: Optional[str] = Field(None, max_length=100)

class TimezoneSignal(BaseModel):
    timezone: Optional[str] = Field(None, max_length=100)
    offset: Optional[int] = Field(None, ge=-840, le=840)

class HardwareSignal(BaseModel):
    cpu_cores: Optional[int] = Field(None, ge=1, le=256)
    device_memory: Optional[float] = Field(None, ge=0.1, le=512.0)

class WebGLSignal(BaseModel):
    vendor: Optional[str] = Field(None, max_length=200)
    renderer: Optional[str] = Field(None, max_length=200)
    version: Optional[str] = Field(None, max_length=200)

class FingerprintAnalyzeRequest(BaseModel):
    domain: Optional[str] = Field(None, max_length=255)
    screen: Optional[ScreenSignal] = None
    browser: Optional[BrowserSignal] = None
    timezone: Optional[TimezoneSignal] = None
    hardware: Optional[HardwareSignal] = None
    webgl: Optional[WebGLSignal] = None
    canvas_hash: Optional[str] = Field(None, max_length=64, description="Hash only, never raw image")
    media_device_count: Optional[int] = Field(None, ge=0, le=100)
    audio_hash: Optional[str] = Field(None, max_length=64, description="Hash only, never raw buffer")
    font_count: Optional[int] = Field(None, ge=0, le=1000)

class RiskFactor(BaseModel):
    signal: str
    impact: float
    reason: str

class FingerprintAnalyzeResponse(BaseModel):
    risk_score: float
    risk_level: str # LOW, MEDIUM, HIGH
    risk_factors: List[RiskFactor]
    detected_signals: List[str]
    recommendation: str
    consistency_score: float
    consistency_issues: List[str]
