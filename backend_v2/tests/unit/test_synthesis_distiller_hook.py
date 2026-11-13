"""Unit tests for synthesis_distiller_hook state compression and Fail-Fast validation."""

from __future__ import annotations

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.dtos.synthesis import SynthesisDistillationDTO
from backend_v2.models.dtos.trace import TraceMatrixPayloadDTO
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode, TargetBlockType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import StepOutputDTO
from backend_v2.services.orchestrator.synthesis_distiller import synthesis_distiller_hook
from backend_v2.tests.factories.model_factories import (
    ExecutionRecordFactory,
    OutputProfileFactory,
    WorkflowFactory,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _create_hook_deps(repo: InMemoryUnifiedWorkflowRepository | None = None) -> HookDependencies:
    """Instantiate HookDependencies wired to an InMemoryUnifiedWorkflowRepository.

    Args:
        repo: Optional pre-seeded InMemoryUnifiedWorkflowRepository.

    Returns:
        Configured HookDependencies instance.
    """
    r = repo if repo is not None else InMemoryUnifiedWorkflowRepository()
    return HookDependencies(
        exec_repo=r,
        workflow_repo=r,
        prompt_block_repo=r,
        output_profile_repo=r,
        identity_repo=r,
        audit_repo=r,
        system_repo=r,
    )


@pytest.mark.asyncio
async def test_synthesis_distiller_hook_evidence_quotes_conversion() -> None:
    """Verify synthesis_distiller_hook compresses matrix step outputs into SynthesisDistillationDTO."""
    repo = InMemoryUnifiedWorkflowRepository()
    wf_id = "wf_0195f3a00000700283456789abcdef01"
    exe_id = "exe_0195f3a00000700283456789abcdef01"
    prof_id = "prof_0195f3a0000070018111111111111111"

    wf = WorkflowFactory.build(
        id=wf_id,
        slug="wf_slug",
        status="ACTIVE",
        version=1,
        organization_id="org_0195f3a00000700283456789abcdef01",
        default_profile_id=prof_id,
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
        model_registry_id="mrg_0195f3a00000700e826807f3bfa3454d",
    )
    await repo.save_workflow(wf)

    exe = ExecutionRecordFactory.build(
        id=exe_id,
        workflow_id=wf.id,
        status=ExecutionStatus.PASSED,
        target_locale="en",
        output_profile_id=prof_id,
        raw_inputs=WorkflowInputs(dynamic_inputs={}),
        step_states={},
    )
    await repo.save_execution(exe)

    prof = OutputProfileFactory.build(
        id=prof_id,
        slug="prof1",
        workflow_id=wf.id,
        name=I18nText(translations={"en": "Prof 1"}),
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070008000000000000001",
                title=I18nText(translations={"en": "Default"}),
                target_blocks=["*"],
            )
        ],
        target_block_order=[TargetBlockType.METADATA_BLOCK],
    )
    repo.set_output_profiles([prof])

    deps = _create_hook_deps(repo)

    step_output = StepOutputDTO(
        step_id="stp_1",
        block_id="blk_1",
        data_type="matrix",
        payload=TraceMatrixPayloadDTO(raw_score=100.0, justification="Test quote 1"),
    )

    state = HookState(
        execution_id=exe_id,
        workflow_id=wf_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={},
            dynamic_inputs={"steps": [step_output]},
            target_locale="en",
        ),
        global_context_vars=GlobalContextVarsDTO(organization_id="org_0195f3a00000700283456789abcdef01"),
    )

    result = await synthesis_distiller_hook(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, SynthesisDistillationDTO)
    assert result.state_delta.delta.distilled_inputs is not None


@pytest.mark.asyncio
async def test_synthesis_distiller_hook_negative_missing_locale_error() -> None:
    """Verify missing target_locale triggers Fail-Fast AppException with VALIDATION_FAILED."""
    deps = _create_hook_deps()

    step_output = StepOutputDTO(
        step_id="stp_1",
        block_id="blk_1",
        data_type="matrix",
        payload=TraceMatrixPayloadDTO(raw_score=100.0),
    )

    state = HookState(
        execution_id="exe_0195f3a00000700283456789abcdef01",
        workflow_id="wf_0195f3a00000700283456789abcdef01",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}, dynamic_inputs={"steps": [step_output]}),
        global_context_vars=GlobalContextVarsDTO(organization_id="org_0195f3a00000700283456789abcdef01"),
    )

    with pytest.raises(AppException) as exc_info:
        await synthesis_distiller_hook(state, deps)

    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert exc_info.value.status_code == 500
