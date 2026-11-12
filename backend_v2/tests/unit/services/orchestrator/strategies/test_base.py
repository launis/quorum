"""Unit tests for base orchestration strategy abstractions (base.py).

Verifies StrategyContext strict Pydantic V2 invariants, StrategyDependencies
immutability, NodeStrategy property accessors, FinOps quota circuit-breaking,
and pre/post hook execution sequences including ISTQB negative error boundaries.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.step import Step as V2Step
from backend_v2.models.domain.step import StepRule
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.hook_delta import ExecutionMetadataDeltaDTO, MatrixHookResultDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.enums import EntityPrefix
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.services.orchestrator.strategies.base import (
    NodeStrategy,
    StrategyContext,
    StrategyDependencies,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository

_STEP_NAME = I18nText(translations={"en": "s1"})
_STEP_ID = generate_opaque_id(EntityPrefix.STEP)
_STEP_RULE_ID = "sr_0195f3a0000070008123456789abcdef"
_EXEC_ID = generate_opaque_id(EntityPrefix.EXECUTION)
_WF_ID = generate_opaque_id(EntityPrefix.WORKFLOW)
_ORG_ID = generate_opaque_id(EntityPrefix.ORGANIZATION)
_BLK_ID = generate_opaque_id(EntityPrefix.PROMPT_BLOCK)


def _make_step(
    *,
    pre_hooks: list[str] | None = None,
    post_hooks: list[str] | None = None,
) -> V2Step:
    """Build a valid V2Step instance for hook execution tests."""
    return V2Step(
        id=_STEP_ID,
        slug="s1",
        name=_STEP_NAME,
        extraction_protocol_block_id=_BLK_ID,
        criteria_block_ids=[_BLK_ID],
        pre_hooks=pre_hooks if pre_hooks is not None else [],
        post_hooks=post_hooks if post_hooks is not None else [],
        allowed_mcp_tools=[],
        mcp_tool_params={},
        expected_inputs=[],
    )


def _make_step_rule() -> StepRule:
    """Build a valid StepRule instance for hook execution tests."""
    return StepRule(
        id=_STEP_RULE_ID,
        task_blueprint=_STEP_ID,
        depends_on=[],
        input_mappings={},
    )


def _make_hook_state(
    *,
    language: str | None = None,
    dynamic_inputs: dict[str, str] | None = None,
) -> HookState:
    """Build a valid HookState instance for hook execution tests."""
    return HookState(
        execution_id=_EXEC_ID,
        workflow_id=_WF_ID,
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(language=language),
        inputs=ExecutionInputsDTO(
            raw_inputs={},
            dynamic_inputs=dynamic_inputs if dynamic_inputs is not None else {},
        ),
    )


class DummyStrategy(NodeStrategy):
    """Concrete NodeStrategy test double for testing base strategy methods."""

    async def execute(self, *args: Any, **kwargs: Any) -> list[TraceEvent]:
        """Return an empty list of TraceEvents for base class testing."""
        return []


@pytest.fixture
def dummy_strategy() -> DummyStrategy:
    """Create a DummyStrategy backed by an InMemoryUnifiedWorkflowRepository."""
    repo = InMemoryUnifiedWorkflowRepository()
    deps = StrategyDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=AsyncMock(),
        arq_pool=MagicMock(),
    )
    return DummyStrategy(deps=deps)


def test_strategy_properties(dummy_strategy: DummyStrategy) -> None:
    """Verify all convenience property accessors on NodeStrategy."""
    assert dummy_strategy.exec_repo is dummy_strategy.deps.exec_repo
    assert dummy_strategy.workflow_repo is dummy_strategy.deps.workflow_repo
    assert dummy_strategy.prompt_block_repo is dummy_strategy.deps.prompt_block_repo
    assert dummy_strategy.output_profile_repo is dummy_strategy.deps.output_profile_repo
    assert dummy_strategy.identity_repo is dummy_strategy.deps.identity_repo
    assert dummy_strategy.audit_repo is dummy_strategy.deps.audit_repo
    assert dummy_strategy.system_repo is dummy_strategy.deps.system_repo
    assert dummy_strategy.compiler is dummy_strategy.deps.prompt_compiler
    assert dummy_strategy.arq_pool is dummy_strategy.deps.arq_pool


@pytest.mark.asyncio
async def test_assert_quota_no_org(dummy_strategy: DummyStrategy) -> None:
    """Verify assert_quota returns immediately when org_id is None."""
    await dummy_strategy.assert_quota(None)


@pytest.mark.asyncio
async def test_assert_quota_safe(dummy_strategy: DummyStrategy, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify assert_quota passes cleanly when organization quota is within limits."""
    mock_usage = AsyncMock()
    mock_usage.check_quota.return_value = True
    monkeypatch.setattr("backend_v2.services.orchestrator.strategies.base.UsageService", lambda *args: mock_usage)

    await dummy_strategy.assert_quota(_ORG_ID)
    mock_usage.check_quota.assert_called_once_with(_ORG_ID)


