import re
from typing import Dict, Any, List, Tuple

class ConsistencyEngine:
    """
    Evaluates cross-signal browser fingerprint coherence.
    Detects impossible or tampered browser configurations (e.g. Windows UA with Apple M2 GPU,
    or Mac platform with Direct3D WebGL renderer).
    """

    @classmethod
    def evaluate(cls, signals: Dict[str, Any]) -> Tuple[float, List[str]]:
        issues = []
        deductions = 0.0

        screen = signals.get("screen") or {}
        browser = signals.get("browser") or {}
        tz = signals.get("timezone") or {}
        hw = signals.get("hardware") or {}
        webgl = signals.get("webgl") or {}

        ua = str(browser.get("user_agent") or "").strip()
        platform = str(browser.get("platform") or "").strip()
        vendor = str(browser.get("vendor") or "").strip()
        renderer = str(webgl.get("renderer") or "").strip()
        gpu_vendor = str(webgl.get("vendor") or "").strip()
        tz_name = str(tz.get("timezone") or "").strip()
        tz_offset = tz.get("offset")

        # 1. OS vs Platform checks
        if "Windows" in ua or "Win64" in ua or "WOW64" in ua:
            if platform and not platform.startswith("Win"):
                issues.append(f"OS/Platform mismatch: User-Agent indicates Windows but platform is '{platform}'.")
                deductions += 25.0
        elif "Macintosh" in ua or "Mac OS X" in ua:
            if platform and platform not in ("MacIntel", "MacPPC", "Mac68K", "Macintosh"):
                issues.append(f"OS/Platform mismatch: User-Agent indicates macOS but platform is '{platform}'.")
                deductions += 25.0
        elif "Linux" in ua and "Android" not in ua:
            if platform and not platform.startswith("Linux") and platform not in ("X11", "FreeBSD"):
                issues.append(f"OS/Platform mismatch: User-Agent indicates Linux but platform is '{platform}'.")
                deductions += 20.0

        # 2. WebGL / GPU vs Operating System checks
        renderer_lower = renderer.lower()
        if "apple m" in renderer_lower or "apple gpu" in renderer_lower or "metal" in renderer_lower:
            if "windows" in ua.lower() or platform.startswith("Win"):
                issues.append("GPU/OS mismatch: Apple Silicon/Metal GPU reported on a Windows platform.")
                deductions += 30.0
        
        if "direct3d" in renderer_lower or "d3d" in renderer_lower:
            if "mac" in platform.lower() or "macintosh" in ua.lower():
                issues.append("GPU/OS mismatch: Microsoft Direct3D renderer reported on a macOS platform.")
                deductions += 30.0

        # 3. Browser Vendor checks
        if "chrome" in ua.lower() and "edg" not in ua.lower() and "opr" not in ua.lower():
            if vendor and vendor != "Google Inc.":
                issues.append(f"Vendor mismatch: Google Chrome reported with non-standard vendor '{vendor}'.")
                deductions += 15.0
        elif "safari" in ua.lower() and "chrome" not in ua.lower():
            if vendor and "Apple" not in vendor:
                issues.append(f"Vendor mismatch: Safari reported with non-Apple vendor '{vendor}'.")
                deductions += 15.0

        # 4. Screen resolution sanity
        w = screen.get("width")
        h = screen.get("height")
        if w and h:
            if w < 320 or h < 320:
                issues.append(f"Unusual screen dimensions: {w}x{h} is uncharacteristically small for modern browsers.")
                deductions += 15.0
            if w > 7680 or h > 4320:
                issues.append(f"Unusual screen dimensions: {w}x{h} exceeds standard display bounds.")
                deductions += 10.0

        # 5. Hardware concurrency sanity
        cores = hw.get("cpu_cores")
        if cores is not None:
            if cores <= 0 or (cores > 64 and cores not in (96, 128, 192, 256)):
                issues.append(f"Unusual CPU core count: {cores} is an atypical browser concurrency value.")
                deductions += 15.0

        # 6. Timezone name vs offset sanity
        if tz_name and tz_offset is not None:
            tz_lower = tz_name.lower()
            if "utc" in tz_lower or "gmt" in tz_lower:
                if abs(tz_offset) > 1:
                    issues.append(f"Timezone offset conflict: '{tz_name}' reported with offset {tz_offset} minutes.")
                    deductions += 15.0
            elif "tokyo" in tz_lower:
                if tz_offset != -540:  # JS offset for UTC+9 is -540
                    issues.append(f"Timezone offset conflict: '{tz_name}' (JST UTC+9) should have offset -540, got {tz_offset}.")
                    deductions += 15.0

        final_score = max(0.0, min(100.0, 100.0 - deductions))
        return round(final_score, 1), issues
