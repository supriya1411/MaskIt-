def test_create_and_list_policy(client, auth_headers):
    # 1. Create custom policy
    create_res = client.post("/api/v1/policies", json={
        "name": "Aggressive Antifingerprint Policy",
        "masking_strength": "AGGRESSIVE",
        "strategy": "AI_GENERATED",
        "protected_signals": ["CANVAS", "WEBGL", "AUDIO"],
        "session_persistence": True,
        "rules_json": {"noise_level": 0.15, "mask_canvas": True}
    }, headers=auth_headers)
    assert create_res.status_code == 201
    pol_id = create_res.json()["id"]

    # 2. List policies
    list_res = client.get("/api/v1/policies", headers=auth_headers)
    assert list_res.status_code == 200
    policies = list_res.json()
    assert any(p["id"] == pol_id for p in policies)

def test_update_policy(client, auth_headers):
    create_res = client.post("/api/v1/policies", json={
        "name": "Initial Policy",
        "masking_strength": "BALANCED",
        "strategy": "STATIC",
        "protected_signals": ["CANVAS"]
    }, headers=auth_headers)
    pol_id = create_res.json()["id"]

    # Update name and strength
    up_res = client.put(f"/api/v1/policies/{pol_id}", json={
        "name": "Updated Shield Policy",
        "masking_strength": "STEALTH"
    }, headers=auth_headers)
    assert up_res.status_code == 200
    assert up_res.json()["name"] == "Updated Shield Policy"
    assert up_res.json()["masking_strength"] == "STEALTH"
