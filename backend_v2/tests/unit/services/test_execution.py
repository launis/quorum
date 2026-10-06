from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

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
from backend_v2.models.domain.inputs import WorkflowInputs, WorkflowInputsIngress
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    MatrixScale,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.step import ExpectedInput, Step, StepRule
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.system_config import ModelProfile, SystemConfigModelRegistry
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.atom_result import EvaluatedAtomDTO, HydratedAtomDTO
from backend_v2.models.dtos.context_variables import ContextVariablesDTO, EvaluatedMatrixContextDTO
from backend_v2.models.dtos.flat_record import FlatExecutionRecordDTO
from backend_v2.models.dtos.matrix_scorecard import HumanOverrideRequest, ScorecardAtomDTO
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.dtos.trace import ExecutionCreateDTO
from backend_v2.models.dtos.workflow_schema import WorkflowSchemaResponseDTO
from backend_v2.models.enums import CognitiveTier, ExecutionStatus, LLMProvider, SDUIComponentType, VisualIntent
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.models.view.sdui import (
    MarkdownBlock,
    ReportView,
)
from backend_v2.services.execution import ExecutionService, create_execution_record
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _make_test_record(
    execution_id: str = "exe_0123456789abcdef",
    workflow_id: str = "wor_0123456789abcdef",
    organization_id: str = "org_1",
    created_by: str = "u1",
    status: ExecutionStatus = ExecutionStatus.PASSED,
    target_locale: str = "en",
    profile_id: str | None = None,
    **kwargs: Any,
) -> ExecutionRecord:
    clean_kwargs = {k: v for k, v in kwargs.items() if k != "is_public"}
    data = {
        "id": execution_id,
        "workflow_id": workflow_id,
        "organization_id": organization_id,
        "created_by": created_by,
        "status": status,
        "target_locale": target_locale,
        "output_profile_id": profile_id,
        "raw_inputs": WorkflowInputs(),
        "frozen_context": FrozenContext(),
        "metadata": ExecutionMetadata(),
        "step_states": {},
        "execution_trace": [],
        **clean_kwargs,
    }
    return ExecutionRecord.model_validate(data, strict=False)


def _make_test_profile(
    profile_id: str = "prf_0123456789abcdef",
    workflow_id: str = "wor_0123456789abcdef",
    organization_id: str = "org_1",
    **kwargs: Any,
) -> OutputProfile:
    data = {
        "id": profile_id,
        "slug": "test-profile",
        "workflow_id": workflow_id,
        "organization_id": organization_id,
        "name": I18nText(translations={"en": "Test Profile"}),
        "target_block_order": [],
        **kwargs,
    }
    return OutputProfile.model_validate(data, strict=False)


def _make_test_workflow(
    workflow_id: str = "wor_0123456789abcdef",
    organization_id: str = "org_1",
    default_profile_id: str | None = "prf_0123456789abcdef",
    model_registry_id: str | None = "sys_e26807f3bfa3454d",
    **kwargs: Any,
) -> Workflow:
    data = {
        "id": workflow_id,
        "slug": "test-wf",
        "name": I18nText(translations={"en": "Test WF"}),
        "description": I18nText(translations={"en": "Desc"}),
        "status": "ACTIVE",
        "version": 1,
        "organization_id": organization_id,
        "is_public": False,
        "default_profile_id": default_profile_id,
        "model_registry_id": model_registry_id,
        "historical_context_mode": "DISABLED",
        "expected_inputs": [],
        "steps": [],
        **kwargs,
    }
    return Workflow.model_validate(data, strict=False)


def _create_test_service(
    repo: InMemoryUnifiedWorkflowRepository | None = None,
    usage_service: Any = None,
    executor: Any = None,
    storage_driver: Any = None,
) -> tuple[ExecutionService, InMemoryUnifiedWorkflowRepository]:
    unified_repo = repo or InMemoryUnifiedWorkflowRepository()
    service = ExecutionService(
        exec_repo=unified_repo,
        workflow_repo=unified_repo,
        comp_repo=unified_repo,
        prompt_block_repo=unified_repo,
        output_profile_repo=unified_repo,
        identity_repo=unified_repo,
        system_repo=unified_repo,
        report_repo=unified_repo,
        usage_service=usage_service or AsyncMock(),
        executor=executor or Mock(),
        storage_driver=storage_driver,
    )
    return service, unified_repo


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
    executor_mock = Mock()
    arq_pool = AsyncMock()
    service, repo = _create_test_service(executor=executor_mock)

    rec = _make_test_record(id="exe_0123456789abcdef", status=ExecutionStatus.PENDING)
    repo.set_execution(rec)

    initiator = TokenData(id="u1", role=UserRole.ROOT)

    with pytest.raises(AppException) as exc_info:
        await service.resume_execution(initiator=initiator, execution_id="exe_0123456789abcdef", arq_pool=arq_pool)

    assert "cannot be resumed due to unresumable state" in exc_info.value.message
    assert exc_info.value.details["error_code"] == "UNRESUMABLE_STATE_ERROR"


@pytest.mark.asyncio
async def test_list_executions_admin_sees_all() -> None:
    executor_mock = Mock()
    service, repo = _create_test_service(executor=executor_mock)

    rec1 = _make_test_record(id="exe_0123456789abcde1", organization_id="org_1", status=ExecutionStatus.PASSED)
    rec2 = _make_test_record(id="exe_0123456789abcde2", organization_id="org_2", status=ExecutionStatus.PASSED)
    repo.set_execution(rec1)
    repo.set_execution(rec2)

    initiator = TokenData(id="u1", role=UserRole.ROOT)

    with patch.object(service, "check_resumability", return_value=False):
        results = await service.list_executions(initiator=initiator)

    assert len(results) == 2


@pytest.mark.asyncio
async def test_list_executions_tenant_sees_own() -> None:
    executor_mock = Mock()
    service, repo = _create_test_service(executor=executor_mock)

    rec1 = _make_test_record(
        id="exe_0123456789abcde1", organization_id="org_1", created_by="u2", status=ExecutionStatus.PASSED
    )
    rec2 = _make_test_record(
        id="exe_0123456789abcde2", organization_id="org_2", created_by="u3", status=ExecutionStatus.PASSED
    )
    repo.set_execution(rec1)
    repo.set_execution(rec2)

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    with patch.object(service, "check_resumability", return_value=False):
        results = await service.list_executions(initiator=initiator)

    assert len(results) == 1
    assert results[0].organization_id == "org_1"


@pytest.mark.asyncio
async def test_get_execution_admin_sees_any() -> None:
    executor_mock = Mock()
    service, repo = _create_test_service(executor=executor_mock)

    rec = _make_test_record(id="exe_0123456789abcdef", organization_id="org_other", status=ExecutionStatus.PASSED)
    repo.set_execution(rec)

    initiator = TokenData(id="u1", role=UserRole.ROOT)

    with patch.object(service, "check_resumability", return_value=False):
        result = await service.get_execution(initiator=initiator, execution_id="exe_0123456789abcdef")

    assert result.organization_id == "org_other"


@pytest.mark.asyncio
async def test_get_execution_tenant_sees_own() -> None:
    executor_mock = Mock()
    service, repo = _create_test_service(executor=executor_mock)

    rec = _make_test_record(
        id="exe_0123456789abcdef", organization_id="org_1", created_by="u2", status=ExecutionStatus.PASSED
    )
    repo.set_execution(rec)

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    with patch.object(service, "check_resumability", return_value=False):
        result = await service.get_execution(initiator=initiator, execution_id="exe_0123456789abcdef")

    assert result.organization_id == "org_1"


