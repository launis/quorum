from collections.abc import Awaitable
from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookResult,
    HookState,
)
from backend_v2.hooks.linguistics import detect_performative_patterns
from backend_v2.models.domain.linguistics import LinguisticsPayloadDTO
from backend_v2.models.execution_core import ExecutionMetadata


@pytest.fixture
def mock_deps() -> HookDependencies:
    system_repo = MagicMock()
    system_repo.get_system_config = AsyncMock()
    return HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=system_repo,
        search_client=AsyncMock(),
    )


def test_linguistics_payload_dto() -> None:
    """Test safe extraction logic inside LinguisticsPayloadDTO."""
    # Language in global vars
    dto1 = LinguisticsPayloadDTO(dynamic_inputs={})
    assert dto1.extract_language({"language": "fi"}) == "fi"

    # Default fallback to en
    dto2 = LinguisticsPayloadDTO(dynamic_inputs={})
    assert dto2.extract_language({}) == "en"

    # Input aggregation
    dto3 = LinguisticsPayloadDTO(dynamic_inputs={"foo": "bar", "num": 123, "empty": ""})
    # Text concatenates properly
    assert "bar" in dto3.get_text_to_scan()
    assert "foo" not in dto3.get_text_to_scan()  # only values are scanned


@pytest.mark.asyncio
async def test_detect_performative_patterns_success_en(mock_deps: HookDependencies) -> None:
    """Test successful detection of English performative patterns."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "q1": "It is important to note that this is a game changer.",
                "q2": "Regular text with no fillers.",
            }
        ),
    )

    cast(AsyncMock, mock_deps.system_repo.get_system_config).return_value = {
        "id": "sys_e0b2a3c4d5e6f7a8",
        "slug": "lexicon",
        "type": "performative_lexicons",
        "lexicon_configs": {
            "en": {
                "language_code": "en",
                "language_name": "English",
                "fuzz_threshold": 90.0,
                "words": ["game changer", "it is important to note"],
            }
        },
    }
    result = await cast(Awaitable[HookResult], detect_performative_patterns(state, mock_deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "global_context_vars" in result.state_delta.delta
    assert "step_linguistics" in result.state_delta.delta["global_context_vars"]

    patterns = result.state_delta.delta["global_context_vars"]["step_linguistics"]["performative_patterns"]
    assert len(patterns) == 2
    phrases = [p["detected_phrase"] for p in patterns]
    assert "game changer" in phrases
    assert "it is important to note" in phrases
    assert patterns[0]["pattern_id"].startswith("ptrn_")


@pytest.mark.asyncio
async def test_detect_performative_patterns_success_fi(mock_deps: HookDependencies) -> None:
    """Test successful detection of Finnish performative patterns when lang is set."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "fi-FI"}),
        inputs=ExecutionInputsDTO(
            raw_inputs={"q1": "Tämä on täysin mullistava innovaatio.", "q2": "Syventyä asiaan tarkemmin."}
        ),
    )

    cast(AsyncMock, mock_deps.system_repo.get_system_config).return_value = {
        "id": "sys_e0b2a3c4d5e6f7a8",
        "slug": "lexicon",
        "type": "performative_lexicons",
        "lexicon_configs": {
            "fi": {
                "language_code": "fi",
                "language_name": "Finnish",
                "fuzz_threshold": 90.0,
                "words": ["mullistava", "syventyä"],
            }
        },
    }
    result = await cast(Awaitable[HookResult], detect_performative_patterns(state, mock_deps))

    assert result.success is True
    assert result.state_delta is not None
    patterns = result.state_delta.delta["global_context_vars"]["step_linguistics"]["performative_patterns"]
    assert len(patterns) == 2
    phrases = [p["detected_phrase"] for p in patterns]
    assert "mullistava" in phrases
    assert "syventyä" in phrases
    assert patterns[0]["pattern_id"].startswith("ptrn_")


@pytest.mark.asyncio
async def test_detect_performative_patterns_no_matches(mock_deps: HookDependencies) -> None:
    """Test behavior when no patterns are matched."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(
            raw_inputs={"q1": "Just some plain text that is completely fine.", "q2": "Nothing to see here."}
        ),
    )

    cast(AsyncMock, mock_deps.system_repo.get_system_config).return_value = {
        "id": "sys_e0b2a3c4d5e6f7a8",
        "slug": "lexicon",
        "type": "performative_lexicons",
        "lexicon_configs": {
            "en": {
                "language_code": "en",
                "language_name": "English",
                "fuzz_threshold": 90.0,
                "words": ["something else"],
            }
        },
    }
    result = await cast(Awaitable[HookResult], detect_performative_patterns(state, mock_deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "global_context_vars" in result.state_delta.delta
    assert len(result.state_delta.delta["global_context_vars"]["step_linguistics"]["performative_patterns"]) == 0


@pytest.mark.asyncio
async def test_detect_performative_patterns_heterogeneous_metadata_payload(mock_deps: HookDependencies) -> None:
    """Regression Test: Hook must handle runtime payload containing None and nested metadata dictionaries."""
    state = HookState(
        execution_id="exe_f63119cec7e14224803b557b8e843650",
        workflow_id="wf_executive_review",
        step_id="sr_f0a26d17cc9b48a7",
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "fi"}),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "organization_id": None,
                "user_id": None,
                "dynamic_inputs": {"product_text": "Tämä on täysin mullistava ja poikkeuksellinen innovaatio."},
                "_step_metadata": {"execution_id": "exe_f63119cec7e14224803b557b8e843650"},
            }
        ),
    )

    cast(AsyncMock, mock_deps.system_repo.get_system_config).return_value = {
        "id": "sys_e0b2a3c4d5e6f7a8",
        "slug": "lexicon",
        "type": "performative_lexicons",
        "lexicon_configs": {
            "fi": {
                "language_code": "fi",
                "language_name": "Finnish",
                "fuzz_threshold": 90.0,
                "words": ["mullistava"],
            }
        },
    }
    result = await cast(Awaitable[HookResult], detect_performative_patterns(state, mock_deps))

    assert result.success is True
    assert result.state_delta is not None
    patterns = result.state_delta.delta["global_context_vars"]["step_linguistics"]["performative_patterns"]
    assert len(patterns) == 1
    assert patterns[0]["detected_phrase"] == "mullistava"
