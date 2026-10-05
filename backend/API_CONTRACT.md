# MaskIt API Specification & Contract (v1)

This document specifies the exact REST and WebSocket contracts for the **MaskIt AI-Powered Browser Fingerprint Privacy Shield** backend.

---

## Base URLs
- **REST API Prefix:** `/api/v1`
- **Health Check:** `/health`
- **Real-Time WebSocket:** `/ws/dashboard`
- **Interactive Swagger Docs:** `/docs`
- **Redoc:** `/redoc`

---

## Authentication & Security
All authenticated endpoints require an `Authorization` HTTP header with a Bearer JWT token:
```http
Authorization: Bearer <access_token>
```

Tokens are signed using `HS256` and expire in 60 minutes.

---

## 1. Authentication Endpoints

### `POST /api/v1/auth/register`
Creates a new user account and initializes default privacy policy rules.

**Request Body (`application/json`):**
```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

**Response (`201 Created`):**
```json
{
  "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2026-10-05T12:00:00Z",
  "updated_at": "2026-10-05T12:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Email already registered or invalid format.
- `422 Unprocessable Entity`: Password < 8 characters.

---

### `POST /api/v1/auth/login`
Authenticates user credentials and issues a JWT bearer token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

**Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
}
```

---

### `GET /api/v1/auth/me`
Retrieves authenticated user details.

**Headers:** `Authorization: Bearer <token>`

**Response (`200 OK`):**
```json
{
  "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2026-10-05T12:00:00Z",
  "updated_at": "2026-10-05T12:00:00Z"
}
```

---

## 2. Session Tracking

### `POST /api/v1/session/start`
Initializes a new active protection session for the extension or dashboard client.

**Request Body:**
```json
{
  "client_type": "EXTENSION",
  "user_agent": "Mozilla/5.0 ...",
  "ip_address": "127.0.0.1"
}
```

**Response (`201 Created`):**
```json
{
  "id": "22e7d704-5807-42f0-9b4e-86d7dbce7714",
  "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "session_token": "sess_8Fk2b0VqP...",
  "client_type": "EXTENSION",
  "is_active": true,
  "started_at": "2026-10-05T12:05:00Z",
  "ended_at": null,
  "last_seen_at": "2026-10-05T12:05:00Z"
}
```

### `POST /api/v1/session/end`
Terminates an active session.

**Request Body:**
```json
{
  "session_token": "sess_8Fk2b0VqP..."
}
```

---

## 3. Protect My Data (Core Feature)

### `POST /api/v1/protection/sites`
Adds a website/domain to the user's active protection list.

**Request Body:**
```json
{
  "domain": "youtube.com",
  "policy_id": "e81e1948-2898-466d-9653-56886e082855"
}
```

**Response (`201 Created`):**
```json
{
  "id": "a90b4d99-52e1-451f-bfa9-c70e28f0ee01",
  "domain": "youtube.com",
  "enabled": true,
  "status": "ACTIVE",
  "policy_id": "e81e1948-2898-466d-9653-56886e082855",
  "created_at": "2026-10-05T12:10:00Z",
  "updated_at": "2026-10-05T12:10:00Z",
  "last_activity_at": null
}
```

### `GET /api/v1/protection/sites`
Returns all protected domains registered by the authenticated user.

### `PUT /api/v1/protection/sites/{id}`
Updates site protection status (e.g. pause/resume) or modifies attached policy.

**Request Body:**
```json
{
  "enabled": false
}
```

### `DELETE /api/v1/protection/sites/{id}`
Removes domain protection rule. Returns `204 No Content`.

### `GET /api/v1/protection/summary`
Calculates real-time protection summary metrics from PostgreSQL:
```json
{
  "protected_sites": 4,
  "active_sites": 3,
  "protection_events": 142,
  "signals_protected": 128,
  "high_risk_probes": 56,
  "average_risk_before": 79.4,
  "average_risk_after": 22.1,
  "protection_rate": 90.1
}
```

### `GET /api/v1/protection/sites/{id}/analytics`
Returns granular telemetry and probe distribution for an individual protected site.

---

## 4. Extension Synchronization

### `POST /api/v1/extension/register`
Registers an installed browser extension instance.

**Request Body:**
```json
{
  "client_version": "1.0.4",
  "browser_type": "Chrome"
}
```

### `GET /api/v1/extension/config`
Retrieves full configuration and active domain rules to be cached locally by the extension:
```json
{
  "sync_interval": 30,
  "global_enabled": true,
  "sites": [
    {
      "domain": "youtube.com",
      "enabled": true,
      "policy": {
        "mask_canvas": true,
        "mask_webgl": true,
        "mask_navigator": true,
        "mask_screen": true,
        "mask_timezone": true,
        "mask_audio": true
      }
    }
  ]
}
```

### `POST /api/v1/extension/event`
Submits privacy-safe telemetry events when the local extension intercepts and masks a fingerprint attempt.

---

## 5. Fingerprint Analysis & Deterministic Risk Engine

### `POST /api/v1/fingerprint/analyze`
Evaluates privacy-safe attributes and returns an exact deterministic risk score (0–100) and OS/browser consistency assessment.

**Request Body:**
```json
{
  "domain": "youtube.com",
  "screen": {
    "width": 1920,
    "height": 1080,
    "color_depth": 24,
    "pixel_ratio": 1.0
  },
  "browser": {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36",
    "language": "en-US",
    "platform": "Win32",
    "vendor": "Google Inc."
  },
  "timezone": {
    "timezone": "America/New_York",
    "offset": -240
  },
  "hardware": {
    "cpu_cores": 16,
    "device_memory": 32.0
  },
  "webgl": {
    "vendor": "Google Inc. (NVIDIA)",
    "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 4070 Direct3D11)",
    "version": "WebGL 2.0"
  },
  "canvas_hash": "a5e8f4139c878b4a5323dd85303ec36e1ef6a721",
  "audio_hash": "b2c918349fa812039cf8794bbad819230571",
  "font_count": 84,
  "media_device_count": 4
}
```

**Response (`200 OK`):**
```json
{
  "risk_score": 83.2,
  "risk_level": "HIGH",
  "risk_factors": [
    {
      "signal": "CANVAS",
      "impact": 24.6,
      "reason": "Canvas rendering exposes exact GPU rasterization, anti-aliasing quirks, and subpixel font rendering."
    },
    {
      "signal": "WEBGL",
      "impact": 24.0,
      "reason": "Dedicated GPU vendor/renderer detected (ANGLE (NVIDIA, NVIDIA GeForce RTX)."
    },
    {
      "signal": "AUDIO",
      "impact": 16.0,
      "reason": "AudioContext frequency processing reveals underlying sound hardware and DSP oscillator differences."
    },
    {
      "signal": "HARDWARE",
      "impact": 10.0,
      "reason": "Hardware attributes exposed (16 cores, 32.0GB RAM). Unusual hardware increases trackability."
    },
    {
      "signal": "FONTS",
      "impact": 14.0,
      "reason": "84 distinct fonts detected. Large font libraries identify individual workstations."
    }
  ],
  "detected_signals": ["CANVAS", "WEBGL", "AUDIO", "HARDWARE", "FONTS", "MEDIA_DEVICES", "NAVIGATOR", "SCREEN", "TIMEZONE"],
  "recommendation": "ENABLE_STRONG_PROTECTION",
  "consistency_score": 100.0,
  "consistency_issues": []
}
```

---

## 6. Telemetry & Events

### `POST /api/v1/events`
Stores a privacy-safe telemetry event in PostgreSQL.

**Supported Event Types:**
- `FINGERPRINT_PROBE`
- `ATTRIBUTE_DETECTED`
- `MASK_APPLIED`
- `POLICY_CHANGED`
- `SESSION_STARTED`
- `SESSION_ENDED`
- `SITE_PROTECTED`
- `SITE_UNPROTECTED`

---

## 7. Live Dashboard Endpoints
All metrics are dynamically queried from PostgreSQL (no hardcoded data).

- `GET /api/v1/dashboard/overview`: High-level summary metrics.
- `GET /api/v1/dashboard/timeline`: Recent probe and masking frequency.
- `GET /api/v1/dashboard/signals`: Breakdown of probes and masks by signal vector.
- `GET /api/v1/dashboard/risk`: Distribution of risk scores across scans.

---

## 8. Real-Time Streaming WebSocket

### `WebSocket /ws/dashboard`
Connects a real-time event pipeline.
Whenever a domain probe or masking action occurs, the server automatically broadcasts:
```json
{
  "event": "SITE_PROTECTED",
  "domain": "youtube.com",
  "signal": "WEBGL",
  "action": "MASKED",
  "risk_before": 81.0,
  "risk_after": 21.0,
  "consistency": 98.0,
  "timestamp": "2026-10-05T12:15:30.123456Z"
}
```

**Client Ping:**
Send `{"action": "PING"}` to receive `{"event": "PONG"}`.

---

## 9. Health & Diagnostics

### `GET /health`
Returns connection status of PostgreSQL and Redis:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2026-10-05T12:00:00Z"
}
```
If PostgreSQL is unreachable, returns HTTP `503 Service Unavailable`.
If Redis is temporarily down, returns HTTP `200` with `redis: "fallback_memory_mode"`.
