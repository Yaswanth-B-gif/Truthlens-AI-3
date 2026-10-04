from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_demo_endpoint():
    res = client.post("/api/analyze/demo", json={"scenario": "trustworthy"})
    assert res.status_code == 200
    data = res.json()
    assert "trust_score" in data
    assert "classification" in data
    assert len(data["claims"]) > 0

def test_text_analysis_endpoint():
    text = "The Intergovernmental Panel on Climate Change (IPCC) synthesis report confirms global temperatures have increased due to anthropogenic carbon emissions."
    res = client.post("/api/analyze/text", json={"text": text, "title": "Climate Science Report"})
    assert res.status_code == 200
    data = res.json()
    assert data["trust_score"] > 50
    assert "explanation" in data
    assert len(data["claims"]) > 0

def test_dashboard_endpoint():
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "total_analyses" in data
    assert "score_distribution" in data

def test_history_endpoint():
    res = client.get("/api/history")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