@pytest.mark.asyncio
async def test_delete_execution_tenant_deletes_own() -> None:
    executor_mock = Mock()
    service, repo = _create_test_service(executor=executor_mock)

    rec = _make_test_record(id="exe_0123456789abcdef", organization_id="org_1", created_by="u2")
    repo.set_execution(rec)

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")
    result = await service.delete_execution(initiator=initiator, execution_id="exe_0123456789abcdef")

    assert result is True
    assert await repo.get_execution("exe_0123456789abcdef") is None


@pytest.mark.asyncio
async def test_start_execution_success() -> None:
    executor_mock = Mock()
    arq_pool = AsyncMock()
    service, repo = _create_test_service(executor=executor_mock)

    valid_profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-profile",
        workflow_id="wor_0123456789abcdef",
        name=I18nText(translations={"en": "Test Profile"}),
        target_block_order=[],
    )
    repo.set_output_profiles([valid_profile])
    service.usage_service.check_quota.return_value = True

    wf = _make_test_workflow(default_profile_id=valid_profile.id)
    repo.set_workflow(wf)

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        target_locale="en",
        profile_id=valid_profile.id,
        matrix_sampling_strategy=10,
    )

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    result = await service.start_execution(initiator=initiator, payload=payload, arq_pool=arq_pool)

    assert result.workflow_id == "wor_0123456789abcdef"
    assert result.status == ExecutionStatus.PENDING
    assert result.metadata is not None
    assert result.metadata.model_registry_id == "sys_e26807f3bfa3454d"
    arq_pool.enqueue_job.assert_called_once()


@pytest.mark.asyncio
async def test_start_execution_model_registry_override() -> None:
    """Verify that payload.model_registry_id overrides workflow.model_registry_id."""
    executor_mock = Mock()
    arq_pool = AsyncMock()
    service, repo = _create_test_service(executor=executor_mock)

    valid_profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-profile",
        workflow_id="wor_0123456789abcdef",
        name=I18nText(translations={"en": "Test Profile"}),
        target_block_order=[],
    )
    repo.set_output_profiles([valid_profile])

    override_reg = SystemConfigModelRegistry(
        id="sys_6f8b1c4a2e0d49f1",
        name="Override Model Registry",
        type="model_registry",
        default_provider=LLMProvider.AI_STUDIO,
        tier_definitions={
            CognitiveTier.FAST: ModelProfile(provider="ai_studio", model_name="gemini-2.5-flash"),
            CognitiveTier.BALANCED: ModelProfile(provider="ai_studio", model_name="gemini-2.5-flash"),
            CognitiveTier.DEEP: ModelProfile(provider="ai_studio", model_name="gemini-2.5-pro"),
            CognitiveTier.REASONING: ModelProfile(provider="ai_studio", model_name="gemini-2.5-pro"),
        },
    )
    repo.set_model_registry(override_reg)

    wf = _make_test_workflow(default_profile_id=valid_profile.id)
    repo.set_workflow(wf)
    service.usage_service.check_quota.return_value = True

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        target_locale="en",
        profile_id=valid_profile.id,
        matrix_sampling_strategy=10,
        model_registry_id="sys_6f8b1c4a2e0d49f1",
    )

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    result = await service.start_execution(initiator=initiator, payload=payload, arq_pool=arq_pool)

    assert result.metadata is not None
    assert result.metadata.model_registry_id == "sys_6f8b1c4a2e0d49f1"


@pytest.mark.asyncio
async def test_start_execution_permission_denied() -> None:
    service, repo = _create_test_service()

    wf = _make_test_workflow(organization_id="org_other", is_public=False)
    repo.set_workflow(wf)
    service.usage_service.check_quota.return_value = True

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        target_locale="en",
        profile_id="prf_0123456789abcdef",
        matrix_sampling_strategy=10,
    )
    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_my")

    with pytest.raises(PermissionDeniedError) as exc_info:
        await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())
    assert "You do not have permission to execute this workflow." in str(exc_info.value)


@pytest.mark.asyncio
async def test_render_execution_flat() -> None:
    executor_mock = Mock()
    arq_pool = AsyncMock()
    service, repo = _create_test_service(executor=executor_mock)

    rec = _make_test_record(id="exe_0123456789abcdef", workflow_id="wf_1", organization_id="org_1", created_by="u2")
    repo.set_execution(rec)

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    mock_dto = Mock()
    with patch("backend_v2.services.blueprint.BlueprintTransformer") as mock_transformer_class:
        mock_transformer = AsyncMock()
        mock_transformer.build_report_dto.return_value = mock_dto
        mock_transformer_class.return_value = mock_transformer

        flat_rec = FlatExecutionRecordDTO(
            execution_id="exe_0123456789abcdef",
            workflow_id="wf_1",
            status="PASSED",
            matrix_metrics={"flat": "data"},
        )
        with patch("backend_v2.services.flattener.FlatFileService.flatten_results", return_value=flat_rec):
            data, mime, filename = await service.render_execution(
                initiator=initiator,
                execution_id="exe_0123456789abcdef",
                format_type="flat",
                profile_id="prof_1",
                accept_language="en",
                arq_pool=arq_pool,
            )

    assert data == flat_rec
    assert mime == "application/json"
    assert filename is None


@pytest.mark.asyncio
async def test_render_execution_json() -> None:
    executor_mock = Mock()
    arq_pool = AsyncMock()
    service, repo = _create_test_service(executor=executor_mock)

    rec = _make_test_record(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        organization_id="org_1",
        created_by="u2",
        profile_syntheses={"prof_1": RenderedSynthesisCache()},
    )
    repo.set_execution(rec)

    wf = _make_test_workflow(workflow_id="wor_0123456789abcdef", default_profile_id="prof_1")
    repo.set_workflow(wf)

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    mock_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_1",
    )

    with patch("backend_v2.services.blueprint.BlueprintTransformer") as mock_transformer_class:
        mock_transformer = AsyncMock()
        mock_transformer.build_report_dto.return_value = mock_dto
        mock_transformer_class.return_value = mock_transformer

        data, mime, filename = await service.render_execution(
            initiator=initiator,
            execution_id="exe_0123456789abcdef",
            format_type="json",
            profile_id="prof_1",
            accept_language=None,
            arq_pool=arq_pool,
        )

    assert isinstance(data, ReportDataDTO)
    assert data.workflow_id == "wor_0123456789abcdef"
    assert data.profile_id == "prof_1"
    assert mime == "application/json"
    assert filename is None


@pytest.mark.asyncio
async def test_enqueue_pdf_generation_success() -> None:
    executor_mock = Mock()
    arq_pool = AsyncMock()
    service, repo = _create_test_service(executor=executor_mock)

    rec = _make_test_record(id="exe_0123456789abcdef", workflow_id="wf_1", organization_id="org_1", created_by="u2")
    repo.set_execution(rec)

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")

    await service.enqueue_pdf_generation(
        initiator=initiator,
        execution_id="exe_0123456789abcdef",
        accept_language="fi",
        profile_id="prof_1",
        arq_pool=arq_pool,
    )

    assert repo.get_call_count("update_execution") >= 1
    arq_pool.enqueue_job.assert_called_once_with(
        "generate_pdf_job",
        execution_id="exe_0123456789abcdef",
        accept_language="fi",
        profile_id="prof_1",
        custom_preface_md=None,
        local_time_str=None,
    )


