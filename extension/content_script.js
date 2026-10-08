/**
 * MaskIt Content Script
 * Runs at document_start. Evaluates if current domain is shielded and injects hooks.
 */
(() => {
  const currentDomain = window.location.hostname;

  // Ask background if this domain should be protected
  chrome.runtime.sendMessage(
    { type: 'GET_DOMAIN_STATUS', domain: currentDomain },
    (response) => {
      if (chrome.runtime.lastError || !response) return;

      if (response.shieldActive) {
        injectShieldScript();
      }
    }
  );

  function injectShieldScript() {
    try {
      const script = document.createElement('script');
      script.src = chrome.runtime.getURL('injected.js');
      script.onload = () => script.remove();
      (document.head || document.documentElement).appendChild(script);
    } catch (e) {
      console.error('[MaskIt] Failed to inject shield:', e);
    }
  }

  // Handle runtime settings updates from popup or background
  chrome.runtime.onMessage.addListener((message) => {
    if (message.type === 'SETTINGS_UPDATED') {
      const settings = message.settings;
      const isProtected =
        settings.globalShield ||
        (settings.protectedDomains && settings.protectedDomains.some((d) => currentDomain.includes(d)));
      const isBlocked =
        settings.blockedDomains && settings.blockedDomains.some((d) => currentDomain.includes(d));

      const shouldBeActive = isProtected && !isBlocked;

      window.postMessage(
        {
          type: 'MASKIT_CONFIG_UPDATE',
          config: {
            enabled: shouldBeActive,
            maskCanvas: settings.maskCanvas,
            maskWebGL: settings.maskWebGL,
            maskHardware: settings.maskHardware,
            maskScreen: settings.maskScreen,
            maskAudio: settings.maskAudio,
            spoofedCPU: settings.spoofedCPU,
            spoofedRAM: settings.spoofedRAM,
          },
        },
        '*'
      );
    }
  });

  // Listen for live probe detections from injected script and forward to extension background
  window.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'MASKIT_PROBE_DETECTED') {
      try {
        chrome.runtime.sendMessage({
          type: 'RECORD_TELEMETRY',
          signal: event.data.signal,
          domain: currentDomain,
        });
      } catch (e) {
        // Extension context might be invalidated on reload
      }
    }
  });
})();
