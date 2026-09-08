"""Unit tests for linguistics hooks and domain schemas."""

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
from backend_v2.exceptions import AppException
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
async def test_detect_performative_patterns_skip_override() -> None:
    """Verify scan_for_performative_patterns=False skips scanning."""
    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(raw_inputs={"scan_for_performative_patterns": "false"}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    deps = MagicMock()
    result = await detect_performative_patterns(state, deps)
    assert result.success
    assert result.state_delta is not None
    res_dict = result.state_delta.delta["step_linguistics"]
    assert res_dict["performative_patterns"] == []


@pytest.mark.asyncio
async def test_detect_performative_patterns_prioritizes_user_only() -> None:
    """Verify chat_log_user_only is prioritized to prevent AI self-accusation."""
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

    deps = MagicMock()
    deps.system_repo = AsyncMock()
    deps.system_repo.get_system_config.return_value = {
        "id": "sys_e0b2a3c4d5e6f7a8",
        "slug": "lexicon",
        "type": "performative_lexicons",
        "lexicon_configs": {
            "en": {
                "language_code": "en",
                "language_name": "English",
                "fuzz_threshold": 90.0,
                "words": ["delve into", "myriad of", "cutting edge", "tapestry"],
            }
        },
    }
    result = await detect_performative_patterns(state, deps)

    assert result.success
    assert result.state_delta is not None
    res_dict = result.state_delta.delta["step_linguistics"]
    patterns = res_dict.get("performative_patterns", [])
    assert len(patterns) == 0


@pytest.mark.asyncio
async def test_detect_performative_patterns_detects_exact_and_fuzzy() -> None:
    """Verify detection of exact and fuzzy baseline performative patterns."""
    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "chat_log_user_only": "We need to delve into this rich tapestries.",
                "language": "en",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        metadata=ExecutionMetadata(),
    )

    deps = MagicMock()
    deps.system_repo = AsyncMock()
    deps.system_repo.get_system_config.return_value = {
        "id": "sys_e0b2a3c4d5e6f7a8",
        "slug": "lexicon",
        "type": "performative_lexicons",
        "lexicon_configs": {
            "en": {
                "language_code": "en",
                "language_name": "English",
                "fuzz_threshold": 80.0,
                "words": ["delve into", "tapestry"],
            }
        },
    }
    result = await detect_performative_patterns(state, deps)

    assert result.success
    assert result.state_delta is not None
    res_dict = result.state_delta.delta["step_linguistics"]
    patterns = res_dict.get("performative_patterns", [])
    assert len(patterns) >= 1


@pytest.mark.asyncio
async def test_detect_performative_patterns_missing_user_only_graceful() -> None:
    """Verify fallback to scanning general dynamic inputs when chat_log_user_only is absent."""
    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "chat_log": "**user**: delve into this.\n\n**ai**: yes.",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        metadata=ExecutionMetadata(),
    )

    deps = MagicMock()
    deps.system_repo = AsyncMock()
    deps.system_repo.get_system_config.return_value = {
        "id": "sys_e0b2a3c4d5e6f7a8",
        "slug": "lexicon",
        "type": "performative_lexicons",
        "lexicon_configs": {
            "en": {
                "language_code": "en",
                "language_name": "English",
                "fuzz_threshold": 90.0,
                "words": ["delve into"],
            }
        },
    }
    result = await detect_performative_patterns(state, deps)

    assert result.success
    assert result.state_delta is not None
    res_dict = result.state_delta.delta["step_linguistics"]
    patterns = res_dict.get("performative_patterns", [])
    assert len(patterns) == 1


