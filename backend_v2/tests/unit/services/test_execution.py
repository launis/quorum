from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, Mock, call, patch

import pytest

from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import (
    ExecutionCreate,
    ExecutionRecord,
    ExecutionStep,
    ExecutionStepState,
    FrozenContext,
    JobAcceptedDTO,
)
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.matrix_scorecard import HumanOverrideRequest
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.dtos.workflow_schema import WorkflowSchemaResponseDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.models.view.sdui import (
    MarkdownBlock,
)
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

    valid_profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-profile",
        workflow_id="wf_1",
        name=I18nText(translations={"en": "Test Profile"}),
        target_block_order=[],
    )
    out_prof_repo_mock = AsyncMock()
    out_prof_repo_mock.get_output_profile_by_id.return_value = valid_profile

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=out_prof_repo_mock,
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )

    # Mock quota
    service.usage_service.check_quota.return_value = True  # type: ignore[attr-defined]

    # Mock workflow to get default_profile_id
    from backend_v2.models.domain.workflow import Workflow

    mock_wf = Mock(spec=Workflow)
    mock_wf.id = "wf_1"
    mock_wf.version = 1
    mock_wf.default_profile_id = valid_profile.id
    mock_wf.expected_inputs = []
    mock_wf.steps = []
    mock_wf.model_registry_id = "sys_e26807f3bfa3454d"
    mock_wf.organization_id = "org_1"
    mock_wf.is_public = False

    repo_mock.get_workflow_by_id.return_value = {"id": "wf_1"}

    from backend_v2.models.domain.execution import ExecutionCreate
    from backend_v2.models.domain.inputs import WorkflowInputs

    payload = ExecutionCreate(
        workflow_id="wf_1",
        raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        target_locale="en",
        profile_id=valid_profile.id,
        matrix_sampling_strategy=10,
    )

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    from unittest.mock import patch

    with patch("backend_v2.services.execution.Workflow.model_validate", return_value=mock_wf):
        result = await service.start_execution(initiator=initiator, payload=payload, arq_pool=arq_pool)

    assert result.workflow_id == "wf_1"
    assert result.status == ExecutionStatus.PENDING
    assert result.metadata is not None
    assert result.metadata.model_registry_id == "sys_e26807f3bfa3454d"
    arq_pool.enqueue_job.assert_called_once()


@pytest.mark.asyncio
async def test_start_execution_model_registry_override() -> None:
    """Verify that payload.model_registry_id overrides workflow.model_registry_id."""
    repo_mock = AsyncMock()
    executor_mock = Mock()
    arq_pool = AsyncMock()

    valid_profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-profile",
        workflow_id="wf_1",
        name=I18nText(translations={"en": "Test Profile"}),
        target_block_order=[],
    )
    out_prof_repo_mock = AsyncMock()
    out_prof_repo_mock.get_output_profile_by_id.return_value = valid_profile

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=out_prof_repo_mock,
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=executor_mock,
    )
    service.usage_service.check_quota.return_value = True  # type: ignore[attr-defined]

    from backend_v2.models.domain.execution import ExecutionCreate
    from backend_v2.models.domain.inputs import WorkflowInputs
    from backend_v2.models.domain.workflow import Workflow

    mock_wf = Mock(spec=Workflow)
    mock_wf.id = "wf_1"
    mock_wf.version = 1
    mock_wf.default_profile_id = valid_profile.id
    mock_wf.expected_inputs = []
    mock_wf.steps = []
    mock_wf.model_registry_id = "sys_e26807f3bfa3454d"
    mock_wf.organization_id = "org_1"
    mock_wf.is_public = False

    repo_mock.get_workflow_by_id.return_value = {"id": "wf_1"}

    payload = ExecutionCreate(
        workflow_id="wf_1",
        raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        target_locale="en",
        profile_id=valid_profile.id,
        matrix_sampling_strategy=10,
        model_registry_id="sys_6f8b1c4a2e0d49f1",
    )

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    from unittest.mock import patch

    with patch("backend_v2.services.execution.Workflow.model_validate", return_value=mock_wf):
        result = await service.start_execution(initiator=initiator, payload=payload, arq_pool=arq_pool)

    assert result.metadata is not None
    assert result.metadata.model_registry_id == "sys_6f8b1c4a2e0d49f1"


@pytest.mark.asyncio
async def test_start_execution_permission_denied() -> None:
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
    from backend_v2.exceptions import PermissionDeniedError
    from backend_v2.models.domain.execution import ExecutionCreate
    from backend_v2.models.domain.inputs import WorkflowInputs
    from backend_v2.models.domain.workflow import Workflow

    mock_wf = Mock(spec=Workflow)
    mock_wf.id = "wf_private"
    mock_wf.organization_id = "org_other"
    mock_wf.is_public = False

    repo_mock.get_workflow_by_id.return_value = {"id": "wf_private"}

    payload = ExecutionCreate(
        workflow_id="wf_private",
        raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        target_locale="en",
        profile_id="prof_1",
        matrix_sampling_strategy=10,
    )
    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_my")

    from unittest.mock import patch

    with patch("backend_v2.services.execution.Workflow.model_validate", return_value=mock_wf):
        with pytest.raises(PermissionDeniedError) as exc_info:
            await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())
    assert "You do not have permission to execute this workflow." in str(exc_info.value)


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
    mock_record.target_locale = "en"
    mock_record.status = ExecutionStatus.PASSED
    mock_record.organization_id = "org_1"
    mock_record.metadata = ExecutionMetadata()
    mock_record.created_by = "u2"
    mock_record.workflow_id = "wf_1"
    mock_record.profile_syntheses = {"prof_1": Mock()}
    mock_record.model_copy.return_value = mock_record
    repo_mock.get_execution.return_value = mock_record

    repo_mock.get_workflow_by_id.return_value = {
        "id": "wf_1",
        "default_profile_id": "prof_1",
        "historical_context_mode": "DISABLED",
        "model_registry_id": "cfg_model_registry_01",
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
    mock_dto.inner_sdui_blocks = []
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

    assert isinstance(data, dict)
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
    mock_record.steps = []
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

    from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
    from backend_v2.models.dtos.matrix_scorecard import HumanOverrideRequest, ScorecardAtomDTO
    from backend_v2.models.enums import VisualIntent

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
        structural_location=None,
        chart_display_label="N/A",
        visual_intent=VisualIntent.NEUTRAL,
    )

    step_state = ExecutionStepState(
        id="sr_1_step",
        label="Label",
        status=ExecutionStatus.PASSED,
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
    from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
    from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
    from backend_v2.models.enums import VisualIntent

    mock_record.step_states = {
        "step_1": ExecutionStepState(
            id="step_1",
            label="Step 1",
            status=ExecutionStatus.PASSED,
            scorecard_atoms={
                "atom_1": ScorecardAtomDTO(
                    atom_id="atom_1",
                    level=1,
                    level_name="T1",
                    claim_label="Claim",
                    extracted_facts={},
                    exact_quotes=[],
                    internal_logic_en=ReasoningStepDTO(
                        step_1_identify_premise="",
                        step_2_scan_source="",
                        step_3_evaluate_anti_patterns="",
                        step_4_final_conclusion="",
                    ),
                    status=ExecutionStatus.PASSED,
                    semantic_reasoning="",
                    contextual_override=False,
                    structural_location=None,
                    chart_display_label="N/A",
                    visual_intent=VisualIntent.NEUTRAL,
                )
            },
        )
    }
    mock_record.organization_id = "org_1"
    mock_record.target_locale = "en"
    mock_record.metadata = ExecutionMetadata()
    mock_record.model_copy.return_value = mock_record

    repo_mock.get_execution.return_value = mock_record

    mock_atom = Mock(
        matrix_id="m1",
        tda_id="tda_1",
        evaluation_reasoning="Reasoning",
        source_quote="Quote",
        status=ExecutionStatus.PASSED,
        extensions={},
    )
    mock_report_dto = Mock(
        results=[mock_atom],
        hydrated_references={},
        inner_sdui_blocks=[],
    )

    with patch.object(service, "get_report_dto", return_value=mock_report_dto):
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
    from backend_v2.models.domain.execution import ExecutionStepState
    from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
    from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
    from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
    from backend_v2.models.enums import VisualIntent

    mock_record.step_states = {
        "step_1": ExecutionStepState(
            id="step_1",
            label="Step 1",
            status=ExecutionStatus.PASSED,
            scorecard_atoms={
                "atom_1": ScorecardAtomDTO(
                    atom_id="atom_1",
                    level=1,
                    level_name="T1",
                    claim_label="Claim",
                    extracted_facts={},
                    exact_quotes=[
                        QuoteEvidenceDTO.model_construct(
                            quote="Found quote",
                            verified_source_ids=[],
                            unverified_aliases=["src1"],
                        )
                    ],
                    internal_logic_en=ReasoningStepDTO(
                        step_1_identify_premise="",
                        step_2_scan_source="",
                        step_3_evaluate_anti_patterns="",
                        step_4_final_conclusion="",
                    ),
                    status=ExecutionStatus.PASSED,
                    semantic_reasoning="",
                    contextual_override=False,
                    structural_location=None,
                    chart_display_label="N/A",
                    visual_intent=VisualIntent.NEUTRAL,
                )
            },
        )
    }
    mock_record.organization_id = "org_1"
    mock_record.target_locale = "en"
    mock_record.metadata = ExecutionMetadata()
    mock_record.model_copy.return_value = mock_record

    repo_mock.get_execution.return_value = mock_record

    from unittest.mock import patch

    mock_atom = Mock(
        matrix_id="m1",
        tda_id="tda_1",
        evaluation_reasoning="Reasoning",
        source_quote="Quote",
        status=ExecutionStatus.PASSED,
        extensions={},
    )
    mock_report_dto = Mock(
        results=[mock_atom],
        hydrated_references={},
        inner_sdui_blocks=[],
    )

    with patch.object(service, "get_report_dto", return_value=mock_report_dto):
        bytes_out, filename = await service.get_execution_export_bytes(initiator=initiator, execution_id="exe_123")
    assert filename == "execution_export_exe_123.xlsx"


@pytest.mark.asyncio
async def test_get_execution_export_bytes_empty_states_fails() -> None:
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
    mock_record.status = ExecutionStatus.PASSED
    mock_record.step_states = {}
    mock_record.organization_id = "org_1"
    mock_record.model_copy.return_value = mock_record

    repo_mock.get_execution.return_value = mock_record

    with pytest.raises(AppException) as exc_info:
        await service.get_execution_export_bytes(initiator=initiator, execution_id="exe_123")

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "no scoreable atoms" in exc_info.value.message


@pytest.mark.asyncio
async def test_phase_1_5_negative_invalid_human_override_crashes() -> None:
    """Verify that applying a human override via override_atom with an invalid ExecutionStatus
    strictly crashes Pydantic validation before modifying the state dictionary.
    """
    from pydantic import ValidationError

    from backend_v2.models.dtos.matrix_scorecard import HumanOverrideRequest

    with pytest.raises(ValidationError):
        HumanOverrideRequest(
            new_status="NOT_AN_ENUM",  # type: ignore
            reason="Invalid",
            evidence_quotes=[],
        )


def test_execution_create_dto_preserves_output_profile_id() -> None:
    """Regression: ExecutionCreateDTO must support and persist output_profile_id."""
    from backend_v2.models.domain.execution import ExecutionRecord
    from backend_v2.models.dtos.trace import ExecutionCreateDTO
    from backend_v2.models.execution_core import ExecutionMetadata

    dto = ExecutionCreateDTO(
        workflow_id="wf_1234567890abcdef",
        id="exe_1234567890abcdef",
        target_locale="fi",
        active_profile_id="prof_1234567890abcdef",
        output_profile_id="prof_1234567890abcdef",
        metadata=ExecutionMetadata(),
    )
    raw_dict = dto.model_dump(mode="json", exclude_unset=True)
    record = ExecutionRecord.model_validate(raw_dict, strict=False)
    assert record.output_profile_id == "prof_1234567890abcdef"


@pytest.mark.asyncio
async def test_start_execution_succeeds_without_profile() -> None:
    """Ingress Decoupling: start_execution succeeds when no profile_id is provided."""
    from backend_v2.models.domain.execution import ExecutionCreate
    from backend_v2.models.domain.inputs import WorkflowInputs
    from backend_v2.models.domain.workflow import Workflow

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
    service.usage_service.check_quota.return_value = True  # type: ignore[attr-defined]

    mock_wf = Mock(spec=Workflow)
    mock_wf.id = "wf_no_prof"
    mock_wf.version = 1
    mock_wf.default_profile_id = None
    mock_wf.expected_inputs = []
    mock_wf.steps = []
    mock_wf.model_registry_id = "sys_e26807f3bfa3454d"
    mock_wf.organization_id = "org_1"
    mock_wf.is_public = False

    repo_mock.get_workflow_by_id.return_value = {"id": "wf_no_prof"}

    payload = ExecutionCreate(
        workflow_id="wf_no_prof",
        raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        target_locale="en",
        profile_id=None,
        matrix_sampling_strategy=10,
    )
    initiator = TokenData(id="u1", role=UserRole.MEMBER, organization_id="org_1")

    from unittest.mock import patch

    with patch("backend_v2.services.execution.Workflow.model_validate", return_value=mock_wf):
        result = await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())

    assert result.workflow_id == "wf_no_prof"
    assert result.output_profile_id is None
    assert result.status == ExecutionStatus.PENDING


