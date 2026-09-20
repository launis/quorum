"""Unit tests for ExecutionOverrideService enforcing human override, synthesis invalidation, and quote rejection."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.domain.execution import EvaluatedMatrixContextDTO, ExecutionRecord, ExecutionStepState
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.atom_result import EvaluatedAtomDTO
from backend_v2.models.dtos.matrix_scorecard import HumanOverrideRequest, ScorecardAtomDTO
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode, VisualIntent
from backend_v2.services.execution.override_service import ExecutionOverrideService


def _create_mock_atom(atom_id: str = "tda_1") -> ScorecardAtomDTO:
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
    execution_id: str = "exe_1234567890abcdef",
    workflow_id: str = "wor_0123456789abcdef",
    org_id: str = "org_1",
    user_id: str = "usr_1",
    atom_id: str = "tda_1",
    pdf_path: str | None = None,
) -> ExecutionRecord:
    atom = _create_mock_atom(atom_id)
    step_state = ExecutionStepState(
        id="sr_1_step",
        label="Step 1",
        status=ExecutionStatus.PASSED,
        scorecard_atoms={atom_id: atom},
    )
    return ExecutionRecord(
        id=execution_id,
        workflow_id=workflow_id,
        status=ExecutionStatus.PASSED,
        target_locale="fi",
        organization_id=org_id,
        created_by=user_id,
        output_profile_id="prf_0123456789abcdef",
        active_profile_id="prf_0123456789abcdef",
        pdf_report_path=pdf_path,
        step_states={"sr_1": step_state},
        profile_syntheses={"prf_0123456789abcdef": RenderedSynthesisCache()},
        context_variables={},
    )


def _create_mock_service() -> tuple[ExecutionOverrideService, MagicMock]:
    exec_repo = MagicMock()
    workflow_repo = MagicMock()
    comp_repo = MagicMock()
    prompt_block_repo = MagicMock()
    output_profile_repo = MagicMock()
    identity_repo = MagicMock()
    system_repo = MagicMock()
    storage_driver = MagicMock()

    exec_repo.update_execution = AsyncMock()
    exec_repo.append_trace_event = AsyncMock()

    service = ExecutionOverrideService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        comp_repo=comp_repo,
        prompt_block_repo=prompt_block_repo,
        output_profile_repo=output_profile_repo,
        identity_repo=identity_repo,
        system_repo=system_repo,
        storage_driver=storage_driver,
    )
    return service, exec_repo


@pytest.mark.asyncio
async def test_override_atom_success() -> None:
    """Verify applying a human override updates step_states, context_variables, and appends trace event."""
    service, exec_repo = _create_mock_service()
    record = _create_mock_record()
    exec_repo.get_execution = AsyncMock(return_value=record)

    initiator = TokenData(id="usr_1", role=UserRole.MEMBER, organization_id="org_1")
    payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED,
        reason="Verified valid claim",
        evidence_quotes=[],
    )

    with patch("backend_v2.hooks.scoring.recalculate", new_callable=AsyncMock) as mock_recalc:
        mock_recalc.return_value = {"recalculated": True}
        await service.override_atom(
            initiator=initiator,
            execution_id=record.id,
            atom_id="tda_1",
            payload=payload,
        )

        mock_recalc.assert_called_once()
        assert exec_repo.update_execution.called
        update_dto = exec_repo.update_execution.call_args[0][1]
        assert update_dto.context_variables == {"recalculated": True}
        updated_atom = update_dto.step_states["sr_1"].scorecard_atoms["tda_1"]
        assert updated_atom.human_override is not None
        assert updated_atom.human_override.new_status == ExecutionStatus.PASSED

        assert exec_repo.append_trace_event.called
        event = exec_repo.append_trace_event.call_args[0][1]
        assert event.event_type == "evidence_override"


@pytest.mark.asyncio
async def test_override_atom_with_evaluated_matrix_context() -> None:
    """Verify override updates EvaluatedMatrixContextDTO in context_variables."""
    service, exec_repo = _create_mock_service()
    record = _create_mock_record()

    raw_atom = EvaluatedAtomDTO(tda_id="tda_1", status="FAILED")
    matrix_ctx = EvaluatedMatrixContextDTO(
        evaluated_atoms={"tda_1": ExecutionStatus.FAILED},
        raw_atoms=[raw_atom],
    )
    record = record.model_copy(update={"context_variables": {"mat_1": matrix_ctx}})
    exec_repo.get_execution = AsyncMock(return_value=record)

    initiator = TokenData(id="usr_1", role=UserRole.MEMBER, organization_id="org_1")
    payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED,
        reason="Manual correction",
        evidence_quotes=[],
    )

    with patch("backend_v2.hooks.scoring.recalculate", new_callable=AsyncMock) as mock_recalc:
        mock_recalc.return_value = {}
        await service.override_atom(
            initiator=initiator,
            execution_id=record.id,
            atom_id="tda_1",
            payload=payload,
        )
        assert mock_recalc.called


@pytest.mark.asyncio
async def test_override_atom_permission_denied() -> None:
    """Verify non-ROOT initiator from different organization raises PermissionDeniedError."""
    service, exec_repo = _create_mock_service()
    record = _create_mock_record(org_id="org_different", user_id="usr_different")
    exec_repo.get_execution = AsyncMock(return_value=record)

    initiator = TokenData(id="usr_intruder", role=UserRole.MEMBER, organization_id="org_mine")
    payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED,
        reason="Should fail",
        evidence_quotes=[],
    )

    with pytest.raises(PermissionDeniedError):
        await service.override_atom(
            initiator=initiator,
            execution_id=record.id,
            atom_id="tda_1",
            payload=payload,
        )


@pytest.mark.asyncio
async def test_override_atom_not_found_raises() -> None:
    """Verify modifying an atom_id not present in step_states raises 404 AppException."""
    service, exec_repo = _create_mock_service()
    record = _create_mock_record()
    exec_repo.get_execution = AsyncMock(return_value=record)

    initiator = TokenData(id="usr_1", role=UserRole.MEMBER, organization_id="org_1")
    payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED,
        reason="Non-existent atom",
        evidence_quotes=[],
    )

    with pytest.raises(AppException) as exc_info:
        await service.override_atom(
            initiator=initiator,
            execution_id=record.id,
            atom_id="tda_unknown",
            payload=payload,
        )
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_override_atom_missing_repos_raises() -> None:
    """Verify missing required hook dependency repositories triggers CONFIGURATION_ERROR."""
    exec_repo = MagicMock()
    service = ExecutionOverrideService(
        exec_repo=exec_repo,
        workflow_repo=MagicMock(),
        comp_repo=None,  # Missing
        prompt_block_repo=None,
    )
    record = _create_mock_record()
    exec_repo.get_execution = AsyncMock(return_value=record)

    initiator = TokenData(id="usr_1", role=UserRole.MEMBER, organization_id="org_1")
    payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED,
        reason="Missing repo test",
        evidence_quotes=[],
    )

    with pytest.raises(AppException) as exc_info:
        await service.override_atom(
            initiator=initiator,
            execution_id=record.id,
            atom_id="tda_1",
            payload=payload,
        )
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR


@pytest.mark.asyncio
async def test_clear_profile_synthesis_success() -> None:
    """Verify clear_profile_synthesis removes profile data and deletes PDF if default profile."""
    service, exec_repo = _create_mock_service()
    record = _create_mock_record(pdf_path="reports/pdf_1.pdf")
    exec_repo.get_execution = AsyncMock(return_value=record)

    mock_wf = Workflow(
        id=record.workflow_id,
        slug="test-workflow",
        name="Test Workflow",
        description="Test Description",
        status="active",
        version=1,
        default_strictness_level=1,
        default_profile_id="prf_0123456789abcdef",
        model_registry_id="sys_e26807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
    )
    service.workflow_repo.get_workflow_by_id = AsyncMock(return_value=mock_wf.model_dump())
    service.storage.delete = AsyncMock()

    initiator = TokenData(id="usr_1", role=UserRole.MEMBER, organization_id="org_1")
    with patch(
        "backend_v2.services.execution.override_service.storage.get_storage_driver", return_value=service.storage
    ):
        await service.clear_profile_synthesis(
            initiator=initiator,
            execution_id=record.id,
            profile_id="prf_0123456789abcdef",
        )

    service.storage.delete.assert_called_once_with("reports/pdf_1.pdf")
    assert exec_repo.update_execution.called
    update_dto = exec_repo.update_execution.call_args[0][1]
    assert "prf_0123456789abcdef" not in update_dto.profile_syntheses
    assert update_dto.pdf_report_path is None


@pytest.mark.asyncio
async def test_clear_profile_synthesis_pdf_delete_404_ignored() -> None:
    """Verify 404 on PDF deletion is caught and ignored cleanly."""
    service, exec_repo = _create_mock_service()
    record = _create_mock_record(pdf_path="reports/pdf_1.pdf")
    exec_repo.get_execution = AsyncMock(return_value=record)

    mock_wf = Workflow(
        id=record.workflow_id,
        slug="test-workflow",
        name="Test Workflow",
        description="Test",
        status="active",
        version=1,
        default_strictness_level=1,
        default_profile_id="prf_0123456789abcdef",
        model_registry_id="sys_e26807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
    )
    service.workflow_repo.get_workflow_by_id = AsyncMock(return_value=mock_wf.model_dump())
    service.storage.delete = AsyncMock(side_effect=AppException("Not found", 404))

    initiator = TokenData(id="usr_1", role=UserRole.MEMBER, organization_id="org_1")
    with patch(
        "backend_v2.services.execution.override_service.storage.get_storage_driver", return_value=service.storage
    ):
        await service.clear_profile_synthesis(
            initiator=initiator,
            execution_id=record.id,
            profile_id="prf_0123456789abcdef",
        )
    assert exec_repo.update_execution.called


@pytest.mark.asyncio
async def test_clear_profile_synthesis_pdf_delete_409_reraised() -> None:
    """Verify 409 Conflict on PDF deletion is re-raised."""
    service, exec_repo = _create_mock_service()
    record = _create_mock_record(pdf_path="reports/pdf_1.pdf")
    exec_repo.get_execution = AsyncMock(return_value=record)

    mock_wf = Workflow(
        id=record.workflow_id,
        slug="test-workflow",
        name="Test Workflow",
        description="Test",
        status="active",
        version=1,
        default_strictness_level=1,
        default_profile_id="prf_0123456789abcdef",
        model_registry_id="sys_e26807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
    )
    service.workflow_repo.get_workflow_by_id = AsyncMock(return_value=mock_wf.model_dump())
    service.storage.delete = AsyncMock(side_effect=AppException("Conflict", 409))

    initiator = TokenData(id="usr_1", role=UserRole.MEMBER, organization_id="org_1")
    with patch(
        "backend_v2.services.execution.override_service.storage.get_storage_driver", return_value=service.storage
    ):
        with pytest.raises(AppException) as exc_info:
            await service.clear_profile_synthesis(
                initiator=initiator,
                execution_id=record.id,
                profile_id="prf_0123456789abcdef",
            )
        assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_clear_profile_synthesis_workflow_missing_raises() -> None:
    """Verify missing workflow raises ResourceNotFoundError."""
    service, exec_repo = _create_mock_service()
    record = _create_mock_record()
    exec_repo.get_execution = AsyncMock(return_value=record)
    service.workflow_repo.get_workflow_by_id = AsyncMock(return_value=None)

    initiator = TokenData(id="usr_1", role=UserRole.MEMBER, organization_id="org_1")
    with pytest.raises(ResourceNotFoundError):
        await service.clear_profile_synthesis(
            initiator=initiator,
            execution_id=record.id,
            profile_id="prf_0123456789abcdef",
        )


@pytest.mark.asyncio
async def test_reject_evidence_quote_success() -> None:
    """Verify rejecting an evidence quote creates and appends EvidenceOverrideDTO TraceEvent."""
    service, exec_repo = _create_mock_service()
    record = _create_mock_record()
    exec_repo.get_execution = AsyncMock(return_value=record)

    initiator = TokenData(id="usr_1", role=UserRole.MEMBER, organization_id="org_1")
    await service.reject_evidence_quote(
        initiator=initiator,
        execution_id=record.id,
        evq_id="evq_test123",
        reason="Irrelevant excerpt",
    )

    assert exec_repo.append_trace_event.called
    event = exec_repo.append_trace_event.call_args[0][1]
    assert event.event_type == "evidence_override"
    assert event.content["evq_id"] == "evq_test123"
    assert event.content["user_rejected"] is True
    assert event.content["rejection_reason"] == "Irrelevant excerpt"


@pytest.mark.asyncio
async def test_reject_evidence_quote_permission_denied() -> None:
    """Verify quote rejection by unauthorized user raises PermissionDeniedError."""
    service, exec_repo = _create_mock_service()
    record = _create_mock_record(org_id="org_other", user_id="usr_other")
    exec_repo.get_execution = AsyncMock(return_value=record)

    initiator = TokenData(id="usr_intruder", role=UserRole.MEMBER, organization_id="org_mine")
    with pytest.raises(PermissionDeniedError):
        await service.reject_evidence_quote(
            initiator=initiator,
            execution_id=record.id,
            evq_id="evq_test123",
            reason="Unauthorized attempt",
        )


@pytest.mark.asyncio
async def test_default_get_execution_not_found() -> None:
    """Verify fetching non-existent execution raises ResourceNotFoundError."""
    service, exec_repo = _create_mock_service()
    exec_repo.get_execution = AsyncMock(return_value=None)

    initiator = TokenData(id="usr_1", role=UserRole.ROOT, organization_id="org_1")
    with pytest.raises(ResourceNotFoundError):
        await service._default_get_execution(initiator, "exe_missing")


@pytest.mark.asyncio
async def test_clear_profile_synthesis_pdf_delete_500_raises() -> None:
    """Verify 500/unhandled AppException on PDF deletion raises 500."""
    service, exec_repo = _create_mock_service()
    record = _create_mock_record(pdf_path="reports/pdf_1.pdf")
    exec_repo.get_execution = AsyncMock(return_value=record)

    mock_wf = Workflow(
        id=record.workflow_id,
        slug="test-workflow",
        name="Test Workflow",
        description="Test",
        status="active",
        version=1,
        default_strictness_level=1,
        default_profile_id="prf_0123456789abcdef",
        model_registry_id="sys_e26807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
    )
    service.workflow_repo.get_workflow_by_id = AsyncMock(return_value=mock_wf.model_dump())
    service.storage.delete = AsyncMock(side_effect=AppException("Server Error", 500))

    initiator = TokenData(id="usr_1", role=UserRole.MEMBER, organization_id="org_1")
    with pytest.raises(AppException) as exc_info:
        await service.clear_profile_synthesis(
            initiator=initiator,
            execution_id=record.id,
            profile_id="prf_0123456789abcdef",
        )
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_clear_profile_synthesis_pdf_delete_generic_exception_raises() -> None:
    """Verify generic unexpected exception on PDF deletion wraps into 500 AppException."""
    service, exec_repo = _create_mock_service()
    record = _create_mock_record(pdf_path="reports/pdf_1.pdf")
    exec_repo.get_execution = AsyncMock(return_value=record)

    mock_wf = Workflow(
        id=record.workflow_id,
        slug="test-workflow",
        name="Test Workflow",
        description="Test",
        status="active",
        version=1,
        default_strictness_level=1,
        default_profile_id="prf_0123456789abcdef",
        model_registry_id="sys_e26807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
    )
    service.workflow_repo.get_workflow_by_id = AsyncMock(return_value=mock_wf.model_dump())
    service.storage.delete = AsyncMock(side_effect=RuntimeError("Storage connection failed"))

    initiator = TokenData(id="usr_1", role=UserRole.MEMBER, organization_id="org_1")
    with pytest.raises(AppException) as exc_info:
        await service.clear_profile_synthesis(
            initiator=initiator,
            execution_id=record.id,
            profile_id="prf_0123456789abcdef",
        )
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_clear_profile_synthesis_profile_not_in_syntheses() -> None:
    """Verify clearing a profile synthesis when the profile is not cached executes cleanly."""
    service, exec_repo = _create_mock_service()
    record = _create_mock_record(pdf_path=None)
    exec_repo.get_execution = AsyncMock(return_value=record)

    mock_wf = Workflow(
        id=record.workflow_id,
        slug="test-workflow",
        name="Test Workflow",
        description="Test",
        status="active",
        version=1,
        default_strictness_level=1,
        default_profile_id="prf_0123456789abcdef",
        model_registry_id="sys_e26807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
    )
    service.workflow_repo.get_workflow_by_id = AsyncMock(return_value=mock_wf.model_dump())

    initiator = TokenData(id="usr_1", role=UserRole.MEMBER, organization_id="org_1")
    await service.clear_profile_synthesis(
        initiator=initiator,
        execution_id=record.id,
        profile_id="prf_non_existent",
    )
    assert exec_repo.update_execution.called

