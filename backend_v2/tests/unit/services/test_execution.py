from unittest.mock import AsyncMock, Mock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.v2_core import ExecutionRecord, ExecutionStatus, FrozenContext, WorkflowInputs
from backend_v2.services.execution import ExecutionService, create_execution_record


def test_create_execution_record_factory_success() -> None:
    frozen_context = FrozenContext()
    raw_inputs = WorkflowInputs()

    record = create_execution_record(
        execution_id="exe_1234567890abcdef",
        workflow_id="wf_1",
        raw_inputs=raw_inputs,
        frozen_context=frozen_context,
        source_identity_manifest={},
        output_profile_id="prof_1",
    )

    assert record.id == "exe_1234567890abcdef"
    assert record.workflow_id == "wf_1"
    assert record.status == ExecutionStatus.PENDING
    assert record.output_profile_id == "prof_1"
    assert isinstance(record.frozen_context, FrozenContext)
    assert isinstance(record.raw_inputs, WorkflowInputs)


def test_create_execution_record_factory_fail_fast() -> None:
    frozen_context = FrozenContext()
    raw_inputs = WorkflowInputs()

    # Pass an invalid ID to trigger validation error
    with pytest.raises(AppException) as exc_info:
        create_execution_record(
            execution_id="invalid id with spaces",
            workflow_id="wf_1",
            raw_inputs=raw_inputs,
            frozen_context=frozen_context,
            source_identity_manifest={},
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "ExecutionRecord creation failed" in exc_info.value.message


@pytest.mark.asyncio
async def test_resume_execution_fails_fast_on_invalid_state() -> None:
    repo_mock = AsyncMock()
    executor_mock = Mock()
    arq_pool = AsyncMock()

    # Setup mock to return an already running execution (invalid for resume)
    mock_record = Mock(spec=ExecutionRecord)
    mock_record.status = ExecutionStatus.PENDING
    mock_record.execution_trace = []
    mock_record.model_copy.return_value = mock_record
    repo_mock.get_execution.return_value = mock_record

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )  # noqa: E501
    initiator = TokenData(id="u1", role=UserRole.ROOT)  # Bypasses auth checks

    with pytest.raises(AppException) as exc_info:
        await service.resume_execution(initiator=initiator, execution_id="exe_123", arq_pool=arq_pool)

    assert "cannot be resumed due to unresumable state" in exc_info.value.message
    assert exc_info.value.details["error_code"] == "UNRESUMABLE_STATE_ERROR"


@pytest.mark.asyncio
async def test_list_executions_admin_sees_all() -> None:
    repo_mock = AsyncMock()
    executor_mock = Mock()

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )

    mock_record1 = Mock(spec=ExecutionRecord)
    mock_record1.organization_id = "org_1"
    mock_record1.status = ExecutionStatus.PASSED
    mock_record1.execution_trace = []
    mock_record1.model_copy.return_value = mock_record1

    mock_record2 = Mock(spec=ExecutionRecord)
    mock_record2.organization_id = "org_2"
    mock_record2.status = ExecutionStatus.PASSED
    mock_record2.execution_trace = []
    mock_record2.model_copy.return_value = mock_record2

    repo_mock.get_all_executions.return_value = [mock_record1, mock_record2]

    initiator = TokenData(id="u1", role=UserRole.ROOT)

    from unittest.mock import patch

    with patch.object(service, "check_resumability", return_value=False):
        results = await service.list_executions(initiator=initiator)

    assert len(results) == 2


@pytest.mark.asyncio
async def test_list_executions_tenant_sees_own() -> None:
    repo_mock = AsyncMock()
    executor_mock = Mock()

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )

    mock_record1 = Mock(spec=ExecutionRecord)
    mock_record1.organization_id = "org_1"
    mock_record1.created_by = "u2"
    mock_record1.status = ExecutionStatus.PASSED
    mock_record1.execution_trace = []
    mock_record1.model_copy.return_value = mock_record1

    mock_record2 = Mock(spec=ExecutionRecord)
    mock_record2.organization_id = "org_2"
    mock_record2.created_by = "u3"
    mock_record2.status = ExecutionStatus.PASSED
    mock_record2.execution_trace = []
    mock_record2.model_copy.return_value = mock_record2

    repo_mock.get_all_executions.return_value = [mock_record1, mock_record2]

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    from unittest.mock import patch

    with patch.object(service, "check_resumability", return_value=False):
        results = await service.list_executions(initiator=initiator)

    assert len(results) == 1
    assert results[0].organization_id == "org_1"


