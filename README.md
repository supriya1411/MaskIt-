# MaskIt — AI Browser Fingerprint Privacy Shield (Frontend)

MaskIt is a defense-grade browser fingerprint privacy protection system. This frontend is built with React 19, TypeScript, Tailwind CSS, Framer Motion, Recharts, and Zustand, communicating with the existing FastAPI + PostgreSQL + Redis backend.

---

## 1. Frontend Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Compile production build
npm run build
```

---

## 2. Environment Configuration (`.env`)

Configure the environment variables in `.env` (or see `.env.example`):

```ini
# Backend FastAPI REST URL
VITE_API_BASE_URL="http://localhost:8000/api/v1"

# Backend Real-Time WebSocket Endpoint
VITE_WS_URL="ws://localhost:8000/ws/dashboard"
```

---

## 3. Architecture & API Integration

The frontend connects directly to the existing backend without mock data or simulated responses:

| Feature | Backend Endpoint | Store / Component |
|---|---|---|
| **Authentication** | `POST /api/v1/auth/login`, `/register`, `/me` | `useAuthStore` |
| **Fingerprint Scanner** | `POST /api/v1/fingerprint/analyze` | `/scan` (`ScanBrowserPage`) |
| **Protect My Data** | `POST /api/v1/protection/sites` | `/protect` (`useProtectionStore`) |
| **Protected Sites** | `GET /api/v1/protection/sites` | `/sites` |
| **Site Analytics** | `GET /api/v1/protection/sites/{id}/analytics` | `/sites/:id` |
| **Live Telemetry Stream** | `WebSocket /ws/dashboard` | `/activity` (`dashboardWs`) |
| **Dashboard Overview** | `GET /api/v1/dashboard/overview` | `/dashboard` (`useDashboardStore`) |
| **Analytics Charts** | `GET /api/v1/dashboard/timeline`, `/signals`, `/risk` | `/analytics` |
| **Masking Policies** | `GET /api/v1/policies`, `PUT /api/v1/policies/{id}` | `/policies` (`usePolicyStore`) |
| **System Diagnostics** | `GET /health` | `/settings` |

---

## 4. WebSocket Configuration

Real-time telemetry is streamed via native WebSockets:
- Service: `src/services/websocket.ts`
- Handshake: Automatic reconnect on disconnect, periodic client ping/pong keepalive
- Subscriptions: Real-time event notifications toast on `/dashboard` and live stream list on `/activity`

---

## 5. Browser Extension Integration

The browser extension intercepts tracking scripts locally and queries the backend for domain rules:
1. Extension queries `GET /api/v1/extension/protected-sites`.
2. When a user visits `youtube.com`, the extension checks its local rule cache.
3. The extension hooks into `Canvas.toDataURL`, `WebGL.getParameter`, and `AudioContext` to inject entropy-preserving noise without breaking rendering.
4. Privacy-safe event telemetry is dispatched to `POST /api/v1/extension/event`, which triggers the real-time WebSocket broadcast received by the frontend.

---

## 6. Real Hackathon Demo Flow

1. **Open Landing Page** (`/`):
   - Review the problem, how it works, and the animated pipeline.
2. **Scan Your Browser** (`/scan`):
   - Click **START SCAN**. The frontend reads real client signals (screen, platform, WebGL GPU, canvas hash, timezone) and sends them to `POST /api/v1/fingerprint/analyze`.
   - Inspect the calculated deterministic risk score, detected signals, and consistency rating.
3. **Protect a Website** (`/protect`):
   - Enter `youtube.com` into **PROTECT MY DATA** and click **PROTECT THIS SITE**.
   - Confirmation is displayed once the backend returns `201 Created` and updates PostgreSQL.
4. **Inspect Protected Sites** (`/sites`):
   - View status, pause, resume, or open granular per-site analytics (`/sites/:id`).
5. **View Real-Time Stream** (`/activity`):
   - Live WebSocket events stream in with smooth Framer Motion entrance animations.
6. **Examine Policies & Analytics** (`/policies`, `/analytics`):
   - Inspect Recharts visualizations of real probe frequencies and configure Static, Distribution Sampled, or AI Generated noise strategies.
