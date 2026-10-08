def test_ingest_telemetry_event(client, auth_headers):
    payload = {
        "domain": "youtube.com",
        "event_type": "FINGERPRINT_PROBE",
        "signal_type": "WEBGL",
        "probe_method": "getParameter(UNMASKED_RENDERER_WEBGL)",
        "action": "MASKED",
        "risk_before": 82.0,
        "risk_after": 24.0,
        "consistency_score": 98.0,
        "source": "EXTENSION",
        "privacy_safe_metadata": {
            "vendor_masked": True,
            "accidental_cookie": "secret_session_cookie_that_must_be_stripped"
        }
    }
    res = client.post("/api/v1/events", json=payload, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["domain"] == "youtube.com"
    assert data["signal_type"] == "WEBGL"
    assert data["action"] == "MASKED"

    # Query events
    events_res = client.get("/api/v1/events", headers=auth_headers)
    assert events_res.status_code == 200
    events = events_res.json()
    assert len(events) >= 1
    stored = next(e for e in events if e["domain"] == "youtube.com")
    assert stored["signal_type"] == "WEBGL"
    assert stored["action"] == "MASKED"
    assert stored["risk_before"] == 82.0
    assert stored["risk_after"] == 24.0
