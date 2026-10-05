from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_optional_current_user
from app.models.user import User
from app.schemas.dashboard import (
    DashboardOverviewResponse, TimelinePoint, SignalStat, RiskDistribution
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/dashboard", tags=["Live Dashboard Analytics"])

@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns real PostgreSQL aggregated live metrics:
    protected sites, active sites, scans today, probes, signals detected, masked,
    average risk before/after, consistency, and protection rate.
    Zero fake or hardcoded numbers.
    """
    user_id = current_user.id if current_user else None
    return AnalyticsService.get_overview(db=db, user_id=user_id)

@router.get("/timeline", response_model=List[TimelinePoint])
def get_dashboard_timeline(
    hours: int = 24,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Returns actual time-series telemetry buckets computed from PostgreSQL."""
    user_id = current_user.id if current_user else None
    return AnalyticsService.get_timeline(db=db, user_id=user_id, hours=hours)

@router.get("/signals", response_model=List[SignalStat])
def get_dashboard_signals(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Returns live signal probe vs masking breakdowns per fingerprint vector."""
    user_id = current_user.id if current_user else None
    return AnalyticsService.get_signals_breakdown(db=db, user_id=user_id)

@router.get("/risk", response_model=RiskDistribution)
def get_dashboard_risk_distribution(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Returns categorical risk histogram computed from stored fingerprint events."""
    user_id = current_user.id if current_user else None
    return AnalyticsService.get_risk_distribution(db=db, user_id=user_id)
