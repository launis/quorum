"""Unit tests for typed ExecutionEngine registry and factory."""

from typing import cast
from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import EngineType
from backend_v2.services.orchestrator.engines.base import ExecutionEngine
from backend_v2.services.orchestrator.engines.prompt_engine import PromptEngine
from backend_v2.services.orchestrator.engines.registry import (
    ENGINE_REGISTRY,
    build_execution_engine,
)
from backend_v2.services.orchestrator.engines.synthesis_engine import SynthesisEngine
from backend_v2.services.orchestrator.engines.tda_engine import TDAEngine
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


@pytest.fixture
def mock_prompt_compiler() -> MagicMock:
    """Fixture providing a mocked PromptCompiler instance."""
    return MagicMock(spec=PromptCompiler)


def test_build_execution_engine_tda_returns_tda_engine(
    mock_prompt_compiler: MagicMock,
) -> None:
    """Verify EngineType.TDA resolves to TDAEngine with canonical telemetry label."""
    engine = build_execution_engine(EngineType.TDA, mock_prompt_compiler)
    assert isinstance(engine, TDAEngine)
    assert isinstance(engine, ExecutionEngine)
    assert engine.telemetry_strategy_label == "tda"


def test_build_execution_engine_synthesis_returns_synthesis_engine(
    mock_prompt_compiler: MagicMock,
) -> None:
    """Verify EngineType.SYNTHESIS resolves to SynthesisEngine with canonical telemetry label."""
    engine = build_execution_engine(EngineType.SYNTHESIS, mock_prompt_compiler)
    assert isinstance(engine, SynthesisEngine)
    assert isinstance(engine, ExecutionEngine)
    assert engine.telemetry_strategy_label == "synthesis"


def test_build_execution_engine_prompt_returns_prompt_engine(
    mock_prompt_compiler: MagicMock,
) -> None:
    """Verify EngineType.PROMPT resolves to PromptEngine with canonical telemetry label."""
    engine = build_execution_engine(EngineType.PROMPT, mock_prompt_compiler)
    assert isinstance(engine, PromptEngine)
    assert isinstance(engine, ExecutionEngine)
    assert engine.telemetry_strategy_label == "prompt"


def test_build_execution_engine_unsupported_raises_app_exception(
    mock_prompt_compiler: MagicMock,
) -> None:
    """Verify unmapped EngineType (e.g. CAUSAL_DISCOVERY before Phase 3) raises AppException."""
    # EngineType.CAUSAL_DISCOVERY is not yet in ENGINE_REGISTRY until Phase 3
    with pytest.raises(AppException) as exc_info:
        build_execution_engine(EngineType.CAUSAL_DISCOVERY, mock_prompt_compiler)

    assert exc_info.value.status_code == 422
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED


def test_build_execution_engine_invalid_value_raises_app_exception(
    mock_prompt_compiler: MagicMock,
) -> None:
    """Verify non-enum value raises AppException with VALIDATION_FAILED."""
    with pytest.raises(AppException) as exc_info:
        build_execution_engine(cast(EngineType, "unknown_engine"), mock_prompt_compiler)

    assert exc_info.value.status_code == 422
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED


def test_build_execution_engine_none_raises_app_exception(
    mock_prompt_compiler: MagicMock,
) -> None:
    """Verify None engine_type raises AppException with VALIDATION_FAILED."""
    with pytest.raises(AppException) as exc_info:
        build_execution_engine(cast(EngineType, None), mock_prompt_compiler)

    assert exc_info.value.status_code == 422
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED


def test_engine_registry_contains_expected_keys() -> None:
    """Verify ENGINE_REGISTRY contains the expected core EngineType members."""
    assert EngineType.TDA in ENGINE_REGISTRY
    assert EngineType.SYNTHESIS in ENGINE_REGISTRY
    assert EngineType.PROMPT in ENGINE_REGISTRY
