"""
MaskIt Demo Data Seeder
=======================
Run this script ONCE to populate the local SQLite database with
realistic demo telemetry events so the dashboard shows real metrics.

Usage:
    cd backend
    python seed_demo_data.py
"""

import sys
import os
import random
from datetime import datetime, timezone, timedelta

# Make sure app modules are importable
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app.models.base import Base
from app.models.fingerprint_event import FingerprintEvent
from app.models.masking_event import MaskingEvent
from app.models.analytics_event import AnalyticsEvent
from app.models.protected_site import ProtectedSite
from app.models.user import User

# Create all tables if they don't exist yet
Base.metadata.create_all(bind=engine)

DOMAINS = [
    "youtube.com", "reddit.com", "twitter.com", "facebook.com",
    "instagram.com", "tiktok.com", "amazon.com", "google.com",
    "linkedin.com", "github.com", "stackoverflow.com", "netflix.com",
]

SIGNALS = [
    ("CANVAS", "HIGH", 35),
    ("WEBGL", "HIGH", 32),
    ("AUDIO", "HIGH", 30),
    ("SCREEN", "MEDIUM", 20),
    ("HARDWARE", "MEDIUM", 18),
    ("TIMEZONE", "LOW", 10),
    ("NAVIGATOR", "LOW", 8),
    ("MEDIA_DEVICES", "LOW", 6),
]

SIGNAL_REMAP = {
    "Canvas 2D Hash": "CANVAS",
    "WebGL Renderer": "WEBGL",
    "AudioContext DSP": "AUDIO",
    "Screen & DPI": "SCREEN",
    "Hardware Concurrency": "HARDWARE",
    "Timezone Offset": "TIMEZONE",
    "Navigator Platform": "NAVIGATOR",
    "Battery Status": "MEDIA_DEVICES",
}

ACTIONS = ["MASKED", "NOISE_INJECTED", "NORMALIZED", "BLOCKED"]

def rand_ts(hours_ago_max: int = 72) -> datetime:
    delta = timedelta(seconds=random.randint(60, hours_ago_max * 3600))
    return datetime.now(timezone.utc) - delta

def seed():
    db = SessionLocal()
    try:
        demo_user = db.query(User).filter(User.email == "evaluator@maskit.dev").first()
        demo_user_id = demo_user.id if demo_user else None

        # Normalize legacy display names and attach orphan telemetry to the demo user
        remapped = 0
        for model in (FingerprintEvent, MaskingEvent):
            rows = db.query(model).all()
            for row in rows:
                new_name = SIGNAL_REMAP.get(row.signal_type)
                if new_name:
                    row.signal_type = new_name
                    remapped += 1
                if demo_user_id and row.user_id is None:
                    row.user_id = demo_user_id
        for row in db.query(AnalyticsEvent).all():
            if demo_user_id and row.user_id is None:
                row.user_id = demo_user_id
            meta = row.privacy_safe_metadata or {}
            if meta.get("signal_type") in SIGNAL_REMAP:
                meta = {**meta, "signal_type": SIGNAL_REMAP[meta["signal_type"]]}
                row.privacy_safe_metadata = meta
        db.commit()
        if remapped:
            print(f"Normalized {remapped} legacy signal labels.")

        seeded_sites = 0
        if demo_user_id:
            from app.services.protection_service import ProtectionService
            policy = ProtectionService.get_or_create_default_policy(db, demo_user_id)
            for domain in DOMAINS:
                site = db.query(ProtectedSite).filter(
                    ProtectedSite.user_id == demo_user_id,
                    ProtectedSite.domain == domain,
                ).first()
                if site:
                    continue
                db.add(ProtectedSite(
                    user_id=demo_user_id,
                    domain=domain,
                    enabled=True,
                    policy_id=policy.id,
                    last_activity_at=rand_ts(24),
                ))
                seeded_sites += 1
            db.commit()
            if seeded_sites:
                print(f"Added {seeded_sites} protected sites for evaluator@maskit.dev")
        else:
            print("  (Skipping protected sites — demo user not created yet. Use Instant Demo once, then re-run seeder.)")

        existing_events = db.query(FingerprintEvent).count()
        if existing_events >= 50:
            print(f"Database already has {existing_events} fingerprint events. Skipping new telemetry seed.")
            return

        print("Seeding demo data ...")


        # Fingerprint + Masking + Analytics Events
        fp_count = 0
        mask_count = 0
        analytics_count = 0

        for _ in range(120):
            domain = random.choice(DOMAINS)
            signal_name, level, base_risk = random.choice(SIGNALS)
            ts = rand_ts(72)

            risk_before = random.uniform(55, 95)
            risk_after = random.uniform(12, 38)
            consistency = random.uniform(92, 99.5)
            action = random.choice(ACTIONS)

            fp_ev = FingerprintEvent(
                user_id=demo_user_id,
                session_id=None,
                domain=domain,
                signal_type=signal_name,
                probe_method="JS_API_PROBE",
                risk_score=round(risk_before, 1),
                consistency_score=round(consistency, 1),
                timestamp=ts,
            )
            db.add(fp_ev)
            fp_count += 1

            mask_ev = MaskingEvent(
                user_id=demo_user_id,
                session_id=fp_ev.session_id,
                domain=domain,
                signal_type=signal_name,
                action=action,
                risk_before=round(risk_before, 1),
                risk_after=round(risk_after, 1),
                consistency_before=round(consistency, 1),
                consistency_after=round(consistency, 1),
                timestamp=ts,
            )
            db.add(mask_ev)
            mask_count += 1

            analytics_ev = AnalyticsEvent(
                user_id=demo_user_id,
                domain=domain,
                event_type="PROBE_MASKED",
                risk_score=round(risk_after, 1),
                source="WEB_EXTENSION",
                privacy_safe_metadata={"signal_type": signal_name, "action": action},
                timestamp=ts,
            )
            db.add(analytics_ev)
            analytics_count += 1

        db.commit()

        print(f"Done!")
        print(f"  {seeded_sites} protected sites added")
        print(f"  {fp_count} fingerprint probe events")
        print(f"  {mask_count} masking events")
        print(f"  {analytics_count} analytics events")
        print()
        print("Restart the backend and refresh the dashboard to see real data.")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
