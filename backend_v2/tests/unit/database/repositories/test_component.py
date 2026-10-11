"""Tests for ComponentRepositoryImpl."""

from __future__ import annotations

import copy
from typing import Any

import pytest
from pydantic import JsonValue

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.component import ComponentRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import MatrixRow
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, SystemRulePromptBlock
from backend_v2.tests.factories.model_factories import (
    MatrixPromptBlockFactory,
    SystemRulePromptBlockFactory,
)


class _FakeStorageDriver:
    """Stateful in-memory StorageDriver fake storing raw documents per collection."""

    def __init__(self) -> None:
        self.tables: dict[str, dict[str, dict[str, JsonValue]]] = {}

    def _get_table(self, collection: str) -> Any:
        return self.tables.setdefault(collection, {})

    async def get(self, collection: str, doc_id: str) -> Any:
        table = self._get_table(collection)
        doc = table.get(doc_id)
        return copy.deepcopy(doc) if doc is not None else None

    async def upsert(self, collection: str, data: Any, doc_id: str) -> str:
        table = self._get_table(collection)
        table[doc_id] = copy.deepcopy(data)
        return doc_id

    async def update(self, collection: str, doc_id: str, updates: Any) -> bool:
        table = self._get_table(collection)
        if doc_id not in table:
            return False
        table[doc_id].update(copy.deepcopy(updates))
        return True

    async def delete(self, collection: str, doc_id: str) -> bool:
        table = self._get_table(collection)
        if doc_id in table:
            del table[doc_id]
            return True
        return False

    async def query(
        self,
        collection: str,
        filters: list[Filter] | None = None,
        limit: int | None = None,
        sort_by: str | None = None,
        descending: bool = False,
    ) -> Any:
        table = self._get_table(collection)
        results = list(table.values())
        if filters:
            for f in filters:
                if f.operator == "==":
                    filtered = []
                    for r in results:
                        val = r[f.field] if f.field in r else None
                        if f.field == "name" and val is None:
                            val = r["label"] if "label" in r else None
                        if f.field == "type" and f.value in ("evaluation_matrix", "matrix"):
                            cat = r["category_id"] if "category_id" in r else None
                            is_ev = r["is_evaluative"] if "is_evaluative" in r else None
                            if cat in ("matrix", "evaluation_matrix") or is_ev is True:
                                filtered.append(r)
                                continue
                        if val == f.value:
                            filtered.append(r)
                        elif val is not None and "translations" in val:
                            trans = val["translations"]
                            if ("en" in trans and trans["en"] == f.value) or ("fi" in trans and trans["fi"] == f.value):
                                filtered.append(r)
                    results = filtered
        if limit is not None:
            results = results[:limit]
        return [copy.deepcopy(r) for r in results]


@pytest.fixture
def fake_driver() -> _FakeStorageDriver:
    """Provides a stateful in-memory StorageDriver fake."""
    return _FakeStorageDriver()


@pytest.fixture
def repo(fake_driver: _FakeStorageDriver) -> ComponentRepositoryImpl:
    """Provides a ComponentRepositoryImpl instance with the fake driver."""
    return ComponentRepositoryImpl(fake_driver)


@pytest.fixture
def sample_system_rule() -> SystemRulePromptBlock:
    """Provides a valid SystemRulePromptBlock instance from Polyfactory."""
    return SystemRulePromptBlockFactory.build(
        id="blk_1111111111111111",
        label=I18nText(translations={"en": "Test Rule", "fi": "Testi sääntö"}),
    )


@pytest.fixture
def sample_matrix() -> MatrixPromptBlock:
    """Provides a valid MatrixPromptBlock instance from Polyfactory."""
    return MatrixPromptBlockFactory.build(
        id="blk_2222222222222222",
        label=I18nText(translations={"en": "Test Matrix", "fi": "Testimatriisi"}),
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
    fake_driver: _FakeStorageDriver,
    sample_system_rule: SystemRulePromptBlock,
    sample_matrix: MatrixPromptBlock,
) -> None:
    """Test retrieving all components with and without filters."""
    await fake_driver.upsert("components", sample_system_rule.model_dump(mode="json"), sample_system_rule.id)
    await fake_driver.upsert("components", sample_matrix.model_dump(mode="json"), sample_matrix.id)

    res = await repo.get_all_components()
    assert len(res) == 2

    res_instruction = await repo.get_all_components(type="instruction", exclude_types=["float"])
    assert len(res_instruction) == 1
    assert res_instruction[0].id == "blk_1111111111111111"


@pytest.mark.asyncio
async def test_get_component_by_id(
    repo: ComponentRepositoryImpl,
    fake_driver: _FakeStorageDriver,
    sample_system_rule: SystemRulePromptBlock,
) -> None:
    """Test getting component by ID."""
    await fake_driver.upsert("components", sample_system_rule.model_dump(mode="json"), sample_system_rule.id)
    res = await repo.get_component_by_id("blk_1111111111111111")
    assert res is not None
    assert res.id == "blk_1111111111111111"


