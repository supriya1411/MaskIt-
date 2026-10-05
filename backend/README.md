# MaskIt — AI-Powered Browser Fingerprint Privacy Shield (Backend)

MaskIt is a defense-grade browser fingerprint privacy protection system. The browser extension performs local fingerprint interception and masking on the client device, while this high-performance FastAPI + PostgreSQL + Redis backend coordinates protection rules, privacy-safe telemetry, deterministic risk analysis, cross-signal browser consistency validation, audit logging, and live WebSocket streaming.

---

## Architecture

```
Browser Extension (Local Masking)
        │ (Privacy-Safe Signals)
        ▼
   FastAPI Gateway
   ├── Auth & JWT
   ├── 🛡️ Protect My Data (Domain Rules)
   ├── Deterministic Risk Engine (0-100)
   ├── Cross-Signal Consistency Engine
   ├── ML/Statistical Anomaly Detector
   └── Redis Rate-Limiting & Caching
        │
        ├──► PostgreSQL (UUID, Partitioned Events, Audit Logs)
        └──► WebSocket Stream (/ws/dashboard) ──► Live React Dashboard
```

---

## 1. Folder Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI application entrypoint & middleware
│   ├── config.py                # Pydantic v2 settings from environment
│   ├── database.py              # SQLAlchemy 2 engine & session generator
│   ├── dependencies.py          # Auth bearer tokens, rate limits, DB sessions
│   ├── models/                  # SQLAlchemy 2 relational models
│   │   ├── base.py              # Universal GUID & Timestamp mixins
│   │   ├── user.py              # User authentication records
│   │   ├── session.py           # Active protection sessions
│   │   ├── protected_site.py    # Registered domain protection rules
│   │   ├── policy.py            # Static, Sampled & AI masking policies
│   │   ├── fingerprint_event.py # Fingerprint probe interception events
│   │   ├── masking_event.py     # Applied noise & masking events
│   │   ├── analytics_event.py   # Aggregated telemetry events
│   │   └── audit_log.py         # Immutable privacy-safe audit trails
│   ├── schemas/                 # Pydantic v2 validation models
│   │   ├── auth.py              # Register, Login & JWT tokens
│   │   ├── session.py           # Session lifecycle
│   │   ├── protection.py        # Site rules, analytics & summaries
│   │   ├── policy.py            # Policy CRUD schemas
│   │   ├── fingerprint.py       # Privacy-safe signal analysis schemas
│   │   ├── event.py             # Telemetry & Extension sync schemas
│   │   └── dashboard.py         # Live analytics & timeline metrics
│   ├── routers/                 # Modular API endpoints
│   │   ├── auth.py              # /api/v1/auth
│   │   ├── session.py           # /api/v1/session
│   │   ├── protection.py        # /api/v1/protection
│   │   ├── extension.py         # /api/v1/extension
│   │   ├── fingerprint.py       # /api/v1/fingerprint
│   │   ├── policies.py          # /api/v1/policies
│   │   ├── events.py            # /api/v1/events
│   │   ├── dashboard.py         # /api/v1/dashboard
│   │   ├── audit.py             # /api/v1/audit
│   │   ├── health.py            # /health
│   │   └── websocket.py         # /ws/dashboard
│   ├── services/                # Business logic & algorithms
│   │   ├── auth_service.py       # User auth, hashing & token issuance
│   │   ├── risk_engine.py        # Deterministic 0-100 risk scorer
│   │   ├── consistency_engine.py # Cross-attribute browser validator
│   │   ├── protection_service.py # Domain rules & SQL aggregation
│   │   ├── audit_service.py      # Privacy-by-design audit logger
│   │   ├── analytics_service.py  # Zero-fake-data PostgreSQL queries
│   │   └── redis_service.py      # Resilient caching & rate limiter
│   ├── ml/                      # Machine learning subsystem
│   │   ├── feature_engineering.py # Signal vectorization
│   │   ├── anomaly_detector.py   # Isolation Forest / centroid fallback
│   │   └── profile_generator.py  # Consistent synthetic profiles
│   └── utils/                   # Shared utilities
│       ├── security.py          # Password hashing & JWT
│       ├── validators.py        # RFC domain validation & sanitization
│       └── privacy.py           # SHA-256 hashing & entropy calculation
├── alembic/                     # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py
├── alembic.ini
├── tests/                       # Comprehensive pytest suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_domain_validation.py
│   ├── test_risk_calculation.py
│   ├── test_signal_classification.py
│   ├── test_policies.py
│   ├── test_protected_sites.py
│   ├── test_events.py
│   ├── test_dashboard.py
│   ├── test_consistency.py
│   └── test_websocket.py
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── API_CONTRACT.md
├── frontend-example.js
└── README.md
```

---

## 2. Setup Commands

### Local Environment Setup
```bash
# 1. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install production and development dependencies
pip install -r requirements.txt
```

---

## 3. Environment Configuration (.env)

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Key environment variables:
- `DATABASE_URL`: PostgreSQL connection string (`postgresql://maskit_user:maskit_password@localhost:5432/maskit_db`). Supports `sqlite:///./maskit.db` for local quick start.
- `REDIS_URL`: Redis URI (`redis://localhost:6379/0`). Automatically falls back to in-memory mode if Redis is temporarily unreachable.
- `JWT_SECRET`: 256-bit secret key for signing tokens.
- `DEMO_MODE`: `false` ensures only real extension events are processed.

---

## 4. Database Migration Commands

```bash
# Apply all database migrations to latest revision
alembic upgrade head

# Rollback one migration revision if needed
alembic downgrade -1

# Create a new migration revision
alembic revision --autogenerate -m "Add new telemetry columns"
```

---

## 5. Running the Backend

### Direct Uvicorn Run:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive documentation will be available at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## 6. Docker Commands

Run the full stack (FastAPI backend + PostgreSQL 16 + Redis 7):
```bash
# Start all containers in background
docker compose up --build -d

# Check service health
docker compose ps

# View backend logs
docker compose logs -f backend

# Stop all containers
docker compose down
```

---

## 7. Testing Commands

Run the complete test suite with `pytest`:
```bash
# Run all tests
pytest -v

# Run with coverage report
pytest --cov=app tests/

# Run specific test file
pytest tests/test_risk_calculation.py -v
```

---

## 8. Hackathon Live Demo Walkthrough

1. **User opens MaskIt Dashboard**: Real metrics load from PostgreSQL (starts clean with 0 fake data).
2. **User Clicks "Protect My Data"**: Types `youtube.com` into domain box and clicks **PROTECT THIS SITE**.
3. **Backend Stores Rule**: Creates a `ProtectedSite` row with UUID in PostgreSQL.
4. **Extension Syncs Rule**: The browser extension calls `GET /api/v1/extension/protected-sites` and caches `youtube.com`.
5. **User Visits `youtube.com`**: The extension detects Canvas (`toDataURL`), WebGL (`getParameter`), and AudioContext probes.
6. **Local Protection Applied**: Real noise is injected client-side into canvas buffers and WebGL renderer is normalized.
7. **Telemetry Ingested**: Extension sends privacy-safe signal hashes to `POST /api/v1/extension/event`.
8. **Deterministic Risk Scored**: Backend calculates Risk Before (e.g. 84 HIGH) and Risk After (e.g. 21 LOW), Consistency Score (98%).
9. **WebSocket Emission**: Backend broadcasts `SITE_PROTECTED` / `MASK_APPLIED` event via `/ws/dashboard`.
10. **Live Dashboard Updates**: Counters, risk gauge, and timeline update in real time with zero page refresh!
