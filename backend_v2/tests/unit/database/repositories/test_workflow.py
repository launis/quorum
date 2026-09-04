"""Unit tests for WorkflowRepositoryImpl."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.workflow import WorkflowRepositoryImpl
from backend_v2.exceptions import AppException, WorkflowNotFoundError
from backend_v2.models.core_base import I18nText
from backend_v2.models.dtos.studio import (
    StepCreateDTO,
    StepUpdateDTO,
    WorkflowCreateDTO,
    WorkflowUpdateDTO,
)


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
    mock_driver.upsert.return_value = "wf_1234567890abcdef"
    wf_dto = WorkflowCreateDTO(
        slug=valid_workflow_doc["slug"],
        name=I18nText(translations=valid_workflow_doc["name"]["translations"]),
        description=I18nText(translations=valid_workflow_doc["description"]["translations"]),
        default_profile_id=valid_workflow_doc["default_profile_id"],
        allowed_exports=valid_workflow_doc["allowed_exports"],
        historical_context_mode=valid_workflow_doc["historical_context_mode"],
        steps=[],
    )
    assert await repo.create_workflow(wf_dto) == "wf_1234567890abcdef"

    mock_driver.get.return_value = valid_workflow_doc
    new_id = await repo.update_workflow(
        "wf_1234567890abcdef", WorkflowUpdateDTO(name=I18nText(translations={"en": "Updated"}))
    )
    assert new_id == "wf_1234567890abcdef"

    def_id = await repo.update_workflow_definition("wf_1234567890abcdef", WorkflowUpdateDTO(slug="new_slug"))
    assert def_id == "wf_1234567890abcdef"

    assert await repo.count_workflows() == 1
    assert await repo.delete_workflow("wf_1234567890abcdef") is True


@pytest.mark.asyncio
async def test_save_workflow_and_save_step(
    repo: WorkflowRepositoryImpl, mock_driver: AsyncMock, valid_workflow_doc: dict, valid_step_doc: dict
) -> None:
    """Positive: tests in-place atomic upsert for Workflow and Step domain models."""
    from backend_v2.models.v2_core import Step, Workflow

    wf_model = Workflow.model_validate(valid_workflow_doc, strict=False)
    mock_driver.upsert.return_value = wf_model.id
    saved_wf_id = await repo.save_workflow(wf_model)
    assert saved_wf_id == wf_model.id
    mock_driver.upsert.assert_called_with("workflows", wf_model.model_dump(mode="json"), wf_model.id)

    step_model = Step.model_validate(valid_step_doc, strict=False)
    mock_driver.upsert.return_value = step_model.id
    saved_step_id = await repo.save_step(step_model)
    assert saved_step_id == step_model.id
    mock_driver.upsert.assert_called_with("steps", step_model.model_dump(mode="json"), step_model.id)


@pytest.mark.asyncio
async def test_update_workflow_not_found(repo: WorkflowRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Negative: update_workflow raises WorkflowNotFoundError if workflow does not exist."""
    mock_driver.get.return_value = None
    with pytest.raises(WorkflowNotFoundError):
        await repo.update_workflow("wf_missing", WorkflowUpdateDTO(slug="new_slug"))


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
    step_dto = StepCreateDTO(
        slug=valid_step_doc["slug"],
        name=I18nText(translations=valid_step_doc["name"]["translations"]),
        model_strategy=valid_step_doc["model_strategy"],
        criteria_block_ids=valid_step_doc["criteria_block_ids"],
        extraction_protocol_block_id=valid_step_doc["extraction_protocol_block_id"],
    )
    assert await repo.create_step(step_dto) == "stp_1234567890abcdef"
    assert await repo.update_step("stp_1234567890abcdef", StepUpdateDTO(slug="updated")) == "stp_1234567890abcdef"
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
