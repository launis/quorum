from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStepState
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
from backend_v2.models.state import TraceEvent
from backend_v2.services.execution import ExecutionService
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _create_workflow(
    workflow_id: str = "wor_1234567890abcdef",
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
        model_registry_id="sys_e26807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=steps or [],
    )


def _create_record(
    execution_id: str = "exe_1234567890abcdef",
    workflow_id: str = "wor_1234567890abcdef",
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
        output_profile_id="prf_0123456789abcdef",
        active_profile_id="prf_0123456789abcdef",
        step_states=step_states or {},
        execution_trace=execution_trace or [],
        profile_syntheses={"prf_0123456789abcdef": RenderedSynthesisCache()},
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
        execution_id="exe_1111111111111111",
        status=ExecutionStatus.PASSED,
        organization_id="org_1",
        created_by="u2",
    )
    await repo.save_execution(record)

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")
    arq_pool = AsyncMock()

    with pytest.raises(AppException) as exc_info:
        await service.resume_execution(initiator=initiator, execution_id="exe_1111111111111111", arq_pool=arq_pool)

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
