
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from httpx import AsyncClient

# We need to import app for dependency overrides
from backend.main import app


@pytest.fixture
def mock_repository():
    return AsyncMock()

@pytest.fixture
def mock_prompt_builder():
    m = AsyncMock()
    # Ensure methods are async mocks
    m.preview_step_prompt = AsyncMock()
    m.preview_full_chain_prompts = AsyncMock()
    return m

@pytest.mark.asyncio
async def test_preview_step_success(client: AsyncClient, mock_repository, mock_prompt_builder):
    """Test successful step preview generation."""
    # 1. Setup Mock
    step_id = "step_1"
    mock_prompt_builder.preview_step_prompt.return_value = {
        "system_instruction": "System Prompt Content",
        "user_prompt": "User Prompt Template",
        "agent_class": "TestAgent"
    }

    # 2. Call Endpoint
    # Dependencies are overridden in conftest or we rely on app.dependency_overrides if set up globally
    # Assuming standard pytest-asyncio integration with app fixtures.

    # We need to override the PromptBuilder dependency for this test if not already handled
    from backend.dependencies import get_prompt_builder_dep
    app.dependency_overrides[get_prompt_builder_dep] = lambda: mock_prompt_builder

    response = await client.post(f"/builder/steps/{step_id}/preview")

    # 3. Verify
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["system_instruction"] == "System Prompt Content"
    assert data["user_prompt"] == "User Prompt Template"
    assert data["agent_class"] == "TestAgent"

    mock_prompt_builder.preview_step_prompt.assert_called_once_with(step_id)


@pytest.mark.asyncio
async def test_preview_chain_success(client: AsyncClient, mock_repository, mock_prompt_builder):
    """Test successful workflow chain preview generation."""
    workflow_id = "wf_1"
    mock_prompt_builder.preview_full_chain_prompts.return_value = "# Chain Preview\n\nStep 1..."

    from backend.dependencies import get_prompt_builder_dep
    app.dependency_overrides[get_prompt_builder_dep] = lambda: mock_prompt_builder

    response = await client.get(f"/builder/workflows/{workflow_id}/chain-preview")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["markdown_content"] == "# Chain Preview\n\nStep 1..."

    mock_prompt_builder.preview_full_chain_prompts.assert_called_once_with(workflow_id)


@pytest.mark.asyncio
async def test_preview_step_not_found(client: AsyncClient, mock_prompt_builder):
    step_id = "missing_step"
    from backend.exceptions import StepNotFoundError
    mock_prompt_builder.preview_step_prompt.side_effect = StepNotFoundError(step_id)

    from backend.dependencies import get_prompt_builder_dep
    app.dependency_overrides[get_prompt_builder_dep] = lambda: mock_prompt_builder

    response = await client.post(f"/builder/steps/{step_id}/preview")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_preview_chain_not_found(client: AsyncClient, mock_prompt_builder):
    workflow_id = "missing_wf"
    from backend.exceptions import WorkflowNotFoundError
    mock_prompt_builder.preview_full_chain_prompts.side_effect = WorkflowNotFoundError(workflow_id)

    from backend.dependencies import get_prompt_builder_dep
    app.dependency_overrides[get_prompt_builder_dep] = lambda: mock_prompt_builder

    response = await client.get(f"/builder/workflows/{workflow_id}/chain-preview")

    assert response.status_code == status.HTTP_404_NOT_FOUND
