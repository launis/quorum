from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookState,
)
from backend_v2.hooks.references import generate_bibliography_hook
from backend_v2.models.execution_core import ExecutionMetadata


@pytest.mark.asyncio
async def test_generate_bibliography_hook_success() -> None:
    """Test that bibliography generation returns strictly typed Pydantic dicts."""
    state = HookState(
        execution_id="123",
        workflow_id="wf1",
        step_id="step1",
        inputs=ExecutionInputsDTO(raw_inputs={"text": "This is a dummy text for testing citations."}),
        global_context_vars=GlobalContextVarsDTO(vars={"knowledge_base": {"concepts": []}}),
        metadata=ExecutionMetadata(),
    )

    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    from collections.abc import Awaitable
    from typing import cast

    from backend_v2.core.hook_registry import HookResult

    result = await cast(Awaitable[HookResult], generate_bibliography_hook(state, deps))

    assert result.success is True
    assert isinstance(result.state_delta, HookDeltaDTO)
    assert "bibliography_result" in result.state_delta.delta
    refs = result.state_delta.delta["bibliography_result"]["references"]

    assert len(refs) == 1
    assert refs[0]["source_id"].startswith("ref_")
    assert "url" in refs[0]


@pytest.mark.asyncio
async def test_generate_bibliography_hook_none_state() -> None:
    from collections.abc import Awaitable
    from typing import cast

    from backend_v2.core.hook_registry import HookResult

    deps = MagicMock(spec=HookDependencies)
    result = await cast(Awaitable[HookResult], generate_bibliography_hook(None, deps))  # type: ignore[arg-type]
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta == {}


@pytest.mark.asyncio
async def test_generate_bibliography_hook_invalid_inputs_raises() -> None:
    from collections.abc import Awaitable
    from typing import cast

    from backend_v2.core.hook_registry import HookResult
    from backend_v2.exceptions import AppException

    mock_inputs = MagicMock()
    mock_inputs.raw_inputs = 12345
    state = HookState(
        execution_id="123",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    object.__setattr__(state, "inputs", mock_inputs)
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc:
        await cast(Awaitable[HookResult], generate_bibliography_hook(state, deps))
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_generate_bibliography_hook_none_gvars_raises() -> None:
    from collections.abc import Awaitable
    from typing import cast

    from backend_v2.core.hook_registry import HookResult
    from backend_v2.exceptions import AppException

    state = HookState(
        execution_id="123",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(raw_inputs={"text": "Hello"}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    object.__setattr__(state, "global_context_vars", None)
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc:
        await cast(Awaitable[HookResult], generate_bibliography_hook(state, deps))
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_generate_bibliography_hook_invalid_context_raises() -> None:
    from collections.abc import Awaitable
    from typing import cast

    from backend_v2.core.hook_registry import HookResult
    from backend_v2.exceptions import AppException

    state = HookState(
        execution_id="123",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(raw_inputs={"text": "Hello"}),
        global_context_vars=GlobalContextVarsDTO(vars={"knowledge_base": "not_a_dict"}),
        metadata=ExecutionMetadata(),
    )
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc:
        await cast(Awaitable[HookResult], generate_bibliography_hook(state, deps))
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_generate_bibliography_hook_empty_text_short_circuit() -> None:
    from collections.abc import Awaitable
    from typing import cast

    from backend_v2.core.hook_registry import HookResult

    state = HookState(
        execution_id="123",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(raw_inputs={"text": ""}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    deps = MagicMock(spec=HookDependencies)

    result = await cast(Awaitable[HookResult], generate_bibliography_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta == {}


@pytest.mark.asyncio
async def test_generate_bibliography_hook_with_step_coach_and_no_kb_in_gvars() -> None:
    from collections.abc import Awaitable
    from typing import cast

    from backend_v2.core.hook_registry import HookResult

    state = HookState(
        execution_id="123",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(vars={"step_coach": {"coach_note": "Great"}}),
        metadata=ExecutionMetadata(),
    )
    deps = MagicMock(spec=HookDependencies)

    result = await cast(Awaitable[HookResult], generate_bibliography_hook(state, deps))
    assert result.success is True
    assert "bibliography_result" in result.state_delta.delta
    assert "knowledge_base" in result.state_delta.delta


def test_generate_bibliography_generic_error_raises() -> None:
    from unittest.mock import patch

    from backend_v2.exceptions import AppException
    from backend_v2.hooks.references import generate_bibliography

    with patch("uuid.uuid4", side_effect=RuntimeError("UUID generation failure")):
        with pytest.raises(AppException) as exc:
            generate_bibliography("sample text", None)
        assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_generate_bibliography_hook_unexpected_error_raises() -> None:
    from collections.abc import Awaitable
    from typing import cast
    from unittest.mock import patch

    from backend_v2.core.hook_registry import HookResult
    from backend_v2.exceptions import AppException

    state = HookState(
        execution_id="123",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(raw_inputs={"text": "Valid text"}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    deps = MagicMock(spec=HookDependencies)

    with patch("backend_v2.hooks.references.generate_bibliography", side_effect=RuntimeError("Unexpected error")):
        with pytest.raises(AppException) as exc:
            await cast(Awaitable[HookResult], generate_bibliography_hook(state, deps))
        assert exc.value.status_code == 500
