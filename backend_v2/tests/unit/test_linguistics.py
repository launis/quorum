from typing import cast
from unittest.mock import AsyncMock

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.hooks.linguistics import detect_performative_patterns
from backend_v2.models.domain.linguistics import LinguisticsPayloadDTO


@pytest.fixture
def mock_deps() -> HookDependencies:
    return HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),  # noqa: E501
        search_client=AsyncMock(),
    )


def test_linguistics_payload_dto() -> None:
    """Test safe extraction logic inside LinguisticsPayloadDTO."""
    # Language in global vars
    dto1 = LinguisticsPayloadDTO(dynamic_inputs={})
    assert dto1.extract_language({"language": "fi"}) == "fi"

    # Language in inputs (root)
    dto2 = LinguisticsPayloadDTO(language="es-ES", dynamic_inputs={})
    assert dto2.extract_language({}) == "es"

    # Language missing entirely defaults to en
    dto3 = LinguisticsPayloadDTO(dynamic_inputs={"foo": "bar"})
    assert dto3.extract_language({}) == "en"

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
        metadata={},
        global_context_vars={},
        inputs={"q1": "It is important to note that this is a game changer.", "q2": "Regular text with no fillers."},  # noqa: E501
    )

    mock_deps.system_repo.get_system_config.return_value = {
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
    result = cast(HookResult, await detect_performative_patterns(state, mock_deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "global_context_vars" in result.state_delta
    assert "step_linguistics" in result.state_delta["global_context_vars"]

    patterns = result.state_delta["global_context_vars"]["step_linguistics"]["performative_patterns"]
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
        metadata={},
        global_context_vars={"language": "fi-FI"},
        inputs={"q1": "Tämä on täysin mullistava innovaatio.", "q2": "Syventyä asiaan tarkemmin."},
    )

    mock_deps.system_repo.get_system_config.return_value = {
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
    result = cast(HookResult, await detect_performative_patterns(state, mock_deps))

    assert result.success is True
    assert result.state_delta is not None
    patterns = result.state_delta["global_context_vars"]["step_linguistics"]["performative_patterns"]
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
        metadata={},
        global_context_vars={},
        inputs={"q1": "Just some plain text that is completely fine.", "q2": "Nothing to see here."},
    )

    mock_deps.system_repo.get_system_config.return_value = {
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
    result = cast(HookResult, await detect_performative_patterns(state, mock_deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "global_context_vars" in result.state_delta
    assert len(result.state_delta["global_context_vars"]["step_linguistics"]["performative_patterns"]) == 0