@pytest.mark.asyncio
async def test_get_execution_admin_sees_any() -> None:
    repo_mock = AsyncMock()
    executor_mock = Mock()

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )

    mock_record = Mock(spec=ExecutionRecord)
    mock_record.organization_id = "org_other"
    mock_record.status = ExecutionStatus.PASSED
    mock_record.execution_trace = []
    mock_record.model_copy.return_value = mock_record
    repo_mock.get_execution.return_value = mock_record

    initiator = TokenData(id="u1", role=UserRole.ROOT)

    from unittest.mock import patch

    with patch.object(service, "check_resumability", return_value=False):
        result = await service.get_execution(initiator=initiator, execution_id="exe_1")

    assert result.organization_id == "org_other"


@pytest.mark.asyncio
async def test_get_execution_tenant_sees_own() -> None:
    repo_mock = AsyncMock()
    executor_mock = Mock()

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )

    mock_record = Mock(spec=ExecutionRecord)
    mock_record.organization_id = "org_1"
    mock_record.created_by = "u2"
    mock_record.status = ExecutionStatus.PASSED
    mock_record.execution_trace = []
    mock_record.model_copy.return_value = mock_record
    repo_mock.get_execution.return_value = mock_record

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    from unittest.mock import patch

    with patch.object(service, "check_resumability", return_value=False):
        result = await service.get_execution(initiator=initiator, execution_id="exe_1")

    assert result.organization_id == "org_1"


@pytest.mark.asyncio
async def test_delete_execution_tenant_deletes_own() -> None:
    repo_mock = AsyncMock()
    executor_mock = Mock()

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )

    mock_record = Mock(spec=ExecutionRecord)
    mock_record.organization_id = "org_1"
    mock_record.created_by = "u2"
    repo_mock.get_execution.return_value = mock_record
    repo_mock.delete_execution.return_value = True

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")
    result = await service.delete_execution(initiator=initiator, execution_id="exe_1")

    assert result is True


@pytest.mark.asyncio
async def test_start_execution_success() -> None:
    repo_mock = AsyncMock()
    executor_mock = Mock()
    arq_pool = AsyncMock()

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )

    # Mock quota
    service.usage_service.check_quota.return_value = True  # type: ignore[attr-defined]

    # Mock workflow to get default_profile_id
    from backend_v2.models.v2_core import Workflow

    mock_wf = Mock(spec=Workflow)
    mock_wf.id = "wf_1"
    mock_wf.version = 1
    mock_wf.default_profile_id = "prof_1"
    mock_wf.output_profiles = {"prof_1": Mock()}
    mock_wf.expected_inputs = []
    mock_wf.steps = []
    mock_wf.organization_id = "org_1"

    repo_mock.get_workflow_by_id.return_value = {"id": "wf_1"}

    from backend_v2.models.v2_core import ExecutionCreate, WorkflowInputs

    payload = ExecutionCreate(
        workflow_id="wf_1",
        raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        target_locale="en",
        profile_id="prof_1",
        matrix_sampling_strategy=0,
    )

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    from unittest.mock import patch

    with patch("backend_v2.services.execution.Workflow.model_validate", return_value=mock_wf):
        result = await service.start_execution(initiator=initiator, payload=payload, arq_pool=arq_pool)

    assert result.workflow_id == "wf_1"
    assert result.status == ExecutionStatus.PENDING
    arq_pool.enqueue_job.assert_called_once()


