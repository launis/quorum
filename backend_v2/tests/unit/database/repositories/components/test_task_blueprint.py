"""Unit tests for TaskBlueprintRepositoryImpl."""

from __future__ import annotations

from pathlib import Path

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.task_blueprint import TaskBlueprintRepositoryImpl
from backend_v2.database.tinydb_driver import TinyDBDriver
from backend_v2.database.wrapper import TinyDBClient
from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.step import Step
from backend_v2.models.dtos.studio import StepUpdateDTO
from backend_v2.models.enums import CognitiveTier


@pytest.fixture
def driver(tmp_path: Path) -> StorageDriver:
    """Provides a real TinyDBDriver."""
    db_path = str(tmp_path / "test_tb.json")
    return TinyDBDriver(TinyDBClient(db_path))


@pytest.fixture
def repo(driver: StorageDriver) -> TaskBlueprintRepositoryImpl:
    """Provides a TaskBlueprintRepositoryImpl instance with the real TinyDB driver."""
    return TaskBlueprintRepositoryImpl(driver)


@pytest.fixture
def sample_step() -> Step:
    """Valid Step domain model fixture."""
    return Step(
        id="stp_1234567890abcdef",
        slug="step_guard",
        name=I18nText(translations={"en": "Guard Step", "fi": "Suojavaihe"}),
        cognitive_tier=CognitiveTier.FAST,
        criteria_block_ids=["blk_1234567890abcdef"],
        extraction_protocol_block_id="blk_1234567890abcdef",
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
        "stp_1234567890abcdef", StepUpdateDTO(name=I18nText(translations={"en": "updated"}))
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
    """Negative: corrupted Step blueprint data raises AppException."""
    await driver.upsert("task_blueprints", {"id": "invalid_id"}, "invalid_id")

    with pytest.raises(AppException):
        await repo.get_task_blueprint_by_id("invalid_id")

    with pytest.raises(AppException):
        await repo.get_all_task_blueprints()


@pytest.mark.asyncio
async def test_task_blueprint_not_found(repo: TaskBlueprintRepositoryImpl, sample_step: Step) -> None:
    """Negative: tests not found branches for get, update, and delete."""
    assert await repo.get_task_blueprint_by_id("stp_missing") is None
    assert (
        await repo.update_task_blueprint("stp_missing", StepUpdateDTO(name=I18nText(translations={"en": "missing"})))
        is False
    )
    assert await repo.delete_task_blueprint("stp_missing") is False
