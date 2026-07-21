from unittest.mock import AsyncMock
"""Unit tests for Archivist Domain Models."""

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.archivist import (
    ArchiveCase,
    ArchivistInput,
    ArchivistOutput,
    ArchivistOutputDTO,
)


def test_archivist_input_valid() -> None:
    """Test valid ArchivistInput."""
    data = {
        "chat_log": "hello world",
        "archivist_precedents": [{"case_id": "1", "similarity_score": 90.0, "verdict": "V", "summary": "S"}],
        "last_reasoning_trace": "some trace",
    }
    model = ArchivistInput.model_validate(data)
    assert model.chat_log == "hello world"
    assert model.archivist_precedents is not None
    assert len(model.archivist_precedents) == 1


def test_archivist_input_extra_forbid() -> None:
    """Test that extra fields are forbidden."""
    data = {
        "chat_log": "hello world",
        "archivist_precedents": [{"case_id": "1", "similarity_score": 90.0, "verdict": "V", "summary": "S"}],
        "extra_field": "forbidden",
    }
    with pytest.raises(ValidationError):
        ArchivistInput.model_validate(data)


def test_archive_case_valid() -> None:
    """Test valid ArchiveCase."""
    data = {
        "case_id": "case_1",
        "similarity_score": 0.95,
        "verdict": "Pass",
        "summary": "This is a summary.",
    }
    model = ArchiveCase.model_validate(data)
    assert model.case_id == "case_1"
    assert model.similarity_score == 0.95


def test_archive_case_min_length() -> None:
    """Test ArchiveCase fields min_length."""
    data = {
        "case_id": "",
        "similarity_score": 0.95,
        "verdict": "Pass",
        "summary": "This is a summary.",
    }
    with pytest.raises(ValidationError):
        ArchiveCase.model_validate(data)


def test_archivist_output_dto_valid() -> None:
    """Test valid ArchivistOutputDTO."""
    case_data = {
        "case_id": "case_1",
        "similarity_score": 0.95,
        "verdict": "Pass",
        "summary": "This is a summary.",
    }
    data = {
        "thought_process": "Thinking...",
        "conclusion": "Conclusion.",
        "confidence_score": 0.9,
        "relevant_cases": [case_data],
        "consistency_analysis": "Consistent.",
        "stare_decisis_adherence": True,
        "compliance_analysis": "Aligned",
        "description_key": "desc_1",
        "description": "Optional desc",
    }
    model = ArchivistOutputDTO.model_validate(data)
    assert len(model.relevant_cases) == 1
    assert model.stare_decisis_adherence is True
    assert model.compliance_score == 4.0


def test_archivist_output_dto_compliance_calc() -> None:
    """Test compliance_score calculation from compliance_analysis."""
    data = {
        "thought_process": "Thinking...",
        "conclusion": "Conclusion.",
        "confidence_score": 0.9,
        "relevant_cases": [{"case_id": "c1", "similarity_score": 1.0, "verdict": "V", "summary": "S"}],
        "consistency_analysis": "Consistent.",
        "stare_decisis_adherence": True,
        "compliance_analysis": "Critically Misaligned",
        "description_key": "desc_1",
    }
    model = ArchivistOutputDTO.model_validate(data)
    assert model.compliance_score == 1.0


def test_archivist_output_dto_invalid_compliance() -> None:
    """Test invalid compliance_analysis string."""
    data = {
        "thought_process": "Thinking...",
        "conclusion": "Conclusion.",
        "confidence_score": 0.9,
        "relevant_cases": [{"case_id": "c1", "similarity_score": 1.0, "verdict": "V", "summary": "S"}],
        "consistency_analysis": "Consistent.",
        "stare_decisis_adherence": True,
        "compliance_analysis": "Invalid Value",
        "description_key": "desc_1",
    }
    with pytest.raises(AppException) as exc_info:
        ArchivistOutputDTO.model_validate(data)
    assert "Invalid compliance_analysis" in str(exc_info.value.message)


def test_archivist_output_dto_min_length() -> None:
    """Test ArchivistOutputDTO fields min_length."""
    data = {
        "thought_process": "Thinking...",
        "conclusion": "Conclusion.",
        "confidence_score": 0.9,
        "relevant_cases": [{"case_id": "c1", "similarity_score": 1.0, "verdict": "V", "summary": "S"}],
        "consistency_analysis": "",  # Empty
        "stare_decisis_adherence": True,
        "compliance_analysis": "Aligned",
        "description_key": "desc_1",
    }
    with pytest.raises(ValidationError):
        ArchivistOutputDTO.model_validate(data)


def test_archivist_output_valid() -> None:
    """Test valid ArchivistOutput with metadata inheritance."""
    data = {
        "thought_process": "Thinking...",
        "conclusion": "Conclusion.",
        "confidence_score": 0.9,
        "relevant_cases": [{"case_id": "c1", "similarity_score": 1.0, "verdict": "V", "summary": "S"}],
        "consistency_analysis": "Consistent.",
        "stare_decisis_adherence": True,
        "compliance_analysis": "Aligned",
        "description_key": "desc_1",
    }
    model = ArchivistOutput.model_validate(data)
    assert model.compliance_score == 4.0