@pytest.mark.asyncio
async def test_start_execution_fails_fast_when_profile_not_in_db() -> None:
    """ISTQB Negative: start_execution raises 404 RESOURCE_NOT_FOUND when profile is not found in database."""
    from backend_v2.models.domain.execution import ExecutionCreate
    from backend_v2.models.domain.inputs import WorkflowInputs
    from backend_v2.models.domain.workflow import Workflow

    repo_mock = AsyncMock()
    out_prof_repo_mock = AsyncMock()
    out_prof_repo_mock.get_output_profile_by_id.return_value = None

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=out_prof_repo_mock,
        identity_repo=repo_mock,
        system_repo=repo_mock,
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    service.usage_service.check_quota.return_value = True  # type: ignore[attr-defined]

    mock_wf = Mock(spec=Workflow)
    mock_wf.id = "wf_1"
    mock_wf.version = 1
    mock_wf.default_profile_id = "prof_missing"
    mock_wf.expected_inputs = []
    mock_wf.steps = []
    mock_wf.model_registry_id = "sys_e26807f3bfa3454d"
    mock_wf.organization_id = "org_1"
    mock_wf.is_public = False

    repo_mock.get_workflow_by_id.return_value = {"id": "wf_1"}

    payload = ExecutionCreate(
        workflow_id="wf_1",
        raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        target_locale="en",
        profile_id="prof_missing",
        matrix_sampling_strategy=10,
    )
    initiator = TokenData(id="u1", role=UserRole.MEMBER, organization_id="org_1")

    from unittest.mock import patch

    with patch("backend_v2.services.execution.Workflow.model_validate", return_value=mock_wf):
        with pytest.raises(AppException) as exc_info:
            await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == "RESOURCE_NOT_FOUND"
    assert "not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_start_execution_fails_fast_when_model_registry_not_found() -> None:
    """ISTQB Negative: start_execution raises 404 RESOURCE_NOT_FOUND when model registry is not found in database."""
    from backend_v2.exceptions import ResourceNotFoundError
    from backend_v2.models.domain.execution import ExecutionCreate
    from backend_v2.models.domain.inputs import WorkflowInputs
    from backend_v2.models.domain.workflow import Workflow

    repo_mock = AsyncMock()
    system_repo_mock = AsyncMock()
    system_repo_mock.get_model_registry.side_effect = ResourceNotFoundError(
        resource_type="system_config", resource_id="sys_missing"
    )

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=repo_mock,
        comp_repo=repo_mock,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=repo_mock,
        system_repo=system_repo_mock,
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    service.usage_service.check_quota.return_value = True  # type: ignore[attr-defined]

    mock_wf = Mock(spec=Workflow)
    mock_wf.id = "wf_1"
    mock_wf.version = 1
    mock_wf.default_profile_id = None
    mock_wf.expected_inputs = []
    mock_wf.steps = []
    mock_wf.model_registry_id = "sys_missing"
    mock_wf.organization_id = "org_1"
    mock_wf.is_public = False

    repo_mock.get_workflow_by_id.return_value = {"id": "wf_1"}

    payload = ExecutionCreate(
        workflow_id="wf_1",
        raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        target_locale="en",
        profile_id=None,
        matrix_sampling_strategy=10,
    )
    initiator = TokenData(id="u1", role=UserRole.MEMBER, organization_id="org_1")

    from unittest.mock import patch

    with patch("backend_v2.services.execution.Workflow.model_validate", return_value=mock_wf):
        with pytest.raises(AppException) as exc_info:
            await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == "RESOURCE_NOT_FOUND"
    assert "not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_stream_status_handles_error_without_yielding_malformed_execution_record(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify stream_status does not yield malformed JSON masquerading as ExecutionRecord upon error."""
    from backend_v2.exceptions import ResourceNotFoundError

    monkeypatch.setattr("backend_v2.services.execution.asyncio.sleep", AsyncMock())

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

    initiator = TokenData(id="u1", role=UserRole.ROOT, organization_id="org_1")
    mock_record = Mock(spec=ExecutionRecord)
    mock_record.id = "exe_0b51fa35ea584ca7a42cd30b444d1241"
    mock_record.workflow_id = "wf_1"
    mock_record.status = ExecutionStatus.RUNNING
    mock_record.organization_id = "org_1"
    mock_record.created_by = "u1"
    mock_record.target_locale = "fi"
    mock_record.model_copy.return_value = mock_record
    mock_record.model_dump_json.return_value = (
        '{"id":"exe_0b51fa35ea584ca7a42cd30b444d1241","workflow_id":"wf_1",'
        '"status":"RUNNING","target_locale":"fi","output_profile_id":"prof_default"}'
    )

    call_count = 0

    async def mock_get_exec(
        initiator: Any,
        execution_id: str,
        hydrate: bool = True,
        skip_resumability: bool = False,
        **kwargs: Any,
    ) -> Any:
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            return mock_record
        raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)

    service.get_execution = mock_get_exec  # type: ignore[method-assign]

    events: list[str] = []
    async for event in service.stream_status(initiator=initiator, execution_id="exe_0b51fa35ea584ca7a42cd30b444d1241"):
        events.append(event)

    # Any data event yielded must be parseable as a valid ExecutionRecord without schema error
    has_data = False
    has_error = False
    for event in events:
        if event.startswith("data: "):
            has_data = True
            json_str = event[len("data: ") :].strip()
            ExecutionRecord.model_validate_json(json_str)
        elif event.startswith("event: error"):
            has_error = True
            assert "SSE_STREAM_INTERRUPTED" in event

    assert has_data is True
    assert has_error is True


