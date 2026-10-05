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

def test_protect_invalid_domain_rejected(client, auth_headers):
    res = client.post("/api/v1/protection/sites", json={
        "domain": "invalid..domain"
    }, headers=auth_headers)
    assert res.status_code == 400
