document.addEventListener('DOMContentLoaded', async () => {
  const currentDomainEl = document.getElementById('currentDomain');
  const badgeEl = document.getElementById('badge');
  const siteToggle = document.getElementById('siteToggle');
  const globalToggle = document.getElementById('globalToggle');
  const protectedCountEl = document.getElementById('protectedCount');
  const openScannerBtn = document.getElementById('openScannerBtn');

  let activeDomain = '';

  // 1. Get active tab domain
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.url) {
      try {
        const urlObj = new URL(tab.url);
        activeDomain = urlObj.hostname;
      } catch (e) {
        activeDomain = 'Browser Internal Page';
      }
    }
  } catch (e) {
    activeDomain = 'localhost';
  }

  currentDomainEl.textContent = activeDomain || 'Unknown';

  // 2. Load settings and status
  function refreshStatus() {
    chrome.runtime.sendMessage({ type: 'GET_SETTINGS' }, (response) => {
      if (!response || !response.settings) return;
      const settings = response.settings;

      globalToggle.checked = !!settings.globalShield;
      protectedCountEl.textContent = (settings.protectedDomains || []).length;

      const isSiteProtected =
        (settings.protectedDomains || []).some((d) => activeDomain && activeDomain.includes(d));
      siteToggle.checked = isSiteProtected;

      const isShieldActive = settings.globalShield || isSiteProtected;
      updateBadgeUI(isShieldActive);
    });
  }

  function updateBadgeUI(active) {
    if (active) {
      badgeEl.textContent = 'PROTECTED';
      badgeEl.className = 'status-badge status-protected';
    } else {
      badgeEl.textContent = 'OFF';
      badgeEl.className = 'status-badge status-unprotected';
    }
  }

  refreshStatus();

  // 3. Toggle for current site
  siteToggle.addEventListener('change', () => {
    if (!activeDomain || activeDomain.includes('chrome://')) return;

    const action = siteToggle.checked ? 'PROTECT_DOMAIN' : 'UNPROTECT_DOMAIN';
    chrome.runtime.sendMessage({ type: action, domain: activeDomain }, () => {
      refreshStatus();
    });
  });

  // 4. Toggle for Global Shield
  globalToggle.addEventListener('change', () => {
    chrome.runtime.sendMessage({ type: 'TOGGLE_GLOBAL_SHIELD', value: globalToggle.checked }, () => {
      refreshStatus();
    });
  });

  // 5. Open Web App Scanner
  openScannerBtn.addEventListener('click', () => {
    chrome.tabs.create({ url: 'http://localhost:3000/scan' });
  });
});
