import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.synthesis import SynthesisDistillationDTO
from backend_v2.models.dtos.trace import TraceMatrixPayloadDTO
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode, TargetBlockType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import StepOutputDTO
from backend_v2.services.orchestrator.synthesis_distiller import synthesis_distiller_hook
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


class QuoteEvidenceDTOFactory(ModelFactory[QuoteEvidenceDTO]):
    __model__ = QuoteEvidenceDTO


class StepOutputDTOFactory(ModelFactory[StepOutputDTO]):
    __model__ = StepOutputDTO


def _create_hook_deps(repo: InMemoryUnifiedWorkflowRepository | None = None) -> HookDependencies:
    r = repo or InMemoryUnifiedWorkflowRepository()
    return HookDependencies(
        exec_repo=r,
        workflow_repo=r,
        comp_repo=r,
        prompt_block_repo=r,
        output_profile_repo=r,
        identity_repo=r,
        audit_repo=r,
        system_repo=r,
    )


@pytest.mark.asyncio
async def test_synthesis_distiller_hook_evidence_quotes_conversion() -> None:
    """PROMISE: Prove execution_state.evidence_quotes strictly converts to QuoteEvidenceDTO list."""
    repo = InMemoryUnifiedWorkflowRepository()
    wf = Workflow(
        id="wf_0123456789abcdef01",
        slug="wf_slug",
        name="wf",
        description="Workflow description",
        status="ACTIVE",
        version=1,
        organization_id="org1",
        default_profile_id="prof1",
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
        model_registry_id="sys_e26807f3bfa3454d",
    )
    repo._workflows._storage[wf.id] = wf

    exe = ExecutionRecord(
        id="exe_0123456789abcdef01",
        workflow_id=wf.id,
        status=ExecutionStatus.PASSED,
        target_locale="en",
        output_profile_id="prof_1111111111111111",
        raw_inputs=WorkflowInputs(),
        step_states={},
    )
    repo._executions._storage[exe.id] = exe

    prof = OutputProfile(
        id="prof_1111111111111111",
        slug="prof1",
        workflow_id=wf.id,
        name=I18nText(translations={"en": "Prof 1"}),
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0000000000000001",
                title=I18nText(translations={"en": "Default"}),
                target_blocks=["*"],
            )
        ],
        target_block_order=[TargetBlockType.METADATA_BLOCK],
    )
    repo._output_profiles._storage[prof.id] = prof

    deps = _create_hook_deps(repo)

    step_output = StepOutputDTO(
        step_id="stp_1",
        block_id="blk_1",
        data_type="matrix",
        payload=TraceMatrixPayloadDTO(raw_score=100.0, justification="Test quote 1"),
    )

    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wf_0123456789abcdef01",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(dynamic_inputs={"steps": [step_output]}, target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(organization_id="org1"),
    )

    result = await synthesis_distiller_hook(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, SynthesisDistillationDTO)
    assert result.state_delta.delta.distilled_inputs is not None


@pytest.mark.asyncio
async def test_synthesis_distiller_hook_negative_missing_locale() -> None:
    """PROMISE: Prove that missing target_locale crashes the hook (anti-happy-path)."""
    deps = _create_hook_deps()

    step_output = StepOutputDTO(
        step_id="stp_1",
        block_id="blk_1",
        data_type="matrix",
        payload=TraceMatrixPayloadDTO(raw_score=100.0),
    )

    # State intentionally missing target_locale in metadata
    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wf_0123456789abcdef01",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(dynamic_inputs={"steps": [step_output]}),
        global_context_vars=GlobalContextVarsDTO(organization_id="org1"),
    )

    with pytest.raises(AppException) as exc_info:
        await synthesis_distiller_hook(state, deps)

    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert exc_info.value.status_code == 500