@pytest.mark.asyncio
async def test_detect_performative_patterns_missing_lexicon_config() -> None:
    """Verify missing lexicon config triggers Fail-Fast AppException."""
    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "chat_log_user_only": "delve into this.",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        metadata=ExecutionMetadata(),
    )

    deps = MagicMock()
    deps.system_repo = AsyncMock()
    deps.system_repo.get_system_config.return_value = None

    with pytest.raises(AppException) as exc_info:
        await detect_performative_patterns(state, deps)

    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_detect_performative_patterns_missing_language_words() -> None:
    """Verify missing language words triggers Fail-Fast AppException."""
    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "chat_log_user_only": "delve into this.",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "fi"}),
        metadata=ExecutionMetadata(),
    )

    deps = MagicMock()
    deps.system_repo = AsyncMock()
    deps.system_repo.get_system_config.return_value = {
        "id": "sys_e0b2a3c4d5e6f7a8",
        "slug": "lexicon",
        "type": "performative_lexicons",
        "lexicon_configs": {
            "en": {
                "language_code": "en",
                "language_name": "English",
                "fuzz_threshold": 90.0,
                "words": ["delve into"],
            }
        },
    }

    with pytest.raises(AppException) as exc_info:
        await detect_performative_patterns(state, deps)

    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_detect_performative_patterns_db_exception() -> None:
    """Verify repository database exception is propagated cleanly."""
    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "chat_log_user_only": "delve into this.",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        metadata=ExecutionMetadata(),
    )

    deps = MagicMock()
    deps.system_repo = AsyncMock()
    deps.system_repo.get_system_config.side_effect = RuntimeError("Database down")

    with pytest.raises(AppException) as exc_info:
        await detect_performative_patterns(state, deps)

    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_detect_performative_patterns_heterogeneous_metadata_payload(mock_deps: HookDependencies) -> None:
    """Regression Test: Hook must handle runtime payload containing None and nested metadata dictionaries."""
    state = HookState(
        execution_id="exe_f63119cec7e14224803b557b8e843650",
        workflow_id="wf_executive_review",
        step_id="sr_f0a26d17cc9b48a7",
        metadata=ExecutionMetadata(),
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


@pytest.mark.asyncio
async def test_detect_performative_patterns_dynamic_extraction_anchored(
    mock_deps: HookDependencies, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify dynamic LLM extraction extracts and anchors verbatim performative phrases."""
    # Enable feature flag
    settings = get_settings()
    custom_settings = settings.model_copy(update={"enable_dynamic_performative_extraction": True})
    monkeypatch.setattr("backend_v2.hooks.linguistics.get_settings", lambda: custom_settings)

    state = HookState(
        execution_id="exe_dyn_1",
        workflow_id="wf_dyn",
        step_id="sr_dyn",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "fi"}),
        inputs=ExecutionInputsDTO(
            raw_inputs={"chat_log_user_only": "Haluamme syventyä syvemmälle tähän asiaan ja viedä sen maaliin."}
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
                "fuzz_threshold": 85.0,
                "words": ["syventyä"],
            }
        },
    }

    mock_llm_client = AsyncMock()
    mock_extractor_dto = DynamicLinguisticsExtractorDTO(detected_phrases=["syventyä syvemmälle", "viedä sen maaliin"])

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
    # Both baseline "syventyä" and dynamically anchored phrases are detected
    assert "syventyä" in detected_phrases
    assert "syventyä syvemmälle" in detected_phrases
    assert "viedä sen maaliin" in detected_phrases


@pytest.mark.asyncio
async def test_detect_performative_patterns_dynamic_extraction_unanchored_discarded(
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

    cast(AsyncMock, mock_deps.system_repo.get_system_config).return_value = {
        "id": "sys_e0b2a3c4d5e6f7a8",
        "slug": "lexicon",
        "type": "performative_lexicons",
        "lexicon_configs": {
            "en": {
                "language_code": "en",
                "language_name": "English",
                "fuzz_threshold": 92.0,
                "words": ["delve"],
            }
        },
    }

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
async def test_detect_performative_patterns_dynamic_extraction_disabled_by_default(
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

    cast(AsyncMock, mock_deps.system_repo.get_system_config).return_value = {
        "id": "sys_e0b2a3c4d5e6f7a8",
        "slug": "lexicon",
        "type": "performative_lexicons",
        "lexicon_configs": {
            "en": {
                "language_code": "en",
                "language_name": "English",
                "fuzz_threshold": 92.0,
                "words": ["delve"],
            }
        },
    }

    with patch("backend_v2.hooks.linguistics.LLMClient.from_strategy") as mock_from_strategy:
        result = await cast(Awaitable[HookResult], detect_performative_patterns(state, mock_deps))
        mock_from_strategy.assert_not_called()

    assert result.success is True
    assert result.state_delta is not None
    patterns = result.state_delta.delta["step_linguistics"]["performative_patterns"]
    assert len(patterns) == 1
    assert patterns[0]["detected_phrase"] == "delve"


@pytest.mark.asyncio
async def test_detect_performative_patterns_dynamic_extraction_error_fallback(
    mock_deps: HookDependencies, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that dynamic extraction failures fall back gracefully to baseline seed words."""
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

    cast(AsyncMock, mock_deps.system_repo.get_system_config).return_value = {
        "id": "sys_e0b2a3c4d5e6f7a8",
        "slug": "lexicon",
        "type": "performative_lexicons",
        "lexicon_configs": {
            "en": {
                "language_code": "en",
                "language_name": "English",
                "fuzz_threshold": 92.0,
                "words": ["delve"],
            }
        },
    }

    with patch("backend_v2.hooks.linguistics.LLMClient.from_strategy", side_effect=RuntimeError("LLM API Timeout")):
        result = await cast(Awaitable[HookResult], detect_performative_patterns(state, mock_deps))

    # Does not crash; falls back to baseline "delve"
    assert result.success is True
    assert result.state_delta is not None
    patterns = result.state_delta.delta["step_linguistics"]["performative_patterns"]
    assert len(patterns) == 1
    assert patterns[0]["detected_phrase"] == "delve"
