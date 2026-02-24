from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.dependencies import (
    get_agent_registry_dep,
    get_async_repository,
)
from backend.main import app
from backend.models.auth import TokenData, UserRole

client = TestClient(app)

# Mocks
mock_registry = AsyncMock()
mock_repo = AsyncMock()
mock_handler = MagicMock()


async def mock_get_current_user():
    return TokenData(id="test-user", email="test@example.com", organization_id="org-123", role=UserRole.ADMIN)


@pytest.fixture(autouse=True)
def setup_dependencies():
    app.dependency_overrides = {}
    app.dependency_overrides[get_agent_registry_dep] = lambda: mock_registry
    app.dependency_overrides[get_async_repository] = lambda: mock_repo
    # Mock CurrentUser to bypass auth
    from backend.dependencies import get_current_user_from_header

    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user

    # Mock LLMHandler (for list_providers)
    from backend.dependencies import get_llm_handler_dep

    app.dependency_overrides[get_llm_handler_dep] = lambda: mock_handler

    mock_registry.reset_mock()
    mock_repo.reset_mock()
    mock_handler.reset_mock()

    # Clear side effects
    mock_registry.resolve_model_config.side_effect = None

    yield
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_update_model_config_success():
    payload = {"registry": {"fast": {"model_name": "gpt-4o-mini"}}}

    response = client.post("/llm/config", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_registry.update_model_registry_config.assert_called_once_with(payload["registry"])


@pytest.mark.asyncio
async def test_generate_completion_invalid_strategy():
    # Mock registry raising error
    mock_registry.resolve_model_config.side_effect = ValueError("Unknown strategy")

    payload = {"prompt": "Hello", "model_strategy": "invalid"}
    response = client.post("/llm/completion", json=payload)

    assert response.status_code == 400
    data = response.json()
    assert data["title"] == "Invalid Model Strategy"
    assert "invalid-model-strategy" in data["type"]


@pytest.mark.asyncio
async def test_batch_completion_partial_failure():
    # Mock registry for one success, one failure
    # We can't easily mock separate calls with side_effect in the loop unless we inspect args
    # But we can mock LLMFactory to fail on specific inputs or just verify structure.

    # Simpler: Mock resolve_model_config to succeed.
    mock_config = MagicMock()
    mock_config.provider = "mock"
    mock_config.model_name = "test"
    mock_registry.resolve_model_config.return_value = mock_config

    with pytest.MonkeyPatch.context() as mp:
        mock_provider = AsyncMock()
        mock_provider.generate.side_effect = ["Success", Exception("LLM Error")]

        # Patch factory
        mp.setattr("backend.llm.provider.LLMFactory.create_provider", MagicMock(return_value=mock_provider))

        payload = {"requests": [{"prompt": "A"}, {"prompt": "B"}]}
        response = client.post("/llm/batch-completion", json=payload)

        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        assert len(results) == 2
        assert results[0]["status"] == "success"
        assert results[0]["result"] == "Success"
        assert results[1]["status"] == "error"
        assert results[1]["error_code"] == "LLM_BATCH_ITEM_FAILED"


def test_list_providers():
    # This endpoint relies on settings, so we might need to patch settings or just assert structure
    # It returns settings.model_strategies.
    # LLMHandler is just passed but not used for strategies logic currently (based on refactor).
    mock_handler.fetch_all_available_models.return_value = {"google": ["gemini-pro"], "openai": ["gpt-4-turbo"]}
    response = client.get("/llm/providers")
    assert response.status_code == 200
    data = response.json()
    assert "strategies" in data
    assert "api_keys_set" in data
