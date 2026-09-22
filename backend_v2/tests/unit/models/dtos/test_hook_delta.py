"""Unit tests for hook delta and projection DTOs.

Verifies strict typing, immutability, extra forbidden constraints,
sealed payload unions, and serialization parity across all hook delta models.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.archival import ArchivalPrecedentDTO
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.engine import FlattenedAtom
from backend_v2.models.dtos.hook_delta import (
    AnomalyRetryResultDTO,
    ArchivistPrecedentsResultDTO,
    ExecutionMetadataDeltaDTO,
    ExternalEvidenceResultDTO,
    FlatteningHookOutput,
    HookDeltaDTO,
    InputControlRatioResultDTO,
    MatrixHookResultDTO,
    MatrixProjectionResultDTO,
    MissingContextDTO,
    PassivityDetectionResultDTO,
    ProjectedResultsDTO,
    StepContextMetadataDTO,
    WorkerJobResultDTO,
)
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.enums import ExecutionStatus, LaxSDUIComponentType


def _build_test_atom_result() -> AtomResultDTO:
    """Helper to construct a valid AtomResultDTO fixture."""
    return AtomResultDTO(
        tda_id="tda_11112222333344445555666677778888",
        status=ExecutionStatus.PASSED,
        source_quote="Direct evidence quotation.",
        evaluation_reasoning="Valid justification evidence.",
    )


def test_projected_results_dto() -> None:
    """Verify ProjectedResultsDTO instantiation, immutability, and extra forbid."""
    atom = _build_test_atom_result()
    hydrated = HydratedAtomDTO(
        sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Test assertion",
        source_quote=atom.source_quote,
    )
    dto = ProjectedResultsDTO(results=[atom], hydrated_references={atom.tda_id: hydrated})
    assert len(dto.results) == 1
    assert atom.tda_id in dto.hydrated_references

    with pytest.raises(ValidationError):
        dto.results = []  # type: ignore[misc]

    with pytest.raises(ValidationError):
        ProjectedResultsDTO.model_validate({"results": [atom], "hydrated_references": {}, "extra": 1})


def test_missing_context_dto() -> None:
    """Verify MissingContextDTO instantiation, immutability, and extra forbid."""
    dto = MissingContextDTO(missing_atoms=["Atom A", "Atom B"], missing_context_text="Missing A, B")
    assert dto.missing_atoms == ["Atom A", "Atom B"]
    assert dto.missing_context_text == "Missing A, B"

    with pytest.raises(ValidationError):
        dto.missing_atoms = []  # type: ignore[misc]

    with pytest.raises(ValidationError):
        MissingContextDTO.model_validate({"missing_atoms": [], "forbidden": "field"})


def test_matrix_projection_result_dto() -> None:
    """Verify MatrixProjectionResultDTO instantiation, immutability, and extra forbid."""
    atom = _build_test_atom_result()
    matrix = LightweightMatrixOutput(raw_score=4.0, normalized_score=80.0, justification="Good")
    missing = MissingContextDTO(missing_atoms=["Atom C"])
    dto = MatrixProjectionResultDTO(results=[atom], matrix_output=matrix, missing_context=missing)

    assert len(dto.results) == 1
    assert dto.matrix_output.raw_score == 4.0
    assert dto.missing_context is not None
    assert dto.missing_context.missing_atoms == ["Atom C"]

    with pytest.raises(ValidationError):
        dto.matrix_output = matrix  # type: ignore[misc]

    with pytest.raises(ValidationError):
        MatrixProjectionResultDTO.model_validate({"results": [atom], "matrix_output": matrix, "unexpected": True})


def test_matrix_hook_result_dto() -> None:
    """Verify MatrixHookResultDTO instantiation, immutability, and extra forbid."""
    matrix = LightweightMatrixOutput(raw_score=5.0, normalized_score=100.0)
    quote = QuoteEvidenceDTO(quote="Verifiable text", verified_source_ids=[])
    dto = MatrixHookResultDTO(
        matrix_outputs={"blk_test": matrix},
        missing_contexts={"blk_test": "None missing"},
        atom_quotes={"blk_test": [quote]},
    )
    assert "blk_test" in dto.matrix_outputs
    assert dto.missing_contexts["blk_test"] == "None missing"
    assert len(dto.atom_quotes["blk_test"]) == 1

    with pytest.raises(ValidationError):
        dto.matrix_outputs = {}  # type: ignore[misc]

    with pytest.raises(ValidationError):
        MatrixHookResultDTO.model_validate(
            {
                "matrix_outputs": {},
                "missing_contexts": {},
                "atom_quotes": {},
                "invalid_extra": "value",
            }
        )


def test_new_hook_payload_dtos() -> None:
    """Verify all newly introduced payload DTOs."""
    passivity = PassivityDetectionResultDTO(passivity_detected=True)
    assert passivity.passivity_detected is True

    anomaly = AnomalyRetryResultDTO(llm_anomaly_retry_requested=True)
    assert anomaly.llm_anomaly_retry_requested is True

    ratio = InputControlRatioResultDTO(input_control_ratio=0.75)
    assert ratio.input_control_ratio == 0.75

    evidence = ExternalEvidenceResultDTO(external_evidence="<evidence>Test</evidence>")
    assert evidence.external_evidence == "<evidence>Test</evidence>"

    trace = MCPAuditTrace(
        tool_id="mcp_search",
        step_name="stp_test",
        query="test",
        source_urls=["https://example.com"],
    )
    metadata_delta = ExecutionMetadataDeltaDTO(
        matrix_sampling_strategy=5,
        estimated_token_count=120,
        mcp_audit_traces=[trace],
    )
    assert metadata_delta.matrix_sampling_strategy == 5
    assert metadata_delta.estimated_token_count == 120
    assert metadata_delta.mcp_audit_traces is not None
    assert len(metadata_delta.mcp_audit_traces) == 1

    precedent = ArchivalPrecedentDTO(id="exe_001", date="2026-09-22", scores="4.5", verdict="Pass")
    precedents_dto = ArchivistPrecedentsResultDTO(archivist_precedents=[precedent])
    assert len(precedents_dto.archivist_precedents) == 1

    flattened = FlattenedAtom(atom_id="atm_001", question="Does it pass?")
    flattening = FlatteningHookOutput(shuffled_atoms=[flattened])
    assert len(flattening.shuffled_atoms) == 1

    atom = _build_test_atom_result()
    step_ctx = StepContextMetadataDTO(
        gvars={"key": "val"},
        doc_aliases=["doc1"],
        dag_results={atom.tda_id: atom},
    )
    assert step_ctx.gvars["key"] == "val"
    assert step_ctx.doc_aliases == ["doc1"]
    assert atom.tda_id in step_ctx.dag_results

    worker_res = WorkerJobResultDTO(status="COMPLETED", execution_id="exe_001", duration_ms=250)
    assert worker_res.status == "COMPLETED"
    assert worker_res.execution_id == "exe_001"
    assert worker_res.duration_ms == 250


def test_hook_delta_dto_variants_and_roundtrip() -> None:
    """Verify HookDeltaDTO with various delta models and full-duplex roundtrip."""
    matrix = LightweightMatrixOutput(raw_score=3.0, normalized_score=60.0)
    matrix_hook_res = MatrixHookResultDTO(
        matrix_outputs={"blk_1": matrix},
        missing_contexts={"blk_1": "Missing"},
        atom_quotes={"blk_1": []},
    )
    meta = ExecutionMetadataDeltaDTO(estimated_token_count=100)
    delta_dto = HookDeltaDTO(delta=matrix_hook_res, metadata_updates=meta)
    assert delta_dto.delta == matrix_hook_res
    assert delta_dto.metadata_updates is not None
    assert delta_dto.metadata_updates.estimated_token_count == 100

    dumped = delta_dto.model_dump(mode="json")
    reconstituted = HookDeltaDTO.model_validate(dumped)
    assert isinstance(reconstituted.delta, MatrixHookResultDTO)
    assert reconstituted.delta.matrix_outputs["blk_1"].raw_score == 3.0

    empty_delta = HookDeltaDTO()
    assert empty_delta.delta is None
    assert empty_delta.metadata_updates is None

    with pytest.raises(ValidationError):
        empty_delta.delta = None  # type: ignore[misc]

    with pytest.raises(ValidationError):
        HookDeltaDTO.model_validate({"extra_forbidden": True})


def test_hook_delta_dto_negative_partitions() -> None:
    """ISTQB Negative Partitions: Assert raw dictionaries are rejected in delta and metadata_updates."""
    with pytest.raises(ValidationError):
        HookDeltaDTO(delta={"raw": 1})  # type: ignore[arg-type]

    with pytest.raises(ValidationError):
        HookDeltaDTO(metadata_updates={"invalid_key": "val"})  # type: ignore[arg-type]
