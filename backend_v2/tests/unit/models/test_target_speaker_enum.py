"""Unit tests for TargetSpeaker StrEnum."""

from typing import Annotated

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend_v2.models.enums import TargetSpeaker


class DummySpeakerModel(BaseModel):
    """Test model for verifying TargetSpeaker serialization."""

    model_config = ConfigDict(strict=True, extra="forbid")
    speaker: Annotated[TargetSpeaker, Field(default=TargetSpeaker.USER, strict=False)] = TargetSpeaker.USER


def test_target_speaker_enum_values() -> None:
    """Test TargetSpeaker values adhere to strict binary dichotomy."""
    assert TargetSpeaker.USER == "USER"
    assert TargetSpeaker.AI == "AI"
    assert TargetSpeaker.USER.value == "USER"
    assert TargetSpeaker.AI.value == "AI"
    assert len(TargetSpeaker) == 2


def test_target_speaker_banned_values() -> None:
    """Test that legacy or fuzzy values are strictly banned."""
    valid_values = {s.value for s in TargetSpeaker}
    assert "ALL" not in valid_values
    assert "ASSISTANT" not in valid_values
    assert "user" not in valid_values
    assert "ai" not in valid_values


def test_target_speaker_pydantic_serialization() -> None:
    """Test TargetSpeaker serialization and validation in Pydantic models."""
    # Default is USER
    m1 = DummySpeakerModel()
    assert m1.speaker == TargetSpeaker.USER
    assert m1.model_dump(mode="json") == {"speaker": "USER"}

    # Explicit AI
    m2 = DummySpeakerModel(speaker=TargetSpeaker.AI)
    assert m2.speaker == TargetSpeaker.AI
    assert m2.model_dump(mode="json") == {"speaker": "AI"}

    # Validation from valid strings
    m3 = DummySpeakerModel.model_validate({"speaker": "AI"})
    assert m3.speaker == TargetSpeaker.AI

    m4 = DummySpeakerModel.model_validate({"speaker": "USER"})
    assert m4.speaker == TargetSpeaker.USER

    # Rejection of invalid strings
    with pytest.raises(ValidationError):
        DummySpeakerModel.model_validate({"speaker": "ALL"})

    with pytest.raises(ValidationError):
        DummySpeakerModel.model_validate({"speaker": "ASSISTANT"})

    with pytest.raises(ValidationError):
        DummySpeakerModel.model_validate({"speaker": "user"})
