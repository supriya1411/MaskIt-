import uuid
from typing import List, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, select

from app.models.protected_site import ProtectedSite
from app.models.policy import Policy
from app.models.fingerprint_event import FingerprintEvent
from app.models.masking_event import MaskingEvent
from app.models.analytics_event import AnalyticsEvent
from app.schemas.protection import ProtectionSummary, SiteAnalytics
from app.utils.validators import sanitize_and_validate_domain

class ProtectionService:
    @staticmethod
    def get_or_create_default_policy(db: Session, user_id: uuid.UUID) -> Policy:
        policy = db.query(Policy).filter(Policy.user_id == user_id, Policy.name == "Default Privacy Shield").first()
        if not policy:
            policy = Policy(
                user_id=user_id,
                name="Default Privacy Shield",
                enabled=True,
                masking_strength="BALANCED",
                protected_signals=["CANVAS", "WEBGL", "NAVIGATOR", "SCREEN", "TIMEZONE", "FONTS", "MEDIA_DEVICES", "AUDIO", "HARDWARE"],
                strategy="DISTRIBUTION_SAMPLED",
                session_persistence=True,
                rules_json={
                    "mask_canvas": True,
                    "mask_webgl": True,
                    "mask_navigator": True,
                    "mask_screen": True,
                    "mask_timezone": True,
                    "mask_audio": True,
                    "noise_level": 0.05
                }
            )
            db.add(policy)
            db.commit()
            db.refresh(policy)
        return policy

    @staticmethod
    def add_site(db: Session, user_id: uuid.UUID, raw_domain: str, policy_id: Optional[uuid.UUID] = None) -> ProtectedSite:
        domain = sanitize_and_validate_domain(raw_domain)

        # Check if site already exists for this user
        existing = db.query(ProtectedSite).filter(
            ProtectedSite.user_id == user_id,
            ProtectedSite.domain == domain
        ).first()

        if existing:
            # Re-enable if disabled
            existing.enabled = True
            if policy_id:
                existing.policy_id = policy_id
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            return existing

        if not policy_id:
            default_pol = ProtectionService.get_or_create_default_policy(db, user_id)
            policy_id = default_pol.id

        new_site = ProtectedSite(
            user_id=user_id,
            domain=domain,
            enabled=True,
            policy_id=policy_id
        )
        db.add(new_site)
        db.commit()
        db.refresh(new_site)
        return new_site

    @staticmethod
    def get_user_sites(db: Session, user_id: uuid.UUID) -> List[ProtectedSite]:
        return db.query(ProtectedSite).filter(ProtectedSite.user_id == user_id).order_by(ProtectedSite.created_at.desc()).all()

    @staticmethod
    def get_site(db: Session, user_id: uuid.UUID, site_id: uuid.UUID) -> Optional[ProtectedSite]:
        return db.query(ProtectedSite).filter(ProtectedSite.user_id == user_id, ProtectedSite.id == site_id).first()

    @staticmethod
    def update_site(db: Session, user_id: uuid.UUID, site_id: uuid.UUID, enabled: Optional[bool] = None, policy_id: Optional[uuid.UUID] = None) -> Optional[ProtectedSite]:
        site = db.query(ProtectedSite).filter(ProtectedSite.user_id == user_id, ProtectedSite.id == site_id).first()
        if not site:
            return None
        if enabled is not None:
            site.enabled = enabled
        if policy_id is not None:
            site.policy_id = policy_id
        site.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(site)
        return site

    @staticmethod
    def delete_site(db: Session, user_id: uuid.UUID, site_id: uuid.UUID) -> bool:
        site = db.query(ProtectedSite).filter(ProtectedSite.user_id == user_id, ProtectedSite.id == site_id).first()
        if not site:
            return False
        db.delete(site)
        db.commit()
        return True

    @staticmethod
    def get_summary(db: Session, user_id: uuid.UUID) -> ProtectionSummary:
        total_sites = db.query(func.count(ProtectedSite.id)).filter(ProtectedSite.user_id == user_id).scalar() or 0
        active_sites = db.query(func.count(ProtectedSite.id)).filter(ProtectedSite.user_id == user_id, ProtectedSite.enabled == True).scalar() or 0
        
        # Events calculations from PostgreSQL
        total_events = db.query(func.count(AnalyticsEvent.id)).filter(AnalyticsEvent.user_id == user_id).scalar() or 0
        signals_protected = db.query(func.count(MaskingEvent.id)).filter(MaskingEvent.user_id == user_id).scalar() or 0
        high_risk_probes = db.query(func.count(FingerprintEvent.id)).filter(
            FingerprintEvent.user_id == user_id,
            FingerprintEvent.risk_score >= 70.0
        ).scalar() or 0

        avg_risk_before = db.query(func.avg(MaskingEvent.risk_before)).filter(MaskingEvent.user_id == user_id).scalar()
        avg_risk_after = db.query(func.avg(MaskingEvent.risk_after)).filter(MaskingEvent.user_id == user_id).scalar()

        avg_before = round(float(avg_risk_before), 1) if avg_risk_before is not None else 0.0
        avg_after = round(float(avg_risk_after), 1) if avg_risk_after is not None else 0.0

        protection_rate = 0.0
        if signals_protected > 0 or total_events > 0:
            total_probes = db.query(func.count(FingerprintEvent.id)).filter(FingerprintEvent.user_id == user_id).scalar() or 0
            if total_probes > 0:
                protection_rate = round(min(100.0, (signals_protected / total_probes) * 100.0), 1)
            else:
                protection_rate = 100.0 if signals_protected > 0 else 0.0

        return ProtectionSummary(
            protected_sites=total_sites,
            active_sites=active_sites,
            protection_events=total_events,
            signals_protected=signals_protected,
            high_risk_probes=high_risk_probes,
            average_risk_before=avg_before,
            average_risk_after=avg_after,
            protection_rate=protection_rate
        )

    @staticmethod
    def get_site_analytics(db: Session, user_id: uuid.UUID, site_id: uuid.UUID) -> Optional[SiteAnalytics]:
        site = db.query(ProtectedSite).filter(ProtectedSite.user_id == user_id, ProtectedSite.id == site_id).first()
        if not site:
            return None

        domain = site.domain
        total_events = db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.domain == domain,
            AnalyticsEvent.user_id == user_id
        ).scalar() or 0

        probes = db.query(func.count(FingerprintEvent.id)).filter(
            FingerprintEvent.domain == domain,
            FingerprintEvent.user_id == user_id
        ).scalar() or 0

        signals_masked = db.query(func.count(MaskingEvent.id)).filter(
            MaskingEvent.domain == domain,
            MaskingEvent.user_id == user_id
        ).scalar() or 0

        # Per signal counts
        def count_signal(sig_name: str) -> int:
            return db.query(func.count(FingerprintEvent.id)).filter(
                FingerprintEvent.domain == domain,
                FingerprintEvent.user_id == user_id,
                FingerprintEvent.signal_type == sig_name
            ).scalar() or 0

        canvas_cnt = count_signal("CANVAS")
        webgl_cnt = count_signal("WEBGL")
        nav_cnt = count_signal("NAVIGATOR")
        screen_cnt = count_signal("SCREEN")
        tz_cnt = count_signal("TIMEZONE")
        media_cnt = count_signal("MEDIA_DEVICES")
        audio_cnt = count_signal("AUDIO")

        avg_before = db.query(func.avg(MaskingEvent.risk_before)).filter(
            MaskingEvent.domain == domain,
            MaskingEvent.user_id == user_id
        ).scalar()
        avg_after = db.query(func.avg(MaskingEvent.risk_after)).filter(
            MaskingEvent.domain == domain,
            MaskingEvent.user_id == user_id
        ).scalar()
        avg_consistency = db.query(func.avg(FingerprintEvent.consistency_score)).filter(
            FingerprintEvent.domain == domain,
            FingerprintEvent.user_id == user_id
        ).scalar()

        return SiteAnalytics(
            site_id=site.id,
            domain=site.domain,
            enabled=site.enabled,
            events=total_events,
            fingerprint_probes=probes,
            canvas_events=canvas_cnt,
            webgl_events=webgl_cnt,
            navigator_events=nav_cnt,
            screen_events=screen_cnt,
            timezone_events=tz_cnt,
            media_devices_events=media_cnt,
            audio_events=audio_cnt,
            signals_masked=signals_masked,
            risk_before=round(float(avg_before), 1) if avg_before is not None else 0.0,
            risk_after=round(float(avg_after), 1) if avg_after is not None else 0.0,
            consistency_score=round(float(avg_consistency), 1) if avg_consistency is not None else 100.0,
            last_activity=site.last_activity_at
        )