@pytest.mark.asyncio
async def test_override_atom_success() -> None:
    executor_mock = Mock()
    service, repo = _create_test_service(executor=executor_mock)

    record = create_execution_record(
        execution_id="exe_1234567890abcdef",
        workflow_id="wf_1",
        raw_inputs=WorkflowInputs(),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        output_profile_id="prof_1",
    )

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
    repo.set_execution(record)

    initiator = TokenData(id="u2", role=UserRole.MEMBER, organization_id="org_1")
    payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED,
        reason="Override reason",
        evidence_quotes=[],
    )

    with patch("backend_v2.hooks.scoring.recalculate", new_callable=AsyncMock) as mock_recalc:
        mock_recalc.return_value = {}
        await service.override_atom(
            initiator=initiator,
            execution_id="exe_1234567890abcdef",
            atom_id="tda_1",
            payload=payload,
        )
        mock_recalc.assert_called_once()

    assert repo.get_call_count("update_execution") >= 1
    assert repo.get_call_count("append_trace_event") >= 1


@pytest.mark.asyncio
async def test_get_execution_export_bytes_success() -> None:
    executor_mock = Mock()
    service, repo = _create_test_service(executor=executor_mock)

    initiator = TokenData(id="u1", role=UserRole.ROOT)

    atom1 = ScorecardAtomDTO(
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
    step_state = ExecutionStepState(
        id="step_1",
        label="Step 1",
        status=ExecutionStatus.PASSED,
        scorecard_atoms={"atom_1": atom1},
    )
    rec = _make_test_record(
        id="exe_0123456789abcdef",
        status=ExecutionStatus.PASSED,
        step_states={"step_1": step_state},
        organization_id="org_1",
    )
    repo.set_execution(rec)

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
        hydrated_references={
            "tda_1": HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Claim 1",
            )
        },
        inner_sdui_blocks=[],
    )

    with patch.object(service, "get_report_dto", return_value=mock_report_dto):
        bytes_out, filename = await service.get_execution_export_bytes(
            initiator=initiator, execution_id="exe_0123456789abcdef"
        )

    assert filename == "execution_export_exe_0123456789abcdef.xlsx"
    assert len(bytes_out) > 0
    assert bytes_out.startswith(b"PK")


@pytest.mark.asyncio
async def test_get_execution_export_bytes_quotes_bug() -> None:
    executor_mock = Mock()
    service, repo = _create_test_service(executor=executor_mock)

    initiator = TokenData(id="u1", role=UserRole.ROOT)

    trace = TraceEvent(
        event_type="output",
        step_name="step_1",
        content={
            "type": "ATOM_COMPLETED",
            "atom_id": "test_atom_1",
            "status": "PASS",
            "exact_quotes": [{"text": "Found quote", "source_alias": "src1"}],
        },
    )

    atom1 = ScorecardAtomDTO(
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
    step_state = ExecutionStepState(
        id="step_1",
        label="Step 1",
        status=ExecutionStatus.PASSED,
        scorecard_atoms={"atom_1": atom1},
    )
    rec = _make_test_record(
        id="exe_0123456789abcdef",
        status=ExecutionStatus.PASSED,
        execution_trace=[trace],
        step_states={"step_1": step_state},
        organization_id="org_1",
    )
    repo.set_execution(rec)

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
        hydrated_references={
            "tda_1": HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Claim 1",
            )
        },
        inner_sdui_blocks=[],
    )

    with patch.object(service, "get_report_dto", return_value=mock_report_dto):
        bytes_out, filename = await service.get_execution_export_bytes(
            initiator=initiator, execution_id="exe_0123456789abcdef"
        )
    assert filename == "execution_export_exe_0123456789abcdef.xlsx"


@pytest.mark.asyncio
async def test_get_execution_export_bytes_empty_states_fails() -> None:
    executor_mock = Mock()
    service, repo = _create_test_service(executor=executor_mock)

    initiator = TokenData(id="u1", role=UserRole.ROOT)

    rec = _make_test_record(id="exe_0123456789abcdef", status=ExecutionStatus.PASSED, step_states={})
    repo.set_execution(rec)

    with pytest.raises(AppException) as exc_info:
        await service.get_execution_export_bytes(initiator=initiator, execution_id="exe_0123456789abcdef")

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "no scoreable atoms" in exc_info.value.message


@pytest.mark.asyncio
async def test_phase_1_5_negative_invalid_human_override_crashes() -> None:
    """Verify that applying a human override via override_atom with an invalid ExecutionStatus
    strictly crashes Pydantic validation before modifying the state dictionary.
    """
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        HumanOverrideRequest(
            new_status="NOT_AN_ENUM",  # type: ignore[arg-type]
            reason="Invalid",
            evidence_quotes=[],
        )


def test_execution_create_dto_preserves_output_profile_id() -> None:
    """Regression: ExecutionCreateDTO must support and persist output_profile_id."""
    dto = ExecutionCreateDTO(
        workflow_id="wf_1234567890abcdef",
        target_locale="fi",
        active_profile_id="prof_1234567890abcdef",
        output_profile_id="prof_1234567890abcdef",
        metadata=ExecutionMetadata(),
    )
    raw_dict = dto.model_dump(mode="json", exclude_unset=True)
    raw_dict["id"] = "exe_1234567890abcdef"
    record = ExecutionRecord.model_validate(raw_dict, strict=False)
    assert record.output_profile_id == "prof_1234567890abcdef"


@pytest.mark.asyncio
async def test_start_execution_succeeds_without_profile() -> None:
    """Ingress Decoupling: start_execution succeeds when no profile_id is provided."""
    service, repo = _create_test_service()
    service.usage_service.check_quota.return_value = True

    wf = _make_test_workflow(default_profile_id=None)
    repo.set_workflow(wf)

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        target_locale="en",
        profile_id=None,
        matrix_sampling_strategy=10,
    )
    initiator = TokenData(id="u1", role=UserRole.MEMBER, organization_id="org_1")

    result = await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())

    assert result.workflow_id == "wor_0123456789abcdef"
    assert result.output_profile_id is None
    assert result.status == ExecutionStatus.PENDING