@pytest.mark.asyncio
async def test_get_component_by_name(
    repo: ComponentRepositoryImpl,
    fake_driver: _FakeStorageDriver,
    sample_system_rule: SystemRulePromptBlock,
) -> None:
    """Test getting component by name."""
    await fake_driver.upsert("components", sample_system_rule.model_dump(mode="json"), sample_system_rule.id)
    res = await repo.get_component_by_name("Test Rule")
    assert res is not None
    assert res.id == "blk_1111111111111111"


@pytest.mark.asyncio
async def test_update_component_metadata(
    repo: ComponentRepositoryImpl,
    fake_driver: _FakeStorageDriver,
    sample_system_rule: SystemRulePromptBlock,
) -> None:
    """Test updating metadata for component."""
    await fake_driver.upsert("components", sample_system_rule.model_dump(mode="json"), sample_system_rule.id)
    res = await repo.update_component_metadata("blk_1111111111111111", "mod", "cls")
    assert res is True
    updated = await fake_driver.get("components", "blk_1111111111111111")
    assert updated is not None
    assert updated["module"] == "mod"
    assert updated["class_name"] == "cls"


@pytest.mark.asyncio
async def test_update_component_metadata_not_found(
    repo: ComponentRepositoryImpl,
    fake_driver: _FakeStorageDriver,
) -> None:
    """Test updating metadata for non-existent component."""
    res = await repo.update_component_metadata("blk_0000000000000000", "mod", "cls")
    assert res is False


@pytest.mark.asyncio
async def test_create_register_update_delete_component(
    repo: ComponentRepositoryImpl,
    sample_system_rule: SystemRulePromptBlock,
) -> None:
    """Test basic stateful CRUD roundtrip for generic components."""
    res1 = await repo.create_component(sample_system_rule)
    assert res1 == "blk_1111111111111111"

    fetched = await repo.get_component_by_id("blk_1111111111111111")
    assert fetched is not None
    assert fetched.id == "blk_1111111111111111"

    updated_rule = sample_system_rule.model_copy(update={"instruction_text": "Updated instruction."})
    res2 = await repo.update_component("blk_1111111111111111", updated_rule)
    assert res2 == "blk_1111111111111111"

    refetched = await repo.get_component_by_id("blk_1111111111111111")
    assert refetched is not None
    assert isinstance(refetched, SystemRulePromptBlock)
    assert refetched.instruction_text == "Updated instruction."

    res3 = await repo.delete_component("blk_1111111111111111")
    assert res3 is True

    assert await repo.get_component_by_id("blk_1111111111111111") is None


@pytest.mark.asyncio
async def test_delete_component_not_found(
    repo: ComponentRepositoryImpl,
) -> None:
    """Test deleting non-existent component."""
    res = await repo.delete_component("blk_0000000000000000")
    assert res is False


@pytest.mark.asyncio
async def test_update_component_not_found(
    repo: ComponentRepositoryImpl,
    sample_system_rule: SystemRulePromptBlock,
) -> None:
    """Negative: update_component raises ResourceNotFoundError when component missing."""
    with pytest.raises(ResourceNotFoundError):
        await repo.update_component("blk_0000000000000000", sample_system_rule)


@pytest.mark.asyncio
async def test_get_components_using_dimension(
    repo: ComponentRepositoryImpl,
    fake_driver: _FakeStorageDriver,
    sample_matrix: MatrixPromptBlock,
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
    await fake_driver.upsert("components", sample_matrix.model_dump(mode="json"), sample_matrix.id)
    await fake_driver.upsert("components", other_matrix.model_dump(mode="json"), other_matrix.id)

    matches = await repo.get_components_using_dimension("dim_target")
    assert matches == ["blk_2222222222222222"]


@pytest.mark.asyncio
async def test_update_component_empty_payload(
    repo: ComponentRepositoryImpl,
) -> None:
    """Negative ISTQB Boundary Partition: Updating non-existent component raises ResourceNotFoundError."""
    empty_id = "blk_0000000000000000"
    dummy_rule = SystemRulePromptBlockFactory.build(id=empty_id)
    with pytest.raises(ResourceNotFoundError):
        await repo.update_component(empty_id, dummy_rule)


@pytest.mark.asyncio
async def test_get_component_malformed_id(
    repo: ComponentRepositoryImpl,
    fake_driver: _FakeStorageDriver,
) -> None:
    """Negative ISTQB Boundary Partition: Corrupt/malformed document in database raises AppException."""
    malformed_id = "blk_9999999999999999"
    await fake_driver.upsert("components", {"id": malformed_id, "corrupted": True}, malformed_id)
    with pytest.raises(AppException) as exc_info:
        await repo.get_component_by_id(malformed_id)
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
