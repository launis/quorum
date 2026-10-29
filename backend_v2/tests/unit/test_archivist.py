"""Unit tests for Archivist Domain Models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
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
    """Test that extra fields are forbidden on ArchivistInput."""
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
    """Test ArchiveCase fields min_length boundary."""
    data = {
        "case_id": "",
        "similarity_score": 0.95,
        "verdict": "Pass",
        "summary": "This is a summary.",
    }
    with pytest.raises(ValidationError):
        ArchiveCase.model_validate(data)


def test_archivist_output_dto_valid() -> None:
    """Test valid ArchivistOutputDTO and matching pre-populated compliance_score."""
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

    # Verify branch where compliance_score already matches expected_score
    model_matched = ArchivistOutputDTO.model_validate({**data, "compliance_score": 4.0})
    assert model_matched.compliance_score == 4.0


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
    """Test invalid compliance_analysis literal."""
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
    with pytest.raises(ValidationError):
        ArchivistOutputDTO.model_validate(data)


def test_archivist_output_dto_min_length() -> None:
    """Test ArchivistOutputDTO fields min_length boundary."""
    data = {
        "thought_process": "Thinking...",
        "conclusion": "Conclusion.",
        "confidence_score": 0.9,
        "relevant_cases": [{"case_id": "c1", "similarity_score": 1.0, "verdict": "V", "summary": "S"}],
        "consistency_analysis": "",
        "stare_decisis_adherence": True,
        "compliance_analysis": "Aligned",
        "description_key": "desc_1",
    }
    with pytest.raises(ValidationError):
        ArchivistOutputDTO.model_validate(data)


def test_archivist_output_dto_negative_app_exceptions() -> None:
    """Verify ArchivistOutputDTO raises AppException on ISTQB boundary and hallucination inputs."""
    base_data = {
        "thought_process": "Thinking...",
        "conclusion": "Conclusion.",
        "confidence_score": 0.9,
        "relevant_cases": [{"case_id": "c1", "similarity_score": 1.0, "verdict": "V", "summary": "S"}],
        "consistency_analysis": "Consistent.",
        "stare_decisis_adherence": True,
        "compliance_analysis": "Aligned",
    }

    # Negative 1: Boundary violation confidence_score < 0.0 (min - 0.01)
    with pytest.raises(AppException) as exc_low:
        ArchivistOutputDTO.model_validate({**base_data, "confidence_score": -0.01})
    assert exc_low.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

    # Negative 2: Boundary violation confidence_score > 1.0 (max + 0.01)
    with pytest.raises(AppException) as exc_high:
        ArchivistOutputDTO.model_validate({**base_data, "confidence_score": 1.01})
    assert exc_high.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

    # Negative 3: Hallucinated empty marker in thought_process
    with pytest.raises(AppException) as exc_hallucination:
        ArchivistOutputDTO.model_validate({**base_data, "thought_process": "null"})
    assert exc_hallucination.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED


def test_archivist_output_valid() -> None:
    """Test valid ArchivistOutput with metadata inheritance and negative AppException check."""
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

    # Negative: Empty conclusion raises AppException
    with pytest.raises(AppException) as exc_empty:
        ArchivistOutput.model_validate({**data, "conclusion": "   "})
    assert exc_empty.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED
