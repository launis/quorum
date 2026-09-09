from __future__ import annotations

"""Unit tests for ingress DTOs (ChatTurnAnchorDTO, ChatTurnAnchorsResponseDTO)."""

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.ingress import ChatTurnAnchorDTO, ChatTurnAnchorsResponseDTO


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

    # Frozen check
    with pytest.raises(ValidationError):
        dto.speaker = "ai"  # type: ignore[misc]


def test_chat_turn_anchor_dto_invalid_speaker() -> None:
    """Test validation failure on invalid speaker role."""
    with pytest.raises(ValidationError):
        ChatTurnAnchorDTO(
            speaker="system",  # type: ignore[arg-type]
            start_phrase="Hello world test",
            end_phrase="Goodbye world test",
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
