"""Unit tests for MatrixRepositoryImpl."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.matrix import MatrixRepositoryImpl
from backend_v2.exceptions import ResourceNotFoundError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.models.v2_core import MatrixRow, MatrixScale


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Provides a mocked StorageDriver."""
    driver = AsyncMock(spec=StorageDriver)
    driver.query.return_value = []
    driver.get.return_value = None
    driver.upsert.return_value = "blk_1234567890abcdef"
    driver.update.return_value = True
    driver.delete.return_value = True
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> MatrixRepositoryImpl:
    """Provides a MatrixRepositoryImpl instance with the mocked driver."""
    return MatrixRepositoryImpl(mock_driver)


@pytest.fixture
def sample_matrix() -> MatrixPromptBlock:
    """Provides a valid MatrixPromptBlock instance."""
    return MatrixPromptBlock(
        id="blk_1234567890abcdef",
        slug="mat_1",
        label=I18nText(translations={"en": "Test Matrix", "fi": "Testimatriisi"}),
        description=I18nText(translations={"en": "Description", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        scales=[
            MatrixScale(score=1, ai_label="POOR", name=I18nText(translations={"en": "Poor", "fi": "Heikko"})),
            MatrixScale(
                score=5, ai_label="EXCELLENT", name=I18nText(translations={"en": "Excellent", "fi": "Erinomainen"})
            ),
        ],
        rows=[
            MatrixRow(
                label=I18nText(translations={"en": "dim_1", "fi": "dim_1"}),
                ai_description="Evaluate dimension 1",
            )
        ],
    )


@pytest.mark.asyncio
async def test_matrix_crud_and_dimension_lookup(
    repo: MatrixRepositoryImpl, mock_driver: AsyncMock, sample_matrix: MatrixPromptBlock
) -> None:
    """Positive: tests matrix listing, getting by ID, creation, update, deletion, and dimension search."""
    sample_doc = sample_matrix.model_dump(mode="json")
    mock_driver.query.return_value = [sample_doc]
    mock_driver.get.return_value = sample_doc

    matrices = await repo.get_all_matrices()
    assert len(matrices) == 1
    assert matrices[0].id == "blk_1234567890abcdef"

    matrix = await repo.get_matrix_by_id("blk_1234567890abcdef")
    assert matrix is not None
    assert matrix.id == "blk_1234567890abcdef"

    dim_matches = await repo.get_matrices_using_dimension("dim_1")
    assert dim_matches == ["blk_1234567890abcdef"]

    assert await repo.create_matrix(sample_matrix) == "blk_1234567890abcdef"
    assert await repo.update_matrix("blk_1234567890abcdef", sample_matrix) == "blk_1234567890abcdef"
    assert await repo.delete_matrix("blk_1234567890abcdef") is True


@pytest.mark.asyncio
async def test_matrix_not_found(
    repo: MatrixRepositoryImpl, mock_driver: AsyncMock, sample_matrix: MatrixPromptBlock
) -> None:
    """Negative: update raises ResourceNotFoundError and delete returns False when matrix is missing."""
    mock_driver.get.return_value = None

    assert await repo.get_matrix_by_id("blk_0000000000000000") is None

    with pytest.raises(ResourceNotFoundError):
        await repo.update_matrix("blk_0000000000000000", sample_matrix)

    assert await repo.delete_matrix("blk_0000000000000000") is False