@pytest.mark.asyncio
async def test_render_execution_flat() -> None:
    repo_mock = AsyncMock()
    executor_mock = Mock()
    arq_pool = AsyncMock()

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )

    mock_record = Mock(spec=ExecutionRecord)
    mock_record.status = ExecutionStatus.PASSED
    mock_record.organization_id = "org_1"
    mock_record.created_by = "u2"
    mock_record.workflow_id = "wf_1"
    mock_record.execution_trace = []
    mock_record.model_copy.return_value = mock_record
    repo_mock.get_execution.return_value = mock_record

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    from unittest.mock import patch

    mock_dto = Mock()
    with patch("backend_v2.services.execution.BlueprintTransformer") as mock_transformer_class:
        mock_transformer = AsyncMock()
        mock_transformer.build_report_dto.return_value = mock_dto
        mock_transformer_class.return_value = mock_transformer

        with patch("backend_v2.services.execution.FlatFileService.flatten_results", return_value={"flat": "data"}):
            data, mime, filename = await service.render_execution(
                initiator=initiator,
                execution_id="exe_1",
                format_type="flat",
                profile_id="prof_1",
                accept_language="en",
                arq_pool=arq_pool,
            )

    assert data == {"flat": "data"}
    assert mime == "application/json"
    assert filename is None


@pytest.mark.asyncio
async def test_render_execution_json() -> None:
    repo_mock = AsyncMock()
    executor_mock = Mock()
    arq_pool = AsyncMock()

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )

    mock_record = Mock(spec=ExecutionRecord)
    mock_record.status = ExecutionStatus.PASSED
    mock_record.organization_id = "org_1"
    mock_record.metadata = {}
    mock_record.created_by = "u2"
    mock_record.workflow_id = "wf_1"
    mock_record.profile_syntheses = {"prof_1": Mock()}
    mock_record.model_copy.return_value = mock_record
    repo_mock.get_execution.return_value = mock_record

    repo_mock.get_workflow_by_id.return_value = {
        "id": "wf_1",
        "default_profile_id": "prof_1",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "slug": "test",
        "version": 1,
        "name": {},
        "description": {},
        "steps": [],
    }

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    from unittest.mock import patch

    # Mocking BlueprintTransformer
    mock_dto = Mock()
    mock_dto.evaluative_matrices = []
    mock_dto.informational_matrices = []
    mock_dto.layouts = []
    mock_dto.has_warning = False
    mock_dto.model_dump.return_value = {"workflow_id": "wf_1", "profile_id": "prof_1"}

    with patch("backend_v2.services.execution.BlueprintTransformer") as mock_transformer_class:
        mock_transformer = AsyncMock()
        mock_transformer.build_report_dto.return_value = mock_dto
        mock_transformer_class.return_value = mock_transformer

        with patch(
            "backend_v2.services.execution.Workflow.model_validate", return_value=Mock(default_profile_id="prof_1")
        ):
            data, mime, filename = await service.render_execution(
                initiator=initiator,
                execution_id="exe_1",
                format_type="json",
                profile_id="prof_1",
                accept_language=None,
                arq_pool=arq_pool,
            )

    assert data["workflow_id"] == "wf_1"
    assert data["profile_id"] == "prof_1"
    assert mime == "application/json"
    assert filename is None


@pytest.mark.asyncio
async def test_enqueue_pdf_generation_success() -> None:
    repo_mock = AsyncMock()
    executor_mock = Mock()
    arq_pool = AsyncMock()

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )

    mock_record = Mock(spec=ExecutionRecord)
    mock_record.id = "exe_1"
    mock_record.workflow_id = "wf_1"
    mock_record.status = ExecutionStatus.PASSED
    mock_record.step_states = {}
    mock_record.execution_trace = []
    mock_record.organization_id = "org_1"
    mock_record.created_by = "u2"

    repo_mock.get_execution.return_value = mock_record

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    await service.enqueue_pdf_generation(
        initiator=initiator, execution_id="exe_1", accept_language="fi", profile_id="prof_1", arq_pool=arq_pool
    )

    repo_mock.update_execution.assert_called_once()
    arq_pool.enqueue_job.assert_called_once_with(
        "generate_pdf_job",
        execution_id="exe_1",
        accept_language="fi",
        profile_id="prof_1",
        custom_preface_md=None,
        local_time_str=None,
    )


