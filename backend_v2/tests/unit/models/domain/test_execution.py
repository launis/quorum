"""Unit tests for execution domain models."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.execution import (
    EvaluatedMatrixContextDTO,
    EvidenceRejectionRequest,
    ExecutionCreate,
    ExecutionRecord,
    ExecutionStep,
    ExecutionSummarySnapshot,
    FrozenContext,
    JobAcceptedDTO,
)
from backend_v2.models.dtos.atom_result import EvaluatedAtomDTO
from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
from backend_v2.models.dtos.theory_manifest import InjectedTheoryManifestDTO
from backend_v2.models.enums import ExecutionStatus, LLMProvider


def test_frozen_context_instantiation() -> None:
    fc = FrozenContext()
    assert fc.compiled_prompts == {}
    assert fc.injected_theory == InjectedTheoryManifestDTO()
    assert fc.generated_schemas == GeneratedSchemaManifestDTO()
    assert fc.ui_hints_snapshot == {}
    assert fc.mcp_tool_audit == []


def test_theory_manifest_immutability() -> None:
    """Test contract: InjectedTheoryManifestDTO rejects in-place attribute mutations."""
    manifest = InjectedTheoryManifestDTO(theories={"th_1": "Theory text"})
    assert manifest.theories["th_1"] == "Theory text"
    with pytest.raises((ValidationError, TypeError)):
        manifest.theories = {"th_2": "New"}  # type: ignore[misc]


def test_schema_manifest_immutability() -> None:
    """Test contract: GeneratedSchemaManifestDTO rejects in-place attribute mutations."""
    manifest = GeneratedSchemaManifestDTO(schemas={"stp_1": {"type": "object"}})
    assert "stp_1" in manifest
    assert manifest["stp_1"] == {"type": "object"}
    with pytest.raises((ValidationError, TypeError)):
        manifest.schemas = {"stp_2": {"type": "string"}}  # type: ignore[misc]


def test_execution_create_defaults() -> None:
    ec = ExecutionCreate(
        workflow_id="wor_1234567890abcdef",
        target_locale="fi",
    )
    assert ec.workflow_id == "wor_1234567890abcdef"
    assert ec.target_locale == "fi"
    assert ec.profile_id is None
    assert ec.matrix_sampling_strategy > 0
    assert ec.provider_override is None
    assert ec.model_registry_id is None


def test_execution_create_custom_and_validator() -> None:
    ec = ExecutionCreate(
        workflow_id="wor_1234567890abcdef",
        target_locale="en",
        profile_id="pro_1234567890abcdef",
        matrix_sampling_strategy=None,
        provider_override=LLMProvider.OPENAI,
        model_registry_id="reg_1234567890abcdef",
    )
    assert ec.matrix_sampling_strategy > 0
    assert ec.provider_override == LLMProvider.OPENAI


def test_execution_create_extra_forbidden() -> None:
    with pytest.raises(ValidationError):
        ExecutionCreate(
            workflow_id="wor_1234567890abcdef",
            target_locale="fi",
            unexpected_field="disallowed",  # type: ignore[call-arg]
        )


def test_execution_step_instantiation() -> None:
    step = ExecutionStep(
        id="stp_step12345678",
        label="Analyst Step",
        status=ExecutionStatus.RUNNING,
    )
    assert step.id == "stp_step12345678"
    assert step.label == "Analyst Step"
    assert step.status == ExecutionStatus.RUNNING
    assert step.scorecard_atoms == {}
    assert step.prompt_tokens == 0
    assert step.has_warning is False


def test_execution_step_extra_forbidden() -> None:
    with pytest.raises(ValidationError):
        ExecutionStep(
            id="stp_step12345678",
            label="Analyst Step",
            unexpected="bad",  # type: ignore[call-arg]
        )


def test_execution_summary_snapshot() -> None:
    snap = ExecutionSummarySnapshot(
        strictness_level=85,
        is_ensemble_run=True,
        is_degraded=False,
    )
    assert snap.strictness_level == 85
    assert snap.is_ensemble_run is True
    assert snap.is_degraded is False
    assert snap.system_concurrency_snapshot == {}


def test_evaluated_matrix_context_dto() -> None:
    dto = EvaluatedMatrixContextDTO(
        evaluated_atoms={"atm_1": "PASSED"},
        raw_atoms=[EvaluatedAtomDTO(tda_id="atm_1", status="PASSED", score=1.0)],
    )
    assert dto.evaluated_atoms == {"atm_1": "PASSED"}
    assert len(dto.raw_atoms) == 1
    assert dto.raw_atoms[0].tda_id == "atm_1"


def test_job_accepted_dto() -> None:
    dto = JobAcceptedDTO(
        status="ACCEPTED",
        message="Job queued",
        execution_id="exe_1234567890abcdef",
    )
    assert dto.status == "ACCEPTED"
    assert dto.execution_id == "exe_1234567890abcdef"


def test_evidence_rejection_request() -> None:
    req = EvidenceRejectionRequest(rejection_reason="Quote out of context")
    assert req.rejection_reason == "Quote out of context"


def test_execution_record_instantiation() -> None:
    rec = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wor_1234567890abcdef",
        target_locale="fi",
        status=ExecutionStatus.PENDING,
        created_at=datetime.now(timezone.utc),
    )
    assert rec.id == "exe_1234567890abcdef"
    assert rec.workflow_id == "wor_1234567890abcdef"
    assert rec.status == ExecutionStatus.PENDING
    assert rec.steps == []
    assert rec.step_states == {}
    assert rec.profile_syntheses == {}
