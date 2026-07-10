from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import (
    ExecutionRecord,
    ExecutionStatus,
    StepRule,
    Workflow,
)
from backend_v2.services.execution import ExecutionService


@pytest.mark.asyncio
async def test_check_resumability_failed_only() -> None:
    # Service and mock initializations
    repo_mock = AsyncMock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=Mock(),
    )

    # Execution status PENDING or COMPLETED should fail check_resumability
    record = Mock(spec=ExecutionRecord)
    record.status = ExecutionStatus.PENDING

    # Milestone 3, Rule 1: Resumable only in FAILED status
    is_res = await service.check_resumability(record)
    assert is_res is False

    record.status = ExecutionStatus.PASSED
    is_res = await service.check_resumability(record)
    assert is_res is False


@pytest.mark.asyncio
async def test_check_resumability_allows_zero_outputs() -> None:
    repo_mock = AsyncMock()
    usage_mock = AsyncMock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=usage_mock,
        executor=Mock(),
    )

    usage_mock.check_quota.return_value = True

    # Execution trace lacking event_type == "output" SHOULD be resumable (e.g. crashed on very first node)
    record = Mock(spec=ExecutionRecord)
    record.status = ExecutionStatus.FAILED
    record.workflow_id = "wf_1"
    record.organization_id = "org_1"
    record.metadata = {"workflow_version": 1}
    record.step_states = {"step_0dfb0101e4714c58bb0d4b430b4b81e3": Mock()}
    record.execution_trace = [TraceEvent(step_name="inputs", event_type="input", content={})]

    mock_wf = Mock(spec=Workflow)
    mock_wf.version = 1
    mock_wf.steps = [StepRule(id="step_0dfb0101e4714c58bb0d4b430b4b81e3", task_blueprint="b1")]
    repo_mock.get_workflow_by_id.return_value = {"id": "wf_1"}

    # Resumption is allowed even if no step has completed (zero output events)
    with patch("backend_v2.services.execution.Workflow.model_validate", return_value=mock_wf):
        is_res = await service.check_resumability(record)

    assert is_res is True


@pytest.mark.asyncio
async def test_check_resumability_allows_sys_render_virtual_steps() -> None:
    repo_mock = AsyncMock()
    usage_mock = AsyncMock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=usage_mock,
        executor=Mock(),
    )

    usage_mock.check_quota.return_value = True

    # Execution has a virtual 'sys_render_' step injected by the PDF generator
    record = Mock(spec=ExecutionRecord)
    record.status = ExecutionStatus.FAILED
    record.workflow_id = "wf_1"
    record.organization_id = "org_1"
    record.metadata = {"workflow_version": 1}
    record.step_states = {
        "step_0dfb0101e4714c58bb0d4b430b4b81e3": Mock(),
        "sys_render_prof_1": Mock(),
    }
    record.execution_trace = []

    # But the active blueprint only has the original DAG step
    mock_wf = Mock(spec=Workflow)
    mock_wf.version = 1
    mock_wf.steps = [StepRule(id="step_0dfb0101e4714c58bb0d4b430b4b81e3", task_blueprint="b1")]
    repo_mock.get_workflow_by_id.return_value = {"id": "wf_1"}

    with patch("backend_v2.services.execution.Workflow.model_validate", return_value=mock_wf):
        is_res = await service.check_resumability(record)

    # Must be resumable even with the virtual step present
    assert is_res is True


@pytest.mark.asyncio
async def test_check_resumability_structural_mismatch() -> None:
    repo_mock = AsyncMock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=Mock(),
    )

    # Execution with active workflow having restructured/different Step IDs
    record = Mock(spec=ExecutionRecord)
    record.status = ExecutionStatus.FAILED
    record.workflow_id = "wf_1"
    record.metadata = {}
    record.execution_trace = [
        TraceEvent(step_name="step_0dfb0101e4714c58bb0d4b430b4b81e3", event_type="output", content={})
    ]

    # Exec states keys: step_0dfb0101e4714c58bb0d4b430b4b81e3
    record.step_states = {"step_0dfb0101e4714c58bb0d4b430b4b81e3": Mock()}

    # Workflow in DB has step_0dfb0101e4714c58bb0d4b430b4b81e3 and step_7bf3ddc4ad2043918f087e2d67019602
    mock_wf = Mock(spec=Workflow)
    mock_wf.steps = [
        StepRule(id="step_0dfb0101e4714c58bb0d4b430b4b81e3", task_blueprint="b1"),
        StepRule(id="step_7bf3ddc4ad2043918f087e2d67019602", task_blueprint="b2"),
    ]
    repo_mock.get_workflow_by_id.return_value = {"id": "wf_1"}

    # Milestone 3, Rule 3: Step ID mismatch fails resumability check
    with patch("backend_v2.services.execution.Workflow.model_validate", return_value=mock_wf):
        is_res = await service.check_resumability(record)

    assert is_res is False


