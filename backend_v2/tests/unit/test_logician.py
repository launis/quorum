from typing import Any
from unittest.mock import patch

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


@pytest.fixture(autouse=True)
def mock_localization() -> Any:
    """Mock LocalizationService to prevent missing directory errors during tests."""
    with patch("backend_v2.models.domain.logician.LocalizationService.translate") as mock:
        mock.return_value = "Mocked description"
        yield mock


def test_logician_input_strictness() -> None:
    """Test that LogicianInput enforces dynamic inputs and forbids extras."""
    # Valid
    inputs = LogicianInput(chat_log="User: Why?", dynamic_inputs={"extra": "allowed_here"})
    assert inputs.chat_log == "User: Why?"

    # Fails min_length
    with pytest.raises(ValidationError):
        LogicianInput(chat_log="")

    # Fails extra
    with pytest.raises(ValidationError):
        LogicianInput(chat_log="Hi", extra_field="fail")  # type: ignore


def test_toulmin_component_strictness() -> None:
    """Test ToulminComponent constraints."""
    # Valid
    comp = ToulminComponent(id="t1", claim="C", data="D", warrant="W")
    assert comp.id == "t1"

    # Fails empty
    with pytest.raises(ValidationError):
        ToulminComponent(id="", claim="C", data="D", warrant="W")

    with pytest.raises(ValidationError):
        ToulminComponent(id="t1", claim="", data="D", warrant="W")

    # Fails extra
    with pytest.raises(ValidationError):
        ToulminComponent(id="t1", claim="C", data="D", warrant="W", extra="X")  # type: ignore


def test_cognitive_level_strictness() -> None:
    """Test CognitiveLevel constraints."""
    # Valid (model validator auto-resolves enum and score if not provided)
    cog = CognitiveLevel(
        bloom_level=BloomLevel.CREATING,
        strategic_depth=StrategicDepth.HIGH,
        bloom_score=6.0,
        strategic_score=3.0,
    )
    assert cog.bloom_score == 6.0

    # Fails bloom_score bounds
    with pytest.raises(ValidationError):
        CognitiveLevel(
            bloom_level=BloomLevel.CREATING,
            strategic_depth=StrategicDepth.HIGH,
            bloom_score=7.0,
            strategic_score=3.0,
        )

    # Fails strategic_score bounds
    with pytest.raises(ValidationError):
        CognitiveLevel(
            bloom_level=BloomLevel.CREATING,
            strategic_depth=StrategicDepth.HIGH,
            bloom_score=5.0,
            strategic_score=0.5,
        )


def test_walton_scheme_strictness() -> None:
    """Test WaltonScheme constraints."""
    # Valid
    scheme = WaltonScheme(identified_scheme="Argument from Expert", critical_questions=["Is the expert credible?"])
    assert scheme.identified_scheme == "Argument from Expert"

    # Fails empty scheme
    with pytest.raises(ValidationError):
        WaltonScheme(identified_scheme="", critical_questions=["Q1"])

    # Fails empty questions list
    with pytest.raises(ValidationError):
        WaltonScheme(identified_scheme="Scheme", critical_questions=[])


def test_logician_data_strictness() -> None:
    """Test LogicianData constraints."""
    comp = ToulminComponent(id="t1", claim="C", data="D", warrant="W")
    cog = CognitiveLevel(
        bloom_level=BloomLevel.CREATING,
        strategic_depth=StrategicDepth.HIGH,
        bloom_score=6.0,
        strategic_score=3.0,
    )
    scheme = WaltonScheme(identified_scheme="Scheme", critical_questions=["Q1"])

    # Valid
    data = LogicianData(toulmin_analysis=[comp], cognitive_level=cog, walton_scheme=scheme, toulmin_score=5.5)
    assert data.toulmin_score == 5.5

    # Fails empty toulmin list
    with pytest.raises(ValidationError):
        LogicianData(toulmin_analysis=[], cognitive_level=cog, walton_scheme=scheme, toulmin_score=5.5)

    # Fails toulmin_score bounds
    with pytest.raises(ValidationError):
        LogicianData(toulmin_analysis=[comp], cognitive_level=cog, walton_scheme=scheme, toulmin_score=6.5)
