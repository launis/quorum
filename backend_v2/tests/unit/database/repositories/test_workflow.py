"""Unit tests for WorkflowRepositoryImpl."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.workflow import WorkflowRepositoryImpl
from backend_v2.exceptions import AppException, WorkflowNotFoundError


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Mock storage driver."""
    driver = AsyncMock(spec=StorageDriver)
    driver.query.return_value = []
    driver.get.return_value = None
    driver.upsert.return_value = "wf_1234567890abcdef"
    driver.update.return_value = True
    driver.delete.return_value = True
    driver.count.return_value = 1
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> WorkflowRepositoryImpl:
    """Workflow repository fixture."""
    return WorkflowRepositoryImpl(mock_driver)


@pytest.fixture
def valid_workflow_doc() -> dict:
    """Valid workflow document fixture."""
    return {
        "id": "wf_1234567890abcdef",
        "slug": "wf_exec",
        "name": {"translations": {"en": "Workflow", "fi": "Työnkulku"}},
        "description": {"translations": {"en": "Desc", "fi": "Kuvaus"}},
        "status": "published",
        "version": 1,
        "default_profile_id": "prf_1234567890abcdef",
        "allowed_exports": ["pdf", "raw_json"],
        "historical_context_mode": "DISABLED",
        "steps": [],
    }


@pytest.fixture
def valid_step_doc() -> dict:
    """Valid step document fixture."""
    return {
        "id": "stp_1234567890abcdef",
        "slug": "step_one",
        "name": {"translations": {"en": "Step 1", "fi": "Vaihe 1"}},
        "model_strategy": "fast",
        "criteria_block_ids": ["blk_1234567890abcdef"],
        "extraction_protocol_block_id": "blk_1234567890abcdef",
    }


@pytest.mark.asyncio
async def test_get_workflow_by_id_and_definition(
    repo: WorkflowRepositoryImpl, mock_driver: AsyncMock, valid_workflow_doc: dict
) -> None:
    """Positive: retrieves valid Workflow domain model via get_workflow_by_id and get_workflow."""
    mock_driver.get.return_value = valid_workflow_doc
    wf = await repo.get_workflow_by_id("wf_1234567890abcdef")
    assert wf is not None
    assert wf.id == "wf_1234567890abcdef"

    wf_def = await repo.get_workflow("wf_1234567890abcdef")
    assert wf_def is not None
    assert wf_def.slug == "wf_exec"


@pytest.mark.asyncio
async def test_get_workflow_not_found(repo: WorkflowRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: returns None when workflow is not found."""
    mock_driver.get.return_value = None
    assert await repo.get_workflow_by_id("wf_missing") is None
    assert await repo.get_workflow_definition("wf_missing") is None


@pytest.mark.asyncio
async def test_get_all_workflows_filters(
    repo: WorkflowRepositoryImpl, mock_driver: AsyncMock, valid_workflow_doc: dict
) -> None:
    """Positive: retrieving workflows with role ROOT, org filter, and corrupted record skipping."""
    mock_driver.query.return_value = [{"id": "corrupted_1"}, valid_workflow_doc]
    workflows = await repo.get_all_workflows(organization_id="org_123", role="MEMBER")
    assert len(workflows) == 1
    assert workflows[0].id == "wf_1234567890abcdef"

    # With ROOT role
    root_workflows = await repo.get_all_workflows(role="ROOT")
    assert len(root_workflows) == 1


@pytest.mark.asyncio
async def test_workflow_lifecycle_and_versioning(
    repo: WorkflowRepositoryImpl, mock_driver: AsyncMock, valid_workflow_doc: dict
) -> None:
    """Positive: tests create, versioned update, definition update, count, and delete."""
    assert await repo.create_workflow(valid_workflow_doc) == "wf_1234567890abcdef"

    mock_driver.get.return_value = valid_workflow_doc
    repo._increment_version = MagicMock(return_value=("wf_exec", "wf_1234567890abcdef_v2", 2))  # type: ignore[method-assign]
    new_id = await repo.update_workflow("wf_1234567890abcdef", {"name": {"translations": {"en": "Updated"}}})
    assert new_id == "wf_1234567890abcdef_v2"

    def_id = await repo.update_workflow_definition("wf_1234567890abcdef", {"slug": "new_slug"})
    assert def_id == "wf_1234567890abcdef_v2"

    assert await repo.count_workflows() == 1
    assert await repo.delete_workflow("wf_1234567890abcdef") is True


@pytest.mark.asyncio
async def test_update_workflow_not_found(repo: WorkflowRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Negative: update_workflow raises WorkflowNotFoundError if workflow does not exist."""
    mock_driver.get.return_value = None
    with pytest.raises(WorkflowNotFoundError):
        await repo.update_workflow("wf_missing", {"name": "New"})


@pytest.mark.asyncio
async def test_step_crud_and_query(repo: WorkflowRepositoryImpl, mock_driver: AsyncMock, valid_step_doc: dict) -> None:
    """Positive: tests step retrieval, creation, update, and deletion."""
    mock_driver.get.return_value = valid_step_doc
    mock_driver.query.return_value = [{"id": "corrupted_step"}, valid_step_doc]

    step = await repo.get_step_by_id("stp_1234567890abcdef")
    assert step is not None
    assert step.id == "stp_1234567890abcdef"

    step_alias = await repo.get_step("stp_1234567890abcdef")
    assert step_alias is not None

    all_steps = await repo.get_all_steps()
    assert len(all_steps) == 1

    mock_driver.upsert.return_value = "stp_1234567890abcdef"
    assert await repo.create_step(valid_step_doc) == "stp_1234567890abcdef"
    assert await repo.update_step("stp_1234567890abcdef", {"slug": "updated"}) == "stp_1234567890abcdef"
    assert await repo.delete_step("stp_1234567890abcdef", force_delete=True) is True


@pytest.mark.asyncio
async def test_delete_step_blocked_by_usage(
    repo: WorkflowRepositoryImpl, mock_driver: AsyncMock, valid_step_doc: dict, valid_workflow_doc: dict
) -> None:
    """Negative: step deletion blocked when used by an active workflow without force_delete."""
    workflow_using_step = dict(valid_workflow_doc)
    workflow_using_step["steps"] = [{"task_blueprint": "stp_1234567890abcdef"}]

    mock_driver.get.return_value = valid_step_doc
    mock_driver.query.return_value = [workflow_using_step]

    with pytest.raises(AppException) as exc_info:
        await repo.delete_step("stp_1234567890abcdef", force_delete=False)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_delete_step_not_found(repo: WorkflowRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: returns False if step does not exist."""
    mock_driver.get.return_value = None
    assert await repo.delete_step("stp_missing") is False