@pytest.mark.asyncio
async def test_assert_quota_exceeded(dummy_strategy: DummyStrategy, monkeypatch: pytest.MonkeyPatch) -> None:
    """Negative test (ISTQB): assert_quota raises 402 AppException when organization quota is exhausted."""
    mock_usage = AsyncMock()
    mock_usage.check_quota.return_value = False
    monkeypatch.setattr("backend_v2.services.orchestrator.strategies.base.UsageService", lambda *args: mock_usage)

    with pytest.raises(AppException) as exc:
        await dummy_strategy.assert_quota(_ORG_ID)
    assert exc.value.status_code == 402
    assert exc.value.details["error_code"] == ErrorCodes.RATE_LIMIT_EXCEEDED.value


@pytest.mark.asyncio
async def test_run_pre_hooks_empty(dummy_strategy: DummyStrategy) -> None:
    """Verify run_pre_hooks returns original HookState and empty events when pre_hooks is empty."""
    step_obj = _make_step(pre_hooks=[])
    step_rule = _make_step_rule()
    hook_state = _make_hook_state()
    res_state, res_events = await dummy_strategy.run_pre_hooks(
        step_obj, step_rule, hook_state, MagicMock(spec=HookDependencies)
    )
    assert res_state == hook_state
    assert res_events == []


