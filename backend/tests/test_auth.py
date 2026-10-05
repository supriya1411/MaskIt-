def test_register_user_success(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "newuser@maskit.dev",
        "password": "SecurePassword123!"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "newuser@maskit.dev"
    assert "id" in data
    assert "hashed_password" not in data

def test_register_duplicate_email(client, test_user):
    res = client.post("/api/v1/auth/register", json={
        "email": test_user.email,
        "password": "AnotherPassword123!"
    })
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"]

def test_login_success(client, test_user):
    res = client.post("/api/v1/auth/login", json={
        "email": "test@maskit.dev",
        "password": "ValidPass123!"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client, test_user):
    res = client.post("/api/v1/auth/login", json={
        "email": "test@maskit.dev",
        "password": "WrongPassword999!"
    })
    assert res.status_code == 401

def test_get_current_user_me(client, auth_headers):
    res = client.get("/api/v1/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "test@maskit.dev"

def test_get_current_user_unauthorized(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