@pytest.mark.asyncio
async def test_start_execution_fails_fast_when_profile_not_in_db() -> None:
    """ISTQB Negative: start_execution raises 404 RESOURCE_NOT_FOUND when profile is not found in database."""
    service, repo = _create_test_service()
    repo.set_output_profiles([])
    service.usage_service.check_quota.return_value = True

    wf = _make_test_workflow(default_profile_id="prf_0123456789abcdef")
    repo.set_workflow(wf)

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        target_locale="en",
        profile_id="prf_0123456789abcdef",
        matrix_sampling_strategy=10,
    )
    initiator = TokenData(id="u1", role=UserRole.MEMBER, organization_id="org_1")

    with pytest.raises(AppException) as exc_info:
        await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == "RESOURCE_NOT_FOUND"
    assert "not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_start_execution_fails_fast_when_model_registry_not_found() -> None:
    """ISTQB Negative: start_execution raises 404 RESOURCE_NOT_FOUND when model registry is not found in database."""
    service, repo = _create_test_service()
    repo.inject_fault(
        "get_model_registry", ResourceNotFoundError(resource_type="system_config", resource_id="sys_0000000000000000")
    )
    service.usage_service.check_quota.return_value = True

    wf = _make_test_workflow(default_profile_id=None, model_registry_id="sys_0000000000000000")
    repo.set_workflow(wf)

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        target_locale="en",
        profile_id=None,
        matrix_sampling_strategy=10,
    )
    initiator = TokenData(id="u1", role=UserRole.MEMBER, organization_id="org_1")

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
    monkeypatch.setattr("backend_v2.services.execution.stream_service.asyncio.sleep", AsyncMock())

    service, repo = _create_test_service()

    initiator = TokenData(id="u1", role=UserRole.ROOT, organization_id="org_1")
    rec = _make_test_record(
        id="exe_0b51fa35ea584ca7a42cd30b444d1241",
        workflow_id="wf_1",
        status=ExecutionStatus.RUNNING,
        organization_id="org_1",
        created_by="u1",
        target_locale="fi",
        profile_id="prof_default",
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
            return rec
        raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)

    service.get_execution = mock_get_exec  # type: ignore[method-assign]

    events: list[str] = []
    async for event in service.stream_status(initiator=initiator, execution_id="exe_0b51fa35ea584ca7a42cd30b444d1241"):
        events.append(event)

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
    service, repo = _create_test_service()
    service.usage_service.check_quota.return_value = True

    expected_input = ExpectedInput(
        input_key="chat_log",
        label=I18nText(translations={"fi": "Keskusteluhistoria (Chat)", "en": "Chat"}),
        required=True,
        is_chat_history=True,
        input_modes=["file", "paste"],
        description=I18nText(translations={"en": "Chat", "fi": "Keskustelu"}),
    )
    wf = _make_test_workflow(default_profile_id="prf_0123456789abcdef", expected_inputs=[expected_input])
    repo.set_workflow(wf)

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
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
        profile_id="prf_0123456789abcdef",
        matrix_sampling_strategy=10,
    )
    initiator = TokenData(id="u1", role=UserRole.MEMBER, organization_id="org_1")

    with pytest.raises(AppException) as exc_info:
        await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "collision" in exc_info.value.details
    assert exc_info.value.details["collision"]["slot"] == "chat_log"


@pytest.mark.asyncio
async def test_start_execution_fails_fast_on_missing_required_input() -> None:
    """ISTQB Negative: start_execution raises 400 VALIDATION_FAILED when a required input is missing."""
    service, repo = _create_test_service()
    service.usage_service.check_quota.return_value = True

    expected_input = ExpectedInput(
        input_key="chat_log",
        label=I18nText(translations={"fi": "Keskusteluhistoria (Chat)", "en": "Chat"}),
        required=True,
        is_chat_history=True,
        input_modes=["file", "paste"],
        description=I18nText(translations={"en": "Chat", "fi": "Keskustelu"}),
    )
    wf = _make_test_workflow(default_profile_id="prf_0123456789abcdef", expected_inputs=[expected_input])
    repo.set_workflow(wf)

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs={"product_text": "Delivered material"}),
        target_locale="fi",
        profile_id="prf_0123456789abcdef",
        matrix_sampling_strategy=10,
    )
    initiator = TokenData(id="u1", role=UserRole.MEMBER, organization_id="org_1")

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
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ADMIN, organization_id="org_0123456789abcdef")

    res = await service.list_executions(initiator=initiator)
    assert res == []


@pytest.mark.asyncio
async def test_get_and_delete_execution_not_found_and_permission_denied() -> None:
    service, repo = _create_test_service()

    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.MEMBER, organization_id="org_tenant_a")

    with pytest.raises(ResourceNotFoundError):
        await service.get_execution(initiator=initiator, execution_id="exe_0123456789abcdef")

    with pytest.raises(ResourceNotFoundError):
        await service.delete_execution(initiator=initiator, execution_id="exe_0123456789abcdef")

    alien_record = _make_test_record(
        id="exe_0123456789abcdef",
        organization_id="org_tenant_b",
        created_by="usr_alien000000000",
        is_public=False,
        status=ExecutionStatus.PASSED,
    )
    repo.set_execution(alien_record)

    with pytest.raises(PermissionDeniedError):
        await service.get_execution(initiator=initiator, execution_id="exe_0123456789abcdef")

    with pytest.raises(PermissionDeniedError):
        await service.delete_execution(initiator=initiator, execution_id="exe_0123456789abcdef")


@pytest.mark.asyncio
async def test_start_execution_with_steps_and_blocks() -> None:
    service, repo = _create_test_service()
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
    repo.set_prompt_blocks([matrix_block])

    step_obj = Step(
        id="stp_0123456789abcdef",
        slug="step-1",
        name=I18nText(translations={"en": "Step 1"}),
        role_block_id=None,
        extraction_protocol_block_id="blk_0123456789abcdef",
        criteria_block_ids=["blk_0123456789abcdef"],
    )
    repo.seed_raw_step(step_obj.id, step_obj)

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
    repo.set_workflow(wf)
    repo.set_output_profiles(
        [
            {
                "id": "prf_0123456789abcdef",
                "slug": "profile-test",
                "workflow_id": "wor_0123456789abcdef",
                "name": {"translations": {"en": "Output Profile"}},
                "target_block_order": ["executive_summary_block"],
            }
        ]
    )

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
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ADMIN, organization_id="org_1")

    rec1 = _make_test_record(
        id="exe_0123456789abcde1",
        organization_id="org_1",
        is_public=False,
        status=ExecutionStatus.PASSED,
        frozen_context=FrozenContext(),
        frozen_context_storage_path=None,
    )
    repo.set_execution(rec1)

    b1, name1 = await service.get_frozen_context_bytes(initiator, "exe_0123456789abcde1")
    assert b1 is not None
    assert name1 == "frozen_context_exe_0123456789abcde1.json"

    rec2 = _make_test_record(
        id="exe_0123456789abcde2",
        organization_id="org_1",
        is_public=False,
        status=ExecutionStatus.PASSED,
        frozen_context=None,
        frozen_context_storage_path="storage/fc.json",
    )
    repo.set_execution(rec2)

    with patch("backend_v2.services.storage.get_storage_driver") as mock_storage_driver:
        mock_driver = AsyncMock()
        mock_driver.read.return_value = FrozenContext().model_dump_json().encode("utf-8")
        mock_storage_driver.return_value = mock_driver

        b2, name2 = await service.get_frozen_context_bytes(initiator, "exe_0123456789abcde2")
        assert b2 is not None

        mock_driver.read.side_effect = Exception("Storage failed")
        with pytest.raises(AppException):
            await service.get_frozen_context_bytes(initiator, "exe_0123456789abcde2")


@pytest.mark.asyncio
async def test_clear_profile_synthesis() -> None:
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_1", role=UserRole.ADMIN, organization_id="org_1")

    rec = _make_test_record(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        organization_id="org_1",
        is_public=False,
        status=ExecutionStatus.PASSED,
        profile_syntheses={"prof_1": RenderedSynthesisCache()},
        pdf_report_path="reports/report.pdf",
    )
    repo.set_execution(rec)

    wf = _make_test_workflow(default_profile_id="prof_1")
    repo.set_workflow(wf)

    driver = AsyncMock()
    service._override.storage = driver
    await service.clear_profile_synthesis(initiator, "exe_0123456789abcdef", "prof_1")
    driver.delete.assert_called_once_with("reports/report.pdf")

    repo.set_workflow(None)
    with pytest.raises(ResourceNotFoundError):
        await service.clear_profile_synthesis(initiator, "exe_0123456789abcdef", "prof_1")