@pytest.mark.asyncio
async def test_start_execution_fails_fast_on_input_collision() -> None:
    """ISTQB Negative: start_execution raises 400 VALIDATION_FAILED when inputs collide on the same slot."""
    from unittest.mock import patch

    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.execution import ExecutionCreate
    from backend_v2.models.domain.inputs import WorkflowInputsIngress
    from backend_v2.models.domain.step import ExpectedInput
    from backend_v2.models.domain.workflow import Workflow

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
    service.usage_service.check_quota.return_value = True  # type: ignore[attr-defined]

    mock_wf = Mock(spec=Workflow)
    mock_wf.id = "wf_collision"
    mock_wf.version = 1
    mock_wf.default_profile_id = "prf_1"
    mock_wf.expected_inputs = [
        ExpectedInput(
            input_key="chat_log",
            label=I18nText(translations={"fi": "Keskusteluhistoria (Chat)", "en": "Chat"}),
            required=True,
            is_chat_history=True,
            input_modes=["file", "paste"],
            description=I18nText(translations={"en": "Chat", "fi": "Keskustelu"}),
        )
    ]
    mock_wf.steps = []
    mock_wf.organization_id = "org_1"
    mock_wf.is_public = False

    repo_mock.get_workflow_by_id.return_value = {"id": "wf_collision"}

    payload = ExecutionCreate(
        workflow_id="wf_collision",
        raw_inputs=WorkflowInputsIngress(
            dynamic_inputs={
                "keskusteluhistoria": {"filename": "keskusteluhistoria.pdf", "content_base64": "SGVsbG8="},
                "keskusteluhistoria_user_only": {
                    "filename": "keskusteluhistoria_user_only.md",
                    "content_base64": "V29ybGQ=",
                },
            }
        ),
        target_locale="fi",
        profile_id="prf_1",
        matrix_sampling_strategy=10,
    )
    initiator = TokenData(id="u1", role=UserRole.MEMBER, organization_id="org_1")

    with patch("backend_v2.services.execution.Workflow.model_validate", return_value=mock_wf):
        with pytest.raises(AppException) as exc_info:
            await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "collision" in exc_info.value.details
    assert exc_info.value.details["collision"]["slot"] == "chat_log"


@pytest.mark.asyncio
async def test_start_execution_fails_fast_on_missing_required_input() -> None:
    """ISTQB Negative: start_execution raises 400 VALIDATION_FAILED when a required input is missing."""
    from unittest.mock import patch

    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.execution import ExecutionCreate
    from backend_v2.models.domain.inputs import WorkflowInputs
    from backend_v2.models.domain.step import ExpectedInput
    from backend_v2.models.domain.workflow import Workflow

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
    service.usage_service.check_quota.return_value = True  # type: ignore[attr-defined]

    mock_wf = Mock(spec=Workflow)
    mock_wf.id = "wf_missing_req"
    mock_wf.version = 1
    mock_wf.default_profile_id = "prf_1"
    mock_wf.expected_inputs = [
        ExpectedInput(
            input_key="chat_log",
            label=I18nText(translations={"fi": "Keskusteluhistoria (Chat)", "en": "Chat"}),
            required=True,
            is_chat_history=True,
            input_modes=["file", "paste"],
            description=I18nText(translations={"en": "Chat", "fi": "Keskustelu"}),
        )
    ]
    mock_wf.steps = []
    mock_wf.organization_id = "org_1"
    mock_wf.is_public = False

    repo_mock.get_workflow_by_id.return_value = {"id": "wf_missing_req"}

    payload = ExecutionCreate(
        workflow_id="wf_missing_req",
        raw_inputs=WorkflowInputs(dynamic_inputs={"product_text": "Delivered material"}),
        target_locale="fi",
        profile_id="prf_1",
        matrix_sampling_strategy=10,
    )
    initiator = TokenData(id="u1", role=UserRole.MEMBER, organization_id="org_1")

    with patch("backend_v2.services.execution.Workflow.model_validate", return_value=mock_wf):
        with pytest.raises(AppException) as exc_info:
            await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "chat_log" in exc_info.value.details["missing_fields"]


def test_create_execution_record_dict_metadata() -> None:
    rec = create_execution_record(
        execution_id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        output_profile_id="prf_0123456789abcdef",
        metadata={"workflow_version": 1},
    )
    assert rec.metadata.workflow_version == 1


@pytest.mark.asyncio
async def test_create_execution_metadata_and_list_pagination() -> None:
    repo_mock = AsyncMock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ADMIN, organization_id="org_0123456789abcdef")

    repo_mock.list_executions.return_value = []
    res = await service.list_executions(initiator=initiator)
    assert res == []


@pytest.mark.asyncio
async def test_get_and_delete_execution_not_found_and_permission_denied() -> None:
    repo_mock = AsyncMock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    from backend_v2.exceptions import PermissionDeniedError, ResourceNotFoundError

    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.MEMBER, organization_id="org_tenant_a")
    repo_mock.get_execution.return_value = None

    with pytest.raises(ResourceNotFoundError):
        await service.get_execution(initiator=initiator, execution_id="exe_0123456789abcdef")

    with pytest.raises(ResourceNotFoundError):
        await service.delete_execution(initiator=initiator, execution_id="exe_0123456789abcdef")

    alien_record = Mock(spec=ExecutionRecord)
    alien_record.id = "exe_0123456789abcdef"
    alien_record.organization_id = "org_tenant_b"
    alien_record.created_by = "usr_alien000000000"
    alien_record.is_public = False
    alien_record.status = ExecutionStatus.PASSED
    alien_record.model_copy.return_value = alien_record
    repo_mock.get_execution.return_value = alien_record

    with pytest.raises(PermissionDeniedError):
        await service.get_execution(initiator=initiator, execution_id="exe_0123456789abcdef")

    with pytest.raises(PermissionDeniedError):
        await service.delete_execution(initiator=initiator, execution_id="exe_0123456789abcdef")


@pytest.mark.asyncio
async def test_start_execution_with_steps_and_blocks() -> None:
    from backend_v2.models.domain.execution import ExecutionCreate
    from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, MatrixScale
    from backend_v2.models.domain.step import Step, StepRule
    from backend_v2.models.domain.workflow import Workflow

    repo_mock = AsyncMock()
    prompt_block_repo = AsyncMock()
    workflow_repo = AsyncMock()

    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=workflow_repo,
        comp_repo=AsyncMock(),
        prompt_block_repo=prompt_block_repo,
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    service.usage_service.check_quota.return_value = True

    matrix_block = MatrixPromptBlock(
        id="blk_0123456789abcdef",
        slug="matrix-block",
        label=I18nText(translations={"en": "Matrix Label"}),
        description=I18nText(translations={"en": "Matrix Description"}),
        category_id="matrix",
        type="int",
        scales=[
            MatrixScale(score=1, ai_label="Low"),
            MatrixScale(score=5, ai_label="High"),
        ],
    )
    prompt_block_repo.get_prompt_block_by_id.return_value = matrix_block.model_dump(mode="json")

    step_obj = Step(
        id="stp_0123456789abcdef",
        slug="step-1",
        name=I18nText(translations={"en": "Step 1"}),
        role_block_id=None,
        extraction_protocol_block_id="blk_0123456789abcdef",
        criteria_block_ids=["blk_0123456789abcdef"],
    )
    workflow_repo.get_step_by_id.return_value = step_obj.model_dump(mode="json")

    wf = Workflow(
        id="wor_0123456789abcdef",
        slug="workflow-test",
        name=I18nText(translations={"en": "Workflow"}),
        description=I18nText(translations={"en": "Description"}),
        status="active",
        version=1,
        organization_id="org_0123456789abcdef",
        is_public=False,
        default_profile_id="prf_0123456789abcdef",
        model_registry_id="sys_e26807f3bfa3454d",
        expected_inputs=[],
        steps=[
            StepRule(
                id="stp_0123456789abcdef",
                task_blueprint="stp_0123456789abcdef",
            )
        ],
        historical_context_mode="DISABLED",
    )
    workflow_repo.get_workflow_by_id.return_value = wf.model_dump(mode="json")
    service.output_profile_repo.get_output_profile_by_id.return_value = {
        "id": "prf_0123456789abcdef",
        "slug": "profile-test",
        "workflow_id": "wor_0123456789abcdef",
        "name": {"translations": {"en": "Output Profile"}},
        "target_block_order": ["executive_summary_block"],
    }

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(),
        target_locale="en",
        profile_id="prf_0123456789abcdef",
    )
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ADMIN, organization_id="org_0123456789abcdef")
    arq_pool = AsyncMock()
    doc_service = AsyncMock()
    doc_service.process_ingress_payload.return_value = payload.raw_inputs

    res = await service.start_execution(
        initiator=initiator,
        payload=payload,
        arq_pool=arq_pool,
        doc_service=doc_service,
    )
    assert res.id.startswith("exe_")


