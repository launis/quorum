"""Unit tests for ExecutionIngressService and create_execution_record factory."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import AppException, ConfigurationError, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionCreate, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs, WorkflowInputsIngress
from backend_v2.models.domain.matrix import MatrixScale
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PersonaPromptBlock, ProtocolPromptBlock
from backend_v2.models.domain.step import ExpectedInput, Step, StepRule
from backend_v2.models.domain.system_config import SystemValidationRulesDTO
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.telemetry import TraceContextCarrierDTO
from backend_v2.models.enums import ComponentType, HistoricalContextMode, PromptBlockCategory, StepType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.execution.ingress_service import (
    ExecutionIngressService,
    _generate_sdui_hints,
    create_execution_record,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryBlueprintTransformerRepository


@pytest.fixture
def initiator() -> TokenData:
    """Fixture providing standard user token data."""
    return TokenData(id="usr_0123456789abcdef", role=UserRole.MEMBER, organization_id="org_0123456789abcdef")


def _create_test_workflow() -> Workflow:
    return Workflow(
        id="wor_0123456789abcdef",
        slug="test-workflow",
        name="Test Workflow",
        description="Test Workflow Description",
        status="active",
        version=1,
        default_strictness_level=50,
        model_registry_id="sys_e26807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        expected_inputs=[
            ExpectedInput(
                input_key="chat_log",
                label=I18nText(translations={"en": "Chat Log", "fi": "Keskustelu"}),
                required=True,
                is_chat_history=True,
                input_modes=["file", "paste"],
                description=I18nText(translations={"en": "Chat Log", "fi": "Keskustelu"}),
            )
        ],
        steps=[
            StepRule(
                id="stp_0123456789abcdef",
                task_blueprint="stp_0123456789abcdef",
            )
        ],
        default_profile_id="prf_0123456789abcdef",
        organization_id="org_0123456789abcdef",
        is_public=False,
    )


def test_create_execution_record_injects_w3c_telemetry() -> None:
    """Verify create_execution_record attaches trace context to record.metadata.telemetry."""
    record = create_execution_record(
        execution_id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
    )

    assert record.metadata is not None
    assert record.metadata.telemetry is not None
    assert record.metadata.telemetry.traceparent.startswith("00-")


def test_create_execution_record_preserves_custom_carrier() -> None:
    """Verify custom carrier in metadata is preserved rather than overwritten."""
    custom = TraceContextCarrierDTO(traceparent="00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01")
    meta = ExecutionMetadata(telemetry=custom)
    record = create_execution_record(
        execution_id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        metadata=meta,
    )

    assert record.metadata is not None
    assert record.metadata.telemetry == custom


def test_create_execution_record_handles_dict_metadata() -> None:
    """Verify dictionary metadata is converted and injected with trace context."""
    record = create_execution_record(
        execution_id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        metadata={"workflow_version": 2},  # type: ignore[arg-type]
    )

    assert record.metadata is not None
    assert record.metadata.workflow_version == 2
    assert record.metadata.telemetry is not None


def test_create_execution_record_validation_failure() -> None:
    """Verify invalid parameters trigger Fail-Fast AppException."""
    with pytest.raises(AppException) as exc_info:
        create_execution_record(
            execution_id="invalid_id",  # Invalid ID pattern
            workflow_id="wor_0123456789abcdef",
            raw_inputs=WorkflowInputs(),
            frozen_context=FrozenContext(),
            source_identity_manifest={},
        )
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_workflow_ui_schema() -> None:
    """Verify get_workflow_ui_schema returns expected inputs or raises 404."""
    workflow = _create_test_workflow()
    workflow_repo = InMemoryBlueprintTransformerRepository()
    workflow_repo.get_workflow_by_id.return_value = workflow.model_dump()

    service = ExecutionIngressService(
        exec_repo=InMemoryBlueprintTransformerRepository(),
        workflow_repo=workflow_repo,
    )

    schema = await service.get_workflow_ui_schema("wor_0123456789abcdef")
    assert len(schema.expected_inputs) == 1
    assert schema.expected_inputs[0].input_key == "chat_log"

    workflow_repo.get_workflow_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await service.get_workflow_ui_schema("wor_0123456789abcdef")


@pytest.mark.asyncio
async def test_generate_sdui_hints_and_matrix_scales() -> None:
    """Verify _generate_sdui_hints correctly extracts component types and scale extrema."""
    workflow = _create_test_workflow()

    step_obj = Step(
        id="stp_0123456789abcdef",
        slug="analytical-step",
        name=I18nText(translations={"en": "Analytical Step", "fi": "Analyysi"}),
        type=StepType.LOGIC,
        hook="my_hook",
        role_block_id="blk_0123456789abcdef",
        extraction_protocol_block_id="blk_1123456789abcdef",
        criteria_block_ids=["blk_2123456789abcdef"],
    )

    role_block = PersonaPromptBlock(
        id="blk_0123456789abcdef",
        slug="role-block",
        category_id=PromptBlockCategory.AGENT_ROLE,
        label=I18nText(translations={"en": "Role Block"}),
        description=I18nText(translations={"en": "Role Description"}),
    )
    protocol_block = ProtocolPromptBlock(
        id="blk_1123456789abcdef",
        slug="protocol-block",
        category_id=PromptBlockCategory.PROTOCOL,
        label=I18nText(translations={"en": "Protocol Block"}),
        description=I18nText(translations={"en": "Protocol Description"}),
    )
    matrix_block = MatrixPromptBlock(
        id="blk_2123456789abcdef",
        slug="matrix-block",
        category_id=PromptBlockCategory.MATRIX,
        label=I18nText(translations={"en": "Matrix Block"}),
        description=I18nText(translations={"en": "Matrix Description"}),
        scales=[
            MatrixScale(score=1, ai_label="LOW"),
            MatrixScale(score=5, ai_label="HIGH"),
        ],
    )

    workflow_repo = InMemoryBlueprintTransformerRepository()
    workflow_repo.get_step_by_id.return_value = step_obj.model_dump()

    prompt_block_repo = InMemoryBlueprintTransformerRepository()

    async def mock_get_pb(pb_id: str) -> dict[str, Any] | None:
        if pb_id == "blk_0123456789abcdef":
            return role_block.model_dump()
        if pb_id == "blk_1123456789abcdef":
            return protocol_block.model_dump()
        if pb_id == "blk_2123456789abcdef":
            return matrix_block.model_dump()
        return None

    prompt_block_repo.get_prompt_block_by_id.side_effect = mock_get_pb

    hints_dto = await _generate_sdui_hints(
        workflow=workflow,
        prompt_block_repo=prompt_block_repo,
        workflow_repo=workflow_repo,
        target_locale="en",
    )
    ui_hints = hints_dto.ui_hints
    steps = hints_dto.steps
    step_states = hints_dto.step_states

    assert len(steps) == 1
    assert len(step_states) == 1
    assert steps[0].id == "stp_0123456789abcdef"
    assert steps[0].label == "Analytical Step"
    assert "blk_2123456789abcdef" in ui_hints
    assert ui_hints["blk_2123456789abcdef"].component_type == ComponentType.SLIDER
    assert ui_hints["blk_2123456789abcdef"].validation_rules == SystemValidationRulesDTO(max=5.0)
    assert ui_hints["blk_0123456789abcdef"].component_type == ComponentType.HIDDEN


@pytest.mark.asyncio
async def test_generate_sdui_hints_missing_step_raises() -> None:
    """Verify _generate_sdui_hints raises ConfigurationError when step blueprint is missing."""
    workflow = _create_test_workflow()
    workflow_repo = InMemoryBlueprintTransformerRepository()
    workflow_repo.get_step_by_id.return_value = None

    with pytest.raises(ConfigurationError):
        await _generate_sdui_hints(
            workflow=workflow,
            prompt_block_repo=InMemoryBlueprintTransformerRepository(),
            workflow_repo=workflow_repo,
            target_locale="en",
        )


@pytest.mark.asyncio
async def test_start_execution_happy_path(initiator: TokenData) -> None:
    """Verify start_execution sets up record with W3C carrier and enqueues job."""
    workflow = _create_test_workflow()

    step_obj = Step(
        id="stp_0123456789abcdef",
        slug="analytical-step",
        name=I18nText(translations={"en": "Analytical Step", "fi": "Analyysi"}),
        type=StepType.LOGIC,
        hook="my_hook",
    )

    profile_obj = OutputProfile(
        id="prf_0123456789abcdef",
        slug="test-profile",
        name=I18nText(translations={"en": "Test Profile"}),
        workflow_id="wor_0123456789abcdef",
        target_block_order=[],
        visible_block_extensions=[],
        visible_workflow_extensions=[],
    )

    exec_repo = InMemoryBlueprintTransformerRepository()

    workflow_repo = InMemoryBlueprintTransformerRepository()
    workflow_repo.get_workflow_by_id.return_value = workflow.model_dump()
    workflow_repo.get_step_by_id.return_value = step_obj.model_dump()

    prompt_block_repo = InMemoryBlueprintTransformerRepository()
    output_profile_repo = InMemoryBlueprintTransformerRepository()
    output_profile_repo.get_output_profile_by_id.return_value = profile_obj.model_dump()

    system_repo = InMemoryBlueprintTransformerRepository()
    system_repo.get_model_registry.return_value = {"id": "sys_e26807f3bfa3454d"}

    usage_service = AsyncMock()
    usage_service.check_quota = AsyncMock(return_value=True)

    arq_pool = AsyncMock()

    service = ExecutionIngressService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        prompt_block_repo=prompt_block_repo,
        output_profile_repo=output_profile_repo,
        system_repo=system_repo,
        usage_service=usage_service,
    )

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputsIngress(dynamic_inputs={"chat_log": "Hello, world!"}),
        target_locale="fi",
        profile_id="prf_0123456789abcdef",
        matrix_sampling_strategy=10,
    )

    record = await service.start_execution(
        initiator=initiator,
        payload=payload,
        arq_pool=arq_pool,
    )

    assert record.id.startswith("exe_")
    assert record.workflow_id == "wor_0123456789abcdef"
    assert record.metadata is not None
    assert record.metadata.telemetry is not None
    assert record.metadata.telemetry.traceparent.startswith("00-")

    # Verify repository call persisted the record with telemetry
    assert exec_repo.create_execution.called
    saved_dto = exec_repo.create_execution.call_args[0][0]
    assert saved_dto.metadata is not None
    assert saved_dto.metadata.telemetry is not None

    # Verify arq background worker received execution_id
    assert arq_pool.enqueue_job.called
    call_kwargs = arq_pool.enqueue_job.call_args[1]
    assert call_kwargs["execution_id"] == record.id
    assert call_kwargs["workflow_id"] == "wor_0123456789abcdef"


@pytest.mark.asyncio
async def test_start_execution_permission_denied(initiator: TokenData) -> None:
    """Verify start_execution rejects access if workflow organization does not match."""
    workflow = _create_test_workflow().model_copy(
        update={"organization_id": "org_other_organization", "is_public": False}
    )

    workflow_repo = InMemoryBlueprintTransformerRepository()
    workflow_repo.get_workflow_by_id.return_value = workflow.model_dump()

    service = ExecutionIngressService(
        exec_repo=InMemoryBlueprintTransformerRepository(),
        workflow_repo=workflow_repo,
    )

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputsIngress(dynamic_inputs={"chat_log": "Hello"}),
        target_locale="fi",
        matrix_sampling_strategy=10,
    )

    with pytest.raises(PermissionDeniedError):
        await service.start_execution(
            initiator=initiator,
            payload=payload,
            arq_pool=AsyncMock(),
        )


@pytest.mark.asyncio
async def test_start_execution_quota_exceeded(initiator: TokenData) -> None:
    """Verify start_execution raises 402 RATE_LIMIT_EXCEEDED when quota is exhausted."""
    workflow = _create_test_workflow()
    workflow_repo = InMemoryBlueprintTransformerRepository()
    workflow_repo.get_workflow_by_id.return_value = workflow.model_dump()

    usage_service = AsyncMock()
    usage_service.check_quota = AsyncMock(return_value=False)

    service = ExecutionIngressService(
        exec_repo=InMemoryBlueprintTransformerRepository(),
        workflow_repo=workflow_repo,
        usage_service=usage_service,
    )

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputsIngress(dynamic_inputs={"chat_log": "Hello"}),
        target_locale="fi",
        matrix_sampling_strategy=10,
    )

    with pytest.raises(AppException) as exc_info:
        await service.start_execution(
            initiator=initiator,
            payload=payload,
            arq_pool=AsyncMock(),
        )
    assert exc_info.value.status_code == 402


@pytest.mark.asyncio
async def test_start_execution_workflow_not_found(initiator: TokenData) -> None:
    """Verify start_execution raises ResourceNotFoundError when workflow does not exist."""
    workflow_repo = InMemoryBlueprintTransformerRepository()
    workflow_repo.get_workflow_by_id.return_value = None

    service = ExecutionIngressService(
        exec_repo=InMemoryBlueprintTransformerRepository(),
        workflow_repo=workflow_repo,
    )

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputsIngress(dynamic_inputs={"chat_log": "Hello"}),
        target_locale="fi",
        matrix_sampling_strategy=10,
    )

    with pytest.raises(ResourceNotFoundError):
        await service.start_execution(
            initiator=initiator,
            payload=payload,
            arq_pool=AsyncMock(),
        )


@pytest.mark.asyncio
async def test_start_execution_missing_dependencies_and_entities(initiator: TokenData) -> None:
    """Verify start_execution Fail-Fast on missing repositories or non-existent configuration entities."""
    workflow = _create_test_workflow()
    workflow_repo = InMemoryBlueprintTransformerRepository()
    workflow_repo.get_workflow_by_id.return_value = workflow.model_dump()

    # Case 1: Missing prompt_block_repo
    service = ExecutionIngressService(
        exec_repo=InMemoryBlueprintTransformerRepository(),
        workflow_repo=workflow_repo,
        prompt_block_repo=None,
    )
    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputsIngress(dynamic_inputs={"chat_log": "Hello"}),
        target_locale="fi",
        matrix_sampling_strategy=10,
    )
    with pytest.raises(AppException) as exc_info:
        await service.start_execution(initiator, payload, AsyncMock())
    assert exc_info.value.status_code == 500

    # Case 2: Missing output_profile_repo when profile requested
    prompt_block_repo = InMemoryBlueprintTransformerRepository()
    step_obj = Step(
        id="stp_0123456789abcdef",
        slug="step-slug",
        name=I18nText(translations={"en": "Analytical Step"}),
        type=StepType.LOGIC,
        hook="my_hook",
    )
    workflow_repo.get_step_by_id.return_value = step_obj.model_dump()

    service_no_profile_repo = ExecutionIngressService(
        exec_repo=InMemoryBlueprintTransformerRepository(),
        workflow_repo=workflow_repo,
        prompt_block_repo=prompt_block_repo,
        output_profile_repo=None,
    )
    with pytest.raises(AppException) as exc_info:
        await service_no_profile_repo.start_execution(initiator, payload, AsyncMock())
    assert exc_info.value.status_code == 500

    # Case 3: Output profile not found
    output_profile_repo = InMemoryBlueprintTransformerRepository()
    output_profile_repo.get_output_profile_by_id.return_value = None
    service_profile_missing = ExecutionIngressService(
        exec_repo=InMemoryBlueprintTransformerRepository(),
        workflow_repo=workflow_repo,
        prompt_block_repo=prompt_block_repo,
        output_profile_repo=output_profile_repo,
    )
    with pytest.raises(AppException) as exc_info:
        await service_profile_missing.start_execution(initiator, payload, AsyncMock())
    assert exc_info.value.status_code == 404

    # Case 4: Output profile workflow mismatch
    mismatched_profile = OutputProfile(
        id="prf_0123456789abcdef",
        slug="mismatch",
        name=I18nText(translations={"en": "Mismatch"}),
        workflow_id="wor_mismatched00000000",
        target_block_order=[],
        visible_block_extensions=[],
        visible_workflow_extensions=[],
    )
    output_profile_repo.get_output_profile_by_id.return_value = mismatched_profile.model_dump()
    service_mismatch = ExecutionIngressService(
        exec_repo=InMemoryBlueprintTransformerRepository(),
        workflow_repo=workflow_repo,
        prompt_block_repo=prompt_block_repo,
        output_profile_repo=output_profile_repo,
    )
    with pytest.raises(AppException) as exc_info:
        await service_mismatch.start_execution(initiator, payload, AsyncMock())
    assert exc_info.value.status_code == 400

    # Case 5: Missing system_repo
    workflow_repo.get_workflow_by_id.return_value = workflow.model_dump()
    matching_profile = OutputProfile(
        id="prf_0123456789abcdef",
        slug="matching",
        name=I18nText(translations={"en": "Matching"}),
        workflow_id="wor_0123456789abcdef",
        target_block_order=[],
        visible_block_extensions=[],
        visible_workflow_extensions=[],
    )
    output_profile_repo.get_output_profile_by_id.return_value = matching_profile.model_dump()
    service_no_sys = ExecutionIngressService(
        exec_repo=InMemoryBlueprintTransformerRepository(),
        workflow_repo=workflow_repo,
        prompt_block_repo=prompt_block_repo,
        output_profile_repo=output_profile_repo,
        system_repo=None,
    )
    with pytest.raises(AppException) as exc_info:
        await service_no_sys.start_execution(initiator, payload, AsyncMock())
    assert exc_info.value.status_code == 500

    # Case 7: Model registry not found
    system_repo = InMemoryBlueprintTransformerRepository()
    system_repo.get_model_registry.return_value = None
    service_reg_missing = ExecutionIngressService(
        exec_repo=InMemoryBlueprintTransformerRepository(),
        workflow_repo=workflow_repo,
        prompt_block_repo=prompt_block_repo,
        output_profile_repo=output_profile_repo,
        system_repo=system_repo,
    )
    with pytest.raises(AppException) as exc_info:
        await service_reg_missing.start_execution(initiator, payload, AsyncMock())
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_generate_sdui_hints_invalid_step_format_raises() -> None:
    """Verify _generate_sdui_hints raises AppException when step blueprint fails Pydantic validation."""
    workflow = _create_test_workflow()
    workflow_repo = InMemoryBlueprintTransformerRepository()
    workflow_repo.get_step_by_id.return_value = {"id": "invalid_id_not_matching_step_schema"}

    with pytest.raises(AppException) as exc_info:
        await _generate_sdui_hints(
            workflow=workflow,
            prompt_block_repo=InMemoryBlueprintTransformerRepository(),
            workflow_repo=workflow_repo,
            target_locale="en",
        )
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_generate_sdui_hints_missing_and_invalid_prompt_block_raises() -> None:
    """Verify _generate_sdui_hints raises ConfigurationError on missing PB and AppException on malformed PB."""
    workflow = _create_test_workflow()
    step_obj = Step(
        id="stp_0123456789abcdef",
        slug="analytical-step",
        name=I18nText(translations={"en": "Analytical Step"}),
        type=StepType.LOGIC,
        hook="my_hook",
        role_block_id="blk_0123456789abcdef",
    )
    workflow_repo = InMemoryBlueprintTransformerRepository()
    workflow_repo.get_step_by_id.return_value = step_obj.model_dump()
    prompt_block_repo = InMemoryBlueprintTransformerRepository()
    prompt_block_repo.get_prompt_block_by_id.return_value = None

    # Missing PB raises ConfigurationError
    with pytest.raises(ConfigurationError):
        await _generate_sdui_hints(
            workflow=workflow,
            prompt_block_repo=prompt_block_repo,
            workflow_repo=workflow_repo,
            target_locale="en",
        )

    # Malformed PB raises AppException(status_code=500)
    prompt_block_repo.get_prompt_block_by_id.return_value = {"id": "invalid_not_prompt_block"}
    with pytest.raises(AppException) as exc_info:
        await _generate_sdui_hints(
            workflow=workflow,
            prompt_block_repo=prompt_block_repo,
            workflow_repo=workflow_repo,
            target_locale="en",
        )
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_start_execution_with_doc_service(initiator: TokenData) -> None:
    """Verify start_execution invokes doc_service.process_ingress_payload when provided."""
    workflow = _create_test_workflow()
    step_obj = Step(
        id="stp_0123456789abcdef",
        slug="analytical-step",
        name=I18nText(translations={"en": "Analytical Step"}),
        type=StepType.LOGIC,
        hook="my_hook",
    )
    workflow_repo = InMemoryBlueprintTransformerRepository()
    workflow_repo.get_workflow_by_id.return_value = workflow.model_dump()
    workflow_repo.get_step_by_id.return_value = step_obj.model_dump()

    prompt_block_repo = InMemoryBlueprintTransformerRepository()
    output_profile_repo = InMemoryBlueprintTransformerRepository()
    output_profile_repo.get_output_profile_by_id.return_value = OutputProfile(
        id="prf_0123456789abcdef",
        slug="test-profile",
        name=I18nText(translations={"en": "Test Profile"}),
        workflow_id="wor_0123456789abcdef",
        target_block_order=[],
        visible_block_extensions=[],
        visible_workflow_extensions=[],
    ).model_dump()

    system_repo = InMemoryBlueprintTransformerRepository()
    system_repo.get_model_registry.return_value = {"id": "sys_e26807f3bfa3454d"}

    service = ExecutionIngressService(
        exec_repo=InMemoryBlueprintTransformerRepository(),
        workflow_repo=workflow_repo,
        prompt_block_repo=prompt_block_repo,
        output_profile_repo=output_profile_repo,
        system_repo=system_repo,
    )

    doc_service = AsyncMock()
    processed_ingress = WorkflowInputsIngress(dynamic_inputs={"chat_log": "Extracted text"})
    doc_service.process_ingress_payload = AsyncMock(return_value=processed_ingress)

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputsIngress(dynamic_inputs={"chat_log": "Raw input"}),
        target_locale="en",
    )

    record = await service.start_execution(
        initiator=initiator,
        payload=payload,
        arq_pool=AsyncMock(),
        doc_service=doc_service,
    )
    assert record.raw_inputs.dynamic_inputs["chat_log"] == "Extracted text"
    assert doc_service.process_ingress_payload.called


@pytest.mark.asyncio
async def test_start_execution_missing_model_registry_id_raises(initiator: TokenData) -> None:
    """Verify start_execution raises 404 when model_registry_id resolves to empty."""
    workflow = _create_test_workflow()
    step_obj = Step(
        id="stp_0123456789abcdef",
        slug="analytical-step",
        name=I18nText(translations={"en": "Analytical Step"}),
        type=StepType.LOGIC,
        hook="my_hook",
    )
    workflow_repo = InMemoryBlueprintTransformerRepository()
    workflow_repo.get_workflow_by_id.return_value = workflow.model_dump()
    workflow_repo.get_step_by_id.return_value = step_obj.model_dump()

    prompt_block_repo = InMemoryBlueprintTransformerRepository()
    output_profile_repo = InMemoryBlueprintTransformerRepository()
    output_profile_repo.get_output_profile_by_id.return_value = OutputProfile(
        id="prf_0123456789abcdef",
        slug="test-profile",
        name=I18nText(translations={"en": "Test Profile"}),
        workflow_id="wor_0123456789abcdef",
        target_block_order=[],
        visible_block_extensions=[],
        visible_workflow_extensions=[],
    ).model_dump()

    service = ExecutionIngressService(
        exec_repo=InMemoryBlueprintTransformerRepository(),
        workflow_repo=workflow_repo,
        prompt_block_repo=prompt_block_repo,
        output_profile_repo=output_profile_repo,
        system_repo=InMemoryBlueprintTransformerRepository(),
    )

    payload = ExecutionCreate(
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputsIngress(dynamic_inputs={"chat_log": "Hello"}),
        target_locale="en",
        model_registry_id="",
    )

    with pytest.raises(AppException) as exc_info:
        await service.start_execution(initiator, payload, AsyncMock())
    assert exc_info.value.status_code == 404
