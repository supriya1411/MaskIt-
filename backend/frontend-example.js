/**
 * MaskIt Frontend Integration Reference (frontend-example.js)
 * Demonstrates complete workflow:
 * 1. Register / Login
 * 2. Start Protection Session
 * 3. 🛡️ Protect My Data (Add domain e.g. youtube.com)
 * 4. Load Protected Sites
 * 5. Analyze Fingerprint with Risk Engine
 * 6. Send Local Masking Telemetry Event
 * 7. Load Live Dashboard Metrics
 * 8. Connect Live WebSocket Stream
 */

const API_BASE = "http://localhost:8000/api/v1";
const WS_BASE = "ws://localhost:8000/ws/dashboard";

let authToken = null;
let currentSessionToken = null;

// 1. Register or Login
async function loginOrRegister(email, password) {
  try {
    const loginRes = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (loginRes.ok) {
      const data = await loginRes.json();
      authToken = data.access_token;
      console.log("Logged in successfully. Token acquired.");
      return authToken;
    }

    // If login failed, register new user
    const regRes = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (regRes.ok) {
      return await loginOrRegister(email, password);
    }
  } catch (err) {
    console.error("Auth failed:", err);
  }
}

// 2. Start Active Protection Session
async function startSession() {
  const res = await fetch(`${API_BASE}/session/start`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({
      client_type: "EXTENSION",
      user_agent: navigator.userAgent,
    }),
  });

  const session = await res.json();
  currentSessionToken = session.session_token;
  console.log("Active Session Token:", currentSessionToken);
  return session;
}

// 3. 🛡️ Protect My Data: Add Domain
async function protectSite(domain) {
  console.log(`🛡️ Protecting domain: ${domain}...`);
  const res = await fetch(`${API_BASE}/protection/sites`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ domain }),
  });

  const site = await res.json();
  console.log("Site protected:", site);
  return site;
}

// 4. Load Protected Sites
async function loadProtectedSites() {
  const res = await fetch(`${API_BASE}/protection/sites`, {
    headers: { Authorization: `Bearer ${authToken}` },
  });
  const sites = await res.json();
  console.log("Protected Sites:", sites);
  return sites;
}

// 5. Analyze Fingerprint with Deterministic Risk Engine
async function analyzeFingerprint() {
  const payload = {
    domain: "youtube.com",
    screen: {
      width: window.screen.width,
      height: window.screen.height,
      color_depth: window.screen.colorDepth,
      pixel_ratio: window.devicePixelRatio || 1,
    },
    browser: {
      user_agent: navigator.userAgent,
      language: navigator.language,
      platform: navigator.platform,
      vendor: navigator.vendor,
    },
    timezone: {
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      offset: new Date().getTimezoneOffset(),
    },
    hardware: {
      cpu_cores: navigator.hardwareConcurrency || 8,
      device_memory: navigator.deviceMemory || 8,
    },
    webgl: {
      renderer: "ANGLE (NVIDIA, GeForce RTX 3070)",
      vendor: "Google Inc. (NVIDIA)",
    },
    canvas_hash: "a4f89d38c1a6382ef94",
    audio_hash: "7bc32f91a082b9e4a2",
    font_count: 52,
    media_device_count: 2,
  };

  const res = await fetch(`${API_BASE}/fingerprint/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const analysis = await res.json();
  console.log("Risk Score:", analysis.risk_score, "Level:", analysis.risk_level);
  console.log("Consistency Score:", analysis.consistency_score);
  return analysis;
}

// 6. Send Telemetry Event from Extension
async function sendTelemetryEvent(domain, signalType, action, riskBefore, riskAfter) {
  const res = await fetch(`${API_BASE}/events`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({
      domain,
      event_type: "MASK_APPLIED",
      signal_type: signalType,
      probe_method: "WebGL.getParameter",
      action: action, // e.g. MASKED
      risk_before: riskBefore,
      risk_after: riskAfter,
      source: "EXTENSION",
      privacy_safe_metadata: {
        vendor_spoofed: true,
      },
    }),
  });

  const eventRes = await res.json();
  console.log("Telemetry Event Ingested:", eventRes);
  return eventRes;
}

// 7. Load Live Dashboard Overview
async function loadDashboard() {
  const res = await fetch(`${API_BASE}/dashboard/overview`, {
    headers: { Authorization: `Bearer ${authToken}` },
  });
  const overview = await res.json();
  console.log("Live Dashboard Metrics (from PostgreSQL):", overview);
  return overview;
}

// 8. Connect Real-Time WebSocket
function connectWebSocket() {
  const ws = new WebSocket(WS_BASE);

  ws.onopen = () => {
    console.log("Connected to MaskIt WebSocket Stream.");
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("🔴 Live Event Broadcast Received:", data);
  };

  ws.onerror = (err) => {
    console.error("WebSocket error:", err);
  };

  ws.onclose = () => {
    console.log("WebSocket connection closed. Reconnecting in 3s...");
    setTimeout(connectWebSocket, 3000);
  };

  return ws;
}

// Full automated pipeline execution
async function runDemo() {
  console.log("=== STARTING MASKIT PIPELINE DEMO ===");
  await loginOrRegister("demo@maskit.dev", "SecurePassword123!");
  await startSession();
  connectWebSocket();
  await protectSite("youtube.com");
  await loadProtectedSites();
  const analysis = await analyzeFingerprint();
  await sendTelemetryEvent("youtube.com", "WEBGL", "MASKED", analysis.risk_score, 21.0);
  await loadDashboard();
  console.log("=== MASKIT DEMO COMPLETED ===");
}

if (typeof window !== "undefined") {
  window.MaskItDemo = { runDemo, loginOrRegister, protectSite, analyzeFingerprint, loadDashboard };
}
