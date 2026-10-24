"""Unit tests for ingress DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.ingress import (
    ChatTurnAnchorDTO,
    ChatTurnAnchorsResponseDTO,
    PdfBlockSignatureDTO,
    PdfCellCoordinatesDTO,
    PdfTextBlockDTO,
    RawTurnDTO,
    ResolvedIngressDTO,
)


def test_chat_turn_anchor_dto_valid() -> None:
    """Test valid instantiation and frozen strictness of ChatTurnAnchorDTO."""
    dto = ChatTurnAnchorDTO(
        speaker="user",
        start_phrase="Tämä on esimerkkilause alussa",
        end_phrase="Tämä on esimerkkilause lopussa",
    )
    assert dto.speaker == "user"
    assert dto.start_phrase == "Tämä on esimerkkilause alussa"
    assert dto.end_phrase == "Tämä on esimerkkilause lopussa"
    assert ChatTurnAnchorDTO.model_config["frozen"] is True
    assert hash(dto) is not None


def test_chat_turn_anchor_dto_invalid_speaker() -> None:
    """Test validation failure on invalid speaker role."""
    with pytest.raises(ValidationError):
        ChatTurnAnchorDTO.model_validate(
            {
                "speaker": "system",
                "start_phrase": "Hello world test",
                "end_phrase": "Goodbye world test",
            }
        )


def test_chat_turn_anchor_dto_short_phrase_fails() -> None:
    """Test validation failure on too short phrases (< 3 chars)."""
    with pytest.raises(ValidationError):
        ChatTurnAnchorDTO(
            speaker="user",
            start_phrase="hi",
            end_phrase="bye",
        )


def test_chat_turn_anchor_dto_extra_fields_forbidden() -> None:
    """Test that extra fields trigger ValidationError under extra='forbid'."""
    with pytest.raises(ValidationError):
        ChatTurnAnchorDTO.model_validate(
            {
                "speaker": "ai",
                "start_phrase": "Valid start phrase",
                "end_phrase": "Valid end phrase",
                "extra_field": "disallowed",
            }
        )


def test_chat_turn_anchors_response_dto_valid() -> None:
    """Test valid ChatTurnAnchorsResponseDTO with turns array."""
    turn = ChatTurnAnchorDTO(
        speaker="ai",
        start_phrase="Vastaus alkaa tästä sanasta",
        end_phrase="Vastaus päättyy tähän lauseeseen",
    )
    resp = ChatTurnAnchorsResponseDTO(turns=[turn])
    assert len(resp.turns) == 1
    assert resp.turns[0].speaker == "ai"


def test_chat_turn_anchors_response_dto_empty_turns_allowed() -> None:
    """Test that empty turns array is valid schema for dialogue absence."""
    resp = ChatTurnAnchorsResponseDTO(turns=[])
    assert resp.turns == []


def test_chat_turn_anchors_response_dto_rejects_extra_and_invalid_turns() -> None:
    """Negative Test: Extra fields and invalid turn elements fail validation on ChatTurnAnchorsResponseDTO."""
    with pytest.raises(ValidationError):
        ChatTurnAnchorsResponseDTO.model_validate({"turns": [], "extra_field": "forbidden"})
    with pytest.raises(ValidationError):
        ChatTurnAnchorsResponseDTO.model_validate({"turns": ["invalid_turn_string"]})


def test_resolved_ingress_dto_valid() -> None:
    """Test valid ResolvedIngressDTO instantiation and frozen immutability."""
    dto = ResolvedIngressDTO(
        resolved_inputs={"doc_text": "Sample text", "turn_count": 5},
        source_identity_manifest={"doc_text": "sample.pdf", "turn_count": "metadata"},
    )
    assert dto.resolved_inputs["doc_text"] == "Sample text"
    assert dto.resolved_inputs["turn_count"] == 5
    assert dto.source_identity_manifest["doc_text"] == "sample.pdf"
    assert ResolvedIngressDTO.model_config["frozen"] is True


def test_resolved_ingress_dto_extra_fields_forbidden() -> None:
    """Negative Test: Extra fields trigger ValidationError under extra='forbid'."""
    with pytest.raises(ValidationError):
        ResolvedIngressDTO.model_validate(
            {
                "resolved_inputs": {"key": "val"},
                "source_identity_manifest": {"key": "source"},
                "extra_key": "forbidden",
            }
        )


def test_resolved_ingress_dto_missing_or_invalid_types_rejected() -> None:
    """Negative Test: Missing required fields or non-string manifest values fail validation."""
    with pytest.raises(ValidationError):
        ResolvedIngressDTO.model_validate({"resolved_inputs": {"key": "val"}})
    with pytest.raises(ValidationError):
        ResolvedIngressDTO.model_validate(
            {
                "resolved_inputs": {"key": "val"},
                "source_identity_manifest": {"key": 12345},
            }
        )


def test_pdf_cell_coordinates_dto_valid_and_frozen() -> None:
    """Test valid instantiation, hashability, and frozen immutability of PdfCellCoordinatesDTO."""
    dto = PdfCellCoordinatesDTO(x0=10.0, y0=20.0, x1=100.0, y1=50.0)
    assert dto.x0 == 10.0
    assert dto.y0 == 20.0
    assert dto.x1 == 100.0
    assert dto.y1 == 50.0
    assert PdfCellCoordinatesDTO.model_config["frozen"] is True
    assert hash(dto) is not None


def test_pdf_cell_coordinates_dto_rejects_extra_and_invalid_types() -> None:
    """Negative Test: Extra fields and non-float strict types fail validation on PdfCellCoordinatesDTO."""
    with pytest.raises(ValidationError):
        PdfCellCoordinatesDTO.model_validate({"x0": 10.0, "y0": 20.0, "x1": 100.0, "y1": 50.0, "extra": 1.0})
    with pytest.raises(ValidationError):
        PdfCellCoordinatesDTO.model_validate({"x0": "not_a_float", "y0": 20.0, "x1": 100.0, "y1": 50.0})


def test_pdf_text_block_dto_valid_and_frozen() -> None:
    """Test valid instantiation, hashability, and frozen immutability of PdfTextBlockDTO."""
    dto = PdfTextBlockDTO(
        x0=59.0,
        y0=120.0,
        x1=500.0,
        y1=160.0,
        text="Hello world",
        block_no=1,
        block_type=0,
    )
    assert dto.text == "Hello world"
    assert dto.block_no == 1
    assert dto.block_type == 0
    assert PdfTextBlockDTO.model_config["frozen"] is True
    assert hash(dto) is not None


def test_pdf_text_block_dto_rejects_extra_and_invalid_types() -> None:
    """Negative Test: Extra fields and type mismatches fail validation on PdfTextBlockDTO."""
    with pytest.raises(ValidationError):
        PdfTextBlockDTO.model_validate(
            {
                "x0": 59.0,
                "y0": 120.0,
                "x1": 500.0,
                "y1": 160.0,
                "text": "Hello",
                "block_no": 1,
                "block_type": 0,
                "unexpected": True,
            }
        )
    with pytest.raises(ValidationError):
        PdfTextBlockDTO.model_validate(
            {
                "x0": 59.0,
                "y0": 120.0,
                "x1": 500.0,
                "y1": 160.0,
                "text": "Hello",
                "block_no": "1",
                "block_type": 0,
            }
        )


def test_raw_turn_dto_valid_and_frozen() -> None:
    """Test valid instantiation, hashability, and frozen immutability of RawTurnDTO."""
    dto = RawTurnDTO(role="user", content="Sample user prompt")
    assert dto.role == "user"
    assert dto.content == "Sample user prompt"
    assert RawTurnDTO.model_config["frozen"] is True
    assert hash(dto) is not None


def test_raw_turn_dto_rejects_extra_and_invalid_types() -> None:
    """Negative Test: Extra fields and non-string content fail validation on RawTurnDTO."""
    with pytest.raises(ValidationError):
        RawTurnDTO.model_validate({"role": "user", "content": "Prompt", "extra": "bad"})
    with pytest.raises(ValidationError):
        RawTurnDTO.model_validate({"role": "user", "content": 12345})


def test_pdf_block_signature_dto_valid_and_hashable() -> None:
    """Test valid instantiation, set deduplication hashability, and frozen immutability of PdfBlockSignatureDTO."""
    sig1 = PdfBlockSignatureDTO(page_idx=0, x0=59.0, y0=120.0, x1=400.0, y1=140.0, text="Sample block")
    sig2 = PdfBlockSignatureDTO(page_idx=0, x0=59.0, y0=120.0, x1=400.0, y1=140.0, text="Sample block")
    seen = {sig1}
    assert sig2 in seen
    assert PdfBlockSignatureDTO.model_config["frozen"] is True


def test_pdf_block_signature_dto_rejects_extra_and_invalid_types() -> None:
    """Negative Test: Extra fields and invalid page_idx type fail validation on PdfBlockSignatureDTO."""
    with pytest.raises(ValidationError):
        PdfBlockSignatureDTO.model_validate(
            {"page_idx": 0, "x0": 1.0, "y0": 2.0, "x1": 3.0, "y1": 4.0, "text": "ok", "extra": 1}
        )
    with pytest.raises(ValidationError):
        PdfBlockSignatureDTO.model_validate({"page_idx": "0", "x0": 1.0, "y0": 2.0, "x1": 3.0, "y1": 4.0, "text": "ok"})
