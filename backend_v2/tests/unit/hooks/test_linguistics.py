from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.linguistics import detect_performative_patterns
from backend_v2.models.execution_core import ExecutionMetadata


@pytest.mark.asyncio
async def test_detect_performative_patterns_empty_state() -> None:
    deps = MagicMock()
    result = await detect_performative_patterns(None, deps)  # type: ignore[arg-type]
    assert result.success
    assert result.state_delta is not None
    assert result.state_delta.delta == {}


@pytest.mark.asyncio
async def test_detect_performative_patterns_skip_override() -> None:
    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(raw_inputs={"scan_for_performative_patterns": "false"}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(target_locale="en"),
    )
    deps = MagicMock()
    result = await detect_performative_patterns(state, deps)
    assert result.success
    assert result.state_delta is not None
    res_dict = result.state_delta.delta["step_linguistics"]
    assert res_dict["performative_patterns"] == []


@pytest.mark.asyncio
async def test_detect_performative_patterns_prioritizes_user_only() -> None:
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
        metadata=ExecutionMetadata(target_locale="en"),
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
        metadata=ExecutionMetadata(target_locale="en"),
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
    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "chat_log": "**user**: delve into this.\n\n**ai**: yes.",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        metadata=ExecutionMetadata(target_locale="en"),
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
    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "chat_log_user_only": "delve into this.",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        metadata=ExecutionMetadata(target_locale="en"),
    )

    deps = MagicMock()
    deps.system_repo = AsyncMock()
    deps.system_repo.get_system_config.return_value = None

    with pytest.raises(AppException) as exc_info:
        await detect_performative_patterns(state, deps)

    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_detect_performative_patterns_missing_language_words() -> None:
    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "chat_log_user_only": "delve into this.",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "fi"}),
        metadata=ExecutionMetadata(target_locale="fi"),
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
    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "chat_log_user_only": "delve into this.",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"language": "en"}),
        metadata=ExecutionMetadata(target_locale="en"),
    )

    deps = MagicMock()
    deps.system_repo = AsyncMock()
    deps.system_repo.get_system_config.side_effect = RuntimeError("Database down")

    with pytest.raises(AppException) as exc_info:
        await detect_performative_patterns(state, deps)

    assert exc_info.value.status_code == 500
