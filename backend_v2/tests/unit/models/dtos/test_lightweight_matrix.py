"""Unit tests for lightweight matrix DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.lightweight_matrix import (
    LevelStatsDTO,
    LightweightMatrixOutput,
    MatrixAggregationStateDTO,
    MergedFactsDTO,
    OutputProfileConfig,
    ScoringResultDTO,
    XAILogDto,
)
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.system import HealthCheckResponseDTO
from backend_v2.models.dtos.trace import TraceEventMetadataDTO
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

    dto_explicit = LevelStatsDTO(hits=2, total=10, dlqs=2, pos_hits=1, pos_total=5, inv_clean=1, inv_total=5)
    assert dto_explicit.hits == 2
    assert dto_explicit.total == 10
    assert dto_explicit.dlqs == 2
    assert dto_explicit.pos_hits == 1
    assert dto_explicit.pos_total == 5
    assert dto_explicit.inv_clean == 1
    assert dto_explicit.inv_total == 5

    # Rejection of float counts under strict integer typing
    with pytest.raises(ValidationError):
        LevelStatsDTO.model_validate({"hits": 2.5, "total": 10})

    # Boundary Value Analysis: minimum valid 0 and invalid -1 (min - 1)
    dto_zero = LevelStatsDTO(hits=0, total=0, dlqs=0, pos_hits=0, pos_total=0, inv_clean=0, inv_total=0)
    assert dto_zero.hits == 0
    assert dto_zero.total == 0

    with pytest.raises(ValidationError):
        LevelStatsDTO(hits=-1, total=5)

    with pytest.raises(ValidationError):
        LevelStatsDTO(hits=0, total=5, dlqs=-1)

    # Negative extra forbidden
    with pytest.raises(ValidationError):
        LevelStatsDTO.model_validate({"hits": 1, "total": 2, "extra": "forbidden"})

    # Immutability configuration
    assert LevelStatsDTO.model_config["frozen"] is True
    assert LevelStatsDTO.model_config["strict"] is True
    assert LevelStatsDTO.model_config["extra"] == "forbid"


def test_lightweight_matrix_output_normalized_score_validation() -> None:
    """Test LightweightMatrixOutput normalized_score bounds validation."""
    valid_dto = LightweightMatrixOutput(normalized_score=85.5, evaluated_atoms={}, extensions={})
    assert valid_dto.normalized_score == 85.5

    # Exact ISTQB boundaries (0.0 and 100.0)
    assert LightweightMatrixOutput(normalized_score=0.0, evaluated_atoms={}, extensions={}).normalized_score == 0.0
    assert LightweightMatrixOutput(normalized_score=100.0, evaluated_atoms={}, extensions={}).normalized_score == 100.0

    # Out-of-bounds partitions (min - 0.01 and max + 0.01)
    with pytest.raises(ValidationError):
        LightweightMatrixOutput(normalized_score=-0.01, evaluated_atoms={}, extensions={})

    with pytest.raises(ValidationError):
        LightweightMatrixOutput(normalized_score=100.01, evaluated_atoms={}, extensions={})

    with pytest.raises(ValidationError):
        LightweightMatrixOutput(normalized_score=150.0, evaluated_atoms={}, extensions={})

    with pytest.raises(ValidationError):
        LightweightMatrixOutput(normalized_score=-5.0, evaluated_atoms={}, extensions={})

    # Extra forbidden
    with pytest.raises(ValidationError):
        LightweightMatrixOutput.model_validate({"extra_field": 123})


def test_output_profile_config() -> None:
    """Test OutputProfileConfig validation and extra forbidden."""
    cfg = OutputProfileConfig(
        visible_block_extensions=[XaiExtensionType.CITATION],
        visible_workflow_extensions=[],
    )
    assert len(cfg.visible_block_extensions) == 1
    assert cfg.visible_workflow_extensions == []

    with pytest.raises(ValidationError):
        OutputProfileConfig.model_validate(
            {
                "visible_block_extensions": [],
                "visible_workflow_extensions": [],
                "unsupported": "extra",
            }
        )


def test_xai_log_dto() -> None:
    """Test XAILogDto defaults, trace assignment, and extra forbidden."""
    log = XAILogDto.model_validate({"pedagogical_key": "test_key"})
    assert log.pedagogical_key == "test_key"
    assert log.engine_debug_trace == {}

    custom_log = XAILogDto(pedagogical_key="key2", engine_debug_trace={"ratio": 1.25})
    assert custom_log.engine_debug_trace == {"ratio": 1.25}

    with pytest.raises(ValidationError):
        XAILogDto.model_validate({"pedagogical_key": "key", "unknown": "extra"})


def test_scoring_result_dto() -> None:
    """Test ScoringResultDTO fields, frozen immutability, and extra forbidden."""
    xai = XAILogDto(pedagogical_key="p_key", engine_debug_trace={})
    stats = LevelStatsDTO(hits=2, total=4)
    result = ScoringResultDTO(
        score=75.0,
        xai_log=xai,
        breakdown={"1": stats},
    )
    assert result.score == 75.0
    assert result.xai_log.pedagogical_key == "p_key"
    assert result.breakdown["1"].hits == 2

    # Immutability configuration
    assert ScoringResultDTO.model_config["frozen"] is True
    assert ScoringResultDTO.model_config["strict"] is True
    assert ScoringResultDTO.model_config["extra"] == "forbid"

    # Extra forbidden
    with pytest.raises(ValidationError):
        ScoringResultDTO.model_validate({"score": 75.0, "xai_log": xai, "breakdown": {}, "extra_field": 1})


def test_merged_facts_dto() -> None:
    """Test MergedFactsDTO extra forbidden."""
    facts = MergedFactsDTO()
    assert isinstance(facts, MergedFactsDTO)
    assert MergedFactsDTO.model_config["frozen"] is True

    with pytest.raises(ValidationError):
        MergedFactsDTO.model_validate({"extra": "bad"})


def test_matrix_aggregation_state_dto() -> None:
    """Test MatrixAggregationStateDTO defaults, explicit fields, immutability, and strict validation."""
    empty_state = MatrixAggregationStateDTO.model_validate({})
    assert empty_state.scale_stats == {}
    assert empty_state.evaluated_atoms == {}
    assert empty_state.extensions == {}
    assert empty_state.missing_atoms == []
    assert empty_state.atom_quotes == []
    assert empty_state.display_stats == {}

    stats = LevelStatsDTO(hits=1, total=2)
    quote = QuoteEvidenceDTO(
        source_quotes=("Evidence text",),
        verified_source_ids=["doc_0"],
        unverified_aliases=[],
        is_verified=True,
    )
    populated_state = MatrixAggregationStateDTO(
        scale_stats={1.0: stats},
        evaluated_atoms={"a0": ExecutionStatus.PASSED},
        extensions={"citations": ["cite_1"]},
        missing_atoms=["a1"],
        atom_quotes=[quote],
        display_stats={"1": stats},
    )
    assert populated_state.scale_stats[1.0].hits == 1
    assert populated_state.evaluated_atoms["a0"] == ExecutionStatus.PASSED
    assert populated_state.atom_quotes[0].get_quotes() == ("Evidence text",)
    assert populated_state.display_stats["1"].total == 2

    # Immutability (frozen=True)
    assert MatrixAggregationStateDTO.model_config["frozen"] is True
    assert MatrixAggregationStateDTO.model_config["strict"] is True
    assert MatrixAggregationStateDTO.model_config["extra"] == "forbid"

    # Extra forbidden
    with pytest.raises(ValidationError):
        MatrixAggregationStateDTO.model_validate({"unexpected_key": "value"})

    # Invalid type in evaluated_atoms
    with pytest.raises(ValidationError):
        MatrixAggregationStateDTO.model_validate({"evaluated_atoms": {"a0": 123}})


def test_lightweight_matrix_and_trace_dtos_enforce_extra_forbid() -> None:
    """Verify matrix, health, and trace DTOs validate cleanly and serialize with exclude_none=True."""
    level_stats = LevelStatsDTO(hits=3, total=5, dlqs=0, pos_hits=2, pos_total=3, inv_clean=1, inv_total=2)
    xai_log = XAILogDto(
        pedagogical_key="xai_unified_engine_breakdown",
        engine_debug_trace={
            "engine": "unified",
            "strictness_level": 50,
            "stats": {"1.0": level_stats.model_dump()},
            "log_trace": ["Level 1.0: 3/5"],
        },
    )
    matrix_out = LightweightMatrixOutput(
        raw_score=3.5,
        normalized_score=70.0,
        level_breakdown={"1.0": level_stats},
        justification="Grounded evidence",
        xai_log=xai_log,
        evaluated_atoms={"a0": ExecutionStatus.PASSED},
        extensions={XaiExtensionType.CITATION: "Quote 1"},
    )
    health_dto = HealthCheckResponseDTO(
        status="ok",
        version="2.9.0",
        environment="development",
        storage_backend="POSTGRES",
        gcp_region="europe-north1",
        primary_domain="qrum.ai",
    )
    trace_meta = TraceEventMetadataDTO(
        latency_ms=42.5,
        chunk_size=1,
        generated_schema={"type": "object", "properties": {"score": {"type": "number"}}},
        mcp_audit_traces=[],
    )

    matrix_dumped = matrix_out.model_dump(mode="json", exclude_none=True)
    trace_dumped = trace_meta.model_dump(mode="json", exclude_none=True)
    health_dumped = health_dto.model_dump(mode="json", exclude_none=True)

    assert "allowed_extensions" not in matrix_dumped
    assert "atom_quotes" not in matrix_dumped
    assert "context_char_length" not in trace_dumped
    assert trace_dumped["generated_schema"] == {"type": "object", "properties": {"score": {"type": "number"}}}
    assert health_dumped["status"] == "ok"

    # Negative: extra keys rejected across all closed DTOs
    with pytest.raises(ValidationError):
        LightweightMatrixOutput.model_validate({**matrix_dumped, "undeclared_key": 1})
    with pytest.raises(ValidationError):
        TraceEventMetadataDTO.model_validate({**trace_dumped, "undeclared_key": 1})
