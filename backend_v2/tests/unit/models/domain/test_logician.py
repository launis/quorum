import pytest
from pydantic import ValidationError

from backend_v2.models.domain.logician import (
    CognitiveLevel,
    LogicianData,
    LogicianInput,
    ToulminComponent,
    WaltonScheme,
)
from backend_v2.models.enums import BloomLevel, StrategicDepth
from unittest.mock import patch


def test_logician_input_strict_validation() -> None:
    """Test that LogicianInput follows V2CoreBase strict constraints."""
    item = LogicianInput(chat_log="User said something")
    assert item.chat_log == "User said something"
    
    with pytest.raises(ValidationError):
        LogicianInput(chat_log="", extra_field="not allowed")


def test_toulmin_component_validation() -> None:
    """Test ToulminComponent constraints."""
    item = ToulminComponent(id="1", claim="A", data="B", warrant="C")
    assert item.claim == "A"
    
    with pytest.raises(ValidationError):
        ToulminComponent(id="1", claim="", data="B", warrant="C") # min_length=1


@patch("backend_v2.services.localization.LocalizationService.translate", return_value="Mocked Translation")
def test_cognitive_level_validation(mock_translate) -> None:
    """Test CognitiveLevel bounds and enum calculation."""
    # Test dictionary hydration
    cl = CognitiveLevel(
        bloom_level=BloomLevel.ANALYZING,
        strategic_depth=StrategicDepth.HIGH,
        bloom_score=4.0,
        strategic_score=3.0
    )
    assert cl.bloom_score == 4.0
    
    # Test bounds
    with pytest.raises(ValidationError):
        CognitiveLevel(
            bloom_level=BloomLevel.ANALYZING,
            strategic_depth=StrategicDepth.HIGH,
            bloom_score=7.0, # le=6.0
            strategic_score=3.0
        )


@patch("backend_v2.services.localization.LocalizationService.translate", return_value="Mocked Translation")
def test_cognitive_level_validator_resolution(mock_translate) -> None:
    """Test the pre-validator parsing strings to enums."""
    cl = CognitiveLevel.model_validate(
        {"bloom_level": "analyzing", "strategic_depth": "high"}
    )
    assert cl.bloom_level == BloomLevel.ANALYZING
    assert cl.strategic_depth == StrategicDepth.HIGH
    assert cl.bloom_score == 4.0
    assert cl.strategic_score == 3.0


def test_walton_scheme_validation() -> None:
    """Test WaltonScheme constraints."""
    scheme = WaltonScheme(identified_scheme="Scheme 1", critical_questions=["Q1"])
    assert scheme.identified_scheme == "Scheme 1"
    
    with pytest.raises(ValidationError):
        WaltonScheme(identified_scheme="Scheme 1", critical_questions=[])


@patch("backend_v2.services.localization.LocalizationService.translate", return_value="Mocked Translation")
def test_logician_data_validation(mock_translate) -> None:
    """Test LogicianData constraints."""
    toulmin = ToulminComponent(id="1", claim="A", data="B", warrant="C")
    cl = CognitiveLevel(
        bloom_level=BloomLevel.ANALYZING,
        strategic_depth=StrategicDepth.HIGH,
        bloom_score=4.0,
        strategic_score=3.0
    )
    walton = WaltonScheme(identified_scheme="Scheme 1", critical_questions=["Q1"])
    
    data = LogicianData(
        toulmin_analysis=[toulmin],
        cognitive_level=cl,
        walton_scheme=walton,
        toulmin_score=5.5
    )
    assert len(data.toulmin_analysis) == 1
    
    with pytest.raises(ValidationError):
        LogicianData(
            toulmin_analysis=[toulmin],
            cognitive_level=cl,
            walton_scheme=walton,
            toulmin_score=7.5 # le=6.0
        )
