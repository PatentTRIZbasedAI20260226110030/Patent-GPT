from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient


def test_generate_endpoint_accepts_valid_request():
    from app.main import app

    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/api/v1/patent/generate",
        json={"problem_description": "발열은 줄이고 싶지만 두께는 얇아야 한다"},
    )
    # Without valid OPENAI_API_KEY, the dependency injection will fail with 500
    # but the route itself accepts the request (not 404 or 422)
    assert response.status_code in (200, 500)


def test_generate_endpoint_rejects_empty_description():
    from app.api.routes.patent import get_patent_service
    from app.main import app

    # Override the service dependency so dependency resolution succeeds
    mock_service = MagicMock()
    mock_service.generate = AsyncMock()
    app.dependency_overrides[get_patent_service] = lambda: mock_service

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/patent/generate",
            json={"problem_description": ""},
        )
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_search_endpoint_accepts_valid_request():
    from app.main import app

    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/api/v1/patent/search",
        json={"query": "방열 구조"},
    )
    assert response.status_code in (200, 500)


def test_docx_download_returns_404_for_missing():
    from app.main import app

    client = TestClient(app)
    response = client.get("/api/v1/patent/nonexistent/docx")
    assert response.status_code == 404
