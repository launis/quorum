from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.exceptions import ServiceUnavailableError
from backend.services.knowledge_base_service import KnowledgeBaseService


@pytest.mark.asyncio
async def test_retrieve_context_empty_kb():
    # Arrange
    mock_repo = AsyncMock()
    mock_repo.get_concepts.return_value = []
    mock_repo.get_references.return_value = []
    mock_repo.get_claims.return_value = []
    # FIX: Pass mock storage_client to prevent real import
    service = KnowledgeBaseService(repository=mock_repo, storage_client=MagicMock())

    # Act
    result = await service.retrieve_context()

    # Assert
    assert result == []
    mock_repo.get_concepts.assert_called_once()
    mock_repo.get_references.assert_called_once()
    mock_repo.get_claims.assert_called_once()


@pytest.mark.asyncio
async def test_retrieve_context_no_query_returns_summary():
    # Arrange
    mock_repo = AsyncMock()
    items = [
        {"id": "1", "type": "concept", "term": "Term1", "definition": "Def1", "source_file": "file1.docx"},
        {"id": "2", "type": "reference", "term": "Ref1", "definition": "Cit1", "source_file": "file2.md"},
    ]
    mock_repo.get_concepts.return_value = [items[0]]
    mock_repo.get_references.return_value = [items[1]]
    mock_repo.get_claims.return_value = []
    service = KnowledgeBaseService(repository=mock_repo, storage_client=MagicMock())

    # Act
    result = await service.retrieve_context(query=None)

    # Assert
    assert len(result) == 2
    assert result[0].term == "Term1"
    assert result[1].term == "Ref1"


@pytest.mark.asyncio
async def test_retrieve_context_with_query_filtering():
    # Arrange
    mock_repo = AsyncMock()
    items = [
        {"id": "1", "type": "concept", "term": "Alpha", "definition": "First letter", "source_file": "doc.md"},
        {"id": "2", "type": "concept", "term": "Beta", "definition": "Second letter", "source_file": "doc.md"},
        {
            "id": "3",
            "type": "claim",
            "term": "Gamma",
            "definition": "Contains alpha inside definition",
            "source_file": "doc.md",
        },
    ]
    mock_repo.get_concepts.return_value = [items[0], items[1]]
    mock_repo.get_references.return_value = []
    mock_repo.get_claims.return_value = [items[2]]
    service = KnowledgeBaseService(repository=mock_repo, storage_client=MagicMock())

    # Act
    # Should match "Alpha" (term) and "Gamma" (definition contains 'alpha')
    result = await service.retrieve_context(query="Alpha")

    # Assert
    assert len(result) == 2
    terms = [r.term for r in result]
    assert "Alpha" in terms
    assert "Gamma" in terms
    assert "Beta" not in terms


@pytest.mark.asyncio
async def test_retrieve_context_no_matches():
    # Arrange
    mock_repo = AsyncMock()
    items = [{"id": "1", "type": "concept", "term": "Foo", "definition": "Bar"}]
    mock_repo.get_concepts.return_value = items
    mock_repo.get_references.return_value = []
    mock_repo.get_claims.return_value = []
    service = KnowledgeBaseService(repository=mock_repo, storage_client=MagicMock())

    # Act
    result = await service.retrieve_context(query="Zulul")

    # Assert
    assert result == []


@pytest.mark.asyncio
async def test_retrieve_context_exception_handling():
    # Arrange
    mock_repo = AsyncMock()
    mock_repo.get_concepts.side_effect = Exception("DB Error")
    service = KnowledgeBaseService(repository=mock_repo, storage_client=MagicMock())

    # Act & Assert
    with pytest.raises(ServiceUnavailableError, match="DB Error"):
        await service.retrieve_context()