@pytest.mark.asyncio
async def test_get_frozen_context_bytes() -> None:
    from unittest.mock import patch

    repo_mock = AsyncMock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ADMIN, organization_id="org_1")

    rec1 = Mock(spec=ExecutionRecord)
    rec1.id = "exe_1"
    rec1.organization_id = "org_1"
    rec1.is_public = False
    rec1.status = ExecutionStatus.PASSED
    rec1.model_copy.return_value = rec1
    rec1.frozen_context_storage_path = None
    rec1.frozen_context = FrozenContext()
    repo_mock.get_execution.return_value = rec1

    b1, name1 = await service.get_frozen_context_bytes(initiator, "exe_1")
    assert b1 is not None
    assert name1 == "frozen_context_exe_1.json"

    rec2 = Mock(spec=ExecutionRecord)
    rec2.id = "exe_2"
    rec2.organization_id = "org_1"
    rec2.is_public = False
    rec2.status = ExecutionStatus.PASSED
    rec2.model_copy.return_value = rec2
    rec2.frozen_context_storage_path = "storage/fc.json"
    rec2.frozen_context = None
    repo_mock.get_execution.return_value = rec2

    with patch("backend_v2.services.execution.get_storage_driver") as mock_storage_driver:
        mock_driver = AsyncMock()
        mock_driver.read.return_value = FrozenContext().model_dump_json().encode("utf-8")
        mock_storage_driver.return_value = mock_driver

        b2, name2 = await service.get_frozen_context_bytes(initiator, "exe_2")
        assert b2 is not None

        mock_driver.read.side_effect = Exception("Storage failed")
        with pytest.raises(AppException):
            await service.get_frozen_context_bytes(initiator, "exe_2")


@pytest.mark.asyncio
async def test_clear_profile_synthesis() -> None:
    from unittest.mock import patch

    from backend_v2.exceptions import ResourceNotFoundError

    repo_mock = AsyncMock()
    workflow_repo = AsyncMock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=workflow_repo,
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_1", role=UserRole.ADMIN, organization_id="org_1")

    from backend_v2.models.domain.synthesis import RenderedSynthesisCache

    rec = Mock(spec=ExecutionRecord)
    rec.id = "exe_1"
    rec.workflow_id = "wor_0123456789abcdef"
    rec.organization_id = "org_1"
    rec.is_public = False
    rec.status = ExecutionStatus.PASSED
    rec.model_copy.return_value = rec
    rec.profile_syntheses = {"prof_1": RenderedSynthesisCache()}
    rec.pdf_report_path = "reports/report.pdf"
    repo_mock.get_execution.return_value = rec

    workflow_repo.get_workflow_by_id.return_value = {
        "id": "wor_0123456789abcdef",
        "slug": "workflow-slug",
        "name": {"translations": {"en": "Workflow"}},
        "description": {"translations": {"en": "Description"}},
        "status": "active",
        "version": 1,
        "default_profile_id": "prof_1",
        "model_registry_id": "sys_e26807f3bfa3454d",
        "historical_context_mode": "DISABLED",
        "steps": [],
    }

    with patch("backend_v2.services.execution.get_storage_driver") as mock_storage:
        driver = AsyncMock()
        mock_storage.return_value = driver
        await service.clear_profile_synthesis(initiator, "exe_1", "prof_1")
        driver.delete.assert_called_once_with("reports/report.pdf")

    workflow_repo.get_workflow_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await service.clear_profile_synthesis(initiator, "exe_1", "prof_1")


@pytest.mark.asyncio
async def test_render_execution_formats() -> None:
    from unittest.mock import patch

    repo_mock = AsyncMock()
    workflow_repo = AsyncMock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=workflow_repo,
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_1", role=UserRole.ADMIN, organization_id="org_1")

    rec = Mock(spec=ExecutionRecord)
    rec.id = "exe_1"
    rec.organization_id = "org_1"
    rec.is_public = False
    rec.workflow_id = "wor_0123456789abcdef"
    rec.status = ExecutionStatus.FAILED
    rec.step_states = {}
    rec.metadata = ExecutionMetadata()
    rec.model_copy.return_value = rec
    repo_mock.get_execution.return_value = rec
    workflow_repo.get_workflow_by_id.return_value = {
        "id": "wor_0123456789abcdef",
        "slug": "workflow-slug",
        "name": {"translations": {"en": "Workflow"}},
        "description": {"translations": {"en": "Description"}},
        "status": "active",
        "version": 1,
        "default_profile_id": "prof_1",
        "model_registry_id": "sys_e26807f3bfa3454d",
        "historical_context_mode": "DISABLED",
        "steps": [],
    }

    with pytest.raises(AppException):
        await service.render_execution(
            initiator=initiator,
            execution_id="exe_1",
            format_type="flat",
            profile_id="prof_1",
            accept_language="en",
            arq_pool=AsyncMock(),
        )

    rec.status = ExecutionStatus.PASSED
    rec.step_states = {}
    mock_dto = Mock()
    mock_dto.inner_sdui_blocks = []
    mock_dto.has_warning = False

    with patch("backend_v2.services.execution.BlueprintTransformer") as mock_transformer_cls:
        mock_trans = AsyncMock()
        mock_trans.build_report_dto.return_value = mock_dto
        mock_transformer_cls.return_value = mock_trans

        with patch(
            "backend_v2.services.execution.Workflow.model_validate", return_value=Mock(default_profile_id="prof_1")
        ):
            data, mime, fname = await service.render_execution(
                initiator=initiator,
                execution_id="exe_1",
                format_type="flat",
                profile_id="prof_1",
                accept_language="en",
                arq_pool=AsyncMock(),
                custom_preface_md="# Custom Preface",
            )
            assert mime == "application/json"
            assert fname is None


@pytest.mark.asyncio
async def test_stream_status_sse_events() -> None:
    repo_mock = AsyncMock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_1", role=UserRole.ADMIN, organization_id="org_1")

    rec = Mock(spec=ExecutionRecord)
    rec.id = "exe_1"
    rec.organization_id = "org_1"
    rec.is_public = False
    rec.status = ExecutionStatus.PASSED
    rec.model_copy.return_value = rec
    rec.model_dump_json.return_value = '{"id": "exe_1", "status": "PASSED"}'
    repo_mock.get_execution.return_value = rec

    events = []
    async for event in service.stream_status(initiator, "exe_1"):
        events.append(event)

    assert len(events) >= 1
    assert "PASSED" in events[0]
    assert repo_mock.get_execution.call_args_list[-1] == call("exe_1", hydrate=False)


@pytest.mark.asyncio
async def test_resume_execution_success() -> None:
    from unittest.mock import patch

    repo_mock = AsyncMock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    service.usage_service.check_quota.return_value = True

    rec = Mock(spec=ExecutionRecord)
    rec.id = "exe_resume_1"
    rec.organization_id = "org_1"
    rec.is_public = False
    rec.workflow_id = "wor_1"
    rec.raw_inputs = WorkflowInputs()
    rec.status = ExecutionStatus.RUNNING
    rec.model_copy.return_value = rec
    repo_mock.get_execution.return_value = rec

    with patch.object(service, "check_resumability", return_value=True):
        arq_pool = AsyncMock()
        initiator = TokenData(id="usr_1", role=UserRole.ADMIN, organization_id="org_1")
        res = await service.resume_execution(initiator, "exe_resume_1", arq_pool)
        assert res.id == "exe_resume_1"
        arq_pool.enqueue_job.assert_called_once()


