from fastapi.testclient import TestClient

from backend_v2.main import app

client = TestClient(app)


def test_docs_endpoint() -> None:
    """Test that the OpenAPI docs endpoint is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text


def test_openapi_schema() -> None:
    """Test that the OpenAPI schema is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Cognitive Quorum API"
