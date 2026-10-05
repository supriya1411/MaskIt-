from app.services.risk_engine import RiskEngine

def test_deterministic_risk_scoring():
    sample_signals = {
        "screen": {"width": 1920, "height": 1080, "color_depth": 24, "pixel_ratio": 1.0},
        "browser": {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36",
            "platform": "Win32",
            "vendor": "Google Inc."
        },
        "timezone": {"timezone": "America/New_York", "offset": -240},
        "hardware": {"cpu_cores": 16, "device_memory": 32.0},
        "webgl": {"renderer": "NVIDIA GeForce RTX 3080", "vendor": "Google Inc. (NVIDIA)"},
        "canvas_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "audio_hash": "f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2",
        "font_count": 85,
        "media_device_count": 4
    }

    # Run multiple times to confirm 100% determinism (no random variation)
    run1 = RiskEngine.analyze(sample_signals)
    run2 = RiskEngine.analyze(sample_signals)
    run3 = RiskEngine.analyze(sample_signals)

    assert run1["risk_score"] == run2["risk_score"] == run3["risk_score"]
    assert run1["risk_level"] == run2["risk_level"] == "HIGH"
    assert len(run1["risk_factors"]) == len(run2["risk_factors"])
    assert run1["detected_signals"] == run2["detected_signals"]
    assert "WEBGL" in run1["detected_signals"]
    assert "CANVAS" in run1["detected_signals"]
    assert run1["recommendation"] == "ENABLE_STRONG_PROTECTION"

def test_minimal_signals_low_risk():
    minimal_signals = {
        "screen": {"width": 1920, "height": 1080},
        "timezone": {"timezone": "UTC", "offset": 0}
    }
    result = RiskEngine.analyze(minimal_signals)
    assert result["risk_score"] <= 35.0
    assert result["risk_level"] == "LOW"
