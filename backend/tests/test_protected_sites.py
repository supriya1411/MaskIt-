def test_protect_site_flow(client, auth_headers):
    # 1. Protect youtube.com
    res = client.post("/api/v1/protection/sites", json={
        "domain": "youtube.com"
    }, headers=auth_headers)
    assert res.status_code == 201
    site_data = res.json()
    assert site_data["domain"] == "youtube.com"
    assert site_data["enabled"] is True
    assert site_data["status"] == "ACTIVE"
    site_id = site_data["id"]

    # 2. List protected sites (only authenticated user's sites)
    list_res = client.get("/api/v1/protection/sites", headers=auth_headers)
    assert list_res.status_code == 200
    sites = list_res.json()
    assert any(s["id"] == site_id for s in sites)

    # 3. Pause protection
    update_res = client.put(f"/api/v1/protection/sites/{site_id}", json={
        "enabled": False
    }, headers=auth_headers)
    assert update_res.status_code == 200
    assert update_res.json()["enabled"] is False
    assert update_res.json()["status"] == "PAUSED"

    # 4. Delete site
    del_res = client.delete(f"/api/v1/protection/sites/{site_id}", headers=auth_headers)
    assert del_res.status_code == 204

def test_protected_sites_include_real_risk(client, auth_headers):
    client.post("/api/v1/protection/sites", json={"domain": "reddit.com"}, headers=auth_headers)
    client.post("/api/v1/events", json={
        "domain": "reddit.com",
        "event_type": "FINGERPRINT_PROBE",
        "signal_type": "CANVAS_HASH",
        "action": "MASKED",
        "risk_before": 81.0,
        "risk_after": 19.0,
    }, headers=auth_headers)

    sites = client.get("/api/v1/protection/sites", headers=auth_headers).json()
    reddit = next(s for s in sites if s["domain"] == "reddit.com")
    assert reddit["risk_before"] == 81.0
    assert reddit["risk_after"] == 19.0

    analytics = client.get(
        f"/api/v1/protection/sites/{reddit['id']}/analytics",
        headers=auth_headers,
    ).json()
    assert analytics["canvas_events"] >= 1
    assert analytics["risk_before"] == 81.0


def test_protect_invalid_domain_rejected(client, auth_headers):
    res = client.post("/api/v1/protection/sites", json={
        "domain": "invalid..domain"
    }, headers=auth_headers)
    assert res.status_code == 400
