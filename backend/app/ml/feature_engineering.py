from typing import Dict, Any, List
import hashlib

# Standard browser/platform categories
COMMON_OS = ["Windows", "Macintosh", "Linux", "Android", "iPhone", "Other"]
COMMON_BROWSERS = ["Chrome", "Safari", "Firefox", "Edge", "Other"]
COMMON_GPUS = ["Apple M", "NVIDIA", "Intel", "AMD Radeon", "Adreno", "Mali", "Other"]

def extract_feature_vector(fingerprint_dict: Dict[str, Any]) -> List[float]:
    """
    Transforms privacy-safe fingerprint signals into a fixed-length numerical vector
    suitable for scikit-learn models or statistical anomaly scoring.
    Features:
    [0] screen_width_normalized (w / 3840)
    [1] screen_height_normalized (h / 2160)
    [2] pixel_ratio
    [3] color_depth
    [4] cpu_cores (normalized / 64)
    [5] device_memory (normalized / 64)
    [6] timezone_offset_normalized (offset / 840)
    [7] font_count_normalized (count / 200)
    [8] media_device_count_normalized (count / 10)
    [9] canvas_hash_entropy_est
    [10] audio_hash_entropy_est
    [11] webgl_gpu_category_code
    [12] os_category_code
    [13] browser_category_code
    """
    screen = fingerprint_dict.get("screen") or {}
    browser = fingerprint_dict.get("browser") or {}
    tz = fingerprint_dict.get("timezone") or {}
    hw = fingerprint_dict.get("hardware") or {}
    webgl = fingerprint_dict.get("webgl") or {}

    w = float(screen.get("width") or 1920) / 3840.0
    h = float(screen.get("height") or 1080) / 2160.0
    dpr = float(screen.get("pixel_ratio") or 1.0)
    cd = float(screen.get("color_depth") or 24) / 32.0

    cores = float(hw.get("cpu_cores") or 8) / 64.0
    mem = float(hw.get("device_memory") or 8.0) / 64.0
    tz_offset = float(tz.get("offset") if tz.get("offset") is not None else -480) / 840.0
    fonts = float(fingerprint_dict.get("font_count") or 50) / 200.0
    media_count = float(fingerprint_dict.get("media_device_count") or 2) / 10.0

    # Canvas and Audio hash entropy proxy from hex digest
    canvas_hash = fingerprint_dict.get("canvas_hash") or ""
    canvas_entropy = len(set(canvas_hash)) / 16.0 if canvas_hash else 0.5

    audio_hash = fingerprint_dict.get("audio_hash") or ""
    audio_entropy = len(set(audio_hash)) / 16.0 if audio_hash else 0.5

    # GPU category encoding
    renderer = str(webgl.get("renderer") or "").lower()
    gpu_code = 6.0 # Other
    for idx, gpu_name in enumerate(COMMON_GPUS[:-1]):
        if gpu_name.lower() in renderer:
            gpu_code = float(idx)
            break

    # OS code
    platform = str(browser.get("platform") or "").lower()
    ua = str(browser.get("user_agent") or "").lower()
    os_code = 5.0
    if "win" in platform or "windows" in ua:
        os_code = 0.0
    elif "mac" in platform or "macintosh" in ua:
        os_code = 1.0
    elif "linux" in platform or "x11" in ua:
        os_code = 2.0
    elif "android" in ua:
        os_code = 3.0
    elif "iphone" in ua or "ipad" in ua:
        os_code = 4.0

    # Browser code
    browser_code = 4.0
    if "edg" in ua:
        browser_code = 3.0
    elif "chrome" in ua:
        browser_code = 0.0
    elif "safari" in ua and "chrome" not in ua:
        browser_code = 1.0
    elif "firefox" in ua:
        browser_code = 2.0

    return [
        round(w, 4), round(h, 4), round(dpr, 2), round(cd, 2),
        round(cores, 4), round(mem, 4), round(tz_offset, 4),
        round(fonts, 4), round(media_count, 4), round(canvas_entropy, 4),
        round(audio_entropy, 4), gpu_code, os_code, browser_code
    ]
