"""Unit tests for TaskBlueprintRepositoryImpl."""

from __future__ import annotations

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.postgres.storage_driver import PostgresStorageDriver
from backend_v2.database.repositories.components.task_blueprint import TaskBlueprintRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.step import Step
from backend_v2.models.dtos.studio import StepUpdateDTO
from backend_v2.models.enums import CognitiveTier


@pytest.fixture
def driver() -> StorageDriver:
    """Provide an in-memory PostgresStorageDriver instance for hermetic testing.

    Returns:
        Configured StorageDriver instance with pool initialization disabled.
    """
    return PostgresStorageDriver(auto_initialize_pool=False)


@pytest.fixture
def repo(driver: StorageDriver) -> TaskBlueprintRepositoryImpl:
    """Provide a TaskBlueprintRepositoryImpl instance backed by the stateful driver.

    Args:
        driver: Stateful in-memory storage driver.

    Returns:
        Configured TaskBlueprintRepositoryImpl instance.
    """
    return TaskBlueprintRepositoryImpl(driver)


@pytest.fixture
def sample_step() -> Step:
    """Provide a valid Step domain model fixture.

    Returns:
        Validated Step domain model.
    """
    return Step(
        id="stp_0195f3a0000070018234567890abcdef",
        slug="step_guard",
        name=I18nText(translations={"en": "Guard Step", "fi": "Suojavaihe"}),
        cognitive_tier=CognitiveTier.FAST,
        criteria_block_ids=["blk_0195f3a0000070018234567890abcdef"],
        extraction_protocol_block_id="blk_0195f3a0000070018234567890abcdef",
        mcp_tool_params={},
    )


@pytest.mark.asyncio
async def test_task_blueprint_crud(repo: TaskBlueprintRepositoryImpl, sample_step: Step) -> None:
    """Positive: tests CRUD operations for TaskBlueprints with real persistence."""
    created_id = await repo.create_task_blueprint(sample_step)
    assert created_id == sample_step.id

    model = await repo.get_task_blueprint_by_id(sample_step.id)
    assert model is not None
    assert model.id == sample_step.id
    assert model.slug == "step_guard"

    all_models = await repo.get_all_task_blueprints()
    assert len(all_models) == 1
    assert all_models[0].id == sample_step.id

    assert await repo.delete_task_blueprint(sample_step.id) is True
    assert await repo.get_task_blueprint_by_id(sample_step.id) is None
    assert len(await repo.get_all_task_blueprints()) == 0


@pytest.mark.asyncio
async def test_update_task_blueprint(
    repo: TaskBlueprintRepositoryImpl, driver: StorageDriver, sample_step: Step
) -> None:
    """Positive: tests versioned update of TaskBlueprint with real version incrementation."""
    await repo.create_task_blueprint(sample_step)

    res = await repo.update_task_blueprint(
        "stp_0195f3a0000070018234567890abcdef", StepUpdateDTO(name=I18nText(translations={"en": "updated"}))
    )
    assert res is True

    new_version_id = f"{sample_step.id}_v2"
    persisted_raw = await driver.get("task_blueprints", new_version_id)
    assert persisted_raw is not None
    assert persisted_raw["id"] == new_version_id
    assert persisted_raw["slug"] == sample_step.id
    assert persisted_raw["version"] == 2
    assert persisted_raw["is_latest"] is True


@pytest.mark.asyncio
async def test_task_blueprint_parsing_failures(repo: TaskBlueprintRepositoryImpl, driver: StorageDriver) -> None:
    """Negative: corrupted Step blueprint data raises AppException with VALIDATION_FAILED."""
    await driver.upsert(
        "task_blueprints",
        {"id": "stp_0195f3a0000070018111111111111111", "invalid": "data"},
        "stp_0195f3a0000070018111111111111111",
    )

    with pytest.raises(AppException) as exc_info_by_id:
        await repo.get_task_blueprint_by_id("stp_0195f3a0000070018111111111111111")
    assert exc_info_by_id.value.status_code == 500
    assert exc_info_by_id.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "stp_0195f3a0000070018111111111111111" in exc_info_by_id.value.message

    with pytest.raises(AppException) as exc_info_all:
        await repo.get_all_task_blueprints()
    assert exc_info_all.value.status_code == 500
    assert exc_info_all.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "stp_0195f3a0000070018111111111111111" in exc_info_all.value.message


@pytest.mark.asyncio
async def test_get_all_task_blueprints_corrupted_without_id_raises_app_exception(
    repo: TaskBlueprintRepositoryImpl,
    driver: StorageDriver,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negative boundary: get_all_task_blueprints logs 'unknown' when corrupted record lacks id."""

    async def _query_corrupted(collection: str, *args: object, **kwargs: object) -> list[dict[str, str]]:
        return [{"invalid_field": "corrupted"}]

    monkeypatch.setattr(driver, "query", _query_corrupted)

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_task_blueprints()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "unknown" in exc_info.value.message


@pytest.mark.asyncio
async def test_task_blueprint_not_found(repo: TaskBlueprintRepositoryImpl) -> None:
    """Negative boundary: tests not found branches for get, update, and delete."""
    assert await repo.get_task_blueprint_by_id("stp_0195f3a0000070008000000000000000") is None
    assert (
        await repo.update_task_blueprint(
            "stp_0195f3a0000070008000000000000000", StepUpdateDTO(name=I18nText(translations={"en": "missing"}))
        )
        is False
    )
    assert await repo.delete_task_blueprint("stp_0195f3a0000070008000000000000000") is False