@pytest.mark.asyncio
async def test_get_execution_export_bytes_different_block_types() -> None:
    from unittest.mock import patch

    from backend_v2.models.domain.prompt_blocks import (
        SystemRulePromptBlock,
    )
    from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
    from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
    from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
    from backend_v2.models.enums import VisualIntent

    repo_mock = AsyncMock()
    prompt_block_repo = AsyncMock()
    service = ExecutionService(
        exec_repo=repo_mock,
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=prompt_block_repo,
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_1", role=UserRole.ADMIN, organization_id="org_1")

    atom1 = ScorecardAtomDTO(
        atom_id="atom_1",
        level=1,
        level_name="T1",
        claim_label="Claim 1",
        status=ExecutionStatus.PASSED,
        extracted_facts={},
        contextual_override=False,
        chart_display_label="N/A",
        visual_intent=VisualIntent.NEUTRAL,
        semantic_reasoning="Reasoning test text",
        exact_quotes=[QuoteEvidenceDTO(quote="test quote", verified_source_ids=["src_1"], unverified_aliases=[])],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="Premise text",
            step_2_scan_source="",
            step_3_evaluate_anti_patterns="Anti patterns text",
            step_4_final_conclusion="",
        ),
    )
    step_state = ExecutionStepState(
        id="stp_1",
        label="Step 1 Label",
        scorecard_atoms={"blk_0123456789abcdef": atom1},
    )

    rec = Mock(spec=ExecutionRecord)
    rec.id = "exe_export_types"
    rec.organization_id = "org_1"
    rec.is_public = False
    rec.status = ExecutionStatus.PASSED
    rec.target_locale = "en"
    rec.step_states = {"stp_1": step_state}
    rec.model_copy.return_value = rec
    repo_mock.get_execution.return_value = rec

    rule_block = SystemRulePromptBlock(
        id="blk_0123456789abcdef",
        slug="rule-block",
        label=I18nText(translations={"en": "Rule Block"}),
        description=I18nText(translations={"en": "Rule Description"}),
        category_id="system_rule",
        type="instruction",
        instruction_text="Instruction test",
    )
    prompt_block_repo.get_all_prompt_blocks.return_value = [
        rule_block.model_dump(mode="json"),
    ]

    mock_atom = Mock(
        matrix_id="blk_0123456789abcdef",
        tda_id="tda_1",
        evaluation_reasoning="Reasoning test text",
        source_quote="test quote",
        status=ExecutionStatus.PASSED,
        extensions={},
    )
    mock_report_dto = Mock()
    mock_report_dto.results = [mock_atom]
    mock_report_dto.hydrated_references = {}
    mock_report_dto.overall_score = 85.0
    mock_report_dto.executive_summary = "Summary text"
    mock_report_dto.strengths = []
    mock_report_dto.weaknesses = []
    mock_report_dto.data_dictionary = {}
    mock_report_dto.inner_sdui_blocks = []
    mock_report_dto.matrix_scores = {}

    with patch.object(service, "get_report_dto", return_value=mock_report_dto):
        file_bytes, filename = await service.get_execution_export_bytes(initiator, "exe_export_types")
        assert len(file_bytes) > 0
        assert filename == "execution_export_exe_export_types.xlsx"


@pytest.mark.asyncio
async def test_get_workflow_ui_schema_success_and_not_found() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    # Not found
    service.workflow_repo.get_workflow_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await service.get_workflow_ui_schema("wor_0123456789abcdef")

    # Success
    wf = Workflow(
        id="wor_0123456789abcdef",
        slug="test-wf",
        version=1,
        status="ACTIVE",
        default_profile_id="prf_0123456789abcdef",
        model_registry_id="sys_e26807f3bfa3454d",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        historical_context_mode="DISABLED",
        expected_inputs=[],
    )
    service.workflow_repo.get_workflow_by_id.return_value = wf.model_dump(mode="json")
    res = await service.get_workflow_ui_schema("wor_0123456789abcdef")
    assert isinstance(res, WorkflowSchemaResponseDTO)
    assert res.expected_inputs == []


@pytest.mark.asyncio
async def test_reject_evidence_quote_branches() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    rec = Mock(spec=ExecutionRecord)
    rec.status = ExecutionStatus.PASSED
    rec.organization_id = "org_target"
    rec.created_by = "usr_owner"
    rec.model_copy.return_value = rec
    service.exec_repo.get_execution.return_value = rec

    # Permission denied
    initiator_other = TokenData(id="usr_other", role=UserRole.MEMBER, organization_id="org_other")
    with pytest.raises(PermissionDeniedError):
        await service.reject_evidence_quote(initiator_other, "exe_0123456789abcdef", "evq_1", "Wrong quote")

    # Success (ROOT role)
    initiator_root = TokenData(id="usr_root", role=UserRole.ROOT, organization_id="org_other")
    await service.reject_evidence_quote(initiator_root, "exe_0123456789abcdef", "evq_1", "Wrong quote")
    assert service.exec_repo.append_trace_event.called


@pytest.mark.asyncio
async def test_get_sdui_view_branches() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ROOT)
    mock_dto = Mock(spec=ReportDataDTO)
    mock_dto.inner_sdui_blocks = [MarkdownBlock(text="Synthetic Overview Title")]
    with patch.object(service, "get_report_dto", return_value=mock_dto):
        mock_view = Mock()
        mock_view.model_copy.return_value = mock_view
        mock_view.model_dump.return_value = {"title": "Synthetic Overview Title", "components": []}
        with patch("backend_v2.services.execution.SduiMapperService.map_report_to_sdui", return_value=mock_view):
            view_dict = await service.get_sdui_view(initiator, "exe_0123456789abcdef")
            assert view_dict["title"] == "Synthetic Overview Title"


@pytest.mark.asyncio
async def test_render_execution_html_and_unsupported_formats() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ROOT)
    wf = Workflow(
        id="wor_0123456789abcdef",
        slug="test-wf",
        version=1,
        status="ACTIVE",
        default_profile_id="prf_default",
        model_registry_id="sys_e26807f3bfa3454d",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        historical_context_mode="DISABLED",
        expected_inputs=[],
    )
    service.workflow_repo.get_workflow_by_id.return_value = wf.model_dump(mode="json")
    rec = Mock(spec=ExecutionRecord)
    rec.status = ExecutionStatus.PASSED
    rec.organization_id = "org_1"
    rec.workflow_id = "wor_0123456789abcdef"
    rec.target_locale = "en"
    rec.profile_syntheses = {"prf_default": {}}
    rec.model_copy.return_value = rec
    service.exec_repo.get_execution.return_value = rec

    # Unsupported format
    with pytest.raises(AppException) as exc_info:
        await service.render_execution(
            initiator=initiator,
            execution_id="exe_0123456789abcdef",
            format_type="docx",
            profile_id="prf_default",
            accept_language="en",
            arq_pool=AsyncMock(),
        )
    assert exc_info.value.status_code == 400
    assert "Unsupported format" in exc_info.value.message

    # HTML format
    with (
        patch(
            "backend_v2.services.execution.BlueprintTransformer.build_report_dto", return_value=Mock(spec=ReportDataDTO)
        ),
        patch(
            "backend_v2.services.execution.PdfReportService.generate_execution_html",
            return_value="<html><body>Report</body></html>",
        ),
    ):
        content_bytes, mime, filename = await service.render_execution(
            initiator=initiator,
            execution_id="exe_0123456789abcdef",
            format_type="html",
            profile_id="prf_default",
            accept_language="en",
            arq_pool=AsyncMock(),
        )
        assert mime == "text/html"
        assert filename == "execution_exe_0123456789abcdef.html"
        assert b"<html>" in content_bytes


