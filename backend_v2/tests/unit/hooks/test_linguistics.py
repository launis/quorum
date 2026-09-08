"""Unit tests for linguistics hooks and dynamic performative extraction."""

from collections.abc import Awaitable
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookResult,
    HookState,
)
from backend_v2.hooks.linguistics import detect_performative_patterns
from backend_v2.models.domain.linguistics import (
    DynamicLinguisticsExtractorDTO,
    LinguisticsPayloadDTO,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.settings import get_lexical_fuzz_threshold, get_settings


@pytest.fixture
def mock_deps() -> HookDependencies:
    """Fixture providing mocked dependencies for linguistics hook execution."""
    return HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=MagicMock(),
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
    assert "bar" in dto3.get_text_to_scan()
    assert "foo" not in dto3.get_text_to_scan()  # only values are scanned

    # chat_log_user_only prioritization
    dto4 = LinguisticsPayloadDTO(dynamic_inputs={"chat_log": "ai content", "chat_log_user_only": "user text only"})
    assert dto4.get_text_to_scan() == "user text only"


def test_get_lexical_fuzz_threshold_locales() -> None:
    """Verify SSOT get_lexical_fuzz_threshold dynamic resolution by language type."""
    # Agglutinative languages
    assert get_lexical_fuzz_threshold("fi") == 85.0
    assert get_lexical_fuzz_threshold("hu") == 85.0
    assert get_lexical_fuzz_threshold("tr") == 85.0

    # Analytic languages
    assert get_lexical_fuzz_threshold("en") == 92.0
    assert get_lexical_fuzz_threshold("sv") == 92.0
    assert get_lexical_fuzz_threshold("de") == 92.0

    # Isolating languages
    assert get_lexical_fuzz_threshold("zh") == 98.0
    assert get_lexical_fuzz_threshold("ja") == 98.0
    assert get_lexical_fuzz_threshold("ko") == 98.0

    # Fallback default
    assert get_lexical_fuzz_threshold(None) == 90.0
    assert get_lexical_fuzz_threshold("unknown_locale") == 90.0


@pytest.mark.asyncio
async def test_detect_performative_patterns_empty_state() -> None:
    """Verify empty state returns successful no-op."""
    deps = MagicMock()
    result = await detect_performative_patterns(None, deps)  # type: ignore[arg-type]
    assert result.success
    assert result.state_delta is not None
    assert result.state_delta.delta == {}


@pytest.mark.asyncio
async def test_detect_performative_patterns_skip_override(mock_deps: HookDependencies) -> None:
    """Verify scan_for_performative_patterns=False skips scanning but records total_word_count."""
    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "scan_for_performative_patterns": "false",
                "chat_log_user_only": "This is a five word sentence.",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    result = await detect_performative_patterns(state, mock_deps)
    assert result.success
    assert result.state_delta is not None
    res_dict = result.state_delta.delta["step_linguistics"]
    assert res_dict["performative_patterns"] == []
    assert res_dict["total_word_count"] == 6


@pytest.mark.asyncio
async def test_detect_performative_patterns_prioritizes_user_only(
    mock_deps: HookDependencies, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify chat_log_user_only is prioritized to prevent AI self-accusation."""
    settings = get_settings()
    custom_settings = settings.model_copy(update={"enable_dynamic_performative_extraction": True})
    monkeypatch.setattr("backend_v2.hooks.linguistics.get_settings", lambda: custom_settings)

    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "chat_log": "**user**: normal text.\n\n**ai**: we must delve into the myriad of cutting edge tapestry.",
                "chat_log_user_only": "normal text.",
                "language": "en",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        metadata=ExecutionMetadata(),
    )

    mock_llm_client = AsyncMock()
    mock_extractor_dto = DynamicLinguisticsExtractorDTO(detected_phrases=["delve into"])

    with (
        patch("backend_v2.hooks.linguistics.LLMClient.from_strategy", return_value=mock_llm_client),
        patch(
            "backend_v2.hooks.linguistics.LLMTaskExecutor.execute_structured_task",
            return_value=(mock_extractor_dto, None),
        ),
    ):
        result = await cast(Awaitable[HookResult], detect_performative_patterns(state, mock_deps))

    assert result.success
    assert result.state_delta is not None
    res_dict = result.state_delta.delta["step_linguistics"]
    patterns = res_dict.get("performative_patterns", [])
    # "delve into" was not in user text, so it got discarded
    assert len(patterns) == 0
    assert res_dict["total_word_count"] == 2


@pytest.mark.asyncio
async def test_detect_performative_patterns_exact_substring(
    mock_deps: HookDependencies, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify verbatim exact match performative phrases are captured."""
    settings = get_settings()
    custom_settings = settings.model_copy(update={"enable_dynamic_performative_extraction": True})
    monkeypatch.setattr("backend_v2.hooks.linguistics.get_settings", lambda: custom_settings)

    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "chat_log_user_only": "We need to delve into this core matter.",
                "language": "en",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        metadata=ExecutionMetadata(),
    )

    mock_llm_client = AsyncMock()
    mock_extractor_dto = DynamicLinguisticsExtractorDTO(detected_phrases=["delve into"])

    with (
        patch("backend_v2.hooks.linguistics.LLMClient.from_strategy", return_value=mock_llm_client),
        patch(
            "backend_v2.hooks.linguistics.LLMTaskExecutor.execute_structured_task",
            return_value=(mock_extractor_dto, None),
        ),
    ):
        result = await cast(Awaitable[HookResult], detect_performative_patterns(state, mock_deps))

    assert result.success
    assert result.state_delta is not None
    res_dict = result.state_delta.delta["step_linguistics"]
    patterns = res_dict.get("performative_patterns", [])
    assert len(patterns) == 1
    assert patterns[0]["detected_phrase"] == "delve into"
    assert res_dict["total_word_count"] == 8


@pytest.mark.asyncio
async def test_detect_performative_patterns_morphological_inflection(
    mock_deps: HookDependencies, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify Finnish morphological inflection: LLM base form 'syventyä' matches text 'syvennytään'."""
    settings = get_settings()
    custom_settings = settings.model_copy(update={"enable_dynamic_performative_extraction": True})
    monkeypatch.setattr("backend_v2.hooks.linguistics.get_settings", lambda: custom_settings)

    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "chat_log_user_only": "Tässä palaverissa syvennytään tarkemmin tähän kokonaisuuteen.",
                "language": "fi",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "fi"}),
        metadata=ExecutionMetadata(),
    )

    mock_llm_client = AsyncMock()
    # LLM extracts candidate base form or partial phrase
    mock_extractor_dto = DynamicLinguisticsExtractorDTO(detected_phrases=["syvennytään tarkemmin"])

    with (
        patch("backend_v2.hooks.linguistics.LLMClient.from_strategy", return_value=mock_llm_client),
        patch(
            "backend_v2.hooks.linguistics.LLMTaskExecutor.execute_structured_task",
            return_value=(mock_extractor_dto, None),
        ),
    ):
        result = await cast(Awaitable[HookResult], detect_performative_patterns(state, mock_deps))

    assert result.success
    assert result.state_delta is not None
    res_dict = result.state_delta.delta["step_linguistics"]
    patterns = res_dict.get("performative_patterns", [])
    assert len(patterns) == 1
    assert patterns[0]["detected_phrase"] == "syvennytään tarkemmin"


@pytest.mark.asyncio
async def test_detect_performative_patterns_unanchored_discarded(
    mock_deps: HookDependencies, monkeypatch: pytest.MonkeyPatch
) -> None:
    """ISTQB negative test: Unanchored hallucinated phrases from LLM are discarded."""
    settings = get_settings()
    custom_settings = settings.model_copy(update={"enable_dynamic_performative_extraction": True})
    monkeypatch.setattr("backend_v2.hooks.linguistics.get_settings", lambda: custom_settings)

    state = HookState(
        execution_id="exe_dyn_2",
        workflow_id="wf_dyn",
        step_id="sr_dyn",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        inputs=ExecutionInputsDTO(raw_inputs={"chat_log_user_only": "We delve into the core technical details."}),
    )

    mock_llm_client = AsyncMock()
    # LLM hallucinates "paradigm shifting synergy" which is NOT in user text
    mock_extractor_dto = DynamicLinguisticsExtractorDTO(
        detected_phrases=["delve into", "paradigm shifting synergy", "   "]
    )

    with (
        patch("backend_v2.hooks.linguistics.LLMClient.from_strategy", return_value=mock_llm_client),
        patch(
            "backend_v2.hooks.linguistics.LLMTaskExecutor.execute_structured_task",
            return_value=(mock_extractor_dto, None),
        ),
    ):
        result = await cast(Awaitable[HookResult], detect_performative_patterns(state, mock_deps))

    assert result.success is True
    assert result.state_delta is not None
    patterns = result.state_delta.delta["step_linguistics"]["performative_patterns"]
    detected_phrases = [p["detected_phrase"] for p in patterns]
    # "delve into" is anchored; "paradigm shifting synergy" was discarded
    assert "delve into" in detected_phrases
    assert "paradigm shifting synergy" not in detected_phrases


@pytest.mark.asyncio
async def test_detect_performative_patterns_disabled_setting(
    mock_deps: HookDependencies, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that when enable_dynamic_performative_extraction is False, LLM is bypassed."""
    settings = get_settings()
    custom_settings = settings.model_copy(update={"enable_dynamic_performative_extraction": False})
    monkeypatch.setattr("backend_v2.hooks.linguistics.get_settings", lambda: custom_settings)

    state = HookState(
        execution_id="exe_dyn_3",
        workflow_id="wf_dyn",
        step_id="sr_dyn",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        inputs=ExecutionInputsDTO(raw_inputs={"chat_log_user_only": "We delve into this matter."}),
    )

    with patch("backend_v2.hooks.linguistics.LLMClient.from_strategy") as mock_from_strategy:
        result = await cast(Awaitable[HookResult], detect_performative_patterns(state, mock_deps))
        mock_from_strategy.assert_not_called()

    assert result.success is True
    assert result.state_delta is not None
    patterns = result.state_delta.delta["step_linguistics"]["performative_patterns"]
    assert len(patterns) == 0


@pytest.mark.asyncio
async def test_detect_performative_patterns_llm_exception_graceful(
    mock_deps: HookDependencies, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that dynamic extraction failures handle exceptions gracefully without crashing."""
    settings = get_settings()
    custom_settings = settings.model_copy(update={"enable_dynamic_performative_extraction": True})
    monkeypatch.setattr("backend_v2.hooks.linguistics.get_settings", lambda: custom_settings)

    state = HookState(
        execution_id="exe_dyn_4",
        workflow_id="wf_dyn",
        step_id="sr_dyn",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        inputs=ExecutionInputsDTO(raw_inputs={"chat_log_user_only": "We delve into this matter."}),
    )

    with patch("backend_v2.hooks.linguistics.LLMClient.from_strategy", side_effect=RuntimeError("LLM API Timeout")):
        result = await cast(Awaitable[HookResult], detect_performative_patterns(state, mock_deps))

    # Does not crash; gracefully returns empty patterns
    assert result.success is True
    assert result.state_delta is not None
    patterns = result.state_delta.delta["step_linguistics"]["performative_patterns"]
    assert len(patterns) == 0


@pytest.mark.asyncio
async def test_detect_performative_patterns_computes_total_word_count(mock_deps: HookDependencies) -> None:
    """Verify total_word_count is accurately computed regardless of performative phrases."""
    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "scan_for_performative_patterns": "false",
                "chat_log_user_only": "One two three four five six seven eight nine ten.",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    result = await detect_performative_patterns(state, mock_deps)
    res_dict = result.state_delta.delta["step_linguistics"]
    assert res_dict["total_word_count"] == 10
