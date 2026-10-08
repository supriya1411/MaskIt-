# MaskIt — AI Browser Fingerprint Privacy Shield

MaskIt is an end-to-end browser fingerprint privacy shield and virtualization system. It combines a real-time **React 19 Dashboard**, a high-performance **FastAPI Backend**, deterministic **Risk & Policy Engine**, real-time **WebSocket streaming**, and a **Chrome Extension (Manifest V3)** with client-side canvas/WebGL/audio noise injection.

---

## ⚡ Quick Start: Running the Full Stack

You can run both frontend and backend concurrently or individually:

### Option A: Run Both Together (Recommended)
```bash
# 1. Install frontend dependencies
npm install

# 2. Setup backend virtualenv & dependencies
cd backend
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python seed_demo_data.py
cd ..

# 3. Start both services concurrently
npm run dev
```
- **Frontend Dashboard**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### Option B: Run Individually

**Backend (`backend/`):**
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend (root):**
```bash
npm run dev:frontend
```

---

## 2. Environment Configuration (`.env`)

Configure the environment variables in `.env` (or see `.env.example`):

```ini
# Backend REST URL
VITE_API_BASE_URL="http://localhost:8000/api/v1"

# Backend WebSocket URL
VITE_WS_URL="ws://localhost:8000/ws/dashboard"

# Backend Origin
VITE_BACKEND_URL="http://localhost:8000"
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

---

## 7. Cloud Deployment Guide (Vercel + Render / Railway)

### Step 1: Deploy Backend on Render (Free)
1. Go to [Render.com](https://render.com) and log in with GitHub.
2. Click **New +** → **Web Service**.
3. Select your repository: `https://github.com/supriya1411/MaskIt-`.
4. Configure:
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python seed_demo_data.py`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `DATABASE_URL`: `sqlite:///./maskit_local.db`
   - `JWT_SECRET`: `your-random-32-character-secret-key-here`
   - `CORS_ORIGINS`: `*`
6. Click **Deploy Web Service**.
7. Copy your backend URL (e.g. `https://maskit-backend.onrender.com`).

*(Alternative: Click **New +** → **Blueprint** and select your repo to auto-deploy using `render.yaml`)*.

---

### Step 2: Deploy Frontend on Vercel
1. Go to [Vercel.com](https://vercel.com) and click **Add New Project**.
2. Import your GitHub repository `supriya1411/MaskIt-`.
3. Framework Preset: **Vite** (auto-detected via `vercel.json`).
4. In **Environment Variables**, add:
   - `VITE_API_BASE_URL`: `https://<YOUR-RENDER-BACKEND-URL>/api/v1`
   - `VITE_WS_URL`: `wss://<YOUR-RENDER-BACKEND-URL>/ws/dashboard`
   - `VITE_BACKEND_URL`: `https://<YOUR-RENDER-BACKEND-URL>`
5. Click **Deploy**.
6. Your frontend is instantly live at `https://maskit-<your-username>.vercel.app`!
