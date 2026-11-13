"""Unit tests for ExecutionOverrideService enforcing human override, synthesis invalidation, and quote rejection."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, I18nText
from backend_v2.models.domain.execution import EvaluatedMatrixContextDTO, ExecutionRecord, ExecutionStepState
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.atom_result import EvaluatedAtomDTO
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.matrix_scorecard import HumanOverrideRequest, ScorecardAtomDTO
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode, VisualIntent
from backend_v2.services.execution.override_service import ExecutionOverrideService
from backend_v2.services.file_driver import FileDriver
from backend_v2.tests.factories.model_factories import ExecutionRecordFactory, WorkflowFactory
from backend_v2.tests.fakes.in_memory_repositories import (
    InMemoryExecutionRepository,
    InMemoryUnifiedWorkflowRepository,
)

EXEC_ID = "exe_0195f3a0000070018234567890abcdef"
MISSING_EXEC_ID = "exe_0195f3a0000070018234567890abc999"
WORKFLOW_ID = "wf_0195f3a0000070008123456789abcdef"
PROFILE_ID = "prf_0195f3a0000070008123456789abcdef"
OTHER_PROFILE_ID = "prf_0195f3a0000070008123456789abc999"
MODEL_REGISTRY_ID = "mrg_0195f3a00000700e826807f3bfa3454d"
ORG_ID = "org_0195f3a0000070008000000000000001"
OTHER_ORG_ID = "org_0195f3a0000070008000000000000002"
USER_ID = "usr_0195f3a0000070008000000000000001"
OTHER_USER_ID = "usr_0195f3a0000070008000000000000002"
INTRUDER_USER_ID = "usr_0195f3a00000700080000000000000003"
STEP_ID = "stp_0195f3a0000070008000000000000001"
ATOM_ID = "tda_0195f3a0000070008000000000000001"
UNKNOWN_ATOM_ID = "tda_0195f3a0000070008000000000000999"
EVQ_ID = "evq_0195f3a0000070008000000000000001"


def _create_mock_atom(atom_id: str = ATOM_ID) -> ScorecardAtomDTO:
    return ScorecardAtomDTO(
        atom_id=atom_id,
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


def _create_mock_record(
    execution_id: str = EXEC_ID,
    workflow_id: str = WORKFLOW_ID,
    org_id: str = ORG_ID,
    user_id: str = USER_ID,
    atom_id: str = ATOM_ID,
) -> ExecutionRecord:
    atom = _create_mock_atom(atom_id)
    step_state = ExecutionStepState(
        id=STEP_ID,
        label="Step 1",
        status=ExecutionStatus.PASSED,
        scorecard_atoms={atom_id: atom},
    )
    return ExecutionRecordFactory.build(
        id=execution_id,
        workflow_id=workflow_id,
        status=ExecutionStatus.PASSED,
        target_locale="fi",
        organization_id=org_id,
        created_by=user_id,
        output_profile_id=PROFILE_ID,
        steps=[step_state],
        profile_syntheses={
            PROFILE_ID: RenderedSynthesisCache(
                section_syntheses={},
                row_explanations={},
                row_curated_quotes={},
                cited_sources=[],
                xai_highlights=[],
                created_at=datetime.now(UTC),
            )
        },
        context_variables=ContextVariablesDTO(variables={}),
        execution_trace=[],
        state_version=1,
    )


def _create_mock_workflow(
    workflow_id: str = WORKFLOW_ID,
    profile_id: str = PROFILE_ID,
) -> Workflow:
    return WorkflowFactory.build(
        id=workflow_id,
        slug="test-workflow",
        name=I18nText(translations={"en": "Test Workflow"}),
        description=I18nText(translations={"en": "Test Description"}),
        status="active",
        version=1,
        organization_id=ORG_ID,
        default_strictness_level=1,
        default_profile_id=profile_id,
        model_registry_id=MODEL_REGISTRY_ID,
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
        expected_inputs=[],
    )


def _create_mock_service(
    storage_driver: FileDriver | MagicMock | None = None,
) -> tuple[ExecutionOverrideService, InMemoryExecutionRepository, InMemoryUnifiedWorkflowRepository]:
    exec_repo = InMemoryExecutionRepository()
    workflow_repo = InMemoryUnifiedWorkflowRepository()
    resolved_storage: FileDriver = storage_driver if storage_driver is not None else MagicMock(spec=FileDriver)

    service = ExecutionOverrideService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        prompt_block_repo=workflow_repo,
        output_profile_repo=workflow_repo,
        identity_repo=workflow_repo,
        system_repo=workflow_repo,
        storage_driver=resolved_storage,
    )
    return service, exec_repo, workflow_repo


@pytest.mark.asyncio
async def test_override_atom_success() -> None:
    """Verify applying a human override updates steps, context_variables, and appends trace event."""
    service, exec_repo, _ = _create_mock_service()
    record = _create_mock_record()
    assert re.match(OPAQUE_STRIPE_ID_REGEX, record.id)
    await exec_repo.save_execution(record)

    initiator = TokenData(id=USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
    payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED,
        reason="Verified valid claim",
        evidence_quotes=[],
    )

    with patch("backend_v2.hooks.scoring.recalculate", new_callable=AsyncMock) as mock_recalc:
        mock_recalc.return_value = ContextVariablesDTO(variables={"recalculated": True})
        await service.override_atom(
            initiator=initiator,
            execution_id=record.id,
            atom_id=ATOM_ID,
            payload=payload,
        )

        mock_recalc.assert_called_once()
        assert exec_repo.get_call_count("update_execution") > 0
        updated = await exec_repo.get_execution(record.id)
        assert updated is not None
        reconstituted = ExecutionRecord.model_validate(updated.model_dump(mode="json"), strict=False)
        assert re.match(OPAQUE_STRIPE_ID_REGEX, reconstituted.id)
        assert updated.context_variables == ContextVariablesDTO(variables={"recalculated": True})
        updated_step = next(s for s in updated.steps if s.id == STEP_ID)
        updated_atom = updated_step.scorecard_atoms[ATOM_ID]
        assert updated_atom.human_override is not None
        assert updated_atom.human_override.new_status == ExecutionStatus.PASSED
        assert updated.profile_syntheses == {}

        assert exec_repo.get_call_count("append_trace_event") > 0
        assert len(updated.execution_trace) > 0
        event = updated.execution_trace[-1]
        assert event.event_type == "evidence_override"


@pytest.mark.asyncio
async def test_override_atom_mutates_canonical_steps_and_clears_profile_syntheses_atomically() -> None:
    """Verify override_atom mutates canonical steps and clears profile_syntheses atomically in PostgreSQL fake."""
    from backend_v2.database.repositories.execution import ExecutionRepositoryImpl
    from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork

    uow = InMemoryUnitOfWork()
    exec_repo = ExecutionRepositoryImpl(uow_factory=lambda: uow)
    workflow_repo = InMemoryUnifiedWorkflowRepository()
    service = ExecutionOverrideService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        prompt_block_repo=workflow_repo,
        output_profile_repo=workflow_repo,
        identity_repo=workflow_repo,
        system_repo=workflow_repo,
        storage_driver=MagicMock(spec=FileDriver),
    )
    record = _create_mock_record()
    await uow.entities.save_execution(record)

    initiator = TokenData(id=USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
    payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED,
        reason="Verified valid claim with atomic synthesis clear",
        evidence_quotes=[],
    )

    with patch("backend_v2.hooks.scoring.recalculate", new_callable=AsyncMock) as mock_recalc:
        mock_recalc.return_value = ContextVariablesDTO(variables={"recalculated": True})
        await service.override_atom(
            initiator=initiator,
            execution_id=record.id,
            atom_id=ATOM_ID,
            payload=payload,
        )

    persisted = await exec_repo.get_execution(record.id, hydrate=True)
    assert persisted is not None
    assert persisted.profile_syntheses == {}
    assert persisted.state_version == 2
    persisted_step = next(s for s in persisted.steps if s.id == STEP_ID)
    override_dto = persisted_step.scorecard_atoms[ATOM_ID].human_override
    assert override_dto is not None
    assert override_dto.new_status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_override_atom_with_evaluated_matrix_context() -> None:
    """Verify override updates EvaluatedMatrixContextDTO in context_variables."""
    service, exec_repo, _ = _create_mock_service()
    record = _create_mock_record()

    raw_atom = EvaluatedAtomDTO(tda_id=ATOM_ID, status="FAILED", exact_quotes=[])
    matrix_ctx = EvaluatedMatrixContextDTO(
        evaluated_atoms={ATOM_ID: ExecutionStatus.FAILED},
        raw_atoms=[raw_atom],
    )
    record = record.model_copy(update={"context_variables": ContextVariablesDTO(variables={"mat_1": matrix_ctx})})
    await exec_repo.save_execution(record)

    initiator = TokenData(id=USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
    payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED,
        reason="Manual correction",
        evidence_quotes=[],
    )

    with patch("backend_v2.hooks.scoring.recalculate", new_callable=AsyncMock) as mock_recalc:
        mock_recalc.return_value = ContextVariablesDTO(variables={})
        await service.override_atom(
            initiator=initiator,
            execution_id=record.id,
            atom_id=ATOM_ID,
            payload=payload,
        )
        assert mock_recalc.called
        recalc_vars = mock_recalc.call_args.args[0]
        assert isinstance(recalc_vars, ContextVariablesDTO)
        updated_ctx = recalc_vars.variables["mat_1"]
        assert isinstance(updated_ctx, EvaluatedMatrixContextDTO)
        assert updated_ctx.evaluated_atoms[ATOM_ID] == ExecutionStatus.PASSED
        assert updated_ctx.raw_atoms[0].human_override == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_override_atom_permission_denied() -> None:
    """Verify non-ROOT initiator from different organization raises PermissionDeniedError."""
    service, exec_repo, _ = _create_mock_service()
    record = _create_mock_record(org_id=OTHER_ORG_ID, user_id=OTHER_USER_ID)
    await exec_repo.save_execution(record)

    initiator = TokenData(id=INTRUDER_USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
    payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED,
        reason="Should fail",
        evidence_quotes=[],
    )

    with pytest.raises(PermissionDeniedError):
        await service.override_atom(
            initiator=initiator,
            execution_id=record.id,
            atom_id=ATOM_ID,
            payload=payload,
        )


@pytest.mark.asyncio
async def test_override_atom_invalid_atom_id_not_found_error() -> None:
    """Verify modifying an atom_id not present in steps raises 404 AppException."""
    service, exec_repo, _ = _create_mock_service()
    record = _create_mock_record()
    await exec_repo.save_execution(record)

    initiator = TokenData(id=USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
    payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED,
        reason="Non-existent atom",
        evidence_quotes=[],
    )

    with pytest.raises(AppException) as exc_info:
        await service.override_atom(
            initiator=initiator,
            execution_id=record.id,
            atom_id=UNKNOWN_ATOM_ID,
            payload=payload,
        )
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_override_atom_missing_repos_configuration_error() -> None:
    """Verify missing required hook dependency repositories triggers CONFIGURATION_ERROR."""
    exec_repo = InMemoryExecutionRepository()
    service = ExecutionOverrideService(
        exec_repo=exec_repo,
        workflow_repo=InMemoryUnifiedWorkflowRepository(),
        prompt_block_repo=None,
        storage_driver=MagicMock(spec=FileDriver),
    )
    record = _create_mock_record()
    await exec_repo.save_execution(record)

    initiator = TokenData(id=USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
    payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED,
        reason="Missing repo test",
        evidence_quotes=[],
    )

    with pytest.raises(AppException) as exc_info:
        await service.override_atom(
            initiator=initiator,
            execution_id=record.id,
            atom_id=ATOM_ID,
            payload=payload,
        )
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR


@pytest.mark.asyncio
async def test_clear_profile_synthesis_success() -> None:
    """Verify clear_profile_synthesis removes the targeted profile synthesis entry."""
    service, exec_repo, workflow_repo = _create_mock_service()

    record = _create_mock_record()
    await exec_repo.save_execution(record)

    mock_wf = _create_mock_workflow(workflow_id=record.workflow_id, profile_id=PROFILE_ID)
    await workflow_repo.save_workflow(mock_wf)

    initiator = TokenData(id=USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
    await service.clear_profile_synthesis(
        initiator=initiator,
        execution_id=record.id,
        profile_id=PROFILE_ID,
    )

    assert exec_repo.get_call_count("update_execution") > 0
    updated = await exec_repo.get_execution(record.id)
    assert updated is not None
    assert PROFILE_ID not in updated.profile_syntheses


@pytest.mark.asyncio
async def test_clear_profile_synthesis_preserves_other_profiles() -> None:
    """Verify clearing a single profile_id preserves unrelated cached syntheses."""
    service, exec_repo, workflow_repo = _create_mock_service()
    other_cache = RenderedSynthesisCache(
        section_syntheses={},
        row_explanations={"blk_0195f3a0000070008123456789abcdef": "Retained"},
        row_curated_quotes={},
        cited_sources=[],
        xai_highlights=[],
        created_at=datetime.now(UTC),
    )
    record = _create_mock_record()
    record = record.model_copy(
        update={
            "profile_syntheses": {
                **record.profile_syntheses,
                OTHER_PROFILE_ID: other_cache,
            }
        }
    )
    await exec_repo.save_execution(record)

    mock_wf = _create_mock_workflow(workflow_id=record.workflow_id, profile_id=PROFILE_ID)
    await workflow_repo.save_workflow(mock_wf)

    initiator = TokenData(id=USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
    await service.clear_profile_synthesis(
        initiator=initiator,
        execution_id=record.id,
        profile_id=PROFILE_ID,
    )
    updated = await exec_repo.get_execution(record.id)
    assert updated is not None
    assert PROFILE_ID not in updated.profile_syntheses
    assert OTHER_PROFILE_ID in updated.profile_syntheses


@pytest.mark.asyncio
async def test_clear_profile_synthesis_occ_conflict_raises_409() -> None:
    """Verify clear_profile_synthesis raises 409 CONFLICT when state_version advances concurrently."""
    service, exec_repo, workflow_repo = _create_mock_service()
    record = _create_mock_record()
    await exec_repo.save_execution(record)
    mock_wf = _create_mock_workflow(workflow_id=record.workflow_id, profile_id=PROFILE_ID)
    await workflow_repo.save_workflow(mock_wf)

    async def _stale_getter(initiator: TokenData, execution_id: str) -> ExecutionRecord:
        await exec_repo.update_execution(
            execution_id,
            ExecutionUpdateDTO(expected_state_version=1, current_step="advanced"),
        )
        return record

    service._get_execution = _stale_getter
    initiator = TokenData(id=USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
    with pytest.raises(AppException) as exc_info:
        await service.clear_profile_synthesis(
            initiator=initiator,
            execution_id=record.id,
            profile_id=PROFILE_ID,
        )
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_clear_profile_synthesis_workflow_missing_raises() -> None:
    """Verify missing workflow raises ResourceNotFoundError."""
    service, exec_repo, _ = _create_mock_service()
    record = _create_mock_record()
    await exec_repo.save_execution(record)

    initiator = TokenData(id=USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
    with pytest.raises(ResourceNotFoundError):
        await service.clear_profile_synthesis(
            initiator=initiator,
            execution_id=record.id,
            profile_id=PROFILE_ID,
        )


@pytest.mark.asyncio
async def test_clear_profile_synthesis_permission_denied_with_custom_getter() -> None:
    """Verify clear_profile_synthesis enforces modification permission check when custom getter returns record."""
    record = _create_mock_record(org_id=OTHER_ORG_ID, user_id=OTHER_USER_ID)
    exec_repo = InMemoryExecutionRepository()
    workflow_repo = InMemoryUnifiedWorkflowRepository()

    async def _custom_get_execution(initiator: TokenData, execution_id: str) -> ExecutionRecord:
        return record

    service = ExecutionOverrideService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        storage_driver=MagicMock(spec=FileDriver),
        get_execution_fn=_custom_get_execution,
    )
    initiator = TokenData(id=INTRUDER_USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)

    with pytest.raises(PermissionDeniedError):
        await service.clear_profile_synthesis(
            initiator=initiator,
            execution_id=record.id,
            profile_id=PROFILE_ID,
        )


@pytest.mark.asyncio
async def test_reject_evidence_quote_success() -> None:
    """Verify rejecting an evidence quote creates and appends EvidenceOverrideDTO TraceEvent."""
    service, exec_repo, _ = _create_mock_service()
    record = _create_mock_record()
    await exec_repo.save_execution(record)

    initiator = TokenData(id=USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
    await service.reject_evidence_quote(
        initiator=initiator,
        execution_id=record.id,
        evq_id=EVQ_ID,
        reason="Irrelevant excerpt",
    )

    assert exec_repo.get_call_count("append_trace_event") > 0
    updated = await exec_repo.get_execution(record.id)
    assert updated is not None
    assert len(updated.execution_trace) > 0
    event = updated.execution_trace[-1]
    assert event.event_type == "evidence_override"
    assert type(event.content) is dict
    assert event.content["evq_id"] == EVQ_ID
    assert event.content["user_rejected"] is True
    assert event.content["rejection_reason"] == "Irrelevant excerpt"


@pytest.mark.asyncio
async def test_reject_evidence_quote_permission_denied() -> None:
    """Verify quote rejection by unauthorized user raises PermissionDeniedError."""
    service, exec_repo, _ = _create_mock_service()
    record = _create_mock_record(org_id=OTHER_ORG_ID, user_id=OTHER_USER_ID)
    await exec_repo.save_execution(record)

    initiator = TokenData(id=INTRUDER_USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
    with pytest.raises(PermissionDeniedError):
        await service.reject_evidence_quote(
            initiator=initiator,
            execution_id=record.id,
            evq_id=EVQ_ID,
            reason="Unauthorized attempt",
        )


@pytest.mark.asyncio
async def test_default_get_execution_not_found() -> None:
    """Verify fetching non-existent execution raises ResourceNotFoundError."""
    service, _, _ = _create_mock_service()

    initiator = TokenData(id=USER_ID, role=UserRole.ROOT, organization_id=ORG_ID)
    with pytest.raises(ResourceNotFoundError):
        await service._default_get_execution(initiator, MISSING_EXEC_ID)


@pytest.mark.asyncio
async def test_clear_profile_synthesis_update_500_failure() -> None:
    """Verify 500 AppException on persistence update during clear_profile_synthesis propagates."""
    service, exec_repo, workflow_repo = _create_mock_service()

    record = _create_mock_record()
    await exec_repo.save_execution(record)

    mock_wf = _create_mock_workflow(workflow_id=record.workflow_id, profile_id=PROFILE_ID)
    await workflow_repo.save_workflow(mock_wf)

    exec_repo.inject_fault("update_execution", AppException("Server Error", 500), trigger_count=1)
    try:
        initiator = TokenData(id=USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
        with pytest.raises(AppException) as exc_info:
            await service.clear_profile_synthesis(
                initiator=initiator,
                execution_id=record.id,
                profile_id=PROFILE_ID,
            )
        assert exc_info.value.status_code == 500
    finally:
        exec_repo.clear_faults()


@pytest.mark.asyncio
async def test_clear_profile_synthesis_injected_conflict_fault_raises_409() -> None:
    """Verify injected 409 conflict fault on clear_profile_synthesis propagates 409 AppException."""
    service, exec_repo, workflow_repo = _create_mock_service()

    record = _create_mock_record()
    await exec_repo.save_execution(record)

    mock_wf = _create_mock_workflow(workflow_id=record.workflow_id, profile_id=PROFILE_ID)
    await workflow_repo.save_workflow(mock_wf)

    exec_repo.inject_fault(
        "update_execution",
        AppException("OCC Conflict", 409, details={"error_code": ErrorCodes.CONFLICT.value}),
        trigger_count=1,
    )
    try:
        initiator = TokenData(id=USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
        with pytest.raises(AppException) as exc_info:
            await service.clear_profile_synthesis(
                initiator=initiator,
                execution_id=record.id,
                profile_id=PROFILE_ID,
            )
        assert exc_info.value.status_code == 409
    finally:
        exec_repo.clear_faults()


@pytest.mark.asyncio
async def test_clear_profile_synthesis_profile_not_in_syntheses() -> None:
    """Verify clearing a profile synthesis when the profile is not cached executes cleanly."""
    service, exec_repo, workflow_repo = _create_mock_service()
    record = _create_mock_record()
    await exec_repo.save_execution(record)

    mock_wf = _create_mock_workflow(workflow_id=record.workflow_id, profile_id=PROFILE_ID)
    await workflow_repo.save_workflow(mock_wf)

    initiator = TokenData(id=USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
    await service.clear_profile_synthesis(
        initiator=initiator,
        execution_id=record.id,
        profile_id=OTHER_PROFILE_ID,
    )
    assert exec_repo.get_call_count("update_execution") > 0


@pytest.mark.asyncio
async def test_override_atom_permission_denied_with_custom_getter() -> None:
    """Verify override_atom enforces modification permission check even when custom get_execution_fn returns record."""
    record = _create_mock_record(org_id=OTHER_ORG_ID, user_id=OTHER_USER_ID)
    exec_repo = InMemoryExecutionRepository()
    workflow_repo = InMemoryUnifiedWorkflowRepository()

    async def _custom_get_execution(initiator: TokenData, execution_id: str) -> ExecutionRecord:
        return record

    service = ExecutionOverrideService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        storage_driver=MagicMock(spec=FileDriver),
        get_execution_fn=_custom_get_execution,
    )
    initiator = TokenData(id=INTRUDER_USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
    payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED,
        reason="Unauthorized override",
        evidence_quotes=[],
    )

    with pytest.raises(PermissionDeniedError):
        await service.override_atom(
            initiator=initiator,
            execution_id=record.id,
            atom_id=ATOM_ID,
            payload=payload,
        )


@pytest.mark.asyncio
async def test_reject_evidence_quote_permission_denied_with_custom_getter() -> None:
    """Verify reject_evidence_quote enforces modification permission check when custom get_execution_fn returns record."""
    record = _create_mock_record(org_id=OTHER_ORG_ID, user_id=OTHER_USER_ID)
    exec_repo = InMemoryExecutionRepository()
    workflow_repo = InMemoryUnifiedWorkflowRepository()

    async def _custom_get_execution(initiator: TokenData, execution_id: str) -> ExecutionRecord:
        return record

    service = ExecutionOverrideService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        storage_driver=MagicMock(spec=FileDriver),
        get_execution_fn=_custom_get_execution,
    )
    initiator = TokenData(id=INTRUDER_USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)

    with pytest.raises(PermissionDeniedError):
        await service.reject_evidence_quote(
            initiator=initiator,
            execution_id=record.id,
            evq_id=EVQ_ID,
            reason="Unauthorized rejection",
        )


@pytest.mark.asyncio
async def test_override_service_raises_conflict_409_when_worker_advances_state_version_concurrently() -> None:
    """Verify override_atom raises HTTP 409 CONFLICT when a worker advances state_version concurrently."""
    service, exec_repo, _ = _create_mock_service()
    record = _create_mock_record()
    await exec_repo.save_execution(record)

    async def _concurrent_worker_advancing_getter(initiator: TokenData, execution_id: str) -> ExecutionRecord:
        fetched = await exec_repo.get_execution(execution_id)
        assert fetched is not None
        assert fetched.state_version == 1
        # Simulate a concurrent worker commit advancing state_version to 2 before override_atom persists.
        await exec_repo.update_execution(
            execution_id,
            ExecutionUpdateDTO(status=ExecutionStatus.RUNNING, expected_state_version=1),
        )
        return fetched

    service._get_execution = _concurrent_worker_advancing_getter
    initiator = TokenData(id=USER_ID, role=UserRole.MEMBER, organization_id=ORG_ID)
    payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED,
        reason="Concurrent human override attempt",
        evidence_quotes=[],
    )

    with patch("backend_v2.hooks.scoring.recalculate", new_callable=AsyncMock) as mock_recalc:
        mock_recalc.return_value = ContextVariablesDTO(variables={"recalculated": True})
        with pytest.raises(AppException) as exc_info:
            await service.override_atom(
                initiator=initiator,
                execution_id=record.id,
                atom_id=ATOM_ID,
                payload=payload,
            )

    assert exc_info.value.status_code == 409
    assert exc_info.value.details is not None
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFLICT.value
    persisted = await exec_repo.get_execution(record.id)
    assert persisted is not None
    assert persisted.state_version == 2
    persisted_step = next(s for s in persisted.steps if s.id == STEP_ID)
    assert persisted_step.scorecard_atoms[ATOM_ID].human_override is None
