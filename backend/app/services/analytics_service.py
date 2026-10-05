from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.protected_site import ProtectedSite
from app.models.fingerprint_event import FingerprintEvent
from app.models.masking_event import MaskingEvent
from app.models.analytics_event import AnalyticsEvent
from app.schemas.dashboard import (
    DashboardOverviewResponse, TimelinePoint, SignalStat, RiskDistribution
)
from app.services.risk_engine import RiskEngine

class AnalyticsService:
    @staticmethod
    def get_overview(db: Session, user_id: Optional[UUID] = None) -> DashboardOverviewResponse:
        # 1. Protected sites & active sites
        site_query = db.query(ProtectedSite)
        if user_id:
            site_query = site_query.filter(ProtectedSite.user_id == user_id)
        protected_sites = site_query.count()
        active_sites = site_query.filter(ProtectedSite.enabled == True).count()

        # 2. Scans today
        now = datetime.now(timezone.utc)
        today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        
        events_today_query = db.query(func.count(AnalyticsEvent.id)).filter(AnalyticsEvent.timestamp >= today_start)
        if user_id:
            events_today_query = events_today_query.filter(AnalyticsEvent.user_id == user_id)
        scans_today = events_today_query.scalar() or 0

        # 3. Fingerprint probes
        probes_query = db.query(func.count(FingerprintEvent.id))
        if user_id:
            probes_query = probes_query.filter(FingerprintEvent.user_id == user_id)
        fingerprint_probes = probes_query.scalar() or 0

        # 4. Signals detected & masked
        signals_detected = fingerprint_probes
        masked_query = db.query(func.count(MaskingEvent.id))
        if user_id:
            masked_query = masked_query.filter(MaskingEvent.user_id == user_id)
        signals_masked = masked_query.scalar() or 0

        # 5. High risk events
        high_risk_query = db.query(func.count(FingerprintEvent.id)).filter(FingerprintEvent.risk_score >= 70.0)
        if user_id:
            high_risk_query = high_risk_query.filter(FingerprintEvent.user_id == user_id)
        high_risk_events = high_risk_query.scalar() or 0

        # 6. Average risks and consistency
        avg_before_q = db.query(func.avg(MaskingEvent.risk_before))
        avg_after_q = db.query(func.avg(MaskingEvent.risk_after))
        avg_cons_q = db.query(func.avg(FingerprintEvent.consistency_score))

        if user_id:
            avg_before_q = avg_before_q.filter(MaskingEvent.user_id == user_id)
            avg_after_q = avg_after_q.filter(MaskingEvent.user_id == user_id)
            avg_cons_q = avg_cons_q.filter(FingerprintEvent.user_id == user_id)

        raw_before = avg_before_q.scalar()
        raw_after = avg_after_q.scalar()
        raw_cons = avg_cons_q.scalar()

        avg_risk_before = round(float(raw_before), 1) if raw_before is not None else 0.0
        avg_risk_after = round(float(raw_after), 1) if raw_after is not None else 0.0
        average_consistency = round(float(raw_cons), 1) if raw_cons is not None else 100.0

        protection_rate = 0.0
        if fingerprint_probes > 0:
            protection_rate = round(min(100.0, (signals_masked / fingerprint_probes) * 100.0), 1)
        elif signals_masked > 0:
            protection_rate = 100.0

        return DashboardOverviewResponse(
            protected_sites=protected_sites,
            active_sites=active_sites,
            scans_today=scans_today,
            fingerprint_probes=fingerprint_probes,
            signals_detected=signals_detected,
            signals_masked=signals_masked,
            high_risk_events=high_risk_events,
            average_risk_before=avg_risk_before,
            average_risk_after=avg_risk_after,
            average_consistency=average_consistency,
            protection_rate=protection_rate
        )

    @staticmethod
    def get_timeline(db: Session, user_id: Optional[UUID] = None, hours: int = 24) -> List[TimelinePoint]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Query recent fingerprint events
        query = db.query(
            FingerprintEvent.timestamp,
            FingerprintEvent.risk_score
        ).filter(FingerprintEvent.timestamp >= cutoff)
        
        if user_id:
            query = query.filter(FingerprintEvent.user_id == user_id)
            
        events = query.order_by(FingerprintEvent.timestamp.asc()).all()
        if not events:
            return []

        # Group by 1-hour or chronological buckets
        points = []
        for ev in events[-30:]: # Return recent chronological timeline points
            points.append(TimelinePoint(
                timestamp=ev.timestamp,
                probes_count=1,
                masked_count=1,
                avg_risk=round(ev.risk_score, 1)
            ))
        return points

    @staticmethod
    def get_signals_breakdown(db: Session, user_id: Optional[UUID] = None) -> List[SignalStat]:
        stats = []
        for signal_name, conf in RiskEngine.SIGNAL_CLASSIFICATION.items():
            probe_q = db.query(func.count(FingerprintEvent.id)).filter(FingerprintEvent.signal_type == signal_name)
            mask_q = db.query(func.count(MaskingEvent.id)).filter(MaskingEvent.signal_type == signal_name)
            if user_id:
                probe_q = probe_q.filter(FingerprintEvent.user_id == user_id)
                mask_q = mask_q.filter(MaskingEvent.user_id == user_id)
            
            cnt = probe_q.scalar() or 0
            masked_cnt = mask_q.scalar() or 0

            stats.append(SignalStat(
                signal=signal_name,
                count=cnt,
                masked_count=masked_cnt,
                risk_level=conf["level"],
                impact_weight=conf["max_impact"]
            ))
        return stats

    @staticmethod
    def get_risk_distribution(db: Session, user_id: Optional[UUID] = None) -> RiskDistribution:
        q = db.query(FingerprintEvent.risk_score)
        if user_id:
            q = q.filter(FingerprintEvent.user_id == user_id)
        scores = [row[0] for row in q.all()]

        if not scores:
            return RiskDistribution(
                low_count=0,
                medium_count=0,
                high_count=0,
                critical_count=0,
                average_score=0.0
            )

        low = sum(1 for s in scores if s < 35.0)
        med = sum(1 for s in scores if 35.0 <= s < 60.0)
        high = sum(1 for s in scores if 60.0 <= s < 80.0)
        crit = sum(1 for s in scores if s >= 80.0)
        avg = round(sum(scores) / len(scores), 1)

        return RiskDistribution(
            low_count=low,
            medium_count=med,
            high_count=high,
            critical_count=crit,
            average_score=avg
        )