@pytest.mark.asyncio
async def test_check_resumability_workflow_version_drift() -> None:
    repo_mock = AsyncMock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=Mock(),
    )

    # Execution started under version 1, but workflow in DB is now version 2
    record = Mock(spec=ExecutionRecord)
    record.status = ExecutionStatus.FAILED
    record.workflow_id = "wf_1"
    record.metadata = {"workflow_version": 1}
    record.execution_trace = [
        TraceEvent(step_name="step_0dfb0101e4714c58bb0d4b430b4b81e3", event_type="output", content={})
    ]
    record.step_states = {"step_0dfb0101e4714c58bb0d4b430b4b81e3": Mock()}

    mock_wf = Mock(spec=Workflow)
    mock_wf.version = 2
    mock_wf.steps = [StepRule(id="step_0dfb0101e4714c58bb0d4b430b4b81e3", task_blueprint="b1")]
    repo_mock.get_workflow_by_id.return_value = {"id": "wf_1"}

    # Milestone 3, Rule 3: Workflow version drift fails resumability check
    with patch("backend_v2.services.execution.Workflow.model_validate", return_value=mock_wf):
        is_res = await service.check_resumability(record)

    assert is_res is False


@pytest.mark.asyncio
async def test_check_resumability_quota_exceeded() -> None:
    repo_mock = AsyncMock()
    usage_mock = AsyncMock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=usage_mock,
        executor=Mock(),
    )

    # Quota check returns False
    usage_mock.check_quota.return_value = False

    record = Mock(spec=ExecutionRecord)
    record.status = ExecutionStatus.FAILED
    record.workflow_id = "wf_1"
    record.organization_id = "org_1"
    record.metadata = {"workflow_version": 1}
    record.execution_trace = [
        TraceEvent(step_name="step_0dfb0101e4714c58bb0d4b430b4b81e3", event_type="output", content={})
    ]
    record.step_states = {"step_0dfb0101e4714c58bb0d4b430b4b81e3": Mock()}

    mock_wf = Mock(spec=Workflow)
    mock_wf.version = 1
    mock_wf.steps = [StepRule(id="step_0dfb0101e4714c58bb0d4b430b4b81e3", task_blueprint="b1")]
    repo_mock.get_workflow_by_id.return_value = {"id": "wf_1"}

    # Milestone 3, Rule 4: Quota exceeded blocks resumption
    with patch("backend_v2.services.execution.Workflow.model_validate", return_value=mock_wf):
        is_res = await service.check_resumability(record)

    assert is_res is False
    usage_mock.check_quota.assert_called_once_with("org_1")


@pytest.mark.asyncio
async def test_check_resumability_successful_resumption() -> None:
    repo_mock = AsyncMock()
    usage_mock = AsyncMock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=usage_mock,
        executor=Mock(),
    )

    # Quota check returns True
    usage_mock.check_quota.return_value = True

    record = Mock(spec=ExecutionRecord)
    record.status = ExecutionStatus.FAILED
    record.workflow_id = "wf_1"
    record.organization_id = "org_1"
    record.metadata = {"workflow_version": 1}
    record.execution_trace = [
        TraceEvent(step_name="step_0dfb0101e4714c58bb0d4b430b4b81e3", event_type="output", content={})
    ]
    record.step_states = {"step_0dfb0101e4714c58bb0d4b430b4b81e3": Mock()}

    mock_wf = Mock(spec=Workflow)
    mock_wf.version = 1
    mock_wf.steps = [StepRule(id="step_0dfb0101e4714c58bb0d4b430b4b81e3", task_blueprint="b1")]
    repo_mock.get_workflow_by_id.return_value = {"id": "wf_1"}

    # Perfect scenario, everything matches and succeeds
    with patch("backend_v2.services.execution.Workflow.model_validate", return_value=mock_wf):
        is_res = await service.check_resumability(record)

    assert is_res is True


@pytest.mark.asyncio
async def test_resume_execution_firewall_denied() -> None:
    repo_mock = AsyncMock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=Mock(),
    )

    # Unresumable record (e.g. status COMPLETED)
    record = Mock(spec=ExecutionRecord)
    record.id = "exe_1"
    record.status = ExecutionStatus.PASSED
    record.execution_trace = []  # Empty trace
    record.organization_id = "org_1"
    record.created_by = "u2"

    repo_mock.get_execution.return_value = record

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")
    arq_pool = AsyncMock()

    # Resumption fails at safety boundary with UNRESUMABLE_STATE_ERROR
    with pytest.raises(AppException) as exc_info:
        await service.resume_execution(initiator=initiator, execution_id="exe_1", arq_pool=arq_pool)

    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == "UNRESUMABLE_STATE_ERROR"
    assert "cannot be resumed due to unresumable state" in exc_info.value.message