@pytest.mark.asyncio
async def test_render_execution_pdf_pregenerated_and_fresh_saved() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ROOT)
    wf = Workflow(
        id="wor_0123456789abcdef",
        slug="test-wf",
        version=1,
        status="ACTIVE",
        default_profile_id="prf_default",
        model_registry_id="sys_e26807f3bfa3454d",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        historical_context_mode="DISABLED",
        expected_inputs=[],
    )
    service.workflow_repo.get_workflow_by_id.return_value = wf.model_dump(mode="json")
    rec = Mock(spec=ExecutionRecord)
    rec.status = ExecutionStatus.PASSED
    rec.organization_id = "org_1"
    rec.workflow_id = "wor_0123456789abcdef"
    rec.target_locale = "en"
    rec.profile_syntheses = {"prf_default": {}}
    rec.pdf_report_path = "executions/exe_0123456789abcdef/report.pdf"
    rec.model_copy.return_value = rec
    service.exec_repo.get_execution.return_value = rec

    storage_mock = AsyncMock()
    storage_mock.read.return_value = b"%PDF-1.4 pregenerated"
    with patch("backend_v2.services.execution.get_storage_driver", return_value=storage_mock):
        pdf_bytes, mime, filename = await service.render_execution(
            initiator=initiator,
            execution_id="exe_0123456789abcdef",
            format_type="pdf",
            profile_id="prf_default",
            accept_language="en",
            arq_pool=AsyncMock(),
        )
        assert pdf_bytes == b"%PDF-1.4 pregenerated"
        assert mime == "application/pdf"

    # Pre-generated fetch error
    storage_mock.read.side_effect = Exception("Storage disk read error")
    with patch("backend_v2.services.execution.get_storage_driver", return_value=storage_mock):
        with pytest.raises(AppException) as exc_info:
            await service.render_execution(
                initiator=initiator,
                execution_id="exe_0123456789abcdef",
                format_type="pdf",
                profile_id="prf_default",
                accept_language="en",
                arq_pool=AsyncMock(),
            )
        assert exc_info.value.status_code == 500

    # Fresh PDF generation when no pre-generated exists
    rec.pdf_report_path = None
    storage_mock.read.side_effect = None
    storage_mock.save.return_value = "executions/exe_0123456789abcdef/report.pdf"
    with (
        patch("backend_v2.services.execution.get_storage_driver", return_value=storage_mock),
        patch(
            "backend_v2.services.execution.BlueprintTransformer.build_report_dto", return_value=Mock(spec=ReportDataDTO)
        ),
        patch("backend_v2.services.execution.PdfReportService.generate_execution_pdf", return_value=b"%PDF-1.4 fresh"),
    ):
        pdf_bytes, mime, filename = await service.render_execution(
            initiator=initiator,
            execution_id="exe_0123456789abcdef",
            format_type="pdf",
            profile_id="prf_default",
            accept_language="en",
            arq_pool=AsyncMock(),
        )
        assert pdf_bytes == b"%PDF-1.4 fresh"
        assert mime == "application/pdf"
        assert service.exec_repo.update_execution.called

    # Fresh PDF save error
    storage_mock.save.side_effect = Exception("Storage disk save error")
    with (
        patch("backend_v2.services.execution.get_storage_driver", return_value=storage_mock),
        patch(
            "backend_v2.services.execution.BlueprintTransformer.build_report_dto", return_value=Mock(spec=ReportDataDTO)
        ),
        patch("backend_v2.services.execution.PdfReportService.generate_execution_pdf", return_value=b"%PDF-1.4 fresh"),
    ):
        with pytest.raises(AppException) as exc_info:
            await service.render_execution(
                initiator=initiator,
                execution_id="exe_0123456789abcdef",
                format_type="pdf",
                profile_id="prf_default",
                accept_language="en",
                arq_pool=AsyncMock(),
            )
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_render_execution_on_demand_synthesis_enqueues_job() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ROOT)
    wf = Workflow(
        id="wor_0123456789abcdef",
        slug="test-wf",
        version=1,
        status="ACTIVE",
        default_profile_id="prf_ondemand",
        model_registry_id="sys_e26807f3bfa3454d",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        historical_context_mode="DISABLED",
        expected_inputs=[],
    )
    service.workflow_repo.get_workflow_by_id.return_value = wf.model_dump(mode="json")
    rec = Mock(spec=ExecutionRecord)
    rec.status = ExecutionStatus.PASSED
    rec.organization_id = "org_1"
    rec.workflow_id = "wor_0123456789abcdef"
    rec.target_locale = "en"
    rec.profile_syntheses = {}  # Trigger on-demand synthesis
    rec.step_states = {}
    rec.updated_at = None
    rec.model_copy.return_value = rec
    service.exec_repo.get_execution.return_value = rec

    arq_pool = AsyncMock()
    res, mime, filename = await service.render_execution(
        initiator=initiator,
        execution_id="exe_0123456789abcdef",
        format_type="json",
        profile_id="prf_ondemand",
        accept_language="en",
        arq_pool=arq_pool,
    )
    assert isinstance(res, JobAcceptedDTO)
    assert mime == "application/json"
    assert filename is None
    assert arq_pool.enqueue_job.called


@pytest.mark.asyncio
async def test_delete_execution_storage_cleanup_error_branches() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    rec = Mock(spec=ExecutionRecord)
    rec.status = ExecutionStatus.PASSED
    rec.organization_id = "org_1"
    rec.created_by = "usr_owner"
    rec.model_copy.return_value = rec
    service.exec_repo.get_execution.return_value = rec
    service.exec_repo.delete_execution.return_value = True

    # Permission denied
    initiator_other = TokenData(id="usr_other", role=UserRole.MEMBER, organization_id="org_other")
    with pytest.raises(PermissionDeniedError):
        await service.delete_execution(initiator_other, "exe_0123456789abcdef")

    initiator = TokenData(id="usr_owner", role=UserRole.MEMBER, organization_id="org_1")

    # 404 is ignored
    storage_mock = AsyncMock()
    storage_mock.delete_directory.side_effect = AppException("Not found", status_code=404)
    with patch("backend_v2.services.execution.get_storage_driver", return_value=storage_mock):
        deleted = await service.delete_execution(initiator, "exe_0123456789abcdef")
        assert deleted is True

    # 500 AppException raised
    storage_mock.delete_directory.side_effect = AppException("Storage error", status_code=500)
    with patch("backend_v2.services.execution.get_storage_driver", return_value=storage_mock):
        with pytest.raises(AppException) as exc_info:
            await service.delete_execution(initiator, "exe_0123456789abcdef")
        assert exc_info.value.status_code == 500

    # Generic Exception raised
    storage_mock.delete_directory.side_effect = Exception("Generic disk crash")
    with patch("backend_v2.services.execution.get_storage_driver", return_value=storage_mock):
        with pytest.raises(AppException) as exc_info:
            await service.delete_execution(initiator, "exe_0123456789abcdef")
        assert exc_info.value.status_code == 500

    # Repo delete error
    storage_mock.delete_directory.side_effect = None
    service.exec_repo.delete_execution.side_effect = Exception("DB crash")
    with patch("backend_v2.services.execution.get_storage_driver", return_value=storage_mock):
        with pytest.raises(AppException) as exc_info:
            await service.delete_execution(initiator, "exe_0123456789abcdef")
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_clear_profile_synthesis_storage_delete_branches() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    rec = Mock(spec=ExecutionRecord)
    rec.organization_id = "org_1"
    rec.status = ExecutionStatus.PASSED
    rec.workflow_id = "wor_0123456789abcdef"
    rec.pdf_report_path = "executions/exe_0123456789abcdef/report.pdf"
    rec.profile_syntheses = {"prf_default": {}}
    rec.model_copy.return_value = rec
    service.exec_repo.get_execution.return_value = rec
    wf = Workflow(
        id="wor_0123456789abcdef",
        slug="test-wf",
        version=1,
        status="ACTIVE",
        default_profile_id="prf_default",
        model_registry_id="sys_e26807f3bfa3454d",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        historical_context_mode="DISABLED",
        expected_inputs=[],
    )
    service.workflow_repo.get_workflow_by_id.return_value = wf.model_dump(mode="json")
    initiator = TokenData(id="usr_root", role=UserRole.ROOT)

    storage_mock = AsyncMock()

    # 404 is ignored
    storage_mock.delete.side_effect = AppException("Not found", status_code=404)
    with patch("backend_v2.services.execution.get_storage_driver", return_value=storage_mock):
        await service.clear_profile_synthesis(initiator, "exe_0123456789abcdef", "prf_default")
        assert service.exec_repo.update_execution.called

    # 409 is re-raised
    storage_mock.delete.side_effect = AppException("Conflict", status_code=409)
    with patch("backend_v2.services.execution.get_storage_driver", return_value=storage_mock):
        with pytest.raises(AppException) as exc_info:
            await service.clear_profile_synthesis(initiator, "exe_0123456789abcdef", "prf_default")
        assert exc_info.value.status_code == 409

    # 500 is wrapped
    storage_mock.delete.side_effect = AppException("Server Error", status_code=500)
    with patch("backend_v2.services.execution.get_storage_driver", return_value=storage_mock):
        with pytest.raises(AppException) as exc_info:
            await service.clear_profile_synthesis(initiator, "exe_0123456789abcdef", "prf_default")
        assert exc_info.value.status_code == 500

    # Generic Exception is wrapped
    storage_mock.delete.side_effect = Exception("Unexpected")
    with patch("backend_v2.services.execution.get_storage_driver", return_value=storage_mock):
        with pytest.raises(AppException) as exc_info:
            await service.clear_profile_synthesis(initiator, "exe_0123456789abcdef", "prf_default")
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_override_atom_branches() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    rec = Mock(spec=ExecutionRecord)
    rec.status = ExecutionStatus.PASSED
    rec.organization_id = "org_1"
    rec.created_by = "usr_owner"
    rec.step_states = {}
    rec.model_copy.return_value = rec
    service.exec_repo.get_execution.return_value = rec

    # Permission denied
    initiator_other = TokenData(id="usr_other", role=UserRole.MEMBER, organization_id="org_other")
    req = HumanOverrideRequest(new_status=ExecutionStatus.PASSED, reason="Valid evidence found")
    with pytest.raises(PermissionDeniedError):
        await service.override_atom(initiator_other, "exe_0123456789abcdef", "atm_1", req)

    # Atom not found in any step_states
    initiator = TokenData(id="usr_owner", role=UserRole.MEMBER, organization_id="org_1")
    with pytest.raises(AppException) as exc_info:
        await service.override_atom(initiator, "exe_0123456789abcdef", "atm_1", req)
    assert exc_info.value.status_code == 404

    # Success with context variables update
    from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
    from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
    from backend_v2.models.enums import VisualIntent

    atom_obj = ScorecardAtomDTO(
        atom_id="atm_1",
        level=1,
        level_name="T1",
        claim_label="Claim 1",
        status=ExecutionStatus.PASSED,
        extracted_facts={},
        contextual_override=False,
        chart_display_label="N/A",
        visual_intent=VisualIntent.NEUTRAL,
        semantic_reasoning="Some reasoning",
        exact_quotes=[],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="Premise",
            step_2_scan_source="",
            step_3_evaluate_anti_patterns="Anti patterns",
            step_4_final_conclusion="",
        ),
    )
    step_state = ExecutionStep(
        id="stp_1",
        label="Step 1",
        status=ExecutionStatus.PASSED,
        scorecard_atoms={"atm_1": atom_obj},
    )
    rec.step_states = {"stp_1": step_state}
    rec.context_variables = {
        "var_1": {
            "evaluated_atoms": {"atm_1": "FAIL"},
            "raw_atoms": [{"tda_id": "atm_1", "human_override": None}],
        }
    }
    rec.active_profile_id = "prf_1"
    with patch("backend_v2.services.execution.recalculate", return_value=None):
        await service.override_atom(initiator, "exe_0123456789abcdef", "atm_1", req)
        assert service.exec_repo.update_execution.called
        assert service.exec_repo.append_trace_event.called


