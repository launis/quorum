from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.integrity import (
    CitationAudit,
    IntegrityGlobalInputsDTO,
    KnowledgeItem,
    StepContext,
)


def test_knowledge_item_strict_validation() -> None:
    """Test that KnowledgeItem follows V2CoreBase strict and frozen constraints."""
    item = KnowledgeItem(term="Gravity", definition="A natural phenomenon.")

    assert item.term == "Gravity"
    assert item.definition == "A natural phenomenon."

    # extra=forbid
    with pytest.raises(ValidationError):
        KnowledgeItem.model_validate(
            {"term": "Gravity", "definition": "A natural phenomenon.", "extra_field": "not allowed"}
        )


def test_step_context_validation() -> None:
    """Test that StepContext properly handles knowledge items and extra forbid."""
    item = KnowledgeItem(term="Test", definition="Def")
    ctx = StepContext(precedents="None", knowledge_items=[item])

    assert ctx.precedents == "None"
    assert len(ctx.knowledge_items) == 1
    assert ctx.knowledge_items[0].term == "Test"

    with pytest.raises(ValidationError):
        StepContext.model_validate(
            {"precedents": "None", "knowledge_items": [{"term": "Test", "definition": "Def"}], "random_key": "val"}
        )


def test_citation_audit_defaults() -> None:
    """Test default values of CitationAudit."""
    audit = CitationAudit()
    assert audit.valid_citations == 0
    assert audit.invalid_citations == []
    assert audit.integrity_score == 1.0


def test_citation_audit_bounds() -> None:
    """Test that CitationAudit integrity_score bounds are enforced."""
    with pytest.raises(AppException) as exc_info:
        CitationAudit(integrity_score=1.5)
    assert "integrity_score must be between 0.0 and 1.0 inclusive" in str(exc_info.value)

    with pytest.raises(AppException) as exc_info:
        CitationAudit(integrity_score=-0.5)
    assert "integrity_score must be between 0.0 and 1.0 inclusive" in str(exc_info.value)


def test_integrity_global_inputs_extract_source_texts() -> None:
    """Test extraction of source texts securely."""
    dto = IntegrityGlobalInputsDTO(
        raw_inputs={"source_1": "Text 1", "source_2": "Text 2", "empty": None, "number": 123}
    )

    texts = dto.extract_source_texts()
    assert len(texts) == 3
    assert "Text 1" in texts
    assert "Text 2" in texts
    assert "123" in texts

    # Test empty raw_inputs
    empty_dto = IntegrityGlobalInputsDTO()
    assert empty_dto.extract_source_texts() == []
