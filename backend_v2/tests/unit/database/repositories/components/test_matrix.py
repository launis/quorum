"""Unit tests for MatrixRepositoryImpl."""

from __future__ import annotations

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.postgres.storage_driver import PostgresStorageDriver
from backend_v2.database.repositories.components.matrix import MatrixRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import MatrixRow, MatrixScale
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.enums import BlockDataType, PromptBlockCategory


@pytest.fixture
def driver() -> StorageDriver:
    """Provide an in-memory PostgresStorageDriver instance for hermetic testing.

    Returns:
        Configured StorageDriver instance with pool initialization disabled.
    """
    return PostgresStorageDriver(auto_initialize_pool=False)


@pytest.fixture
def repo(driver: StorageDriver) -> MatrixRepositoryImpl:
    """Provide a MatrixRepositoryImpl instance backed by the stateful driver.

    Args:
        driver: Stateful in-memory storage driver.

    Returns:
        Configured MatrixRepositoryImpl instance.
    """
    return MatrixRepositoryImpl(driver)


@pytest.fixture
def sample_matrix() -> MatrixPromptBlock:
    """Provide a valid MatrixPromptBlock instance.

    Returns:
        Validated MatrixPromptBlock domain model.
    """
    return MatrixPromptBlock(
        id="blk_0195f3a0000070018234567890abcdef",
        slug="mat_123",
        label=I18nText(translations={"en": "Test Matrix", "fi": "Testimatriisi"}),
        description=I18nText(translations={"en": "Description", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        scales=[
            MatrixScale(
                score=1,
                ai_label="POOR",
                name=I18nText(translations={"en": "Poor", "fi": "Heikko"}),
            ),
            MatrixScale(
                score=5,
                ai_label="EXCELLENT",
                name=I18nText(translations={"en": "Excellent", "fi": "Erinomainen"}),
            ),
        ],
        rows=[
            MatrixRow(
                label=I18nText(translations={"en": "dim_1", "fi": "dim_1"}),
                ai_description="Evaluate dimension 1 for dim_ai_desc",
            )
        ],
    )


@pytest.mark.asyncio
async def test_matrix_crud_and_dimension_lookup_roundtrip(
    repo: MatrixRepositoryImpl,
    sample_matrix: MatrixPromptBlock,
) -> None:
    """Positive: verify full stateful CRUD roundtrip and dimension lookup for matrices."""
    created_id = await repo.create_matrix(sample_matrix)
    assert created_id == sample_matrix.id

    fetched = await repo.get_matrix_by_id(sample_matrix.id)
    assert fetched is not None
    assert isinstance(fetched, MatrixPromptBlock)
    assert fetched.id == sample_matrix.id

    all_matrices = await repo.get_all_matrices()
    assert len(all_matrices) == 1
    assert all_matrices[0].id == sample_matrix.id

    assert await repo.get_matrices_using_dimension("dim_1") == [sample_matrix.id]
    assert await repo.get_matrices_using_dimension("dim_ai_desc") == [sample_matrix.id]
    assert await repo.get_matrices_using_dimension("non_existent_dim") == []

    updated_matrix = sample_matrix.model_copy(update={"ai_description": "Updated cognitive instructions."})
    updated_id = await repo.update_matrix(sample_matrix.id, updated_matrix)
    assert updated_id == sample_matrix.id

    refetched = await repo.get_matrix_by_id(sample_matrix.id)
    assert refetched is not None
    assert isinstance(refetched, MatrixPromptBlock)
    assert refetched.ai_description == "Updated cognitive instructions."

    deleted = await repo.delete_matrix(sample_matrix.id)
    assert deleted is True
    assert await repo.get_matrix_by_id(sample_matrix.id) is None
    assert await repo.get_all_matrices() == []


@pytest.mark.asyncio
async def test_update_matrix_not_found(
    repo: MatrixRepositoryImpl,
    sample_matrix: MatrixPromptBlock,
) -> None:
    """Negative: update_matrix raises ResourceNotFoundError if matrix does not exist."""
    with pytest.raises(ResourceNotFoundError) as exc_info:
        await repo.update_matrix("blk_0195f3a0000070008000000000000000", sample_matrix)

    assert exc_info.value.details["resource_type"] == "Matrix"
    assert exc_info.value.details["resource_id"] == "blk_0195f3a0000070008000000000000000"


@pytest.mark.asyncio
async def test_delete_matrix_not_found(
    repo: MatrixRepositoryImpl,
) -> None:
    """Negative boundary: delete_matrix returns False when matrix does not exist."""
    assert await repo.delete_matrix("blk_0195f3a0000070008000000000000000") is False


@pytest.mark.asyncio
async def test_get_matrix_by_id_corrupted_raises_app_exception(
    repo: MatrixRepositoryImpl,
    driver: StorageDriver,
) -> None:
    """Negative: get_matrix_by_id raises AppException(500) on corrupted record."""
    await driver.upsert(
        "components",
        {"id": "blk_0195f3a0000070018111111111111111", "category_id": "invalid_category"},
        "blk_0195f3a0000070018111111111111111",
    )

    with pytest.raises(AppException) as exc_info:
        await repo.get_matrix_by_id("blk_0195f3a0000070018111111111111111")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "blk_0195f3a0000070018111111111111111" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_matrices_corrupted_with_id_raises_app_exception(
    repo: MatrixRepositoryImpl,
    driver: StorageDriver,
) -> None:
    """Negative: get_all_matrices raises AppException(500) when stored record with ID is invalid."""
    await driver.upsert(
        "components",
        {
            "id": "blk_0195f3a0000070028222222222222222",
            "category_id": PromptBlockCategory.MATRIX.value,
            "type": "invalid_type",
        },
        "blk_0195f3a0000070028222222222222222",
    )

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_matrices()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "blk_0195f3a0000070028222222222222222" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_matrices_corrupted_without_id_raises_app_exception(
    repo: MatrixRepositoryImpl,
    driver: StorageDriver,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negative boundary: get_all_matrices logs 'unknown' when corrupted record lacks id."""

    async def _query_corrupted(collection: str, *args: object, **kwargs: object) -> list[dict[str, str]]:
        return [{"category_id": PromptBlockCategory.MATRIX.value}]

    monkeypatch.setattr(driver, "query", _query_corrupted)

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_matrices()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "unknown" in exc_info.value.message
