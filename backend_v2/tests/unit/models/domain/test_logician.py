import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.logician import (
    CognitiveLevel,
    LogicianData,
    LogicianInput,
    ToulminComponent,
    WaltonScheme,
)
from backend_v2.models.enums import BloomLevel, StrategicDepth


def test_logician_input_strict_validation() -> None:
    """Test that LogicianInput follows V2CoreBase strict constraints."""
    item = LogicianInput(chat_log="User said something")
    assert item.chat_log == "User said something"

    with pytest.raises(ValidationError):
        LogicianInput.model_validate({"chat_log": "", "extra_field": "not allowed"})


def test_toulmin_component_validation() -> None:
    """Test ToulminComponent constraints."""
    item = ToulminComponent(id="1", claim="A", data="B", warrant="C")
    assert item.claim == "A"

    with pytest.raises(ValidationError):
        ToulminComponent(id="1", claim="", data="B", warrant="C")  # min_length=1


def test_cognitive_level_validation() -> None:
    """Test CognitiveLevel bounds."""
    # Test dictionary hydration
    cl = CognitiveLevel(
        bloom_level=BloomLevel.ANALYZING, strategic_depth=StrategicDepth.HIGH, bloom_score=4.0, strategic_score=3.0
    )
    assert cl.bloom_score == 4.0

    # Test bounds
    with pytest.raises(AppException):
        CognitiveLevel(
            bloom_level=BloomLevel.ANALYZING,
            strategic_depth=StrategicDepth.HIGH,
            bloom_score=7.0,  # le=6.0
            strategic_score=3.0,
        )


def test_cognitive_level_validator_resolution() -> None:
    """Test the parsing of strings to enums and verify that scores are mandatory."""
    # Test successful parsing with mandatory scores
    cl = CognitiveLevel.model_validate(
        {"bloom_level": "BLOOM_ANALYZING", "strategic_depth": "STRAT_HIGH", "bloom_score": 4.0, "strategic_score": 3.0}
    )
    assert cl.bloom_level == BloomLevel.ANALYZING
    assert cl.strategic_depth == StrategicDepth.HIGH
    assert cl.bloom_score == 4.0
    assert cl.strategic_score == 3.0

    # Test failure fast when scores are missing
    with pytest.raises(ValidationError) as exc_info:
        CognitiveLevel.model_validate({"bloom_level": "BLOOM_ANALYZING", "strategic_depth": "STRAT_HIGH"})
    assert "bloom_score" in str(exc_info.value)
    assert "strategic_score" in str(exc_info.value)


def test_walton_scheme_validation() -> None:
    """Test WaltonScheme constraints."""
    scheme = WaltonScheme(identified_scheme="Scheme 1", critical_questions=["Q1"])
    assert scheme.identified_scheme == "Scheme 1"

    with pytest.raises(ValidationError):
        WaltonScheme(identified_scheme="Scheme 1", critical_questions=[])


def test_logician_data_validation() -> None:
    """Test LogicianData constraints."""
    toulmin = ToulminComponent(id="1", claim="A", data="B", warrant="C")
    cl = CognitiveLevel(
        bloom_level=BloomLevel.ANALYZING, strategic_depth=StrategicDepth.HIGH, bloom_score=4.0, strategic_score=3.0
    )
    walton = WaltonScheme(identified_scheme="Scheme 1", critical_questions=["Q1"])

    data = LogicianData(toulmin_analysis=[toulmin], cognitive_level=cl, walton_scheme=walton, toulmin_score=5.5)
    assert len(data.toulmin_analysis) == 1

    with pytest.raises(AppException):
        LogicianData(
            toulmin_analysis=[toulmin],
            cognitive_level=cl,
            walton_scheme=walton,
            toulmin_score=7.5,  # le=6.0
        )
