"""Unit tests for VarianceEngineResultDTO."""

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.variance import VarianceEngineResultDTO
from backend_v2.models.enums import AlignmentVerdict


def test_variance_engine_result_dto_positive() -> None:
    """Verify positive instantiation and attribute typing of VarianceEngineResultDTO."""
    dto = VarianceEngineResultDTO(
        mechanical_metric_ref="performative_phrases_count",
        cognitive_metric_ref="llm_authenticity_score",
        variance_score=0.25,
        alignment_verdict=AlignmentVerdict.ALIGNED,
    )
    assert dto.mechanical_metric_ref == "performative_phrases_count"
    assert dto.cognitive_metric_ref == "llm_authenticity_score"
    assert dto.variance_score == 0.25
    assert dto.alignment_verdict == AlignmentVerdict.ALIGNED


def test_variance_engine_result_dto_strict_enum_enforcement() -> None:
    """Verify strict mode requires native AlignmentVerdict instance, while strict=False allows string coercion."""
    # Strict mode rejects raw string
    with pytest.raises(ValidationError):
        VarianceEngineResultDTO.model_validate(
            {
                "mechanical_metric_ref": "mech",
                "cognitive_metric_ref": "cog",
                "variance_score": 1.5,
                "alignment_verdict": "MISALIGNED_SYCOPHANCY",
            },
            strict=True,
        )

    # Ingress hydration with strict=False coerces raw string to AlignmentVerdict
    dto = VarianceEngineResultDTO.model_validate(
        {
            "mechanical_metric_ref": "mech",
            "cognitive_metric_ref": "cog",
            "variance_score": 1.5,
            "alignment_verdict": "MISALIGNED_SYCOPHANCY",
        },
        strict=False,
    )
    assert dto.alignment_verdict == AlignmentVerdict.MISALIGNED_SYCOPHANCY


def test_variance_engine_result_dto_negative_variance_score() -> None:
    """ISTQB negative test: variance_score < 0 raises ValidationError."""
    with pytest.raises(ValidationError):
        VarianceEngineResultDTO(
            mechanical_metric_ref="mech",
            cognitive_metric_ref="cog",
            variance_score=-0.1,
            alignment_verdict=AlignmentVerdict.ALIGNED,
        )


def test_variance_engine_result_dto_invalid_verdict() -> None:
    """ISTQB negative test: invalid alignment verdict string raises ValidationError even with strict=False."""
    with pytest.raises(ValidationError):
        VarianceEngineResultDTO.model_validate(
            {
                "mechanical_metric_ref": "mech",
                "cognitive_metric_ref": "cog",
                "variance_score": 0.5,
                "alignment_verdict": "INVALID_VERDICT",
            },
            strict=False,
        )


def test_variance_engine_result_dto_extra_forbidden() -> None:
    """Verify that extra fields are forbidden by model configuration."""
    with pytest.raises(ValidationError):
        VarianceEngineResultDTO.model_validate(
            {
                "mechanical_metric_ref": "mech",
                "cognitive_metric_ref": "cog",
                "variance_score": 0.5,
                "alignment_verdict": AlignmentVerdict.ALIGNED,
                "unauthorized_field": "forbidden",
            }
        )


def test_variance_engine_result_dto_frozen() -> None:
    """Verify that VarianceEngineResultDTO is frozen/immutable."""
    dto = VarianceEngineResultDTO(
        mechanical_metric_ref="mech",
        cognitive_metric_ref="cog",
        variance_score=0.0,
        alignment_verdict=AlignmentVerdict.ALIGNED,
    )
    with pytest.raises(ValidationError):
        dto.variance_score = 1.0  # type: ignore[misc]
