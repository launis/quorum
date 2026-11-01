from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStepState
from backend_v2.models.domain.prompt_blocks import PersonaPromptBlock
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.enums import (
    BlockDataType,
    CognitiveTier,
    EngineType,
    ExecutionStatus,
    HistoricalContextMode,
    PromptBlockCategory,
    StepType,
)
from backend_v2.models.state import TraceEvent
from backend_v2.services.execution import ExecutionService
from backend_v2.services.orchestrator.dag_executor.workflow_bootstrap_stage import (
    bootstrap_workflow_execution_state,
    compute_step_input_merkle_hash,
)
from backend_v2.services.orchestrator.strategies.base import StrategyDependencies
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _create_workflow(
    workflow_id: str = "wor_0195f3a0000070018234567890abcdef",
    version: int = 1,
    steps: list[StepRule] | None = None,
) -> Workflow:
    return Workflow(
        id=workflow_id,
        slug="test-workflow",
        name=I18nText(translations={"en": "Test Workflow"}),
        description=I18nText(translations={"en": "Test Description"}),
        status="active",
        version=version,
        organization_id="org_1",
        default_strictness_level=50,
        model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=steps or [],
    )


def _create_record(
    execution_id: str = "exe_0195f3a0000070018234567890abcdef",
    workflow_id: str = "wor_0195f3a0000070018234567890abcdef",
    status: ExecutionStatus = ExecutionStatus.FAILED,
    workflow_version: int = 1,
    step_states: dict[str, ExecutionStepState] | None = None,
    execution_trace: list[TraceEvent] | None = None,
    organization_id: str = "org_1",
    created_by: str = "usr_1",
) -> ExecutionRecord:
    return ExecutionRecord(
        id=execution_id,
        workflow_id=workflow_id,
        status=status,
        target_locale="fi",
        organization_id=organization_id,
        created_by=created_by,
        workflow_version=workflow_version,
        output_profile_id="prf_0195f3a0000070008123456789abcdef",
        active_profile_id="prf_0195f3a0000070008123456789abcdef",
        step_states=step_states or {},
        execution_trace=execution_trace or [],
        profile_syntheses={"prf_0195f3a0000070008123456789abcdef": RenderedSynthesisCache.model_validate({})},
        context_variables=ContextVariablesDTO(),
    )


def _create_test_service(
    usage_service: Any = None,
) -> tuple[ExecutionService, InMemoryUnifiedWorkflowRepository]:
    repo = InMemoryUnifiedWorkflowRepository()
    service = ExecutionService(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        system_repo=repo,
        usage_service=usage_service or AsyncMock(),
        executor=Mock(),
    )
    return service, repo


@pytest.mark.asyncio
async def test_check_resumability_failed_only() -> None:
    service, _ = _create_test_service()

    # Execution status PENDING or PASSED should fail check_resumability
    record = _create_record(status=ExecutionStatus.PENDING)
    is_res = await service.check_resumability(record)
    assert is_res is False

    record = _create_record(status=ExecutionStatus.PASSED)
    is_res = await service.check_resumability(record)
    assert is_res is False


@pytest.mark.asyncio
async def test_check_resumability_allows_zero_outputs() -> None:
    usage_mock = AsyncMock()
    service, repo = _create_test_service(usage_service=usage_mock)
    usage_mock.check_quota.return_value = True

    step_id = "step_0dfb0101e4714c58bb0d4b430b4b81e3"
    wf = _create_workflow(steps=[StepRule(id=step_id, task_blueprint="b1")])
    await repo.save_workflow(wf)

    step_state = ExecutionStepState(id=step_id, label="Step 1", status=ExecutionStatus.FAILED)
    record = _create_record(
        step_states={step_id: step_state},
        execution_trace=[TraceEvent(step_name="inputs", event_type="input", content={})],
    )

    is_res = await service.check_resumability(record)
    assert is_res is True


