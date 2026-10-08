/**
 * MaskIt Privacy Shield — Background Service Worker
 *
 * Manages per-domain shield settings and global shield state.
 * Communicates with content scripts and popup.
 */

// Default shield settings
const DEFAULT_SETTINGS = {
  globalShield: true,        // Global ON by default — protects all sites immediately
  protectedDomains: ['youtube.com', 'google.com', 'bing.com'], // Pre-protected popular domains
  blockedDomains: [],        // Domains where shield is disabled
  maskCanvas: true,
  maskWebGL: true,
  maskAudio: true,
  maskHardware: true,
  maskScreen: true,
  maskFonts: true,
  spoofedScreen: { width: 1920, height: 1080 },
  spoofedCPU: 4,
  spoofedRAM: 8,
};

// Backend API configuration
const BACKEND_API_URL = 'http://localhost:8000/api/v1';

// Register extension instance with backend
async function registerWithBackend() {
  try {
    const res = await fetch(`${BACKEND_API_URL}/extension/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ client_version: '1.0.0', browser_type: 'Chrome' }),
    });
    if (res.ok) {
      const data = await res.json();
      await chrome.storage.local.set({ maskit_extension_id: data.extension_id });
      console.log('[MaskIt] Registered with backend:', data.extension_id);
    }
  } catch (e) {
    // Backend may not be active yet, graceful fallback
  }
}

// Sync protected sites from backend to local extension storage
async function syncBackendConfig() {
  try {
    const res = await fetch(`${BACKEND_API_URL}/extension/config`);
    if (res.ok) {
      const data = await res.json();
      const current = await chrome.storage.local.get('maskit_settings');
      const settings = current.maskit_settings || DEFAULT_SETTINGS;

      if (data.sites && Array.isArray(data.sites)) {
        const backendDomains = data.sites.filter((s) => s.enabled).map((s) => s.domain);
        const merged = Array.from(new Set([...settings.protectedDomains, ...backendDomains]));
        settings.protectedDomains = merged;
        await chrome.storage.local.set({ maskit_settings: settings });
        console.log('[MaskIt] Synced protected sites from backend:', merged.length);
      }
    }
  } catch (e) {
    // Graceful offline fallback
  }
}

// Send live probe telemetry to backend
async function sendTelemetryToBackend(domain, signal, action = 'MASKED') {
  try {
    await fetch(`${BACKEND_API_URL}/extension/event`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        domain: domain,
        event_type: 'FINGERPRINT_PROBE',
        signal_type: signal,
        action: action,
        source: 'EXTENSION',
      }),
    });
  } catch (e) {
    // Offline or network error
  }
}

// Initialize storage & sync on install
chrome.runtime.onInstalled.addListener(async () => {
  const existing = await chrome.storage.local.get('maskit_settings');
  if (!existing.maskit_settings) {
    await chrome.storage.local.set({ maskit_settings: DEFAULT_SETTINGS });
    await chrome.storage.local.set({ maskit_domain_stats: {} });
  }
  await registerWithBackend();
  await syncBackendConfig();
  console.log('[MaskIt] Extension installed & initialized.');
});

// Periodic background sync with backend every 30 seconds
setInterval(syncBackendConfig, 30000);
syncBackendConfig();

// Listen for messages from popup and content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_SETTINGS') {
    chrome.storage.local.get('maskit_settings').then((data) => {
      sendResponse({ settings: data.maskit_settings || DEFAULT_SETTINGS });
    });
    return true; // keep channel open for async
  }

  if (message.type === 'SET_SETTINGS') {
    chrome.storage.local.set({ maskit_settings: message.settings }).then(() => {
      sendResponse({ ok: true });
      // Notify all tabs to reload their shield state
      chrome.tabs.query({}, (tabs) => {
        tabs.forEach((tab) => {
          if (tab.id) {
            chrome.tabs.sendMessage(tab.id, { type: 'SETTINGS_UPDATED', settings: message.settings })
              .catch(() => {}); // ignore if tab has no content script
          }
        });
      });
    });
    return true;
  }

  if (message.type === 'GET_DOMAIN_STATUS') {
    const domain = message.domain;
    chrome.storage.local.get('maskit_settings').then((data) => {
      const settings = data.maskit_settings || DEFAULT_SETTINGS;
      const isProtected = settings.globalShield ||
        settings.protectedDomains.some((d) => domain.includes(d));
      const isBlocked = settings.blockedDomains.some((d) => domain.includes(d));
      sendResponse({
        domain,
        shieldActive: isProtected && !isBlocked,
        globalShield: settings.globalShield,
        inProtectedList: settings.protectedDomains.some((d) => domain.includes(d)),
      });
    });
    return true;
  }

  if (message.type === 'PROTECT_DOMAIN') {
    const domain = message.domain;
    chrome.storage.local.get('maskit_settings').then((data) => {
      const settings = data.maskit_settings || DEFAULT_SETTINGS;
      if (!settings.protectedDomains.includes(domain)) {
        settings.protectedDomains.push(domain);
      }
      // Remove from blocked if present
      settings.blockedDomains = settings.blockedDomains.filter((d) => d !== domain);
      chrome.storage.local.set({ maskit_settings: settings }).then(() => {
        sendResponse({ ok: true, settings });
        // Record stats
        recordDomainAction(domain, 'protected');
      });
    });
    return true;
  }

  if (message.type === 'UNPROTECT_DOMAIN') {
    const domain = message.domain;
    chrome.storage.local.get('maskit_settings').then((data) => {
      const settings = data.maskit_settings || DEFAULT_SETTINGS;
      settings.protectedDomains = settings.protectedDomains.filter((d) => d !== domain);
      chrome.storage.local.set({ maskit_settings: settings }).then(() => {
        sendResponse({ ok: true, settings });
      });
    });
    return true;
  }

  if (message.type === 'TOGGLE_GLOBAL_SHIELD') {
    chrome.storage.local.get('maskit_settings').then((data) => {
      const settings = data.maskit_settings || DEFAULT_SETTINGS;
      settings.globalShield = message.value;
      chrome.storage.local.set({ maskit_settings: settings }).then(() => {
        sendResponse({ ok: true, settings });
        updateBadge(message.value);
      });
    });
    return true;
  }

  if (message.type === 'GET_STATS') {
    chrome.storage.local.get('maskit_domain_stats').then((data) => {
      sendResponse({ stats: data.maskit_domain_stats || {} });
    });
    return true;
  }

  if (message.type === 'RECORD_TELEMETRY') {
    const { domain, signal } = message;
    if (domain) {
      recordDomainAction(domain, 'probed');
      sendTelemetryToBackend(domain, signal || 'GENERIC', 'MASKED');
    }
    sendResponse({ ok: true });
    return true;
  }
});

// Update extension badge (toolbar icon)
function updateBadge(shieldOn) {
  if (shieldOn) {
    chrome.action.setBadgeText({ text: 'ON' });
    chrome.action.setBadgeBackgroundColor({ color: '#16a34a' });
  } else {
    chrome.action.setBadgeText({ text: '' });
  }
}

async function recordDomainAction(domain, action) {
  const data = await chrome.storage.local.get('maskit_domain_stats');
  const stats = data.maskit_domain_stats || {};
  if (!stats[domain]) stats[domain] = { protected: 0, scans: 0, lastSeen: null };
  if (action === 'protected') stats[domain].protected++;
  stats[domain].lastSeen = new Date().toISOString();
  await chrome.storage.local.set({ maskit_domain_stats: stats });
}
