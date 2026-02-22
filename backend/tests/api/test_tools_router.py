from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.dependencies import get_async_repository, get_document_service_dep
from backend.main import app

client = TestClient(app)

# Mocks
mock_doc_service = MagicMock()
mock_repo = AsyncMock()
mock_registry = AsyncMock()


@pytest.fixture(autouse=True)
def setup_dependencies():
    app.dependency_overrides = {}
    app.dependency_overrides[get_document_service_dep] = lambda: mock_doc_service
    app.dependency_overrides[get_async_repository] = lambda: mock_repo
    # Registry is usually injected via app state or singleton, but here we might need to mock get_registry if it exists,
    # or rely on the fact that RegistryDep often uses get_repository under the hood or we mock the resolve_model_config.
    # Assuming RegistryDep resolves to a registry object, we need to locate its dependency provider.
    # In backend/dependencies.py: RegistryDep = Annotated[AgentRegistry, Depends(get_agent_registry_dep)]
    from backend.dependencies import get_agent_registry_dep

    app.dependency_overrides[get_agent_registry_dep] = lambda: mock_registry

    mock_doc_service.reset_mock()
    mock_repo.reset_mock()
    mock_registry.reset_mock()

    yield
    app.dependency_overrides = {}


def test_web_scrape_ssrf_blocked():
    # Test Localhost
    response = client.post("/tools/web-scrape", json={"url": "http://localhost:8000"})
    assert response.status_code == 400
    data = response.json()
    assert data["title"] == "Ssrf Protection Blocked"
    assert "ssrf-protection-blocked" in data["type"]

    # Test Private IP
    response = client.post("/tools/web-scrape", json={"url": "http://192.168.1.1"})
    assert response.status_code == 400
    data = response.json()
    assert data["title"] == "Ssrf Protection Blocked"
    assert "ssrf-protection-blocked" in data["type"]


def test_web_scrape_success():
    # Test valid public URL (mocked response)
    response = client.post("/tools/web-scrape", json={"url": "http://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Scraped content placeholder."


@pytest.mark.asyncio
async def test_extract_text_no_content():
    response = client.post("/tools/extract-text")
    assert response.status_code == 400
    data = response.json()
    assert data["title"] == "No Content Provided"
    assert "no-content-provided" in data["type"]


@pytest.mark.asyncio
async def test_extract_text_success_text():
    response = client.post("/tools/extract-text", data={"text": "Hello World"})
    assert response.status_code == 200
    assert response.json()["text"] == "Hello World"


@pytest.mark.asyncio
async def test_extract_concepts_success():
    # Setup Mocks
    from backend.models.llm import LLMProviderConfig

    mock_registry.resolve_model_config = AsyncMock(
        return_value=LLMProviderConfig(
            id="test/google", provider="google", model_name="gemini-1.5-flash", tpm_limit=1000, rpm_limit=100
        )
    )

    from backend.dependencies import get_knowledge_base_service_dep
    from backend.main import app

    mock_kb_service = AsyncMock()
    mock_kb_service.extract_concepts_with_llm.return_value = ["Concept A", "Concept B"]

    app.dependency_overrides[get_knowledge_base_service_dep] = lambda: mock_kb_service
    try:
        response = client.post("/tools/extract-concepts", data={"text": "Hello Concept"})

        assert response.status_code == 200
        assert response.json()["concepts"] == ["Concept A", "Concept B"]
    finally:
        app.dependency_overrides.pop(get_knowledge_base_service_dep, None)