@pytest.mark.asyncio
async def test_render_execution_formats() -> None:
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_1", role=UserRole.ADMIN, organization_id="org_1")

    rec = _make_test_record(
        id="exe_0123456789abcdef",
        organization_id="org_1",
        is_public=False,
        workflow_id="wor_0123456789abcdef",
        status=ExecutionStatus.FAILED,
    )
    repo.set_execution(rec)

    wf = _make_test_workflow()
    repo.set_workflow(wf)

    with pytest.raises(AppException):
        await service.render_execution(
            initiator=initiator,
            execution_id="exe_0123456789abcdef",
            format_type="flat",
            profile_id="prof_1",
            accept_language="en",
            arq_pool=AsyncMock(),
        )

    rec_passed = _make_test_record(
        id="exe_0123456789abcdef",
        organization_id="org_1",
        is_public=False,
        workflow_id="wor_0123456789abcdef",
        status=ExecutionStatus.PASSED,
    )
    repo.set_execution(rec_passed)
    mock_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_1",
    )

    with patch("backend_v2.services.blueprint.BlueprintTransformer") as mock_transformer_cls:
        mock_trans = AsyncMock()
        mock_trans.build_report_dto.return_value = mock_dto
        mock_transformer_cls.return_value = mock_trans

        data, mime, fname = await service.render_execution(
            initiator=initiator,
            execution_id="exe_0123456789abcdef",
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
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_1", role=UserRole.ADMIN, organization_id="org_1")

    rec = _make_test_record(
        id="exe_0123456789abcdef",
        organization_id="org_1",
        is_public=False,
        status=ExecutionStatus.PASSED,
    )
    repo.set_execution(rec)

    events = []
    async for event in service.stream_status(initiator, "exe_0123456789abcdef"):
        events.append(event)

    assert len(events) >= 1
    assert "PASSED" in events[0]
    assert repo.get_call_count("get_execution") >= 1


@pytest.mark.asyncio
async def test_resume_execution_success() -> None:
    service, repo = _create_test_service()
    service.usage_service.check_quota.return_value = True

    rec = _make_test_record(
        id="exe_0123456789abcdef",
        organization_id="org_1",
        workflow_id="wor_0123456789abcdef",
        status=ExecutionStatus.RUNNING,
    )
    repo.set_execution(rec)

    with patch.object(service, "check_resumability", return_value=True):
        arq_pool = AsyncMock()
        initiator = TokenData(id="usr_1", role=UserRole.ADMIN, organization_id="org_1")
        res = await service.resume_execution(initiator, "exe_0123456789abcdef", arq_pool)
        assert res.id == "exe_0123456789abcdef"
        arq_pool.enqueue_job.assert_called_once()


@pytest.mark.asyncio
async def test_get_execution_export_bytes_different_block_types() -> None:
    service, repo = _create_test_service()
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

    rec = _make_test_record(
        id="exe_0123456789abcdef",
        organization_id="org_1",
        status=ExecutionStatus.PASSED,
        target_locale="en",
        step_states={"stp_1": step_state},
    )
    repo.set_execution(rec)

    rule_block = SystemRulePromptBlock(
        id="blk_0123456789abcdef",
        slug="rule-block",
        label=I18nText(translations={"en": "Rule Block"}),
        description=I18nText(translations={"en": "Rule Description"}),
        category_id="system_rule",
        type="instruction",
        instruction_text="Instruction test",
    )
    repo.set_prompt_blocks([rule_block])

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
    mock_report_dto.hydrated_references = {
        "tda_1": HydratedAtomDTO(
            sdui_component=SDUIComponentType.BOOLEAN_CARD,
            resolved_claim="Claim 1",
        )
    }
    mock_report_dto.overall_score = 85.0
    mock_report_dto.executive_summary = "Summary text"
    mock_report_dto.strengths = []
    mock_report_dto.weaknesses = []
    mock_report_dto.data_dictionary = {}
    mock_report_dto.inner_sdui_blocks = []
    mock_report_dto.matrix_scores = {}

    with patch.object(service, "get_report_dto", return_value=mock_report_dto):
        file_bytes, filename = await service.get_execution_export_bytes(initiator, "exe_0123456789abcdef")
        assert len(file_bytes) > 0
        assert filename == "execution_export_exe_0123456789abcdef.xlsx"


@pytest.mark.asyncio
async def test_get_workflow_ui_schema_success_and_not_found() -> None:
    service, repo = _create_test_service()

    with pytest.raises(ResourceNotFoundError):
        await service.get_workflow_ui_schema("wor_0123456789abcdef")

    wf = _make_test_workflow()
    repo.set_workflow(wf)
    res = await service.get_workflow_ui_schema("wor_0123456789abcdef")
    assert isinstance(res, WorkflowSchemaResponseDTO)
    assert res.expected_inputs == []


@pytest.mark.asyncio
async def test_reject_evidence_quote_branches() -> None:
    service, repo = _create_test_service()
    rec = _make_test_record(
        id="exe_0123456789abcdef",
        organization_id="org_target",
        created_by="usr_owner",
        status=ExecutionStatus.PASSED,
    )
    repo.set_execution(rec)

    initiator_other = TokenData(id="usr_other", role=UserRole.MEMBER, organization_id="org_other")
    with pytest.raises(PermissionDeniedError):
        await service.reject_evidence_quote(initiator_other, "exe_0123456789abcdef", "evq_1", "Wrong quote")

    initiator_root = TokenData(id="usr_root", role=UserRole.ROOT, organization_id="org_other")
    await service.reject_evidence_quote(initiator_root, "exe_0123456789abcdef", "evq_1", "Wrong quote")
    assert repo.get_call_count("append_trace_event") >= 1


@pytest.mark.asyncio
async def test_get_sdui_view_branches() -> None:
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ROOT)
    mock_dto = Mock(spec=ReportDataDTO)
    mock_dto.inner_sdui_blocks = [MarkdownBlock(text="Synthetic Overview Title")]
    with patch.object(service, "get_report_dto", return_value=mock_dto):
        mock_view = Mock(spec=ReportView)
        mock_view.title = "Synthetic Overview Title"
        mock_view.model_copy.return_value = mock_view
        with patch(
            "backend_v2.services.sdui_mapper_service.SduiMapperService.map_report_to_sdui", return_value=mock_view
        ):
            view_dict = await service.get_sdui_view(initiator, "exe_0123456789abcdef")
            assert view_dict.title == "Synthetic Overview Title"


