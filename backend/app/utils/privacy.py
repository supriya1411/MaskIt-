import hashlib
import math
from typing import Dict, Any, Optional

def hash_privacy_safe(value: Optional[str]) -> Optional[str]:
    """Generates a one-way SHA-256 hash of a string, ensuring raw data is never retained."""
    if value is None:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def estimate_signal_entropy(signal_type: str, raw_val: Any) -> float:
    """
    Returns an estimated Shannon information entropy in bits for fingerprint signals
    grounded in empirical EFF Panopticlick / AmIUnique research:
    - Canvas: ~14.0 bits
    - WebGL Renderer: ~12.5 bits
    - Audio buffer hash: ~10.5 bits
    - Fonts list / count: ~8.0 bits
    - Screen resolution / depth: ~4.8 bits
    - Hardware concurrency / RAM: ~3.5 bits
    - Timezone: ~3.1 bits
    - Navigator language/platform: ~4.2 bits
    """
    entropy_baselines = {
        "CANVAS": 14.2,
        "WEBGL": 12.8,
        "AUDIO": 10.4,
        "FONTS": 8.5,
        "SCREEN": 4.8,
        "HARDWARE": 3.6,
        "NAVIGATOR": 4.2,
        "TIMEZONE": 3.2,
        "MEDIA_DEVICES": 5.1
    }
    base = entropy_baselines.get(signal_type.upper(), 3.0)
    
    # Adjust slightly based on variance if provided
    if isinstance(raw_val, str) and len(raw_val) > 0:
        char_counts = {}
        for c in raw_val:
            char_counts[c] = char_counts.get(c, 0) + 1
        str_entropy = 0.0
        for count in char_counts.values():
            p = count / len(raw_val)
            str_entropy -= p * math.log2(p)
        return round(min(18.0, base + (str_entropy * 0.2)), 2)

    return base

FORBIDDEN_KEYS = {
    "password", "cookie", "cookies", "token", "auth", "session_cookie",
    "raw_image", "image_data", "raw_canvas", "raw_audio", "audio_buffer",
    "credit_card", "ssn", "query", "url_query", "body", "post_data"
}

def sanitize_privacy_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Enforces privacy-by-design by filtering out any sensitive, raw, or PII keys.
    """
    if not metadata or not isinstance(metadata, dict):
        return {}

    sanitized = {}
    for key, val in metadata.items():
        k_lower = key.lower()
        if any(forbidden in k_lower for forbidden in FORBIDDEN_KEYS):
            continue
        
        # Don't accept large payload strings (e.g., base64 images)
        if isinstance(val, str) and len(val) > 512:
            sanitized[key] = f"[TRUNCATED_HASH:{hash_privacy_safe(val)[:16]}]"
        elif isinstance(val, (int, float, bool, str, list)):
            sanitized[key] = val
            
    return sanitized
