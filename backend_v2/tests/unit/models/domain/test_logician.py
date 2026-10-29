"""Unit tests for Logician Agent domain models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.logician import (
    CognitiveLevel,
    LogicianData,
    LogicianInput,
    LogicianOutput,
    LogicianOutputDTO,
    ToulminComponent,
    WaltonScheme,
)
from backend_v2.models.enums import BloomLevel, StrategicDepth


def test_logician_input_strict_validation() -> None:
    """Test that LogicianInput follows V2CoreBase strict and frozen constraints."""
    item = LogicianInput(chat_log="User said something")
    assert item.chat_log == "User said something"

    with pytest.raises(ValidationError):
        LogicianInput.model_validate({"chat_log": "", "extra_field": "not allowed"})

    with pytest.raises(ValidationError):
        LogicianInput(chat_log="")


def test_toulmin_component_validation() -> None:
    """Test ToulminComponent constraints and negative boundary cases."""
    item = ToulminComponent(id="1", claim="A", data="B", warrant="C")
    assert item.claim == "A"

    with pytest.raises(ValidationError):
        ToulminComponent(id="1", claim="", data="B", warrant="C")

    with pytest.raises(ValidationError):
        ToulminComponent.model_validate({"id": "1", "claim": "A", "data": "B", "warrant": "C", "extra": "x"})


def test_cognitive_level_validation() -> None:
    """Test CognitiveLevel ISTQB boundary values and negative cases for bloom_score and strategic_score."""
    cl_min = CognitiveLevel(
        bloom_level=BloomLevel.ANALYZING,
        strategic_depth=StrategicDepth.HIGH,
        bloom_score=0.0,
        strategic_score=1.0,
    )
    assert cl_min.bloom_score == 0.0
    assert cl_min.strategic_score == 1.0

    cl_max = CognitiveLevel(
        bloom_level=BloomLevel.ANALYZING,
        strategic_depth=StrategicDepth.HIGH,
        bloom_score=6.0,
        strategic_score=4.0,
    )
    assert cl_max.bloom_score == 6.0
    assert cl_max.strategic_score == 4.0

    for invalid_bloom in (-0.1, 6.1):
        with pytest.raises(AppException) as exc_info:
            CognitiveLevel(
                bloom_level=BloomLevel.ANALYZING,
                strategic_depth=StrategicDepth.HIGH,
                bloom_score=invalid_bloom,
                strategic_score=3.0,
            )
        assert exc_info.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED}

    for invalid_strategic in (0.9, 4.1):
        with pytest.raises(AppException) as exc_info:
            CognitiveLevel(
                bloom_level=BloomLevel.ANALYZING,
                strategic_depth=StrategicDepth.HIGH,
                bloom_score=4.0,
                strategic_score=invalid_strategic,
            )
        assert exc_info.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED}


def test_cognitive_level_validator_resolution() -> None:
    """Test the parsing of strings to enums and verify that scores are mandatory."""
    cl = CognitiveLevel.model_validate(
        {"bloom_level": "BLOOM_ANALYZING", "strategic_depth": "STRAT_HIGH", "bloom_score": 4.0, "strategic_score": 3.0}
    )
    assert cl.bloom_level == BloomLevel.ANALYZING
    assert cl.strategic_depth == StrategicDepth.HIGH
    assert cl.bloom_score == 4.0
    assert cl.strategic_score == 3.0

    with pytest.raises(ValidationError) as exc_info:
        CognitiveLevel.model_validate({"bloom_level": "BLOOM_ANALYZING", "strategic_depth": "STRAT_HIGH"})
    assert "bloom_score" in str(exc_info.value)
    assert "strategic_score" in str(exc_info.value)


def test_walton_scheme_validation() -> None:
    """Test WaltonScheme constraints and negative boundary cases."""
    scheme = WaltonScheme(identified_scheme="Scheme 1", critical_questions=["Q1"])
    assert scheme.identified_scheme == "Scheme 1"

    with pytest.raises(ValidationError):
        WaltonScheme(identified_scheme="Scheme 1", critical_questions=[])

    with pytest.raises(ValidationError):
        WaltonScheme(identified_scheme="", critical_questions=["Q1"])


def test_logician_data_and_output_validation() -> None:
    """Test LogicianData, LogicianOutputDTO, and LogicianOutput constraints and ISTQB boundaries."""
    toulmin = ToulminComponent(id="1", claim="A", data="B", warrant="C")
    cl = CognitiveLevel(
        bloom_level=BloomLevel.ANALYZING, strategic_depth=StrategicDepth.HIGH, bloom_score=4.0, strategic_score=3.0
    )
    walton = WaltonScheme(identified_scheme="Scheme 1", critical_questions=["Q1"])

    data_min = LogicianData(toulmin_analysis=[toulmin], cognitive_level=cl, walton_scheme=walton, toulmin_score=0.0)
    assert data_min.toulmin_score == 0.0

    data_max = LogicianData(toulmin_analysis=[toulmin], cognitive_level=cl, walton_scheme=walton, toulmin_score=6.0)
    assert data_max.toulmin_score == 6.0

    dto = LogicianOutputDTO(
        thought_process="Step-by-step Toulmin argumentation analysis.",
        conclusion="Valid deductive chain.",
        confidence_score=0.9,
        logician_data=data_max,
    )
    assert dto.logician_data.toulmin_score == 6.0

    output = LogicianOutput(
        thought_process="Step-by-step Toulmin argumentation analysis.",
        conclusion="Valid deductive chain.",
        confidence_score=0.9,
        logician_data=data_max,
    )
    assert output.logician_data.toulmin_score == 6.0

    for invalid_toulmin in (-0.1, 6.1):
        with pytest.raises(AppException) as exc_info:
            LogicianData(
                toulmin_analysis=[toulmin],
                cognitive_level=cl,
                walton_scheme=walton,
                toulmin_score=invalid_toulmin,
            )
        assert exc_info.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED}

    with pytest.raises(ValidationError):
        LogicianData(
            toulmin_analysis=[],
            cognitive_level=cl,
            walton_scheme=walton,
            toulmin_score=3.0,
        )

    with pytest.raises(AppException):
        LogicianOutput(
            thought_process="Step-by-step Toulmin argumentation analysis.",
            conclusion="Valid deductive chain.",
            confidence_score=1.5,
            logician_data=data_max,
        )
