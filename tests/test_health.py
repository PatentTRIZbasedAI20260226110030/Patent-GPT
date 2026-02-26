from fastapi.testclient import TestClient


def test_health_endpoint():
    from app.main import app

    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