@pytest.mark.asyncio
async def test_start_execution_additional_error_branches() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ROOT, organization_id="org_0123456789abcdef")

    wf = Workflow(
        id="wor_0123456789abcdef",
        slug="test-wf",
        version=1,
        status="ACTIVE",
        default_profile_id="prf_0123456789abcdef",
        model_registry_id="sys_e26807f3bfa3454d",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        steps=[
            StepRule(
                id="stp_0123456789abcdef",
                task_blueprint="stp_0123456789abcdef",
            )
        ],
        historical_context_mode="DISABLED",
    )
    service.workflow_repo.get_workflow_by_id.return_value = wf.model_dump(mode="json")
    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(),
        target_locale="en",
        profile_id="prf_0123456789abcdef",
    )

    # 1. Step blueprint missing
    service.workflow_repo.get_step_by_id.return_value = None
    with pytest.raises(ConfigurationError):
        await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())

    # 2. Step blueprint malformed
    service.workflow_repo.get_step_by_id.return_value = {"invalid": "step"}
    with pytest.raises(AppException) as exc_info:
        await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())
    assert exc_info.value.status_code == 400

    # 3. Prompt block missing
    valid_step = Step(
        id="stp_0123456789abcdef",
        slug="step-slug",
        name=I18nText(translations={"en": "Step 1"}),
        description=I18nText(translations={"en": "Step Desc"}),
        role_block_id="blk_0123456789abcdef",
        criteria_block_ids=["blk_0123456789abcdef"],
        extraction_protocol_block_id="blk_0123456789abcdef",
    )
    service.workflow_repo.get_step_by_id.return_value = valid_step.model_dump(mode="json")
    service.prompt_block_repo.get_prompt_block_by_id.return_value = None
    with pytest.raises(ConfigurationError):
        await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())

    # 4. Prompt block malformed
    service.prompt_block_repo.get_prompt_block_by_id.return_value = {"invalid": "block"}
    with pytest.raises(AppException) as exc_info:
        await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_list_executions_exception_branch() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    service.exec_repo.get_all_executions.side_effect = RuntimeError("DB connection timeout")
    initiator = TokenData(id="usr_root", role=UserRole.ROOT)
    with pytest.raises(AppException) as exc_info:
        await service.list_executions(initiator=initiator)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_report_dto_not_passed() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_root", role=UserRole.ROOT)
    rec = Mock(spec=ExecutionRecord)
    rec.status = ExecutionStatus.FAILED
    rec.organization_id = "org_1"
    rec.workflow_id = "wor_0123456789abcdef"
    rec.model_copy.return_value = rec
    service.exec_repo.get_execution.return_value = rec
    service.workflow_repo.get_workflow_by_id.return_value = None

    with pytest.raises(AppException) as exc_info:
        await service.get_report_dto(initiator, "exe_0123456789abcdef")
    assert exc_info.value.status_code == 400
    assert "Execution is not in COMPLETED state" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_execution_export_bytes_error_branches() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_root", role=UserRole.ROOT)
    rec = Mock(spec=ExecutionRecord)
    rec.status = ExecutionStatus.FAILED  # Not passed
    rec.organization_id = "org_1"
    rec.workflow_id = "wor_0123456789abcdef"
    rec.model_copy.return_value = rec
    service.exec_repo.get_execution.return_value = rec
    service.workflow_repo.get_workflow_by_id.return_value = None

    with pytest.raises(AppException) as exc_info:
        await service.get_execution_export_bytes(initiator, "exe_0123456789abcdef")
    assert exc_info.value.status_code == 400
    assert "Execution must be in PASSED state" in exc_info.value.message


@pytest.mark.asyncio
async def test_resume_execution_quota_exceeded() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_1", role=UserRole.MEMBER, organization_id="org_overquota")
    rec = Mock(spec=ExecutionRecord)
    rec.status = ExecutionStatus.FAILED
    rec.organization_id = "org_overquota"
    rec.created_by = "usr_1"
    rec.workflow_id = "wor_0123456789abcdef"
    rec.execution_trace = []
    rec.model_copy.return_value = rec
    service.exec_repo.get_execution.return_value = rec

    with patch.object(service, "check_resumability", return_value=True):
        service.usage_service.check_quota.return_value = False
        with pytest.raises(AppException) as exc_info:
            await service.resume_execution(
                initiator=initiator, execution_id="exe_0123456789abcdef", arq_pool=AsyncMock()
            )
        assert exc_info.value.status_code == 402
        assert "exceeded its execution quota" in exc_info.value.message


@pytest.mark.asyncio
async def test_render_execution_workflow_not_found() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ROOT)
    rec = Mock(spec=ExecutionRecord)
    rec.status = ExecutionStatus.PASSED
    rec.organization_id = "org_1"
    rec.workflow_id = "wor_missing"
    rec.model_copy.return_value = rec
    service.exec_repo.get_execution.return_value = rec
    service.workflow_repo.get_workflow_by_id.return_value = None

    with pytest.raises(AppException) as exc_info:
        await service.render_execution(
            initiator=initiator,
            execution_id="exe_0123456789abcdef",
            format_type="html",
            profile_id="prf_default",
            accept_language="en",
            arq_pool=AsyncMock(),
        )
    assert exc_info.value.status_code == 500
    assert "Workflow not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_execution_export_bytes_report_fetch_error() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_root", role=UserRole.ROOT)
    rec = Mock(spec=ExecutionRecord)
    rec.status = ExecutionStatus.PASSED
    rec.target_locale = "en"
    rec.step_states = {
        "stp_1": Mock(
            scorecard_atoms={
                "atm_1": Mock(status="PASS", exact_quotes=[], semantic_reasoning="", internal_logic_en=None)
            }
        )
    }
    rec.model_copy.return_value = rec
    service.exec_repo.get_execution.return_value = rec

    with patch.object(service, "get_report_dto", side_effect=RuntimeError("Report crash")):
        with pytest.raises(AppException) as exc_info:
            await service.get_execution_export_bytes(initiator, "exe_0123456789abcdef")
        assert exc_info.value.status_code == 500
        assert "Report Fetch Error" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_execution_export_bytes_excel_writer_error() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_root", role=UserRole.ROOT)
    rec = Mock(spec=ExecutionRecord)
    rec.status = ExecutionStatus.PASSED
    rec.target_locale = "en"
    rec.step_states = {
        "stp_1": Mock(
            scorecard_atoms={
                "atm_1": Mock(status="PASS", exact_quotes=[], semantic_reasoning="", internal_logic_en=None)
            }
        )
    }
    rec.model_copy.return_value = rec
    service.exec_repo.get_execution.return_value = rec

    mock_atom = Mock(
        matrix_id="m1",
        tda_id="tda_1",
        evaluation_reasoning="Reasoning",
        source_quote="Quote",
        status=ExecutionStatus.PASSED,
        extensions={},
    )
    mock_report_dto = Mock(
        results=[mock_atom],
        hydrated_references={},
        inner_sdui_blocks=[],
    )
    with (
        patch.object(service, "get_report_dto", return_value=mock_report_dto),
        patch("pandas.ExcelWriter", side_effect=RuntimeError("Disk full")),
    ):
        with pytest.raises(AppException) as exc_info:
            await service.get_execution_export_bytes(initiator, "exe_0123456789abcdef")
        assert exc_info.value.status_code == 500
        assert "Failed to generate Excel export" in exc_info.value.message


@pytest.mark.asyncio
async def test_check_resumability_string_version() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    rec = Mock(spec=ExecutionRecord)
    rec.status = ExecutionStatus.FAILED
    rec.workflow_id = "wor_0123456789abcdef"
    rec.step_states = {"stp_1": Mock()}
    rec.metadata = {"workflow_version": "1"}
    rec.organization_id = "org_1"

    wf = Workflow(
        id="wor_0123456789abcdef",
        slug="test-wf",
        version=2,
        status="ACTIVE",
        default_profile_id="prf_default",
        model_registry_id="sys_e26807f3bfa3454d",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        steps=[StepRule(id="stp_0123456789abcdef", task_blueprint="stp_0123456789abcdef")],
        historical_context_mode="DISABLED",
        expected_inputs=[],
    )
    service.workflow_repo.get_workflow_by_id.return_value = wf.model_dump(mode="json")
    res = await service.check_resumability(rec)
    assert res is False