@pytest.mark.asyncio
async def test_check_resumability_allows_sys_render_virtual_steps() -> None:
    usage_mock = AsyncMock()
    service, repo = _create_test_service(usage_service=usage_mock)
    usage_mock.check_quota.return_value = True

    step_id = "step_0dfb0101e4714c58bb0d4b430b4b81e3"
    wf = _create_workflow(steps=[StepRule(id=step_id, task_blueprint="b1")])
    await repo.save_workflow(wf)

    step_state = ExecutionStepState(id=step_id, label="Step 1", status=ExecutionStatus.FAILED)
    virtual_state = ExecutionStepState(id="sys_render_prof_1", label="Render", status=ExecutionStatus.PASSED)
    record = _create_record(
        step_states={step_id: step_state, "sys_render_prof_1": virtual_state},
    )

    is_res = await service.check_resumability(record)
    assert is_res is True


@pytest.mark.asyncio
async def test_check_resumability_structural_mismatch() -> None:
    service, repo = _create_test_service()

    step_id1 = "step_0dfb0101e4714c58bb0d4b430b4b81e3"
    step_id2 = "step_7bf3ddc4ad2043918f087e2d67019602"
    wf = _create_workflow(
        steps=[
            StepRule(id=step_id1, task_blueprint="b1"),
            StepRule(id=step_id2, task_blueprint="b2"),
        ]
    )
    await repo.save_workflow(wf)

    step_state1 = ExecutionStepState(id=step_id1, label="Step 1", status=ExecutionStatus.FAILED)
    record = _create_record(
        step_states={step_id1: step_state1},
        execution_trace=[TraceEvent(step_name=step_id1, event_type="output", content={})],
    )

    is_res = await service.check_resumability(record)
    assert is_res is False


@pytest.mark.asyncio
async def test_check_resumability_workflow_version_drift() -> None:
    service, repo = _create_test_service()

    step_id = "step_0dfb0101e4714c58bb0d4b430b4b81e3"
    wf = _create_workflow(version=2, steps=[StepRule(id=step_id, task_blueprint="b1")])
    await repo.save_workflow(wf)

    step_state = ExecutionStepState(id=step_id, label="Step 1", status=ExecutionStatus.FAILED)
    record = _create_record(
        workflow_version=1,
        step_states={step_id: step_state},
        execution_trace=[TraceEvent(step_name=step_id, event_type="output", content={})],
    )

    is_res = await service.check_resumability(record)
    assert is_res is False


@pytest.mark.asyncio
async def test_check_resumability_quota_exceeded() -> None:
    usage_mock = AsyncMock()
    service, repo = _create_test_service(usage_service=usage_mock)
    usage_mock.check_quota.return_value = False

    step_id = "step_0dfb0101e4714c58bb0d4b430b4b81e3"
    wf = _create_workflow(steps=[StepRule(id=step_id, task_blueprint="b1")])
    await repo.save_workflow(wf)

    step_state = ExecutionStepState(id=step_id, label="Step 1", status=ExecutionStatus.FAILED)
    record = _create_record(
        organization_id="org_1",
        step_states={step_id: step_state},
        execution_trace=[TraceEvent(step_name=step_id, event_type="output", content={})],
    )

    is_res = await service.check_resumability(record)
    assert is_res is False
    usage_mock.check_quota.assert_called_once_with("org_1")


@pytest.mark.asyncio
async def test_check_resumability_successful_resumption() -> None:
    usage_mock = AsyncMock()
    service, repo = _create_test_service(usage_service=usage_mock)
    usage_mock.check_quota.return_value = True

    step_id = "step_0dfb0101e4714c58bb0d4b430b4b81e3"
    wf = _create_workflow(steps=[StepRule(id=step_id, task_blueprint="b1")])
    await repo.save_workflow(wf)

    step_state = ExecutionStepState(id=step_id, label="Step 1", status=ExecutionStatus.FAILED)
    record = _create_record(
        organization_id="org_1",
        step_states={step_id: step_state},
        execution_trace=[TraceEvent(step_name=step_id, event_type="output", content={})],
    )

    is_res = await service.check_resumability(record)
    assert is_res is True