@pytest.mark.asyncio
async def test_render_execution_html_and_unsupported_formats() -> None:
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ROOT)
    wf = _make_test_workflow(default_profile_id="prf_0123456789abcdef")
    repo.set_workflow(wf)
    prof = _make_test_profile(profile_id="prf_0123456789abcdef", workflow_id="wor_0123456789abcdef")
    repo.set_output_profiles([prof])

    rec = _make_test_record(
        id="exe_0123456789abcdef",
        organization_id="org_1",
        workflow_id="wor_0123456789abcdef",
        target_locale="en",
        status=ExecutionStatus.PASSED,
        profile_syntheses={"prf_0123456789abcdef": {}},
    )
    repo.set_execution(rec)

    with pytest.raises(AppException) as exc_info:
        await service.render_execution(
            initiator=initiator,
            execution_id="exe_0123456789abcdef",
            format_type="docx",
            profile_id="prf_0123456789abcdef",
            accept_language="en",
            arq_pool=AsyncMock(),
        )
    assert exc_info.value.status_code == 400
    assert "Unsupported format" in exc_info.value.message

    with (
        patch(
            "backend_v2.services.blueprint.BlueprintTransformer.build_report_dto", return_value=Mock(spec=ReportDataDTO)
        ),
        patch(
            "backend_v2.services.pdf_generator.PdfReportService.generate_execution_html",
            return_value="<html><body>Report</body></html>",
        ),
    ):
        content_bytes, mime, filename = await service.render_execution(
            initiator=initiator,
            execution_id="exe_0123456789abcdef",
            format_type="html",
            profile_id="prf_0123456789abcdef",
            accept_language="en",
            arq_pool=AsyncMock(),
        )
        assert mime == "text/html"
        assert filename == "execution_exe_0123456789abcdef.html"
        assert b"<html>" in content_bytes


@pytest.mark.asyncio
async def test_render_execution_pdf_pregenerated_and_fresh_saved() -> None:
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ROOT)
    wf = _make_test_workflow(default_profile_id="prf_0123456789abcdef")
    repo.set_workflow(wf)
    prof = _make_test_profile(profile_id="prf_0123456789abcdef", workflow_id="wor_0123456789abcdef")
    repo.set_output_profiles([prof])

    rec = _make_test_record(
        id="exe_0123456789abcdef",
        organization_id="org_1",
        workflow_id="wor_0123456789abcdef",
        target_locale="en",
        status=ExecutionStatus.PASSED,
        profile_syntheses={"prf_0123456789abcdef": {}},
        pdf_report_path="executions/exe_0123456789abcdef/report.pdf",
    )
    repo.set_execution(rec)

    storage_mock = AsyncMock()
    storage_mock.read.return_value = b"%PDF-1.4 pregenerated"
    with patch("backend_v2.services.storage.get_storage_driver", return_value=storage_mock):
        pdf_bytes, mime, filename = await service.render_execution(
            initiator=initiator,
            execution_id="exe_0123456789abcdef",
            format_type="pdf",
            profile_id="prf_0123456789abcdef",
            accept_language="en",
            arq_pool=AsyncMock(),
        )
        assert pdf_bytes == b"%PDF-1.4 pregenerated"
        assert mime == "application/pdf"

    storage_mock.read.side_effect = Exception("Storage disk read error")
    with patch("backend_v2.services.storage.get_storage_driver", return_value=storage_mock):
        with pytest.raises(AppException) as exc_info:
            await service.render_execution(
                initiator=initiator,
                execution_id="exe_0123456789abcdef",
                format_type="pdf",
                profile_id="prf_0123456789abcdef",
                accept_language="en",
                arq_pool=AsyncMock(),
            )
        assert exc_info.value.status_code == 500

    rec_fresh = _make_test_record(
        id="exe_0123456789abcdef",
        organization_id="org_1",
        workflow_id="wor_0123456789abcdef",
        target_locale="en",
        status=ExecutionStatus.PASSED,
        profile_syntheses={"prf_0123456789abcdef": {}},
        pdf_report_path=None,
    )
    repo.set_execution(rec_fresh)
    storage_mock.read.side_effect = None
    storage_mock.save.return_value = "executions/exe_0123456789abcdef/report.pdf"
    with (
        patch("backend_v2.services.storage.get_storage_driver", return_value=storage_mock),
        patch(
            "backend_v2.services.blueprint.BlueprintTransformer.build_report_dto", return_value=Mock(spec=ReportDataDTO)
        ),
        patch(
            "backend_v2.services.pdf_generator.PdfReportService.generate_execution_pdf", return_value=b"%PDF-1.4 fresh"
        ),
    ):
        pdf_bytes, mime, filename = await service.render_execution(
            initiator=initiator,
            execution_id="exe_0123456789abcdef",
            format_type="pdf",
            profile_id="prf_0123456789abcdef",
            accept_language="en",
            arq_pool=AsyncMock(),
        )
        assert pdf_bytes == b"%PDF-1.4 fresh"
        assert mime == "application/pdf"
        assert repo.get_call_count("update_execution") >= 1

    repo.set_execution(rec_fresh)
    storage_mock.save.side_effect = Exception("Storage disk save error")
    with (
        patch("backend_v2.services.storage.get_storage_driver", return_value=storage_mock),
        patch(
            "backend_v2.services.blueprint.BlueprintTransformer.build_report_dto", return_value=Mock(spec=ReportDataDTO)
        ),
        patch(
            "backend_v2.services.pdf_generator.PdfReportService.generate_execution_pdf", return_value=b"%PDF-1.4 fresh"
        ),
    ):
        with pytest.raises(AppException) as exc_info:
            await service.render_execution(
                initiator=initiator,
                execution_id="exe_0123456789abcdef",
                format_type="pdf",
                profile_id="prf_0123456789abcdef",
                accept_language="en",
                arq_pool=AsyncMock(),
            )
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_render_execution_on_demand_synthesis_enqueues_job() -> None:
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ROOT)
    wf = _make_test_workflow(default_profile_id="prf_ondemand")
    repo.set_workflow(wf)

    rec = _make_test_record(
        id="exe_0123456789abcdef",
        organization_id="org_1",
        workflow_id="wor_0123456789abcdef",
        target_locale="en",
        status=ExecutionStatus.PASSED,
        profile_syntheses={},
    )
    repo.set_execution(rec)

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
    storage_mock = AsyncMock()
    service, repo = _create_test_service(storage_driver=storage_mock)

    rec = _make_test_record(
        id="exe_0123456789abcdef",
        organization_id="org_1",
        created_by="usr_owner",
        status=ExecutionStatus.PASSED,
    )
    repo.set_execution(rec)

    initiator_other = TokenData(id="usr_other", role=UserRole.MEMBER, organization_id="org_other")
    with pytest.raises(PermissionDeniedError):
        await service.delete_execution(initiator_other, "exe_0123456789abcdef")

    initiator = TokenData(id="usr_owner", role=UserRole.MEMBER, organization_id="org_1")

    storage_mock.delete_directory.side_effect = AppException("Not found", status_code=404)
    deleted = await service.delete_execution(initiator, "exe_0123456789abcdef")
    assert deleted is True

    repo.set_execution(rec)
    storage_mock.delete_directory.side_effect = AppException("Storage error", status_code=500)
    with pytest.raises(AppException) as exc_info:
        await service.delete_execution(initiator, "exe_0123456789abcdef")
    assert exc_info.value.status_code == 500

    repo.set_execution(rec)
    storage_mock.delete_directory.side_effect = Exception("Generic disk crash")
    with pytest.raises(AppException) as exc_info:
        await service.delete_execution(initiator, "exe_0123456789abcdef")
    assert exc_info.value.status_code == 500

    repo.set_execution(rec)
    storage_mock.delete_directory.side_effect = None
    repo.inject_fault("delete_execution", Exception("DB crash"))
    with pytest.raises(AppException) as exc_info:
        await service.delete_execution(initiator, "exe_0123456789abcdef")
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_clear_profile_synthesis_storage_delete_branches() -> None:
    service, repo = _create_test_service()
    rec = _make_test_record(
        id="exe_0123456789abcdef",
        organization_id="org_1",
        status=ExecutionStatus.PASSED,
        workflow_id="wor_0123456789abcdef",
        pdf_report_path="executions/exe_0123456789abcdef/report.pdf",
        profile_syntheses={"prf_default": {}},
    )
    repo.set_execution(rec)

    wf = _make_test_workflow(default_profile_id="prf_default")
    repo.set_workflow(wf)
    initiator = TokenData(id="usr_root", role=UserRole.ROOT)

    storage_mock = AsyncMock()
    service._override.storage = storage_mock

    storage_mock.delete.side_effect = AppException("Not found", status_code=404)
    with patch("backend_v2.services.storage.get_storage_driver", return_value=storage_mock):
        await service.clear_profile_synthesis(initiator, "exe_0123456789abcdef", "prf_default")
        assert repo.get_call_count("update_execution") >= 1

    repo.set_execution(rec)
    storage_mock.delete.side_effect = AppException("Conflict", status_code=409)
    with patch("backend_v2.services.storage.get_storage_driver", return_value=storage_mock):
        with pytest.raises(AppException) as exc_info:
            await service.clear_profile_synthesis(initiator, "exe_0123456789abcdef", "prf_default")
        assert exc_info.value.status_code == 409

    repo.set_execution(rec)
    storage_mock.delete.side_effect = AppException("Server Error", status_code=500)
    with patch("backend_v2.services.storage.get_storage_driver", return_value=storage_mock):
        with pytest.raises(AppException) as exc_info:
            await service.clear_profile_synthesis(initiator, "exe_0123456789abcdef", "prf_default")
        assert exc_info.value.status_code == 500

    repo.set_execution(rec)
    storage_mock.delete.side_effect = Exception("Unexpected")
    with patch("backend_v2.services.storage.get_storage_driver", return_value=storage_mock):
        with pytest.raises(AppException) as exc_info:
            await service.clear_profile_synthesis(initiator, "exe_0123456789abcdef", "prf_default")
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_override_atom_branches() -> None:
    service, repo = _create_test_service()
    rec = _make_test_record(
        id="exe_0123456789abcdef",
        organization_id="org_1",
        created_by="usr_owner",
        status=ExecutionStatus.PASSED,
        step_states={},
    )
    repo.set_execution(rec)

    initiator_other = TokenData(id="usr_other", role=UserRole.MEMBER, organization_id="org_other")
    req = HumanOverrideRequest(new_status=ExecutionStatus.PASSED, reason="Valid evidence found")
    with pytest.raises(PermissionDeniedError):
        await service.override_atom(initiator_other, "exe_0123456789abcdef", "atm_1", req)

    initiator = TokenData(id="usr_owner", role=UserRole.MEMBER, organization_id="org_1")
    with pytest.raises(AppException) as exc_info:
        await service.override_atom(initiator, "exe_0123456789abcdef", "atm_1", req)
    assert exc_info.value.status_code == 404

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
    rec_with_atoms = _make_test_record(
        id="exe_0123456789abcdef",
        organization_id="org_1",
        created_by="usr_owner",
        status=ExecutionStatus.PASSED,
        step_states={"stp_1": step_state},
        context_variables=ContextVariablesDTO(
            variables={
                "var_1": EvaluatedMatrixContextDTO(
                    evaluated_atoms={"atm_1": "FAIL"},
                    raw_atoms=[EvaluatedAtomDTO(tda_id="atm_1", human_override=None)],
                )
            }
        ),
        active_profile_id="prf_1",
    )
    repo.set_execution(rec_with_atoms)

    with patch("backend_v2.hooks.scoring.recalculate", return_value=rec_with_atoms.context_variables):
        await service.override_atom(initiator, "exe_0123456789abcdef", "atm_1", req)
        assert repo.get_call_count("update_execution") >= 1
        assert repo.get_call_count("append_trace_event") >= 1


