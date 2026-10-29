"""Unit tests for OutputProfileRepositoryImpl."""

from __future__ import annotations

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.postgres.storage_driver import PostgresStorageDriver
from backend_v2.database.repositories.components.output_profile import OutputProfileRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.enums import TargetBlockType


@pytest.fixture
def driver() -> StorageDriver:
    """Provide an in-memory PostgresStorageDriver instance for hermetic testing.

    Returns:
        Configured StorageDriver instance with pool initialization disabled.
    """
    return PostgresStorageDriver(auto_initialize_pool=False)


@pytest.fixture
def repo(driver: StorageDriver) -> OutputProfileRepositoryImpl:
    """Provide an OutputProfileRepositoryImpl instance backed by the stateful driver.

    Args:
        driver: Stateful in-memory storage driver.

    Returns:
        Configured OutputProfileRepositoryImpl instance.
    """
    return OutputProfileRepositoryImpl(driver)


@pytest.fixture
def sample_output_profile() -> OutputProfile:
    """Provide a valid OutputProfile instance.

    Returns:
        Validated OutputProfile domain model.
    """
    return OutputProfile(
        id="prf_1234567890abcdef",
        slug="exec-summary",
        workflow_id="wf_1234567890abcdef",
        name=I18nText(translations={"fi": "Tiivistelmä", "en": "Summary"}),
        target_block_order=[
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
            TargetBlockType.GLOBAL_SCORE_BLOCK,
        ],
    )


@pytest.mark.asyncio
async def test_output_profile_crud_roundtrip(
    repo: OutputProfileRepositoryImpl,
    sample_output_profile: OutputProfile,
) -> None:
    """Positive: verify full stateful CRUD roundtrip for OutputProfileRepositoryImpl."""
    created_id = await repo.create_output_profile(sample_output_profile)
    assert created_id == sample_output_profile.id

    fetched = await repo.get_output_profile_by_id(sample_output_profile.id)
    assert fetched is not None
    assert fetched.id == sample_output_profile.id
    assert fetched.slug == "exec-summary"

    all_models = await repo.get_all_output_profiles()
    assert len(all_models) == 1
    assert all_models[0].id == sample_output_profile.id

    all_models_alias = await repo.get_all_output_profiles_models()
    assert len(all_models_alias) == 1
    assert all_models_alias[0].id == sample_output_profile.id

    updated_profile = sample_output_profile.model_copy(
        update={"tone_instruction": "Concise executive style."}
    )
    updated_ok = await repo.update_output_profile(sample_output_profile.id, updated_profile)
    assert updated_ok is True

    refetched = await repo.get_output_profile_by_id(sample_output_profile.id)
    assert refetched is not None
    assert refetched.tone_instruction == "Concise executive style."

    deleted_ok = await repo.delete_output_profile(sample_output_profile.id)
    assert deleted_ok is True
    assert await repo.get_output_profile_by_id(sample_output_profile.id) is None
    assert await repo.get_all_output_profiles() == []


@pytest.mark.asyncio
async def test_get_output_profile_by_id_not_found(repo: OutputProfileRepositoryImpl) -> None:
    """Negative boundary: get_output_profile_by_id returns None when profile does not exist."""
    assert await repo.get_output_profile_by_id("prf_0000000000000000") is None


@pytest.mark.asyncio
async def test_update_output_profile_not_found(
    repo: OutputProfileRepositoryImpl,
    sample_output_profile: OutputProfile,
) -> None:
    """Negative boundary: update_output_profile returns False when profile does not exist."""
    assert await repo.update_output_profile("prf_0000000000000000", sample_output_profile) is False


@pytest.mark.asyncio
async def test_delete_output_profile_not_found(repo: OutputProfileRepositoryImpl) -> None:
    """Negative boundary: delete_output_profile returns False when profile does not exist."""
    assert await repo.delete_output_profile("prf_0000000000000000") is False


@pytest.mark.asyncio
async def test_get_output_profile_by_id_corrupted_raises_app_exception(
    repo: OutputProfileRepositoryImpl,
    driver: StorageDriver,
) -> None:
    """Negative: get_output_profile_by_id raises AppException(500) on corrupted record."""
    await driver.upsert(
        "output_profiles",
        {"id": "prf_1111111111111111", "invalid_field": "corrupted"},
        "prf_1111111111111111",
    )

    with pytest.raises(AppException) as exc_info:
        await repo.get_output_profile_by_id("prf_1111111111111111")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "prf_1111111111111111" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_output_profiles_corrupted_with_id_raises_app_exception(
    repo: OutputProfileRepositoryImpl,
    driver: StorageDriver,
) -> None:
    """Negative: get_all_output_profiles raises AppException(500) when stored record with ID is invalid."""
    await driver.upsert(
        "output_profiles",
        {"id": "prf_2222222222222222", "invalid_field": "corrupted"},
        "prf_2222222222222222",
    )

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_output_profiles_models()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "prf_2222222222222222" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_output_profiles_corrupted_without_id_raises_app_exception(
    repo: OutputProfileRepositoryImpl,
    driver: StorageDriver,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negative boundary: get_all_output_profiles logs 'unknown' when corrupted record lacks id."""

    async def _query_corrupted(collection: str, *args: object, **kwargs: object) -> list[dict[str, str]]:
        return [{"invalid_field": "corrupted"}]

    monkeypatch.setattr(driver, "query", _query_corrupted)

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_output_profiles()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "unknown" in exc_info.value.message
