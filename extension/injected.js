/**
 * MaskIt Injected Script
 * Runs in the webpage context to intercept fingerprinting APIs:
 * - Canvas 2D noise injection
 * - WebGL vendor/renderer spoofing
 * - Hardware concurrency (CPU cores) normalization
 * - Device memory (RAM) normalization
 * - Screen dimensions normalization
 * - AudioContext frequency jitter
 */
(() => {
  if (window.__MASKIT_INJECTED__) return;
  window.__MASKIT_INJECTED__ = true;

  let activeConfig = {
    enabled: true,
    maskCanvas: true,
    maskWebGL: true,
    maskHardware: true,
    maskScreen: true,
    maskAudio: true,
    spoofedCPU: 4,
    spoofedRAM: 8,
    spoofedScreen: { width: 1920, height: 1080 },
  };

  // Listen for config messages from content_script
  window.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'MASKIT_CONFIG_UPDATE') {
      activeConfig = { ...activeConfig, ...event.data.config };
    }
  });

  // 1. Hardware Concurrency (CPU Cores)
  try {
    Object.defineProperty(navigator, 'hardwareConcurrency', {
      get: () => activeConfig.enabled && activeConfig.maskHardware ? activeConfig.spoofedCPU : 16,
      configurable: true,
    });
  } catch (e) {}

  // 2. Device Memory (RAM in GB)
  try {
    Object.defineProperty(navigator, 'deviceMemory', {
      get: () => activeConfig.enabled && activeConfig.maskHardware ? activeConfig.spoofedRAM : 8,
      configurable: true,
    });
  } catch (e) {}

  // 3. Screen Dimensions
  try {
    const origScreen = window.screen;
    const screenProxy = new Proxy(origScreen, {
      get(target, prop) {
        if (!activeConfig.enabled || !activeConfig.maskScreen) return target[prop];
        if (prop === 'width' || prop === 'availWidth') return activeConfig.spoofedScreen.width;
        if (prop === 'height' || prop === 'availHeight') return activeConfig.spoofedScreen.height;
        if (prop === 'colorDepth' || prop === 'pixelDepth') return 24;
        return typeof target[prop] === 'function' ? target[prop].bind(target) : target[prop];
      },
    });

    Object.defineProperty(window, 'screen', {
      get: () => screenProxy,
      configurable: true,
    });
  } catch (e) {}

  // 4. WebGL Spoofing (Unmasked Vendor & Renderer)
  const hookWebGL = (glProto) => {
    if (!glProto || !glProto.getParameter) return;
    const origGetParameter = glProto.getParameter;
    glProto.getParameter = function (param) {
      if (activeConfig.enabled && activeConfig.maskWebGL) {
        // UNMASKED_VENDOR_WEBGL = 0x9245
        if (param === 0x9245) return 'Google Inc. (MaskIt Cohort)';
        // UNMASKED_RENDERER_WEBGL = 0x9246
        if (param === 0x9246) return 'ANGLE (Generic Standard Display Driver)';
      }
      return origGetParameter.apply(this, arguments);
    };
  };

  try {
    if (window.WebGLRenderingContext) hookWebGL(WebGLRenderingContext.prototype);
    if (window.WebGL2RenderingContext) hookWebGL(WebGL2RenderingContext.prototype);
  } catch (e) {}

  // 5. Canvas Noise Injection (Protects 2D rasterization sub-pixel profiling)
  try {
    const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function (type, ...args) {
      if (activeConfig.enabled && activeConfig.maskCanvas && this.width > 0 && this.height > 0) {
        try {
          const ctx = this.getContext('2d');
          if (ctx) {
            const shiftX = (Math.random() - 0.5) * 0.02;
            const shiftY = (Math.random() - 0.5) * 0.02;
            ctx.transform(1, shiftX, shiftY, 1, 0, 0);
          }
        } catch (e) {}
      }
      return origToDataURL.apply(this, [type, ...args]);
    };

    const origToBlob = HTMLCanvasElement.prototype.toBlob;
    HTMLCanvasElement.prototype.toBlob = function (callback, ...args) {
      if (activeConfig.enabled && activeConfig.maskCanvas && this.width > 0 && this.height > 0) {
        try {
          const ctx = this.getContext('2d');
          if (ctx) {
            const shiftX = (Math.random() - 0.5) * 0.02;
            const shiftY = (Math.random() - 0.5) * 0.02;
            ctx.transform(1, shiftX, shiftY, 1, 0, 0);
          }
        } catch (e) {}
      }
      return origToBlob.apply(this, [callback, ...args]);
    };
  } catch (e) {}

  // 6. AudioContext Micro-Jitter
  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (AudioContextClass) {
      const origCreateAnalyser = AudioContextClass.prototype.createAnalyser;
      AudioContextClass.prototype.createAnalyser = function () {
        const analyser = origCreateAnalyser.apply(this, arguments);
        const origGetFloatFreq = analyser.getFloatFrequencyData;
        analyser.getFloatFrequencyData = function (array) {
          origGetFloatFreq.apply(this, arguments);
          if (activeConfig.enabled && activeConfig.maskAudio && array && array.length) {
            const jitter = (Math.random() - 0.5) * 0.05;
            for (let i = 0; i < Math.min(array.length, 16); i++) {
              array[i] += jitter;
            }
          }
        };
        return analyser;
      };
    }
  } catch (e) {}

  console.info('[MaskIt Extension] Privacy hooks activated for current domain.');
})();