@pytest.mark.asyncio
async def test_start_execution_additional_error_branches() -> None:
    service, repo = _create_test_service()
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
    repo.set_workflow(wf)
    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(),
        target_locale="en",
        profile_id="prf_0123456789abcdef",
    )

    with pytest.raises(ConfigurationError):
        await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())

    repo.seed_raw_step("stp_0123456789abcdef", {"invalid": "step"})
    with pytest.raises(AppException) as exc_info:
        await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())
    assert exc_info.value.status_code == 400

    valid_step = Step(
        id="stp_0123456789abcdef",
        slug="step-slug",
        name=I18nText(translations={"en": "Step 1"}),
        description=I18nText(translations={"en": "Step Desc"}),
        role_block_id="blk_0123456789abcdef",
        criteria_block_ids=["blk_0123456789abcdef"],
        extraction_protocol_block_id="blk_0123456789abcdef",
    )
    repo.seed_raw_step("stp_0123456789abcdef", valid_step)
    with pytest.raises(ConfigurationError):
        await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())

    repo.seed_raw_prompt_block("blk_0123456789abcdef", {"invalid": "block"})
    with pytest.raises(AppException) as exc_info:
        await service.start_execution(initiator=initiator, payload=payload, arq_pool=AsyncMock())
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_list_executions_exception_branch() -> None:
    service, repo = _create_test_service()
    repo.inject_fault("get_all_executions", RuntimeError("DB connection timeout"))
    initiator = TokenData(id="usr_root", role=UserRole.ROOT)
    with pytest.raises(AppException) as exc_info:
        await service.list_executions(initiator=initiator)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_report_dto_not_passed() -> None:
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_root", role=UserRole.ROOT)
    rec = _make_test_record(id="exe_0123456789abcdef", status=ExecutionStatus.FAILED)
    repo.set_execution(rec)

    with pytest.raises(AppException) as exc_info:
        await service.get_report_dto(initiator, "exe_0123456789abcdef")
    assert exc_info.value.status_code == 400
    assert "Execution is not in COMPLETED state" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_execution_export_bytes_error_branches() -> None:
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_root", role=UserRole.ROOT)
    rec = _make_test_record(id="exe_0123456789abcdef", status=ExecutionStatus.FAILED)
    repo.set_execution(rec)

    with pytest.raises(AppException) as exc_info:
        await service.get_execution_export_bytes(initiator, "exe_0123456789abcdef")
    assert exc_info.value.status_code == 400
    assert "Execution must be in PASSED state" in exc_info.value.message