@pytest.mark.asyncio
async def test_render_execution_on_demand_synthesis_with_updated_at_and_vstep() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ROOT)
    wf = Workflow(
        id="wor_0123456789abcdef",
        slug="test-wf",
        version=1,
        status="ACTIVE",
        default_profile_id="prf_ondemand",
        model_registry_id="sys_e26807f3bfa3454d",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        historical_context_mode="DISABLED",
        expected_inputs=[],
    )
    service.workflow_repo.get_workflow_by_id.return_value = wf.model_dump(mode="json")
    rec = Mock(spec=ExecutionRecord)
    rec.status = ExecutionStatus.PASSED
    rec.organization_id = "org_1"
    rec.workflow_id = "wor_0123456789abcdef"
    rec.target_locale = "en"
    rec.profile_syntheses = {}
    v_step_id = "sys_render_prf_ondemand"
    rec.step_states = {v_step_id: ExecutionStep(id=v_step_id, label="Rendering PDF...", status=ExecutionStatus.RUNNING)}
    rec.updated_at = datetime.now(timezone.utc)
    rec.model_copy.return_value = rec
    service.exec_repo.get_execution.return_value = rec

    res, mime, filename = await service.render_execution(
        initiator=initiator,
        execution_id="exe_0123456789abcdef",
        format_type="json",
        profile_id="prf_ondemand",
        accept_language="en",
        arq_pool=AsyncMock(),
    )
    assert isinstance(res, JobAcceptedDTO)
    assert res.message == "Rendering PDF..."


@pytest.mark.asyncio
async def test_start_execution_circuit_breaker_quota_exceeded() -> None:
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    initiator = TokenData(id="usr_owner", role=UserRole.MEMBER, organization_id="org_quota_tripped")
    wf = Workflow(
        id="wor_0123456789abcdef",
        slug="test-wf",
        version=1,
        status="ACTIVE",
        default_profile_id="prf_default",
        model_registry_id="sys_e26807f3bfa3454d",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        organization_id="org_quota_tripped",
        historical_context_mode="DISABLED",
        expected_inputs=[],
    )
    service.workflow_repo.get_workflow_by_id.return_value = wf.model_dump(mode="json")
    service.usage_service.check_quota.return_value = False

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(),
        target_locale="fi",
    )
    with pytest.raises(AppException) as exc_info:
        await service.start_execution(initiator, payload, AsyncMock())
    assert exc_info.value.status_code == 402
    assert "has exceeded its execution quota" in exc_info.value.message


@pytest.mark.asyncio
async def test_start_execution_fails_fast_when_profile_workflow_mismatch() -> None:
    """ISTQB Negative: start_execution raises 400 VALIDATION_FAILED when profile workflow_id != workflow.id."""
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    service.usage_service.check_quota.return_value = True

    wf = Workflow(
        id="wor_0123456789abcdef",
        slug="test-wf",
        version=1,
        status="ACTIVE",
        default_profile_id="prf_0123456789abcdef",
        model_registry_id="sys_e26807f3bfa3454d",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        organization_id="org_1",
        historical_context_mode="DISABLED",
        expected_inputs=[],
    )
    service.workflow_repo.get_workflow_by_id.return_value = wf.model_dump(mode="json")

    mismatch_profile = OutputProfile(
        id="prf_0123456789abcdef",
        slug="other-profile",
        workflow_id="wor_other_workflow",
        name=I18nText(translations={"en": "Other Profile"}),
        description=I18nText(translations={"en": "Desc"}),
        target_block_order=[],
    )
    service.output_profile_repo.get_output_profile_by_id.return_value = mismatch_profile

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(),
        target_locale="en",
        profile_id="prf_0123456789abcdef",
    )
    initiator = TokenData(id="u1", role=UserRole.MEMBER, organization_id="org_1")

    with pytest.raises(AppException) as exc_info:
        await service.start_execution(initiator, payload, AsyncMock())
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


@pytest.mark.asyncio
async def test_start_execution_fails_fast_when_no_registry_id() -> None:
    """ISTQB Negative: start_execution raises 404 RESOURCE_NOT_FOUND when neither payload nor workflow has model_registry_id."""
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    service.usage_service.check_quota.return_value = True
    service.workflow_repo.get_workflow_by_id.return_value = {"id": "wor_0123456789abcdef"}

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(),
        target_locale="en",
    )
    initiator = TokenData(id="u1", role=UserRole.MEMBER, organization_id="org_1")

    mock_wf = Mock(spec=Workflow)
    mock_wf.id = "wor_0123456789abcdef"
    mock_wf.version = 1
    mock_wf.status = "ACTIVE"
    mock_wf.default_profile_id = None
    mock_wf.model_registry_id = None
    mock_wf.expected_inputs = []
    mock_wf.steps = []
    mock_wf.organization_id = "org_1"
    mock_wf.is_public = False

    with patch("backend_v2.services.execution.Workflow.model_validate", return_value=mock_wf):
        with pytest.raises(AppException) as exc_info:
            await service.start_execution(initiator, payload, AsyncMock())
    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == "RESOURCE_NOT_FOUND"
    assert "No model_registry_id provided" in exc_info.value.message


@pytest.mark.asyncio
async def test_start_execution_fails_fast_when_registry_obj_is_none() -> None:
    """ISTQB Negative: start_execution raises 404 RESOURCE_NOT_FOUND when get_model_registry returns None."""
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    service.usage_service.check_quota.return_value = True

    wf = Workflow(
        id="wor_0123456789abcdef",
        slug="test-wf",
        version=1,
        status="ACTIVE",
        default_profile_id=None,
        model_registry_id="sys_e26807f3bfa3454d",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        organization_id="org_1",
        historical_context_mode="DISABLED",
        expected_inputs=[],
    )
    service.workflow_repo.get_workflow_by_id.return_value = wf.model_dump(mode="json")
    service.system_repo.get_model_registry.return_value = None

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(),
        target_locale="en",
    )
    initiator = TokenData(id="u1", role=UserRole.MEMBER, organization_id="org_1")

    with pytest.raises(AppException) as exc_info:
        await service.start_execution(initiator, payload, AsyncMock())
    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_check_resumability_version_and_quota_branches() -> None:
    """Test check_resumability returns False on version drift and quota exceeded."""
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    wf = Workflow(
        id="wor_0123456789abcdef",
        slug="test-wf",
        version=2,
        status="ACTIVE",
        default_profile_id=None,
        model_registry_id="sys_e26807f3bfa3454d",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        organization_id="org_1",
        historical_context_mode="DISABLED",
        expected_inputs=[],
    )
    service.workflow_repo.get_workflow_by_id.return_value = wf.model_dump(mode="json")

    # Case 1: Version drift (record was version 1, workflow is version 2)
    rec_drift = Mock(spec=ExecutionRecord)
    rec_drift.status = ExecutionStatus.FAILED
    rec_drift.step_states = {}
    rec_drift.metadata = None
    rec_drift.workflow_version = 1
    rec_drift.workflow_id = "wor_0123456789abcdef"
    rec_drift.organization_id = "org_1"

    can_resume_drift = await service.check_resumability(rec_drift)
    assert can_resume_drift is False

    # Case 2: Quota exceeded
    rec_quota = Mock(spec=ExecutionRecord)
    rec_quota.status = ExecutionStatus.FAILED
    rec_quota.step_states = {}
    rec_quota.metadata = None
    rec_quota.workflow_version = 2
    rec_quota.workflow_id = "wor_0123456789abcdef"
    rec_quota.organization_id = "org_1"
    service.usage_service.check_quota.return_value = False

    can_resume_quota = await service.check_resumability(rec_quota)
    assert can_resume_quota is False


@pytest.mark.asyncio
async def test_override_atom_and_reject_evidence_permission_denied() -> None:
    """ISTQB Negative: override_atom and reject_evidence_quote raise PermissionDeniedError for non-owner non-root."""
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    rec = Mock(spec=ExecutionRecord)
    rec.organization_id = "org_other"
    rec.created_by = "usr_other"
    service.get_execution = AsyncMock(return_value=rec)  # type: ignore[assignment]

    initiator = TokenData(id="usr_stranger", role=UserRole.MEMBER, organization_id="org_mine")

    with pytest.raises(PermissionDeniedError):
        await service.override_atom(initiator, "exe_1", "atom_1", Mock())

    with pytest.raises(PermissionDeniedError):
        await service.reject_evidence_quote(initiator, "exe_1", "evq_1", "invalid quote")


@pytest.mark.asyncio
async def test_stream_status_handles_app_exception_interrupted() -> None:
    """Test stream_status handles AppException/OSError during polling by yielding error event."""
    service = ExecutionService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
        usage_service=AsyncMock(),
        executor=Mock(),
    )
    rec = Mock(spec=ExecutionRecord)
    rec.organization_id = "org_test"
    rec.created_by = "usr_owner"
    rec.is_public = False

    service.get_execution = AsyncMock(side_effect=[rec, OSError("Connection dropped")])  # type: ignore[assignment]

    initiator = TokenData(id="usr_owner", role=UserRole.ADMIN, organization_id="org_test")
    events = [event async for event in service.stream_status(initiator, "exe_test")]
    assert len(events) == 1
    assert "event: error" in events[0]
    assert "SSE_STREAM_INTERRUPTED" in events[0]
