"""Unit and integration tests for Admin Studio Prompt Blocks API endpoints."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_current_user_from_header,
    get_studio_output_profile_service,
    get_studio_prompt_block_service,
    get_studio_simulation_service,
    get_studio_workflow_service,
)
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.services.studio.prompt_block_service import StudioPromptBlockService
from backend_v2.services.studio.workflow_service import StudioWorkflowService
from backend_v2.tests.factories import SystemRulePromptBlockFactory
from backend_v2.tests.fakes.in_memory_repositories import InMemoryPromptBlockRepository


def get_root_user() -> TokenData:
    """Provides a Root superuser token for prompt block testing."""
    return TokenData(
        email="root@test.com",
        id="usr_12345678",
        role=UserRole.ROOT,
        organization_id="org_testorg123",
    )


@pytest.fixture
def client(
    studio_prompt_block_service: StudioPromptBlockService,
    studio_workflow_service: StudioWorkflowService,
) -> Generator[TestClient]:
    """TestClient authenticated as ROOT with real domain services backed by in-memory fakes."""
    app.dependency_overrides[get_current_user_from_header] = get_root_user
    app.dependency_overrides[get_studio_prompt_block_service] = lambda: studio_prompt_block_service
    app.dependency_overrides[get_studio_workflow_service] = lambda: studio_workflow_service
    app.dependency_overrides[get_studio_simulation_service] = lambda: studio_workflow_service
    app.dependency_overrides[get_studio_output_profile_service] = lambda: studio_workflow_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_get_prompt_blocks(client: TestClient, fake_prompt_block_repo: InMemoryPromptBlockRepository) -> None:
    """Verifies listing prompt blocks via canonical API prefix with pre-seeded data."""
    block = SystemRulePromptBlockFactory.build()
    fake_prompt_block_repo._save_isolated(block.id, block)

    response = client.get("/api/v2/studio/prompt-blocks")

    assert response.status_code == 200
    blocks = response.json()
    assert len(blocks) >= 1
    matching = [b for b in blocks if b["id"] == block.id]
    assert len(matching) == 1
    assert matching[0]["id"] == block.id


def test_get_single_prompt_block(client: TestClient, fake_prompt_block_repo: InMemoryPromptBlockRepository) -> None:
    """Verifies retrieving a specific prompt block by ID."""
    block = SystemRulePromptBlockFactory.build()
    fake_prompt_block_repo._save_isolated(block.id, block)

    response = client.get(f"/api/v2/studio/prompt-blocks/{block.id}")

    assert response.status_code == 200
    assert response.json()["id"] == block.id


def test_delete_prompt_block(client: TestClient, fake_prompt_block_repo: InMemoryPromptBlockRepository) -> None:
    """Verifies deleting an existing prompt block via canonical API prefix."""
    block = SystemRulePromptBlockFactory.build()
    fake_prompt_block_repo._save_isolated(block.id, block)

    response = client.delete(f"/api/v2/studio/prompt-blocks/{block.id}")

    assert response.status_code == 200
    assert response.json()["deleted_id"] == block.id
    assert fake_prompt_block_repo._get_isolated(block.id) is None


def test_get_prompt_block_nonexistent_triggers_404(client: TestClient) -> None:
    """Negative test: Verifies that requesting a non-existent prompt block returns 404."""
    response = client.get("/api/v2/studio/prompt-blocks/blk_nonexistent0000")
    assert response.status_code == 404


def test_delete_prompt_block_nonexistent_triggers_404(client: TestClient) -> None:
    """Negative test: Verifies that deleting a non-existent prompt block returns 404."""
    response = client.delete("/api/v2/studio/prompt-blocks/blk_nonexistent0000")
    assert response.status_code == 404