@pytest.mark.asyncio
async def test_override_atom_success() -> None:
    from unittest.mock import patch

    from backend_v2.models.dtos.lightweight_matrix import ReasoningStepDTO
    from backend_v2.models.enums import VisualIntent
    from backend_v2.models.v2_core import (
        ExecutionStepState,
        HumanOverrideRequest,
        ScorecardAtomDTO,
    )

    repo_mock = AsyncMock()
    executor_mock = Mock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )

    # Initialize a clean ExecutionRecord
    record = create_execution_record(
        execution_id="exe_1234567890abcdef",
        workflow_id="wf_1",
        raw_inputs=WorkflowInputs(),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        output_profile_id="prof_1",
    )

    # Setup step_states with a ScorecardAtomDTO
    atom = ScorecardAtomDTO(
        atom_id="tda_1",
        level=1,
        level_name="T1",
        claim_label="Claim label",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="",
            step_2_scan_source="",
            step_3_evaluate_anti_patterns="",
            step_4_final_conclusion="",
        ),
        status=ExecutionStatus.FAILED,
        semantic_reasoning="",
        contextual_override=False,
        structural_location="N/A",
        chart_display_label="N/A",
        visual_intent=VisualIntent.NEUTRAL,
    )

    step_state = ExecutionStepState(
        id="sr_1_step",
        label="Label",
        status="PASSED",
        scorecard_atoms={"tda_1": atom},
    )

    record = record.model_copy(
        update={"step_states": {"sr_1": step_state}, "organization_id": "org_1", "created_by": "u2"}
    )

    repo_mock.get_execution.return_value = record

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")
    payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED,
        reason="Override reason",
        evidence_quotes=[],
    )

    with patch("backend_v2.services.execution.recalculate", new_callable=AsyncMock) as mock_recalc:
        await service.override_atom(
            initiator=initiator,
            execution_id="exe_1234567890abcdef",
            atom_id="tda_1",
            payload=payload,
        )
        mock_recalc.assert_called_once()

    repo_mock.update_execution.assert_called_once()
    repo_mock.append_trace_event.assert_called_once()


@pytest.mark.asyncio
async def test_get_execution_export_bytes_success() -> None:
    repo_mock = AsyncMock()
    executor_mock = Mock()

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )

    initiator = TokenData(id="u1", role=UserRole.ROOT)

    mock_record = Mock(spec=ExecutionRecord)
    mock_record.frozen_context = FrozenContext()
    mock_record.frozen_context_storage_path = None
    mock_record.status = ExecutionStatus.PASSED
    mock_record.execution_trace_storage_path = None
    mock_record.execution_trace = []
    mock_record.step_states = {}
    mock_record.organization_id = "org_1"
    mock_record.model_copy.return_value = mock_record

    repo_mock.get_execution.return_value = mock_record

    bytes_out, filename = await service.get_execution_export_bytes(initiator=initiator, execution_id="exe_123")

    assert filename == "execution_export_exe_123.xlsx"
    assert len(bytes_out) > 0
    assert bytes_out.startswith(b"PK")


@pytest.mark.asyncio
async def test_get_execution_export_bytes_quotes_bug() -> None:
    repo_mock = AsyncMock()
    executor_mock = Mock()

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )

    initiator = TokenData(id="u1", role=UserRole.ROOT)

    mock_record = Mock(spec=ExecutionRecord)
    mock_record.frozen_context = FrozenContext()
    mock_record.frozen_context_storage_path = None
    mock_record.status = ExecutionStatus.PASSED
    mock_record.execution_trace_storage_path = None

    # Simulate a trace event with a list of dicts in exact_quotes
    from backend_v2.models.state import TraceEvent

    mock_record.execution_trace = [
        TraceEvent(
            event_type="output",
            step_name="step_1",
            content={
                "type": "ATOM_COMPLETED",
                "atom_id": "test_atom_1",
                "status": "PASS",
                "exact_quotes": [{"text": "Found quote", "source_alias": "src1"}],
            },
        )
    ]
    mock_record.step_states = {}
    mock_record.organization_id = "org_1"
    mock_record.model_copy.return_value = mock_record

    repo_mock.get_execution.return_value = mock_record

    bytes_out, filename = await service.get_execution_export_bytes(initiator=initiator, execution_id="exe_123")
    assert filename == "execution_export_exe_123.xlsx"
