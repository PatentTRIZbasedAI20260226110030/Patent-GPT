from fastapi.testclient import TestClient


def test_generate_endpoint_accepts_valid_request():
    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/api/v1/patent/generate",
        json={"problem_description": "발열은 줄이고 싶지만 두께는 얇아야 한다"},
    )
    # Stub returns 501 Not Implemented for now
    assert response.status_code == 501


def test_generate_endpoint_rejects_empty_description():
    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/api/v1/patent/generate",
        json={"problem_description": ""},
    )
    assert response.status_code == 422
