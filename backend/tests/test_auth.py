from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_and_login():
    import uuid
    random_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    reg_payload = {
        "name": "Dr. Sarah Mitchell",
        "email": random_email,
        "password": "SecurePassword123!"
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == random_email
    
    # Login
    login_payload = {
        "email": random_email,
        "password": "SecurePassword123!"
    }
    login_res = client.post("/api/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    
    # Test /me endpoint
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["name"] == "Dr. Sarah Mitchell"
