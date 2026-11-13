"""Unit tests for execution domain models."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.execution import (
    EvaluatedMatrixContextDTO,
    EvidenceRejectionRequest,
    ExecutionAssignment,
    ExecutionCreate,
    ExecutionStep,
    ExecutionSummarySnapshot,
    FrozenContext,
    JobAcceptedDTO,
    _resolve_default_matrix_sampling_limit,
)
from backend_v2.models.domain.inputs import WorkflowInputsIngress
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.dtos.atom_result import EvaluatedAtomDTO
from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
from backend_v2.models.dtos.theory_manifest import InjectedTheoryManifestDTO
from backend_v2.models.enums import ExecutionStatus, LLMProvider
from backend_v2.tests.factories.model_factories import ExecutionRecordFactory, ExecutionStepFactory


def test_frozen_context_instantiation() -> None:
    """Verify FrozenContext defaults via typed constructor."""
    fc = FrozenContext(
        compiled_prompts={},
        injected_theory=InjectedTheoryManifestDTO(theories={}),
        generated_schemas=GeneratedSchemaManifestDTO(schemas={}),
        ui_hints_snapshot={},
        mcp_tool_audit=[],
    )
    assert fc.compiled_prompts == {}
    assert fc.injected_theory == InjectedTheoryManifestDTO(theories={})
    assert fc.generated_schemas == GeneratedSchemaManifestDTO(schemas={})
    assert fc.ui_hints_snapshot == {}
    assert fc.mcp_tool_audit == []


def test_theory_manifest_immutability() -> None:
    """Test contract: InjectedTheoryManifestDTO rejects in-place attribute mutations."""
    manifest = InjectedTheoryManifestDTO(theories={"th_1": "Theory text"})
    assert manifest.theories["th_1"] == "Theory text"
    with pytest.raises((ValidationError, TypeError)):
        del manifest.theories


def test_schema_manifest_immutability() -> None:
    """Test contract: GeneratedSchemaManifestDTO rejects in-place attribute mutations."""
    manifest = GeneratedSchemaManifestDTO(schemas={"stp_1": {"type": "object"}})
    assert "stp_1" in manifest
    assert manifest["stp_1"] == {"type": "object"}
    with pytest.raises((ValidationError, TypeError)):
        del manifest.schemas


def test_execution_create_defaults() -> None:
    """Verify ExecutionCreate default field resolution."""
    ec = ExecutionCreate.model_validate_json(
        '{"workflow_id": "wor_0195f3a0000070018234567890abcdef", "target_locale": "fi"}'
    )
    assert ec.workflow_id == "wor_0195f3a0000070018234567890abcdef"
    assert ec.target_locale == "fi"
    assert ec.profile_id is None
    assert ec.matrix_sampling_strategy == _resolve_default_matrix_sampling_limit()
    assert ec.provider_override is None
    assert ec.model_registry_id is None


def test_execution_create_custom_and_validator() -> None:
    """Verify ExecutionCreate custom fields and None sampling strategy coercion."""
    ec = ExecutionCreate.model_validate_json(
        '{"workflow_id": "wor_0195f3a0000070018234567890abcdef", '
        '"target_locale": "en", '
        '"profile_id": "pro_0195f3a0000070018234567890abcdef", '
        '"matrix_sampling_strategy": null, '
        '"provider_override": "openai", '
        '"model_registry_id": "reg_0195f3a0000070018234567890abcdef"}'
    )
    assert ec.matrix_sampling_strategy == _resolve_default_matrix_sampling_limit()
    assert ec.provider_override == LLMProvider.OPENAI

    ec2 = ExecutionCreate(
        workflow_id="wor_0195f3a0000070018234567890abcdef",
        target_locale="en",
        matrix_sampling_strategy=5,
        raw_inputs=WorkflowInputsIngress(dynamic_inputs={}),
    )
    assert ec2.matrix_sampling_strategy == 5


def test_execution_create_extra_forbidden() -> None:
    """Verify ExecutionCreate rejects extra fields."""
    with pytest.raises(ValidationError):
        ExecutionCreate.model_validate(
            {
                "workflow_id": "wor_0195f3a0000070018234567890abcdef",
                "target_locale": "fi",
                "unexpected_field": "disallowed",
            }
        )


def test_execution_step_instantiation() -> None:
    """Verify ExecutionStep instantiation and default field values."""
    step = ExecutionStep(
        id="stp_step12345678",
        label="Analyst Step",
        status=ExecutionStatus.RUNNING,
        scorecard_atoms={},
    )
    assert step.id == "stp_step12345678"
    assert step.label == "Analyst Step"
    assert step.status == ExecutionStatus.RUNNING
    assert step.scorecard_atoms == {}
    assert step.prompt_tokens == 0
    assert step.has_warning is False


def test_execution_step_extra_forbidden() -> None:
    """Verify ExecutionStep rejects extra fields."""
    with pytest.raises(ValidationError):
        ExecutionStep.model_validate(
            {
                "id": "stp_step12345678",
                "label": "Analyst Step",
                "unexpected": "bad",
            }
        )


def test_execution_summary_snapshot() -> None:
    """Verify ExecutionSummarySnapshot instantiation."""
    snap = ExecutionSummarySnapshot(
        strictness_level=85,
        is_ensemble_run=True,
        is_degraded=False,
        system_concurrency_snapshot={},
    )
    assert snap.strictness_level == 85
    assert snap.is_ensemble_run is True
    assert snap.is_degraded is False
    assert snap.system_concurrency_snapshot == {}


def test_execution_summary_snapshot_zero_strictness_boundary() -> None:
    """ISTQB Boundary Test: ExecutionSummarySnapshot allows 0% Free strictness level (0-100%)."""
    snap = ExecutionSummarySnapshot(
        strictness_level=0,
        is_ensemble_run=False,
        is_degraded=False,
        system_concurrency_snapshot={},
    )
    assert snap.strictness_level == 0


def test_evaluated_matrix_context_dto() -> None:
    """Verify EvaluatedMatrixContextDTO instantiation."""
    dto = EvaluatedMatrixContextDTO(
        evaluated_atoms={"atm_1": "PASSED"},
        raw_atoms=[EvaluatedAtomDTO(tda_id="atm_1", status="PASSED", score=1.0, exact_quotes=[])],
    )
    assert dto.evaluated_atoms == {"atm_1": "PASSED"}
    assert len(dto.raw_atoms) == 1
    assert dto.raw_atoms[0].tda_id == "atm_1"


def test_job_accepted_dto() -> None:
    """Verify JobAcceptedDTO instantiation."""
    dto = JobAcceptedDTO(
        status="ACCEPTED",
        message="Job queued",
        execution_id="exe_0195f3a0000070018234567890abcdef",
    )
    assert dto.status == "ACCEPTED"
    assert dto.execution_id == "exe_0195f3a0000070018234567890abcdef"


def test_evidence_rejection_request() -> None:
    """Verify EvidenceRejectionRequest instantiation."""
    req = EvidenceRejectionRequest(rejection_reason="Quote out of context")
    assert req.rejection_reason == "Quote out of context"


def test_execution_record_instantiation() -> None:
    """Verify ExecutionRecord instantiation via ExecutionRecordFactory."""
    rec = ExecutionRecordFactory.build(
        id="exe_0195f3a0000070018234567890abcdef",
        workflow_id="wor_0195f3a0000070018234567890abcdef",
        target_locale="fi",
        status=ExecutionStatus.PENDING,
        created_at=datetime.now(UTC),
    )
    assert rec.id == "exe_0195f3a0000070018234567890abcdef"
    assert rec.workflow_id == "wor_0195f3a0000070018234567890abcdef"
    assert rec.status == ExecutionStatus.PENDING
    assert rec.steps == []
    assert rec.step_states == {}
    assert rec.profile_syntheses == {}


def test_execution_record_transition_step_new_step() -> None:
    """Verify ExecutionRecord.transition_step adds a new step immutably."""
    rec = ExecutionRecordFactory.build(
        id="exe_0195f3a0000070018234567890abcdef",
        workflow_id="wor_0195f3a0000070018234567890abcdef",
        target_locale="fi",
        status=ExecutionStatus.PENDING,
        created_at=datetime.now(UTC),
    )
    updated = rec.transition_step(
        step_id="stp_0195f3a0000070018234567890abcdef",
        status=ExecutionStatus.RUNNING,
        progress=25,
        label="Analyze Dialogue",
    )
    # Original record must remain immutable
    assert rec.steps == []
    assert rec.step_states == {}

    # Updated record contains newly transitioned step in both steps list and step_states dict
    assert "stp_0195f3a0000070018234567890abcdef" in updated.step_states
    assert len(updated.steps) == 1
    assert updated.steps[0].id == "stp_0195f3a0000070018234567890abcdef"
    assert updated.steps[0].status == ExecutionStatus.RUNNING
    assert updated.steps[0].progress == 25
    assert updated.steps[0].label == "Analyze Dialogue"
    assert updated.step_states["stp_0195f3a0000070018234567890abcdef"] == updated.steps[0]


def test_execution_record_transition_step_existing_step() -> None:
    """Verify ExecutionRecord.transition_step updates an existing step immutably."""
    initial_step = ExecutionStepFactory.build(
        id="stp_0195f3a0000070018234567890abcdef",
        label="Original Label",
        status=ExecutionStatus.PENDING,
    )
    rec = ExecutionRecordFactory.build(
        id="exe_0195f3a0000070018234567890abcdef",
        workflow_id="wor_0195f3a0000070018234567890abcdef",
        target_locale="fi",
        status=ExecutionStatus.RUNNING,
        steps=[initial_step],
        step_states={"stp_0195f3a0000070018234567890abcdef": initial_step},
        created_at=datetime.now(UTC),
    )
    updated = rec.transition_step(
        step_id="stp_0195f3a0000070018234567890abcdef",
        status=ExecutionStatus.FAILED,
        progress=50,
        last_error="Network timeout",
        has_warning=True,
    )
    assert len(updated.steps) == 1
    step = updated.steps[0]
    assert step.id == "stp_0195f3a0000070018234567890abcdef"
    assert step.label == "Original Label"
    assert step.status == ExecutionStatus.FAILED
    assert step.progress == 50
    assert step.last_error == "Network timeout"
    assert step.has_warning is True
    assert updated.step_states["stp_0195f3a0000070018234567890abcdef"] == step


def test_execution_record_with_step_passed_forwarder() -> None:
    """Verify ExecutionRecord.with_step_passed transitions step to PASSED at 100%."""
    rec = ExecutionRecordFactory.build(
        id="exe_0195f3a0000070018234567890abcdef",
        workflow_id="wor_0195f3a0000070018234567890abcdef",
        target_locale="fi",
        status=ExecutionStatus.RUNNING,
        created_at=datetime.now(UTC),
    )
    updated = rec.with_step_passed(step_id="stp_render", label="Render Report")
    assert "stp_render" in updated.step_states
    assert len(updated.steps) == 1
    step = updated.steps[0]
    assert step.id == "stp_render"
    assert step.label == "Render Report"
    assert step.status == ExecutionStatus.PASSED
    assert step.progress == 100
    assert updated.step_states["stp_render"] == step


def test_execution_record_without_profile_synthesis() -> None:
    """Verify ExecutionRecord.without_profile_synthesis removes target profile synthesis immutably."""
    cache_item = RenderedSynthesisCache(
        section_syntheses={},
        row_explanations={},
        row_curated_quotes={},
        cited_sources=[],
        xai_highlights=[],
        created_at=datetime.now(UTC),
    )
    rec = ExecutionRecordFactory.build(
        id="exe_0195f3a0000070018234567890abcdef",
        workflow_id="wor_0195f3a0000070018234567890abcdef",
        target_locale="fi",
        status=ExecutionStatus.PASSED,
        profile_syntheses={"prf_0195f3a0000070018234567890abcdef": cache_item},
        created_at=datetime.now(UTC),
    )
    unchanged = rec.without_profile_synthesis("prf_99999999999970018234567890abcdef")
    assert unchanged is rec

    removed = rec.without_profile_synthesis("prf_0195f3a0000070018234567890abcdef")
    assert "prf_0195f3a0000070018234567890abcdef" not in removed.profile_syntheses
    assert "prf_0195f3a0000070018234567890abcdef" in rec.profile_syntheses


def test_execution_record_with_updated_and_cleared_profile_syntheses() -> None:
    """Verify ExecutionRecord profile synthesis update and clear helpers."""
    cache_item = RenderedSynthesisCache(
        section_syntheses={},
        row_explanations={},
        row_curated_quotes={},
        cited_sources=[],
        xai_highlights=[],
        created_at=datetime.now(UTC),
    )
    rec = ExecutionRecordFactory.build(
        id="exe_0195f3a0000070018234567890abcdef",
        workflow_id="wor_0195f3a0000070018234567890abcdef",
        target_locale="fi",
        status=ExecutionStatus.PASSED,
        created_at=datetime.now(UTC),
    )
    updated_only_cache = rec.with_updated_profile_synthesis(
        profile_id="prf_0195f3a0000070018234567890abcdef",
        cache=cache_item,
    )
    assert "prf_0195f3a0000070018234567890abcdef" in updated_only_cache.profile_syntheses
    assert updated_only_cache.steps == []

    render_step = ExecutionStepFactory.build(
        id="stp_render",
        label="Render Step",
        status=ExecutionStatus.PASSED,
    )
    updated_with_step = rec.with_updated_profile_synthesis(
        profile_id="prf_0195f3a0000070018234567890abcdef",
        cache=cache_item,
        step_id="stp_render",
        step_state=render_step,
    )
    assert "prf_0195f3a0000070018234567890abcdef" in updated_with_step.profile_syntheses
    assert "stp_render" in updated_with_step.step_states
    assert len(updated_with_step.steps) == 1

    cleared = updated_with_step.with_cleared_profile_syntheses()
    assert cleared.profile_syntheses == {}


def test_execution_record_transition_step_updates_label_and_merkle_hash() -> None:
    """Verify ExecutionRecord.transition_step updates label and input_merkle_hash."""
    initial_step = ExecutionStepFactory.build(
        id="stp_0195f3a0000070018234567890abcdef",
        label="Initial Label",
        status=ExecutionStatus.RUNNING,
    )
    rec = ExecutionRecordFactory.build(
        id="exe_0195f3a0000070018234567890abcdef",
        workflow_id="wor_0195f3a0000070018234567890abcdef",
        target_locale="fi",
        status=ExecutionStatus.RUNNING,
        steps=[initial_step],
        step_states={"stp_0195f3a0000070018234567890abcdef": initial_step},
        created_at=datetime.now(UTC),
    )
    updated = rec.transition_step(
        step_id="stp_0195f3a0000070018234567890abcdef",
        status=ExecutionStatus.PASSED,
        label="Updated Label",
        input_merkle_hash="a" * 64,
    )
    assert updated.steps[0].label == "Updated Label"
    assert updated.steps[0].input_merkle_hash == "a" * 64


@pytest.mark.parametrize("invalid_strictness", [-1, 101])
def test_execution_summary_snapshot_invalid_strictness_bounds(invalid_strictness: int) -> None:
    """ISTQB Negative Boundary Test: strictness_level outside [0, 100] raises ValidationError."""
    with pytest.raises(ValidationError):
        ExecutionSummarySnapshot.model_validate({"strictness_level": invalid_strictness})


@pytest.mark.parametrize("invalid_progress", [-1, 101])
def test_execution_step_invalid_progress_bounds(invalid_progress: int) -> None:
    """ISTQB Negative Boundary Test: progress outside [0, 100] raises ValidationError."""
    with pytest.raises(ValidationError):
        ExecutionStep.model_validate(
            {
                "id": "stp_step12345678",
                "label": "Analyst Step",
                "progress": invalid_progress,
            }
        )


def test_execution_assignment_instantiation_and_iso_coercion() -> None:
    """Verify ExecutionAssignment instantiation and ISO 8601 string timestamp coercion."""
    assignment = ExecutionAssignment.model_validate_json(
        '{"organization_id": "org_0195f3a0000070018234567890abcdef", '
        '"assigned_email": "candidate@example.com", '
        '"workflow_id": "wor_0195f3a0000070018234567890abcdef", '
        '"token_hash": "' + ("a" * 64) + '", '
        '"task_brief_id": "tbr_0195f3a0000070018234567890abcdef", '
        '"task_brief_snapshot": {"id": "tbr_0195f3a0000070018234567890abcdef", '
        '"label": {"translations": {"en": "Brief", "fi": "Tehtävänanto"}}, '
        '"instruction_text": "Complete the assessment.", "source_url": null}, '
        '"hard_deadline_at": "2026-12-31T23:59:59Z", '
        '"created_by": "usr_0195f3a0000070018234567890abcdef"}'
    )
    assert assignment.id.startswith("tsk_")
    assert assignment.task_brief_id == "tbr_0195f3a0000070018234567890abcdef"
    assert assignment.task_brief_snapshot is not None
    assert assignment.task_brief_snapshot.id == "tbr_0195f3a0000070018234567890abcdef"
    assert assignment.hard_deadline_at == datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC)
    assert assignment.activated_at is None


def test_execution_assignment_negative_boundaries() -> None:
    """ISTQB Negative Boundary Test: invalid relative_duration_seconds (<60), invalid task_brief_id, and invalid ISO timestamp."""
    with pytest.raises(ValidationError):
        ExecutionAssignment.model_validate(
            {
                "organization_id": "org_0195f3a0000070018234567890abcdef",
                "assigned_email": "candidate@example.com",
                "workflow_id": "wor_0195f3a0000070018234567890abcdef",
                "task_brief_id": "tbr_not_a_uuidv7",
                "token_hash": "a" * 64,
                "hard_deadline_at": datetime.now(UTC),
                "created_by": "usr_0195f3a0000070018234567890abcdef",
            }
        )
    with pytest.raises(ValidationError):
        ExecutionAssignment.model_validate(
            {
                "organization_id": "org_0195f3a0000070018234567890abcdef",
                "assigned_email": "candidate@example.com",
                "workflow_id": "wor_0195f3a0000070018234567890abcdef",
                "token_hash": "a" * 64,
                "hard_deadline_at": datetime.now(UTC),
                "relative_duration_seconds": 59,
                "created_by": "usr_0195f3a0000070018234567890abcdef",
            }
        )

    with pytest.raises(ValidationError):
        ExecutionAssignment.model_validate(
            {
                "organization_id": "org_0195f3a0000070018234567890abcdef",
                "assigned_email": "candidate@example.com",
                "workflow_id": "wor_0195f3a0000070018234567890abcdef",
                "token_hash": "a" * 64,
                "hard_deadline_at": "not-a-timestamp",
                "created_by": "usr_0195f3a0000070018234567890abcdef",
            }
        )

    with pytest.raises(ValidationError):
        ExecutionAssignment.model_validate(
            {
                "organization_id": "org_0195f3a0000070018234567890abcdef",
                "assigned_email": "candidate@example.com",
                "workflow_id": "wor_0195f3a0000070018234567890abcdef",
                "task_brief_id": "tbr_0195f3a0000070018234567890abcdef",
                "task_brief_snapshot": None,
                "token_hash": "a" * 64,
                "hard_deadline_at": datetime.now(UTC),
                "created_by": "usr_0195f3a0000070018234567890abcdef",
            }
        )

    with pytest.raises(ValidationError):
        ExecutionAssignment.model_validate(
            {
                "organization_id": "org_0195f3a0000070018234567890abcdef",
                "assigned_email": "candidate@example.com",
                "workflow_id": "wor_0195f3a0000070018234567890abcdef",
                "task_brief_id": "tbr_0195f3a0000070018234567890abcdef",
                "task_brief_snapshot": {
                    "id": "tbr_0195f3a0000070018234567890abcdee",
                    "label": {"translations": {"en": "Other", "fi": "Muu"}},
                    "instruction_text": "Other",
                    "source_url": None,
                },
                "token_hash": "a" * 64,
                "hard_deadline_at": datetime.now(UTC),
                "created_by": "usr_0195f3a0000070018234567890abcdef",
            }
        )
