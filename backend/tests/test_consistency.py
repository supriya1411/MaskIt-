from app.services.consistency_engine import ConsistencyEngine

def test_valid_profile_consistency():
    valid_win = {
        "screen": {"width": 1920, "height": 1080},
        "browser": {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36",
            "platform": "Win32",
            "vendor": "Google Inc."
        },
        "webgl": {"renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11)", "vendor": "Google Inc."},
        "timezone": {"timezone": "UTC", "offset": 0},
        "hardware": {"cpu_cores": 8}
    }
    score, issues = ConsistencyEngine.evaluate(valid_win)
    assert score == 100.0
    assert len(issues) == 0

def test_impossible_apple_gpu_on_windows():
    mismatched = {
        "browser": {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36",
            "platform": "Win32"
        },
        "webgl": {"renderer": "Apple M2 Max", "vendor": "Apple Inc."}
    }
    score, issues = ConsistencyEngine.evaluate(mismatched)
    assert score < 80.0
    assert any("Apple" in issue for issue in issues)

def test_direct3d_on_mac():
    mismatched = {
        "browser": {
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15",
            "platform": "MacIntel"
        },
        "webgl": {"renderer": "Microsoft Direct3D11 vs_5_0", "vendor": "Microsoft"}
    }
    score, issues = ConsistencyEngine.evaluate(mismatched)
    assert score < 80.0
    assert any("Direct3D" in issue for issue in issues)