@pytest.mark.asyncio
async def test_resume_execution_firewall_denied() -> None:
    service, repo = _create_test_service()

    record = _create_record(
        execution_id="exe_0195f3a0000070018111111111111111",
        status=ExecutionStatus.PASSED,
        organization_id="org_1",
        created_by="u2",
    )
    await repo.save_execution(record)

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")
    arq_pool = AsyncMock()

    with pytest.raises(AppException) as exc_info:
        await service.resume_execution(
            initiator=initiator, execution_id="exe_0195f3a0000070018111111111111111", arq_pool=arq_pool
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == "UNRESUMABLE_STATE_ERROR"
    assert "cannot be resumed due to unresumable state" in exc_info.value.message


@pytest.mark.asyncio
async def test_check_resumability_missing_step_in_step_states_returns_false() -> None:
    """ISTQB Negative: Missing workflow step from step_states returns False."""
    service, repo = _create_test_service()

    step_id = "step_0dfb0101e4714c58bb0d4b430b4b81e3"
    wf = _create_workflow(steps=[StepRule(id=step_id, task_blueprint="b1")])
    await repo.save_workflow(wf)

    record = _create_record(step_states={})
    is_res = await service.check_resumability(record)
    assert is_res is False


@pytest.mark.asyncio
async def test_resumption_invalidates_passed_step_when_input_merkle_hash_drifts() -> None:
    """Verify resume_execution and bootstrap_workflow_execution_state invalidate drifted PASSED steps and dependents."""
    usage_mock = AsyncMock()
    usage_mock.check_quota.return_value = True
    service, repo = _create_test_service(usage_service=usage_mock)

    blk_1 = PersonaPromptBlock(
        id="blk_0195f3a0000070018111222233334444",
        slug="persona_step_1",
        label=I18nText(translations={"en": "Persona 1", "fi": "Persoona 1"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.EXECUTION_PERSONA,
        type=BlockDataType.INSTRUCTION,
        role_enforcement="Static instruction for step 1.",
    )
    blk_2_v1 = PersonaPromptBlock(
        id="blk_0195f3a0000070028222333344445555",
        slug="persona_step_2",
        label=I18nText(translations={"en": "Persona 2", "fi": "Persoona 2"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.EXECUTION_PERSONA,
        type=BlockDataType.INSTRUCTION,
        role_enforcement="Original instruction for step 2.",
    )
    await repo.create_prompt_block(blk_1)
    await repo.create_prompt_block(blk_2_v1)

    bp_1 = Step(
        id="stp_0195f3a0000070018111222233334444",
        slug="bp_1",
        name=I18nText(translations={"en": "Step 1", "fi": "Vaihe 1"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        type=StepType.LLM,
        engine_type=EngineType.PROMPT,
        cognitive_tier=CognitiveTier.FAST,
        execution_persona_block_id=blk_1.id,
        extraction_protocol_block_id=blk_1.id,
        criteria_block_ids=[blk_1.id],
        mcp_tool_params={},
    )
    bp_2 = Step(
        id="stp_0195f3a0000070028222333344445555",
        slug="bp_2",
        name=I18nText(translations={"en": "Step 2", "fi": "Vaihe 2"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        type=StepType.LLM,
        engine_type=EngineType.PROMPT,
        cognitive_tier=CognitiveTier.FAST,
        execution_persona_block_id=blk_2_v1.id,
        extraction_protocol_block_id=blk_2_v1.id,
        criteria_block_ids=[blk_2_v1.id],
        mcp_tool_params={},
    )
    bp_3 = Step(
        id="stp_0195f3a0000070038333444455556666",
        slug="bp_3",
        name=I18nText(translations={"en": "Step 3", "fi": "Vaihe 3"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        type=StepType.LOGIC,
        hook="custom_logic_hook",
        engine_type=EngineType.SYNTHESIS,
        mcp_tool_params={},
    )
    repo.set_step(bp_1)
    repo.set_step(bp_2)
    repo.set_step(bp_3)

    step_1_id = "stp_0195f3a00000700a8aaa111122223333"
    step_2_id = "stp_0195f3a00000700b8bbb222233334444"
    step_3_id = "stp_0195f3a00000700c8ccc333344445555"
    rule_1 = StepRule(id=step_1_id, task_blueprint=bp_1.id, depends_on=[])
    rule_2 = StepRule(id=step_2_id, task_blueprint=bp_2.id, depends_on=[step_1_id])
    rule_3 = StepRule(id=step_3_id, task_blueprint=bp_3.id, depends_on=[step_2_id])

    wf = _create_workflow(steps=[rule_1, rule_2, rule_3])
    await repo.save_workflow(wf)

    base_rec = _create_record(status=ExecutionStatus.FAILED)
    hash_1 = compute_step_input_merkle_hash(
        step_rule=rule_1,
        step_def=bp_1,
        raw_inputs=base_rec.raw_inputs,
        blocks_by_id={blk_1.id: blk_1, blk_2_v1.id: blk_2_v1},
        upstream_hashes={},
    )
    hash_2_old = compute_step_input_merkle_hash(
        step_rule=rule_2,
        step_def=bp_2,
        raw_inputs=base_rec.raw_inputs,
        blocks_by_id={blk_1.id: blk_1, blk_2_v1.id: blk_2_v1},
        upstream_hashes={step_1_id: hash_1},
    )
    hash_3_old = compute_step_input_merkle_hash(
        step_rule=rule_3,
        step_def=bp_3,
        raw_inputs=base_rec.raw_inputs,
        blocks_by_id={blk_1.id: blk_1, blk_2_v1.id: blk_2_v1},
        upstream_hashes={step_1_id: hash_1, step_2_id: hash_2_old},
    )

    state_1 = ExecutionStepState(id=step_1_id, label="Step 1", status=ExecutionStatus.PASSED, input_merkle_hash=hash_1)
    state_2 = ExecutionStepState(
        id=step_2_id, label="Step 2", status=ExecutionStatus.PASSED, input_merkle_hash=hash_2_old
    )
    state_3 = ExecutionStepState(
        id=step_3_id, label="Step 3", status=ExecutionStatus.PASSED, input_merkle_hash=hash_3_old
    )
    record = _create_record(
        status=ExecutionStatus.FAILED,
        step_states={step_1_id: state_1, step_2_id: state_2, step_3_id: state_3},
        execution_trace=[TraceEvent(step_name="inputs", event_type="input", content={})],
    ).model_copy(update={"steps": [state_1, state_2, state_3]})
    await repo.save_execution(record)

    # Mutate step_2's prompt block so step_2's current Merkle hash drifts while step_1's hash remains valid
    blk_2_v2 = blk_2_v1.model_copy(update={"role_enforcement": "Modified instruction for step 2 causing Merkle drift."})
    await repo.update_prompt_block(blk_2_v2.id, blk_2_v2)

    initiator = TokenData(id="usr_1", role=UserRole.ADMIN, organization_id="org_1")
    arq_pool = AsyncMock()
    resumed = await service.resume_execution(initiator=initiator, execution_id=record.id, arq_pool=arq_pool)

    assert resumed.status == ExecutionStatus.RUNNING
    assert resumed.step_states[step_1_id].status == ExecutionStatus.PASSED
    assert resumed.step_states[step_1_id].input_merkle_hash == hash_1
    assert resumed.step_states[step_2_id].status == ExecutionStatus.PENDING
    assert resumed.step_states[step_2_id].input_merkle_hash is None
    assert resumed.step_states[step_3_id].status == ExecutionStatus.PENDING
    assert resumed.step_states[step_3_id].input_merkle_hash is None

    # Verify bootstrap_workflow_execution_state also enforces the exact same Merkle drift invalidation
    await repo.save_execution(record)
    deps = StrategyDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=None,
    )
    bootstrapped = await bootstrap_workflow_execution_state(
        execution_id=record.id,
        workflow=wf,
        raw_inputs=record.raw_inputs,
        deps=deps,
    )
    assert bootstrapped.exec_record.step_states[step_1_id].status == ExecutionStatus.PASSED
    assert bootstrapped.exec_record.step_states[step_2_id].status == ExecutionStatus.PENDING
    assert bootstrapped.exec_record.step_states[step_3_id].status == ExecutionStatus.PENDING
