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

# Create all tables if they don't exist yet
Base.metadata.create_all(bind=engine)

DOMAINS = [
    "youtube.com", "reddit.com", "twitter.com", "facebook.com",
    "instagram.com", "tiktok.com", "amazon.com", "google.com",
    "linkedin.com", "github.com", "stackoverflow.com", "netflix.com",
]

SIGNALS = [
    ("Canvas 2D Hash",      "HIGH",   35),
    ("WebGL Renderer",      "HIGH",   32),
    ("AudioContext DSP",    "HIGH",   30),
    ("Screen & DPI",        "MEDIUM", 20),
    ("Hardware Concurrency","MEDIUM", 18),
    ("Timezone Offset",     "LOW",    10),
    ("Navigator Platform",  "LOW",     8),
    ("Battery Status",      "LOW",     6),
]

ACTIONS = ["MASKED", "NOISE_INJECTED", "NORMALIZED", "BLOCKED"]

def rand_ts(hours_ago_max: int = 72) -> datetime:
    delta = timedelta(seconds=random.randint(60, hours_ago_max * 3600))
    return datetime.now(timezone.utc) - delta

def seed():
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(FingerprintEvent).count()
        if existing >= 50:
            print(f"Database already has {existing} fingerprint events. Skipping seed.")
            return

        print("Seeding demo data ...")

        # Skip ProtectedSite seeding (requires a valid user_id FK)
        seeded_sites = 0
        print("  (Skipping protected sites — requires a logged-in user)")


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
