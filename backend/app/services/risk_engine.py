from typing import Dict, Any, List, Tuple
from app.services.consistency_engine import ConsistencyEngine
from app.utils.privacy import estimate_signal_entropy

class RiskEngine:
    """
    Deterministic risk calculation engine for browser fingerprinting.
    Produces identical scores for identical inputs without any stochastic or random elements.
    """

    SIGNAL_CLASSIFICATION = {
        "CANVAS": {
            "level": "HIGH",
            "max_impact": 26.0,
            "reason": "Canvas rendering exposes exact GPU rasterization, anti-aliasing quirks, and subpixel font rendering."
        },
        "WEBGL": {
            "level": "HIGH",
            "max_impact": 24.0,
            "reason": "Unmasked GPU vendor and renderer strings drastically narrow the fingerprint identification pool."
        },
        "AUDIO": {
            "level": "HIGH",
            "max_impact": 18.0,
            "reason": "AudioContext frequency processing reveals underlying sound hardware and DSP oscillator differences."
        },
        "FONTS": {
            "level": "MEDIUM",
            "max_impact": 14.0,
            "reason": "Installed system fonts provide high discriminating entropy for cross-site user identification."
        },
        "MEDIA_DEVICES": {
            "level": "MEDIUM",
            "max_impact": 10.0,
            "reason": "Enumeration of microphones, cameras, and audio output counts provides persistent local device entropy."
        },
        "HARDWARE": {
            "level": "MEDIUM",
            "max_impact": 12.0,
            "reason": "CPU cores and RAM memory size narrow device classes and identify high-end or unusual machines."
        },
        "NAVIGATOR": {
            "level": "MEDIUM",
            "max_impact": 10.0,
            "reason": "User-Agent, languages, platform, and vendor combinations expose specific browser release builds."
        },
        "SCREEN": {
            "level": "LOW",
            "max_impact": 8.0,
            "reason": "Resolution and pixel ratio are common but help confirm exact multi-monitor or retina configurations."
        },
        "TIMEZONE": {
            "level": "LOW",
            "max_impact": 6.0,
            "reason": "Timezone and offset narrow geographical location but are shared among many users in the same region."
        }
    }

    @classmethod
    def analyze(cls, signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates a deterministic risk assessment from privacy-safe fingerprint signals.
        """
        risk_factors: List[Dict[str, Any]] = []
        detected_signals: List[str] = []
        total_risk = 0.0

        screen = signals.get("screen") or {}
        browser = signals.get("browser") or {}
        tz = signals.get("timezone") or {}
        hw = signals.get("hardware") or {}
        webgl = signals.get("webgl") or {}
        canvas_hash = signals.get("canvas_hash")
        audio_hash = signals.get("audio_hash")
        font_count = signals.get("font_count")
        media_count = signals.get("media_device_count")

        # 1. Canvas Signal
        if canvas_hash:
            detected_signals.append("CANVAS")
            entropy = estimate_signal_entropy("CANVAS", canvas_hash)
            # High entropy canvas hash increases impact towards 25
            impact = min(25.0, 16.0 + (entropy * 0.6))
            total_risk += impact
            risk_factors.append({
                "signal": "CANVAS",
                "impact": round(impact, 1),
                "reason": cls.SIGNAL_CLASSIFICATION["CANVAS"]["reason"]
            })

        # 2. WebGL Signal
        if webgl.get("renderer") or webgl.get("vendor"):
            detected_signals.append("WEBGL")
            renderer_str = str(webgl.get("renderer") or "")
            # Unusual / unmasked dedicated GPU strings have higher impact than generic 'ANGLE' or 'Mesa'
            is_dedicated = any(k in renderer_str.lower() for k in ("nvidia", "geforce", "rtx", "gtx", "radeon", "apple m"))
            impact = 24.0 if is_dedicated else 16.0
            total_risk += impact
            risk_factors.append({
                "signal": "WEBGL",
                "impact": round(impact, 1),
                "reason": "Dedicated GPU vendor/renderer detected (" + renderer_str[:32] + ")." if is_dedicated else cls.SIGNAL_CLASSIFICATION["WEBGL"]["reason"]
            })

        # 3. Audio Signal
        if audio_hash:
            detected_signals.append("AUDIO")
            impact = 16.0
            total_risk += impact
            risk_factors.append({
                "signal": "AUDIO",
                "impact": round(impact, 1),
                "reason": cls.SIGNAL_CLASSIFICATION["AUDIO"]["reason"]
            })

        # 4. Hardware Signal
        if hw.get("cpu_cores") is not None or hw.get("device_memory") is not None:
            detected_signals.append("HARDWARE")
            cores = hw.get("cpu_cores") or 4
            mem = hw.get("device_memory") or 8
            # Rare hardware combinations (e.g. 16+ cores or > 32GB RAM)
            rarity_bonus = 4.0 if (cores >= 16 or mem >= 32) else 1.0
            impact = min(12.0, 6.0 + rarity_bonus)
            total_risk += impact
            risk_factors.append({
                "signal": "HARDWARE",
                "impact": round(impact, 1),
                "reason": f"Hardware attributes exposed ({cores} cores, {mem}GB RAM). Unusual hardware increases trackability."
            })

        # 5. Fonts Signal
        if font_count is not None and font_count > 0:
            detected_signals.append("FONTS")
            # If font count > 60, system font list is very discriminating
            impact = 14.0 if font_count > 60 else (8.0 if font_count > 20 else 4.0)
            total_risk += impact
            risk_factors.append({
                "signal": "FONTS",
                "impact": round(impact, 1),
                "reason": f"{font_count} distinct fonts detected. Large font libraries identify individual workstations."
            })

        # 6. Media Devices
        if media_count is not None:
            detected_signals.append("MEDIA_DEVICES")
            impact = 8.0 if media_count > 2 else 4.0
            total_risk += impact
            risk_factors.append({
                "signal": "MEDIA_DEVICES",
                "impact": round(impact, 1),
                "reason": cls.SIGNAL_CLASSIFICATION["MEDIA_DEVICES"]["reason"]
            })

        # 7. Navigator Signal
        if browser.get("user_agent") or browser.get("platform"):
            detected_signals.append("NAVIGATOR")
            impact = 8.0
            total_risk += impact
            risk_factors.append({
                "signal": "NAVIGATOR",
                "impact": round(impact, 1),
                "reason": cls.SIGNAL_CLASSIFICATION["NAVIGATOR"]["reason"]
            })

        # 8. Screen Signal
        if screen.get("width") and screen.get("height"):
            detected_signals.append("SCREEN")
            w, h = screen.get("width"), screen.get("height")
            is_common = (w, h) in [(1920, 1080), (1366, 768), (1440, 900), (1536, 864), (2560, 1440)]
            impact = 4.0 if is_common else 8.0
            total_risk += impact
            risk_factors.append({
                "signal": "SCREEN",
                "impact": round(impact, 1),
                "reason": f"Screen dimensions ({w}x{h}, DPR: {screen.get('pixel_ratio', 1)})."
            })

        # 9. Timezone Signal
        if tz.get("timezone") or tz.get("offset") is not None:
            detected_signals.append("TIMEZONE")
            impact = 5.0
            total_risk += impact
            risk_factors.append({
                "signal": "TIMEZONE",
                "impact": round(impact, 1),
                "reason": cls.SIGNAL_CLASSIFICATION["TIMEZONE"]["reason"]
            })

        # Cross-signal consistency evaluation
        consistency_score, consistency_issues = ConsistencyEngine.evaluate(signals)

        # Inconsistency increases fingerprint anomaly risk (spoofing detection)
        if consistency_score < 80.0:
            inconsistency_penalty = round((100.0 - consistency_score) * 0.3, 1)
            total_risk += inconsistency_penalty
            risk_factors.append({
                "signal": "INCONSISTENCY_ANOMALY",
                "impact": inconsistency_penalty,
                "reason": f"Signal inconsistencies detected across browser attributes ({len(consistency_issues)} issues found)."
            })

        # Normalize final risk score to [0, 100]
        final_risk = max(5.0, min(100.0, total_risk))
        final_risk = round(final_risk, 1)

        # Classify risk level
        if final_risk < 35.0:
            risk_level = "LOW"
            recommendation = "STANDARD_SHIELD_SUFFICIENT"
        elif final_risk < 70.0:
            risk_level = "MEDIUM"
            recommendation = "ENABLE_BALANCED_PROTECTION"
        else:
            risk_level = "HIGH"
            recommendation = "ENABLE_STRONG_PROTECTION"

        return {
            "risk_score": final_risk,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "detected_signals": detected_signals,
            "recommendation": recommendation,
            "consistency_score": consistency_score,
            "consistency_issues": consistency_issues
        }
