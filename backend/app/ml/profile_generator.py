import hashlib
from typing import Dict, Any

class ProfileGenerator:
    """
    Generates privacy-preserving, mathematically consistent synthetic browser profiles
    for distribution to the MaskIt browser extension.
    Ensures 100% internal consistency between OS, platform, GPU, screen, and user agent.
    """

    POPULATION_PROFILES = [
        {
            "id": "profile-chrome-win11",
            "os": "Windows",
            "platform": "Win32",
            "browser": "Chrome",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "vendor": "Google Inc.",
            "screen": {"width": 1920, "height": 1080, "color_depth": 24, "pixel_ratio": 1.0},
            "hardware": {"cpu_cores": 8, "device_memory": 8.0},
            "webgl": {
                "vendor": "Google Inc. (NVIDIA)",
                "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)"
            },
            "timezone": {"timezone": "UTC", "offset": 0}
        },
        {
            "id": "profile-safari-macos",
            "os": "macOS",
            "platform": "MacIntel",
            "browser": "Safari",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
            "vendor": "Apple Computer, Inc.",
            "screen": {"width": 2560, "height": 1440, "color_depth": 24, "pixel_ratio": 2.0},
            "hardware": {"cpu_cores": 8, "device_memory": 16.0},
            "webgl": {
                "vendor": "Apple Inc.",
                "renderer": "Apple M2"
            },
            "timezone": {"timezone": "UTC", "offset": 0}
        },
        {
            "id": "profile-chrome-mac",
            "os": "macOS",
            "platform": "MacIntel",
            "browser": "Chrome",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "vendor": "Google Inc.",
            "screen": {"width": 1728, "height": 1117, "color_depth": 24, "pixel_ratio": 2.0},
            "hardware": {"cpu_cores": 10, "device_memory": 16.0},
            "webgl": {
                "vendor": "Google Inc. (Apple)",
                "renderer": "ANGLE (Apple, ANGLE Metal Renderer: Apple M1 Pro, Version 14.5 (Build 23F79))"
            },
            "timezone": {"timezone": "UTC", "offset": 0}
        },
        {
            "id": "profile-firefox-win",
            "os": "Windows",
            "platform": "Win32",
            "browser": "Firefox",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
            "vendor": "",
            "screen": {"width": 1920, "height": 1080, "color_depth": 24, "pixel_ratio": 1.0},
            "hardware": {"cpu_cores": 8, "device_memory": 8.0},
            "webgl": {
                "vendor": "Google Inc. (Intel)",
                "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)"
            },
            "timezone": {"timezone": "UTC", "offset": 0}
        }
    ]

    @classmethod
    def generate_profile(cls, strategy: str = "DISTRIBUTION_SAMPLED", seed_key: str = "default") -> Dict[str, Any]:
        """
        Returns a consistent masking profile based on strategy:
        STATIC -> Always index 0 (standard most common Windows/Chrome)
        DISTRIBUTION_SAMPLED -> Deterministic pick based on seed_key
        AI_GENERATED -> Seeded synthesis adding uniform sub-pixel & canvas micro-noise
        """
        if strategy == "STATIC":
            base = cls.POPULATION_PROFILES[0].copy()
            base["strategy"] = "STATIC"
            return base

        # Hash seed for deterministic reproducible selection per user/session
        h = int(hashlib.sha256(seed_key.encode()).hexdigest(), 16)
        idx = h % len(cls.POPULATION_PROFILES)
        selected = dict(cls.POPULATION_PROFILES[idx])
        selected["strategy"] = strategy

        if strategy == "AI_GENERATED":
            # Add micro-variation parameters for canvas and audio noise injection
            noise_val = ((h % 100) / 1000.0) + 0.001
            selected["noise_vector"] = {
                "canvas_shift": round(noise_val, 4),
                "audio_variance": round(noise_val * 0.5, 5),
                "webgl_fuzzing": True
            }

        return selected