@pytest.mark.asyncio
async def test_resume_execution_quota_exceeded() -> None:
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_1", role=UserRole.MEMBER, organization_id="org_overquota")
    rec = _make_test_record(
        id="exe_0123456789abcdef",
        status=ExecutionStatus.FAILED,
        organization_id="org_overquota",
        created_by="usr_1",
    )
    repo.set_execution(rec)

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
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ROOT)
    rec = _make_test_record(id="exe_0123456789abcdef", workflow_id="wor_missing", status=ExecutionStatus.PASSED)
    repo.set_execution(rec)

    with pytest.raises(AppException) as exc_info:
        await service.render_execution(
            initiator=initiator,
            execution_id="exe_0123456789abcdef",
            format_type="html",
            profile_id="prf_0123456789abcdef",
            accept_language="en",
            arq_pool=AsyncMock(),
        )
    assert exc_info.value.status_code == 500
    assert "Workflow not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_execution_export_bytes_report_fetch_error() -> None:
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_root", role=UserRole.ROOT)
    step_state = ExecutionStepState(
        id="stp_1",
        label="Step 1",
        status=ExecutionStatus.PASSED,
        scorecard_atoms={
            "atm_1": ScorecardAtomDTO(
                atom_id="atm_1",
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
    rec = _make_test_record(id="exe_0123456789abcdef", status=ExecutionStatus.PASSED, step_states={"stp_1": step_state})
    repo.set_execution(rec)

    with patch.object(service, "get_report_dto", side_effect=RuntimeError("Report crash")):
        with pytest.raises(AppException) as exc_info:
            await service.get_execution_export_bytes(initiator, "exe_0123456789abcdef")
        assert exc_info.value.status_code == 500
        assert "Report Fetch Error" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_execution_export_bytes_excel_writer_error() -> None:
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_root", role=UserRole.ROOT)
    step_state = ExecutionStepState(
        id="stp_1",
        label="Step 1",
        status=ExecutionStatus.PASSED,
        scorecard_atoms={
            "atm_1": ScorecardAtomDTO(
                atom_id="atm_1",
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
    rec = _make_test_record(id="exe_0123456789abcdef", status=ExecutionStatus.PASSED, step_states={"stp_1": step_state})
    repo.set_execution(rec)

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
        hydrated_references={
            "tda_1": HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Claim 1",
            )
        },
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
    service, repo = _create_test_service()
    rec = _make_test_record(
        status=ExecutionStatus.FAILED,
        metadata={"workflow_version": "1"},
        step_states={"stp_1": ExecutionStep(id="stp_1", label="Step 1", status=ExecutionStatus.FAILED)},
    )

    wf = _make_test_workflow(
        version=2,
        steps=[StepRule(id="stp_0123456789abcdef", task_blueprint="stp_0123456789abcdef")],
    )
    repo.set_workflow(wf)
    res = await service.check_resumability(rec)
    assert res is False


@pytest.mark.asyncio
async def test_render_execution_on_demand_synthesis_with_updated_at_and_vstep() -> None:
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_0123456789abcdef", role=UserRole.ROOT)
    wf = _make_test_workflow(default_profile_id="prf_ondemand")
    repo.set_workflow(wf)

    v_step_id = "sys_render_prf_ondemand"
    rec = _make_test_record(
        id="exe_0123456789abcdef",
        status=ExecutionStatus.PASSED,
        organization_id="org_1",
        workflow_id="wor_0123456789abcdef",
        target_locale="en",
        profile_syntheses={},
        step_states={v_step_id: ExecutionStep(id=v_step_id, label="Rendering PDF...", status=ExecutionStatus.RUNNING)},
        updated_at=datetime.now(timezone.utc),
    )
    repo.set_execution(rec)

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
    service, repo = _create_test_service()
    initiator = TokenData(id="usr_owner", role=UserRole.MEMBER, organization_id="org_quota_tripped")
    wf = _make_test_workflow(organization_id="org_quota_tripped")
    repo.set_workflow(wf)
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
    service, repo = _create_test_service()
    service.usage_service.check_quota.return_value = True

    wf = _make_test_workflow()
    repo.set_workflow(wf)

    mismatch_profile = OutputProfile(
        id="prf_0123456789abcdef",
        slug="other-profile",
        workflow_id="wor_other_workflow",
        name=I18nText(translations={"en": "Other Profile"}),
        description=I18nText(translations={"en": "Desc"}),
        target_block_order=[],
    )
    repo.set_output_profiles([mismatch_profile])

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
    """ISTQB Negative: start_execution raises 404 RESOURCE_NOT_FOUND when
    neither payload nor workflow has model_registry_id.
    """
    service, repo = _create_test_service()
    service.usage_service.check_quota.return_value = True

    repo.seed_raw_workflow("wor_0123456789abcdef", {"id": "wor_0123456789abcdef"})

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(),
        target_locale="en",
    )
    initiator = TokenData(id="u1", role=UserRole.MEMBER, organization_id="org_1")

    mock_wf = Workflow.model_construct(
        id="wor_0123456789abcdef",
        version=1,
        status="ACTIVE",
        default_profile_id=None,
        model_registry_id=None,
        expected_inputs=[],
        steps=[],
        organization_id="org_1",
        is_public=False,
    )

    with patch("backend_v2.models.domain.workflow.Workflow.model_validate", return_value=mock_wf):
        with pytest.raises(AppException) as exc_info:
            await service.start_execution(initiator, payload, AsyncMock())
    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == "RESOURCE_NOT_FOUND"
    assert "No model_registry_id provided" in exc_info.value.message


@pytest.mark.asyncio
async def test_start_execution_fails_fast_when_registry_obj_is_none() -> None:
    """ISTQB Negative: start_execution raises 404 RESOURCE_NOT_FOUND when get_model_registry returns None."""
    service, repo = _create_test_service()
    service.usage_service.check_quota.return_value = True

    wf = _make_test_workflow(default_profile_id=None, model_registry_id="sys_e26807f3bfa3454d")
    repo.set_workflow(wf)
    repo.set_model_registry(None)

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
    service, repo = _create_test_service()
    wf = _make_test_workflow(version=2, default_profile_id=None)
    repo.set_workflow(wf)

    rec_drift = _make_test_record(
        status=ExecutionStatus.FAILED,
        workflow_version=1,
    )

    can_resume_drift = await service.check_resumability(rec_drift)
    assert can_resume_drift is False

    rec_quota = _make_test_record(
        status=ExecutionStatus.FAILED,
        workflow_version=2,
    )
    service.usage_service.check_quota.return_value = False

    can_resume_quota = await service.check_resumability(rec_quota)
    assert can_resume_quota is False


@pytest.mark.asyncio
async def test_override_atom_and_reject_evidence_permission_denied() -> None:
    """ISTQB Negative: override_atom and reject_evidence_quote raise PermissionDeniedError for non-owner non-root."""
    service, repo = _create_test_service()
    rec = _make_test_record(
        id="exe_1234567890abcdef",
        organization_id="org_other",
        created_by="usr_other",
    )
    repo.set_execution(rec)

    initiator = TokenData(id="usr_stranger", role=UserRole.MEMBER, organization_id="org_mine")

    with pytest.raises(PermissionDeniedError):
        await service.override_atom(initiator, "exe_1234567890abcdef", "atom_1", Mock())

    with pytest.raises(PermissionDeniedError):
        await service.reject_evidence_quote(initiator, "exe_1234567890abcdef", "evq_1", "invalid quote")


@pytest.mark.asyncio
async def test_stream_status_handles_app_exception_interrupted() -> None:
    """Test stream_status handles AppException/OSError during polling by yielding error event."""
    service, repo = _create_test_service()
    rec = _make_test_record(
        id="exe_0000000000000000",
        organization_id="org_test",
        created_by="usr_owner",
    )

    service.get_execution = AsyncMock(side_effect=[rec, OSError("Connection dropped")])  # type: ignore[assignment]

    initiator = TokenData(id="usr_owner", role=UserRole.ADMIN, organization_id="org_test")
    events = [event async for event in service.stream_status(initiator, "exe_0000000000000000")]
    assert len(events) == 1
    assert "event: error" in events[0]
    assert "SSE_STREAM_INTERRUPTED" in events[0]
