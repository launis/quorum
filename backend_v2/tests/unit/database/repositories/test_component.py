"""Tests for ComponentRepositoryImpl."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.component import ComponentRepositoryImpl
from backend_v2.exceptions import ResourceNotFoundError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, SystemRulePromptBlock
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.models.v2_core import MatrixRow, MatrixScale


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Provides a mocked StorageDriver."""
    driver = AsyncMock(spec=StorageDriver)
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> ComponentRepositoryImpl:
    """Provides a ComponentRepositoryImpl instance with the mocked driver."""
    return ComponentRepositoryImpl(mock_driver)


@pytest.fixture
def sample_system_rule() -> SystemRulePromptBlock:
    """Provides a valid SystemRulePromptBlock instance."""
    return SystemRulePromptBlock(
        id="blk_1111111111111111",
        slug="rule_1",
        label=I18nText(translations={"en": "Test Rule", "fi": "Testi sääntö"}),
        description=I18nText(translations={"en": "Description", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.INSTRUCTION,
        instruction_text="Test instruction.",
    )


@pytest.fixture
def sample_matrix() -> MatrixPromptBlock:
    """Provides a valid MatrixPromptBlock instance."""
    return MatrixPromptBlock(
        id="blk_2222222222222222",
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
                label=I18nText(translations={"en": "dim_target", "fi": "dim_target"}),
                ai_description="Evaluate target dimension",
            )
        ],
    )


@pytest.mark.asyncio
async def test_get_all_components(
    repo: ComponentRepositoryImpl,
    mock_driver: AsyncMock,
    sample_system_rule: SystemRulePromptBlock,
    sample_matrix: MatrixPromptBlock,
) -> None:
    """Test retrieving all components with and without filters."""
    mock_driver.query.return_value = [
        sample_system_rule.model_dump(mode="json"),
        sample_matrix.model_dump(mode="json"),
    ]
    res = await repo.get_all_components(type="system_rule")
    assert len(res) == 2
    mock_driver.query.assert_called_once()

    mock_driver.query.reset_mock()
    mock_driver.query.return_value = [
        sample_system_rule.model_dump(mode="json"),
        sample_matrix.model_dump(mode="json"),
    ]
    res2 = await repo.get_all_components(type="instruction", exclude_types=["float"])
    assert len(res2) == 1
    assert res2[0].id == "blk_1111111111111111"


@pytest.mark.asyncio
async def test_get_component_by_id(
    repo: ComponentRepositoryImpl, mock_driver: AsyncMock, sample_system_rule: SystemRulePromptBlock
) -> None:
    """Test getting component by ID."""
    mock_driver.get.return_value = sample_system_rule.model_dump(mode="json")
    res = await repo.get_component_by_id("blk_1111111111111111")
    assert res is not None
    assert res.id == "blk_1111111111111111"
    mock_driver.get.assert_called_once_with("components", "blk_1111111111111111")


@pytest.mark.asyncio
async def test_get_component_by_name(
    repo: ComponentRepositoryImpl, mock_driver: AsyncMock, sample_system_rule: SystemRulePromptBlock
) -> None:
    """Test getting component by name."""
    mock_driver.query.return_value = [sample_system_rule.model_dump(mode="json")]
    res = await repo.get_component_by_name("Test Rule")
    assert res is not None
    assert res.id == "blk_1111111111111111"
    mock_driver.query.assert_called_once()


@pytest.mark.asyncio
async def test_update_component_metadata(
    repo: ComponentRepositoryImpl, mock_driver: AsyncMock, sample_system_rule: SystemRulePromptBlock
) -> None:
    """Test updating metadata for component."""
    mock_driver.get.return_value = sample_system_rule.model_dump(mode="json")
    mock_driver.update.return_value = True
    res = await repo.update_component_metadata("blk_1111111111111111", "mod", "cls")
    assert res is True
    mock_driver.update.assert_called_once_with(
        "components", "blk_1111111111111111", {"module": "mod", "class_name": "cls"}
    )


@pytest.mark.asyncio
async def test_update_component_metadata_not_found(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test updating metadata for non-existent component."""
    mock_driver.get.return_value = None
    res = await repo.update_component_metadata("blk_0000000000000000", "mod", "cls")
    assert res is False


@pytest.mark.asyncio
async def test_create_register_update_delete_component(
    repo: ComponentRepositoryImpl, mock_driver: AsyncMock, sample_system_rule: SystemRulePromptBlock
) -> None:
    """Test basic CRUD for generic components."""
    mock_driver.upsert.return_value = "blk_1111111111111111"
    res1 = await repo.create_component(sample_system_rule)
    res2 = await repo.register_component(sample_system_rule)
    assert res1 == "blk_1111111111111111"
    assert res2 == "blk_1111111111111111"

    mock_driver.get.return_value = sample_system_rule.model_dump(mode="json")
    mock_driver.update.return_value = True
    res3 = await repo.update_component("blk_1111111111111111", sample_system_rule)
    assert res3 == "blk_1111111111111111"

    mock_driver.delete.return_value = True
    res4 = await repo.delete_component("blk_1111111111111111")
    assert res4 is True


@pytest.mark.asyncio
async def test_delete_component_not_found(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test deleting non-existent component."""
    mock_driver.get.return_value = None
    res = await repo.delete_component("blk_0000000000000000")
    assert res is False


@pytest.mark.asyncio
async def test_update_component_not_found(
    repo: ComponentRepositoryImpl, mock_driver: AsyncMock, sample_system_rule: SystemRulePromptBlock
) -> None:
    """Negative: update_component raises ResourceNotFoundError when component missing."""
    mock_driver.get.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await repo.update_component("blk_0000000000000000", sample_system_rule)


@pytest.mark.asyncio
async def test_get_components_using_dimension(
    repo: ComponentRepositoryImpl, mock_driver: AsyncMock, sample_matrix: MatrixPromptBlock
) -> None:
    """Positive: tests searching matrix components referencing a dimension ID."""
    other_matrix = sample_matrix.model_copy(
        update={
            "id": "blk_3333333333333333",
            "rows": [
                MatrixRow(
                    label=I18nText(translations={"en": "other_dim", "fi": "other_dim"}),
                    ai_description="Other description",
                )
            ],
        }
    )
    mock_driver.query.return_value = [
        sample_matrix.model_dump(mode="json"),
        other_matrix.model_dump(mode="json"),
    ]
    matches = await repo.get_components_using_dimension("dim_target")
    assert matches == ["blk_2222222222222222"]
