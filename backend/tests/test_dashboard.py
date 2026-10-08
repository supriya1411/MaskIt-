def test_dashboard_signals_match_seed_aliases(client, auth_headers):
    client.post("/api/v1/events", json={
        "domain": "youtube.com",
        "event_type": "MASK_APPLIED",
        "signal_type": "Canvas 2D Hash",
        "action": "MASKED",
        "risk_before": 70.0,
        "risk_after": 20.0
    }, headers=auth_headers)
    res = client.get("/api/v1/dashboard/signals", headers=auth_headers)
    assert res.status_code == 200
    canvas = next(s for s in res.json() if s["signal"] == "CANVAS")
    assert canvas["count"] >= 1
    assert canvas["masked_count"] >= 1


def test_dashboard_overview_includes_unassigned_telemetry(client, auth_headers):
    client.post("/api/v1/events", json={
        "domain": "ads.example.com",
        "event_type": "FINGERPRINT_PROBE",
        "signal_type": "WEBGL",
        "action": "MASKED",
        "risk_before": 80.0,
        "risk_after": 18.0
    })
    res = client.get("/api/v1/dashboard/overview", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["fingerprint_probes"] >= 1
    assert data["signals_masked"] >= 1
    assert data["average_risk_before"] > 0
    assert data["average_risk_after"] > 0


def test_dashboard_overview_calculations(client, auth_headers):
    # 1. Check baseline
    base_res = client.get("/api/v1/dashboard/overview", headers=auth_headers)
    assert base_res.status_code == 200
    base_data = base_res.json()
    assert "protected_sites" in base_data
    assert "fingerprint_probes" in base_data
    assert "protection_rate" in base_data

    # 2. Add site and event
    client.post("/api/v1/protection/sites", json={"domain": "vimeo.com"}, headers=auth_headers)
    client.post("/api/v1/events", json={
        "domain": "vimeo.com",
        "event_type": "FINGERPRINT_PROBE",
        "signal_type": "CANVAS",
        "action": "MASKED",
        "risk_before": 75.0,
        "risk_after": 20.0
    }, headers=auth_headers)

    # 3. Check updated overview reflects database change
    updated_res = client.get("/api/v1/dashboard/overview", headers=auth_headers)
    assert updated_res.status_code == 200
    updated_data = updated_res.json()
    assert updated_data["protected_sites"] >= 1
    assert updated_data["fingerprint_probes"] >= 1
    assert updated_data["signals_masked"] >= 1

def test_dashboard_signals_breakdown(client, auth_headers):
    res = client.get("/api/v1/dashboard/signals", headers=auth_headers)
    assert res.status_code == 200
    signals = res.json()
    assert any(s["signal"] == "CANVAS" for s in signals)
    assert any(s["signal"] == "WEBGL" for s in signals)

def test_dashboard_risk_distribution(client, auth_headers):
    res = client.get("/api/v1/dashboard/risk", headers=auth_headers)
    assert res.status_code == 200
    risk = res.json()
    assert "low_count" in risk
    assert "high_count" in risk
