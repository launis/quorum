"""Unit tests for KnowledgeRepositoryImpl."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.knowledge import KnowledgeRepositoryImpl
from backend_v2.models.domain.knowledge import ClaimCreateDTO, ConceptCreateDTO, ReferenceCreateDTO


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Mock storage driver."""
    driver = AsyncMock(spec=StorageDriver)
    driver.query.return_value = []
    driver.get.return_value = None
    driver.upsert.return_value = "id_123"
    driver.update.return_value = True
    driver.delete.return_value = True
    driver.clear.return_value = None
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> KnowledgeRepositoryImpl:
    """Knowledge repository fixture."""
    return KnowledgeRepositoryImpl(mock_driver)


@pytest.mark.asyncio
async def test_banned_phrases_crud(repo: KnowledgeRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests banned phrases CRUD with corrupted entries and idempotency."""
    mock_driver.query.side_effect = [
        [{"id": "corrupted"}, {"id": "bp_1", "phrase": "test slop", "language": "en"}],
        [],  # for add_banned_phrase check (not existing)
        [{"id": "bp_1", "phrase": "test slop", "language": "en"}],  # for delete check (found)
        [],  # for delete check (not found)
    ]
    phrases = await repo.get_banned_phrases()
    assert len(phrases) == 1
    assert phrases[0].id == "bp_1"
    assert phrases[0].phrase == "test slop"
    assert phrases[0].language == "en"

    await repo.add_banned_phrase("new slop", language="fi")
    mock_driver.upsert.assert_called_once()

    assert await repo.delete_banned_phrase("test slop") is True
    assert await repo.delete_banned_phrase("missing slop") is False


@pytest.mark.asyncio
async def test_prompt_template_retrieval(repo: KnowledgeRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests prompt template retrieval via direct get, query fallback, and not found."""
    # 1. Direct get
    mock_driver.get.return_value = {
        "system_prompt": "System instruction",
        "user_prompt": "Hello {{name}}",
    }
    template = await repo.get_prompt_template("tpl_1")
    assert template is not None
    assert template.system == "System instruction"
    assert template.user == "Hello {{name}}"

    # 2. Query fallback
    mock_driver.get.return_value = None
    mock_driver.query.return_value = [{"system_prompt": "Fallback sys", "user_prompt": "Fallback usr"}]
    tpl_query = await repo.get_prompt_template("tpl_2")
    assert tpl_query is not None
    assert tpl_query.system == "Fallback sys"

    # 3. Not found
    mock_driver.query.return_value = []
    assert await repo.get_prompt_template("tpl_missing") is None


@pytest.mark.asyncio
async def test_concepts_references_claims_lifecycle(repo: KnowledgeRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests concepts, references, claims CRUD and knowledge base clearing."""
    mock_driver.query.side_effect = [
        [{"name": "No ID Concept"}, {"id": "c1", "name": "Concept 1"}],
        [{"name": "No ID Ref"}, {"id": "r1", "name": "Ref 1"}],
        [{"name": "No ID Claim"}, {"id": "cl1", "name": "Claim 1"}],
    ]

    concepts = await repo.get_concepts()
    assert len(concepts) == 1
    assert concepts[0].id == "c1"

    refs = await repo.get_references()
    assert len(refs) == 1
    assert refs[0].id == "r1"

    claims = await repo.get_claims()
    assert len(claims) == 1
    assert claims[0].id == "cl1"

    assert await repo.add_concept(ConceptCreateDTO(name="Concept 2")) == "id_123"
    assert await repo.add_reference(ReferenceCreateDTO(name="Ref 2")) == "id_123"
    assert await repo.add_claim(ClaimCreateDTO(name="Claim 2")) == "id_123"

    await repo.clear_knowledge_base()
    assert mock_driver.clear.call_count == 3
