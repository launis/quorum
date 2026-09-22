"""Unit tests for lightweight matrix DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.lightweight_matrix import (
    LevelStatsDTO,
    LightweightMatrixOutput,
    MergedFactsDTO,
    OutputProfileConfig,
    ScoringResultDTO,
    XAILogDto,
)
from backend_v2.models.enums import ExecutionStatus, XaiExtensionType


def test_lightweight_matrix_output_coerces_failed_string() -> None:
    """Test that LightweightMatrixOutput correctly coerces 'FAILED' string to ExecutionStatus.FAILED."""
    payload = {"evaluated_atoms": {"a0": "FAILED", "a1": "PASSED"}}
    dto = LightweightMatrixOutput.model_validate(payload)
    assert dto.evaluated_atoms["a0"] == ExecutionStatus.FAILED
    assert dto.evaluated_atoms["a1"] == ExecutionStatus.PASSED


def test_lightweight_matrix_output_rejects_raw_bool() -> None:
    """Test that LightweightMatrixOutput explicitly rejects raw bool values (True/False)."""
    payload = {"evaluated_atoms": {"a0": False}}
    with pytest.raises(ValidationError) as exc:
        LightweightMatrixOutput.model_validate(payload)
    assert "Input should be" in str(exc.value)

    payload_true = {"evaluated_atoms": {"a0": True}}
    with pytest.raises(ValidationError) as exc_true:
        LightweightMatrixOutput.model_validate(payload_true)
    assert "Input should be" in str(exc_true.value)


def test_level_stats_dto_defaults_and_fields() -> None:
    """Test LevelStatsDTO defaults dlqs to 0 and accepts explicit values."""
    dto_default = LevelStatsDTO(hits=3, total=5)
    assert dto_default.hits == 3
    assert dto_default.total == 5
    assert dto_default.dlqs == 0

    dto_explicit = LevelStatsDTO(hits=2.5, total=10.0, dlqs=2)
    assert dto_explicit.hits == 2.5
    assert dto_explicit.total == 10.0
    assert dto_explicit.dlqs == 2

    # Negative extra forbidden
    with pytest.raises(ValidationError):
        LevelStatsDTO(hits=1, total=2, extra="forbidden")  # type: ignore[call-arg]

    # Immutability
    with pytest.raises(ValidationError):
        dto_default.hits = 4  # type: ignore[misc]


def test_lightweight_matrix_output_normalized_score_validation() -> None:
    """Test LightweightMatrixOutput normalized_score bounds validation."""
    valid_dto = LightweightMatrixOutput(normalized_score=85.5)
    assert valid_dto.normalized_score == 85.5

    with pytest.raises(ValidationError):
        LightweightMatrixOutput(normalized_score=150.0)

    with pytest.raises(ValidationError):
        LightweightMatrixOutput(normalized_score=-5.0)

    # Extra forbidden
    with pytest.raises(ValidationError):
        LightweightMatrixOutput(extra_field=123)  # type: ignore[call-arg]


def test_output_profile_config() -> None:
    """Test OutputProfileConfig validation and extra forbidden."""
    cfg = OutputProfileConfig(
        visible_block_extensions=[XaiExtensionType.CITATION],
        visible_workflow_extensions=[],
    )
    assert len(cfg.visible_block_extensions) == 1
    assert cfg.visible_workflow_extensions == []

    with pytest.raises(ValidationError):
        OutputProfileConfig(
            visible_block_extensions=[],
            visible_workflow_extensions=[],
            unsupported="extra",  # type: ignore[call-arg]
        )


def test_xai_log_dto() -> None:
    """Test XAILogDto defaults, trace assignment, and extra forbidden."""
    log = XAILogDto(pedagogical_key="test_key")
    assert log.pedagogical_key == "test_key"
    assert log.engine_debug_trace == {}

    custom_log = XAILogDto(pedagogical_key="key2", engine_debug_trace={"ratio": 1.25})
    assert custom_log.engine_debug_trace == {"ratio": 1.25}

    with pytest.raises(ValidationError):
        XAILogDto(pedagogical_key="key", unknown="extra")  # type: ignore[call-arg]


def test_scoring_result_dto() -> None:
    """Test ScoringResultDTO fields, frozen immutability, and extra forbidden."""
    xai = XAILogDto(pedagogical_key="p_key")
    stats = LevelStatsDTO(hits=2, total=4)
    result = ScoringResultDTO(
        score=75.0,
        xai_log=xai,
        breakdown={"1": stats},
    )
    assert result.score == 75.0
    assert result.xai_log.pedagogical_key == "p_key"
    assert result.breakdown["1"].hits == 2

    # Immutability
    with pytest.raises(ValidationError):
        result.score = 80.0  # type: ignore[misc]

    # Extra forbidden
    with pytest.raises(ValidationError):
        ScoringResultDTO(score=75.0, xai_log=xai, breakdown={}, extra_field=1)  # type: ignore[call-arg]


def test_merged_facts_dto() -> None:
    """Test MergedFactsDTO extra forbidden."""
    facts = MergedFactsDTO()
    assert isinstance(facts, MergedFactsDTO)

    with pytest.raises(ValidationError):
        MergedFactsDTO(extra="bad")  # type: ignore[call-arg]
