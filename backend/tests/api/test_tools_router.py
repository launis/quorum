
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.dependencies import get_document_service_dep, RegistryDep, RepositoryDep, get_async_repository
from backend.services.document_service import DocumentService

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
    mock_registry.resolve_model_config = AsyncMock(return_value={"provider": "google", "model_name": "gemini-1.5-flash"})
    
    # We need to mock the KnowledgeBaseService instantiated inside the route.
    # Since it's instantiated directly, we might need to mock the LLMFactory or the service class itself.
    # This is a limitation of the current route design (no factory injection for KBService).
    # We will accept a 500 error here IF it's due to LLM networking, OR we patch the service.
    
    with pytest.MonkeyPatch.context() as mp:
        mock_kb_service = AsyncMock()
        mock_kb_service.extract_concepts_with_llm.return_value = ["Concept A", "Concept B"]
        
        # Patch the class in the router module
        # Note: We must patch where it is IMPORTED
        # The router does: from backend.services.knowledge_base_service import KnowledgeBaseService
        # So we patch backend.services.knowledge_base_service.KnowledgeBaseService
        mp.setattr("backend.services.knowledge_base_service.KnowledgeBaseService", MagicMock(return_value=mock_kb_service))
        
        # We also need to mock LLMFactory because it's used before KBService
        mock_provider = MagicMock()
        mp.setattr("backend.llm.provider.LLMFactory.create_provider", MagicMock(return_value=mock_provider))

        response = client.post("/tools/extract-concepts", data={"text": "Hello Concept"})
        
        assert response.status_code == 200
        assert response.json()["concepts"] == ["Concept A", "Concept B"]

