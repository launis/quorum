import pytest
from pydantic import ValidationError

from backend.models.dtos.reflection import GuidedReflectionDTO
from backend.services.reflection_service import ReflectionService


def test_reflection_document_generation_complete_data() -> None:
    """Test generating a document with all fields provided."""
    dto = GuidedReflectionDTO(
        q1_goal="My goal was X",
        q2_falsification="I noticed Y",
        q3_synthesis="My unique input Z",
        q4_argumentation="I am confident because W",
    )

    doc = ReflectionService.generate_markdown_document(dto)

    assert "# Reflektiodokumentti" in doc
    assert "**Syötetapa:** Ohjattu käyttöliittymälomake" in doc
    assert "<agency>\nMy goal was X\n</agency>" in doc
    assert "<falsification>\nI noticed Y\n</falsification>" in doc
    assert "<synthesis>\nMy unique input Z\n</synthesis>" in doc
    assert "<argumentation>\nI am confident because W\n</argumentation>" in doc


def test_reflection_document_generation_empty_data() -> None:
    """Test generating a document with no fields provided."""
    dto = GuidedReflectionDTO()

    doc = ReflectionService.generate_markdown_document(dto)

    assert "<agency>\n*Ei vastausta*\n</agency>" in doc
    assert "<falsification>\n*Ei vastausta*\n</falsification>" in doc
    assert "<synthesis>\n*Ei vastausta*\n</synthesis>" in doc
    assert "<argumentation>\n*Ei vastausta*\n</argumentation>" in doc


def test_reflection_document_generation_whitespace_data() -> None:
    """Test generating a document with only whitespace falls back to missing."""
    dto = GuidedReflectionDTO(q1_goal="   ")

    doc = ReflectionService.generate_markdown_document(dto)

    assert "<agency>\n*Ei vastausta*\n</agency>" in doc


def test_guided_reflection_dto_strict_validation() -> None:
    """Test strict Pydantic V2 validation rule on DTO."""
    with pytest.raises(ValidationError):
        # Strict validation should fail if an integer is passed instead of string.
        GuidedReflectionDTO(q1_goal=123)  # type: ignore