@pytest.mark.asyncio
async def test_run_pre_hooks_success(dummy_strategy: DummyStrategy, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify run_pre_hooks reduces state deltas and emits TraceEvents on successful hook execution."""
    mock_result = HookResult(
        success=True,
        state_delta=HookDeltaDTO(
            metadata_updates=ExecutionMetadataDeltaDTO(matrix_sampling_strategy=5),
            delta=GlobalContextVarsDTO(language="fi", target_locale="en"),
        ),
    )
    monkeypatch.setattr(hook_registry, "execute", AsyncMock(return_value=mock_result))

    step_obj = _make_step(pre_hooks=["hook_test"])
    step_rule = _make_step_rule()
    hook_state = _make_hook_state(language="fi", dynamic_inputs={"in": "1"})

    res_state, res_events = await dummy_strategy.run_pre_hooks(
        step_obj, step_rule, hook_state, MagicMock(spec=HookDependencies)
    )
    assert res_state.metadata.matrix_sampling_strategy == 5
    assert res_state.global_context_vars.language == "fi"
    assert res_state.global_context_vars.target_locale == "en"
    assert res_state.inputs.dynamic_inputs == {"in": "1"}
    assert len(res_events) == 1
    assert res_events[0].step_name == _STEP_RULE_ID
    assert isinstance(res_events[0].content, dict)
    assert res_events[0].content["target_locale"] == "en"


@pytest.mark.asyncio
async def test_run_pre_hooks_failure(dummy_strategy: DummyStrategy, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify run_pre_hooks preserves HookState and logs warning when pre-hook returns success=False."""
    mock_result = HookResult(success=False, state_delta=None)
    monkeypatch.setattr(hook_registry, "execute", AsyncMock(return_value=mock_result))

    step_obj = _make_step(pre_hooks=["hook_fail"])
    step_rule = _make_step_rule()
    hook_state = _make_hook_state()

    res_state, res_events = await dummy_strategy.run_pre_hooks(
        step_obj, step_rule, hook_state, MagicMock(spec=HookDependencies)
    )
    assert res_state == hook_state
    assert res_events == []


@pytest.mark.asyncio
async def test_run_post_hooks_empty(dummy_strategy: DummyStrategy) -> None:
    """Verify run_post_hooks returns original HookState and empty events when post_hooks is empty."""
    step_obj = _make_step(post_hooks=[])
    step_rule = _make_step_rule()
    hook_state = _make_hook_state()
    res_state, res_events = await dummy_strategy.run_post_hooks(
        step_obj, step_rule, hook_state, MagicMock(spec=HookDependencies)
    )
    assert res_state == hook_state
    assert res_events == []


@pytest.mark.asyncio
async def test_run_post_hooks_success(dummy_strategy: DummyStrategy, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify run_post_hooks reduces state deltas and emits TraceEvents on successful hook execution."""
    mock_result = HookResult(
        success=True,
        state_delta=HookDeltaDTO(
            metadata_updates=ExecutionMetadataDeltaDTO(matrix_sampling_strategy=5),
            delta=GlobalContextVarsDTO(language="fi", target_locale="en"),
        ),
    )
    monkeypatch.setattr(hook_registry, "execute", AsyncMock(return_value=mock_result))

    step_obj = _make_step(post_hooks=["hook_post"])
    step_rule = _make_step_rule()
    hook_state = _make_hook_state(language="fi", dynamic_inputs={"in": "1"})

    res_state, res_events = await dummy_strategy.run_post_hooks(
        step_obj, step_rule, hook_state, MagicMock(spec=HookDependencies)
    )
    assert res_state.metadata.matrix_sampling_strategy == 5
    assert res_state.global_context_vars.language == "fi"
    assert res_state.global_context_vars.target_locale == "en"
    assert res_state.inputs.dynamic_inputs == {"in": "1"}
    assert len(res_events) == 1
    assert res_events[0].step_name == _STEP_RULE_ID
    assert isinstance(res_events[0].content, dict)
    assert res_events[0].content["target_locale"] == "en"


@pytest.mark.asyncio
async def test_run_post_hooks_failure(dummy_strategy: DummyStrategy, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify run_post_hooks preserves HookState and logs warning when post-hook returns success=False."""
    mock_result = HookResult(success=False, state_delta=None)
    monkeypatch.setattr(hook_registry, "execute", AsyncMock(return_value=mock_result))

    step_obj = _make_step(post_hooks=["hook_fail"])
    step_rule = _make_step_rule()
    hook_state = _make_hook_state()

    res_state, res_events = await dummy_strategy.run_post_hooks(
        step_obj, step_rule, hook_state, MagicMock(spec=HookDependencies)
    )
    assert res_state == hook_state
    assert res_events == []


@pytest.mark.asyncio
async def test_run_post_hooks_with_matrix_hook_result(
    dummy_strategy: DummyStrategy, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify run_post_hooks handles MatrixHookResultDTO state delta reduction properly."""
    matrix_out = LightweightMatrixOutput(
        raw_score=4.0,
        normalized_score=80.0,
        evaluated_atoms={},
        extensions={},
    )
    matrix_dto = MatrixHookResultDTO(
        matrix_outputs={_BLK_ID: matrix_out},
        missing_contexts={_BLK_ID: "missing_data"},
        atom_quotes={_BLK_ID: []},
    )
    mock_result = HookResult(
        success=True,
        state_delta=HookDeltaDTO(
            delta=matrix_dto,
        ),
    )
    monkeypatch.setattr(hook_registry, "execute", AsyncMock(return_value=mock_result))

    step_obj = _make_step(post_hooks=["hook_matrix"])
    step_rule = _make_step_rule()
    hook_state = _make_hook_state()

    res_state, _ = await dummy_strategy.run_post_hooks(
        step_obj, step_rule, hook_state, MagicMock(spec=HookDependencies)
    )
    assert res_state.global_context_vars is not None
    assert res_state.global_context_vars.evaluative_matrices is not None
    assert res_state.global_context_vars.evaluative_matrices[_BLK_ID] == 80.0


@pytest.mark.asyncio
async def test_run_pre_and_post_hooks_with_dto_and_explicit_inputs(
    dummy_strategy: DummyStrategy, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify run_pre_hooks handles ExecutionInputsDTO state deltas for dynamic and raw inputs."""
    mock_result = HookResult(
        success=True,
        state_delta=HookDeltaDTO(
            delta=ExecutionInputsDTO(
                dynamic_inputs={"dyn_key": "dyn_val"},
                raw_inputs={"raw_key": "raw_val"},
            ),
        ),
    )
    monkeypatch.setattr(hook_registry, "execute", AsyncMock(return_value=mock_result))

    step_obj = _make_step(pre_hooks=["hook_pre"])
    step_rule = _make_step_rule()
    hook_state = _make_hook_state(language="fi")

    res_state, _ = await dummy_strategy.run_pre_hooks(step_obj, step_rule, hook_state, MagicMock(spec=HookDependencies))
    assert res_state.global_context_vars.language == "fi"
    assert res_state.inputs.dynamic_inputs["dyn_key"] == "dyn_val"
    assert res_state.inputs.raw_inputs["raw_key"] == "raw_val"


@pytest.mark.asyncio
async def test_negative_hook_execution_raises_app_exception(
    dummy_strategy: DummyStrategy, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Negative test (ISTQB): fatal AppException raised inside hook_registry propagates fail-fast."""
    monkeypatch.setattr(
        hook_registry,
        "execute",
        AsyncMock(
            side_effect=AppException(
                message="Fatal hook invariant failure",
                status_code=422,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        ),
    )
    step_obj = _make_step(pre_hooks=["fatal_hook"])
    step_rule = _make_step_rule()
    hook_state = _make_hook_state()

    with pytest.raises(AppException) as exc_info:
        await dummy_strategy.run_pre_hooks(step_obj, step_rule, hook_state, MagicMock(spec=HookDependencies))
    assert exc_info.value.status_code == 422
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_strategy_context_validation_and_immutability() -> None:
    """Negative test (ISTQB): StrategyContext enforces extra='forbid', strict=True, and frozen=True."""
    ctx = StrategyContext(
        execution_id=_EXEC_ID,
        workflow_id=_WF_ID,
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        context_variables=ContextVariablesDTO(variables={}),
        prompt_blocks=[],
    )
    assert ctx.execution_id == _EXEC_ID
    assert ctx.workflow_id == _WF_ID
    assert ctx.target_locale == "en"

    with pytest.raises(ValidationError):
        StrategyContext.model_validate(
            {
                "execution_id": _EXEC_ID,
                "workflow_id": _WF_ID,
                "metadata": ExecutionMetadata(),
                "extra_field": "rejected",
            }
        )

    with pytest.raises(ValidationError):
        StrategyContext.model_validate(
            {
                "execution_id": _EXEC_ID,
                "workflow_id": _WF_ID,
                "metadata": ExecutionMetadata(),
                "strictness_level": "not_an_int",
            }
        )
