"""Tests for OutputProfileRepositoryImpl."""

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.output_profile import OutputProfileRepositoryImpl
from backend_v2.exceptions import AppException


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Provides a mocked StorageDriver."""
    driver = AsyncMock(spec=StorageDriver)
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> OutputProfileRepositoryImpl:
    """Provides an OutputProfileRepositoryImpl instance with the mocked driver."""
    return OutputProfileRepositoryImpl(mock_driver)


@pytest.mark.asyncio
async def test_output_profile_crud(repo: OutputProfileRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test CRUD operations for OutputProfiles."""
    sample_doc = {
        "id": "prf_1234567890abcdef",
        "slug": "exec-summary",
        "workflow_id": "wf_1234567890abcdef",
        "name": {"translations": {"fi": "Tiivistelmä", "en": "Summary"}},
        "target_block_order": ["executive_summary_block", "global_score_block"],
    }
    mock_driver.get.return_value = sample_doc
    mock_driver.query.return_value = [sample_doc]
    mock_driver.upsert.return_value = "prf_1234567890abcdef"
    mock_driver.update.return_value = True
    mock_driver.delete.return_value = True

    model = await repo.get_output_profile_by_id("prf_1234567890abcdef")
    assert model is not None
    assert model.id == "prf_1234567890abcdef"
    assert model.slug == "exec-summary"

    all_models = await repo.get_all_output_profiles()
    assert len(all_models) == 1
    assert all_models[0].id == "prf_1234567890abcdef"

    assert await repo.create_output_profile(sample_doc) == "prf_1234567890abcdef"
    assert await repo.update_output_profile("prf_1234567890abcdef", {"slug": "updated"}) is True
    assert await repo.delete_output_profile("prf_1234567890abcdef") is True


@pytest.mark.asyncio
async def test_get_all_output_profiles_models_failure(
    repo: OutputProfileRepositoryImpl, mock_driver: AsyncMock
) -> None:
    """Test parsing failure for OutputProfiles models."""
    mock_driver.query.return_value = [{"invalid": "data"}]
    with pytest.raises(AppException) as exc:
        await repo.get_all_output_profiles_models()
    assert exc.value.status_code == 500
