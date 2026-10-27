"""Unit and ISTQB boundary value tests for backend_v2/models/domain/proposition_graph.py.

Covers positive instantiation and >=2 negative boundary cases per model
(PropositionPayloadDTO, NodeDraft, EdgeDraft, PropositionNode, DependencyEdge,
FalsifiedClaimMatch, ReportBinaryPayloadDTO, and CycleDetectedError).
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import generate_uuid7_opaque_id
from backend_v2.models.domain.proposition_graph import (
    CycleDetectedError,
    DependencyEdge,
    EdgeDraft,
    FalsifiedClaimMatch,
    NodeDraft,
    PropositionNode,
    PropositionPayloadDTO,
    ReportBinaryPayloadDTO,
)
from backend_v2.models.enums import DependencyRelationType, EntityPrefix, PropositionNodeType


def test_proposition_payload_and_node_draft_positive_and_boundaries() -> None:
    """Verify PropositionPayloadDTO and NodeDraft valid instantiation and ISTQB float boundaries."""
    payload = PropositionPayloadDTO(
        statement="Revenue grew 18% YoY in Q4.",
        source_atom_id=generate_uuid7_opaque_id(EntityPrefix.TDA),
        source_quotes=("Revenue grew 18% YoY",),
        metadata={"page": 4, "verified": True},
    )
    draft_min = NodeDraft(
        local_key="ground_1",
        node_type=PropositionNodeType.GROUND,
        confidence=0.0,
        payload=payload,
    )
    draft_max = NodeDraft(
        local_key="claim_1",
        node_type=PropositionNodeType.CLAIM,
        confidence=1.0,
        payload=payload,
    )
    assert draft_min.confidence == 0.0
    assert draft_max.confidence == 1.0

    # Negative 1: confidence < 0.0 and > 1.0
    with pytest.raises(ValidationError):
        NodeDraft(local_key="n1", node_type=PropositionNodeType.CLAIM, confidence=-0.001, payload=payload)

    with pytest.raises(ValidationError):
        NodeDraft(local_key="n1", node_type=PropositionNodeType.CLAIM, confidence=1.001, payload=payload)

    # Negative 2: empty statement or invalid source_atom_id regex
    with pytest.raises(ValidationError):
        PropositionPayloadDTO(statement="")

    with pytest.raises(ValidationError):
        PropositionPayloadDTO(statement="Valid", source_atom_id="bad_id")


def test_edge_draft_and_dependency_edge_self_loop_and_weight_boundaries() -> None:
    """Verify EdgeDraft and DependencyEdge enforce [-1.0, 1.0] weights and reject self-loops."""
    edge_draft = EdgeDraft(
        source_key="ground_1",
        target_key="warrant_1",
        relation_type=DependencyRelationType.SUPPORTS,
        causal_weight=-1.0,
    )
    assert edge_draft.causal_weight == -1.0

    now = datetime.now(UTC)
    run_id = generate_uuid7_opaque_id(EntityPrefix.EXECUTION)
    node_a = generate_uuid7_opaque_id(EntityPrefix.NODE)
    node_b = generate_uuid7_opaque_id(EntityPrefix.NODE)
    edge_id = generate_uuid7_opaque_id(EntityPrefix.EDGE)

    persisted_edge = DependencyEdge(
        edge_id=edge_id,
        run_id=run_id,
        source_id=node_a,
        target_id=node_b,
        relation_type=DependencyRelationType.WARRANTS,
        causal_weight=1.0,
        created_at=now,
    )
    assert persisted_edge.edge_id == edge_id

    # Negative 1: Self-loop on EdgeDraft and DependencyEdge
    with pytest.raises(ValidationError):
        EdgeDraft(source_key="same_key", target_key="same_key", relation_type=DependencyRelationType.CAUSES)

    with pytest.raises(ValidationError):
        DependencyEdge(
            edge_id=edge_id,
            run_id=run_id,
            source_id=node_a,
            target_id=node_a,
            relation_type=DependencyRelationType.CAUSES,
            causal_weight=0.5,
            created_at=now,
        )

    # Negative 2: causal_weight < -1.0 and > 1.0
    with pytest.raises(ValidationError):
        EdgeDraft(
            source_key="a",
            target_key="b",
            relation_type=DependencyRelationType.SUPPORTS,
            causal_weight=-1.001,
        )

    with pytest.raises(ValidationError):
        DependencyEdge(
            edge_id=edge_id,
            run_id=run_id,
            source_id=node_a,
            target_id=node_b,
            relation_type=DependencyRelationType.SUPPORTS,
            causal_weight=1.001,
            created_at=now,
        )


def test_proposition_node_falsified_claim_and_report_binary_models() -> None:
    """Verify PropositionNode, FalsifiedClaimMatch, ReportBinaryPayloadDTO, and CycleDetectedError."""
    now = datetime.now(UTC)
    run_id = generate_uuid7_opaque_id(EntityPrefix.EXECUTION)
    node_id = generate_uuid7_opaque_id(EntityPrefix.NODE)
    warrant_id = generate_uuid7_opaque_id(EntityPrefix.NODE)
    claim_id = generate_uuid7_opaque_id(EntityPrefix.NODE)
    report_id = generate_uuid7_opaque_id(EntityPrefix.REPORT)

    node = PropositionNode(
        node_id=node_id,
        run_id=run_id,
        node_type=PropositionNodeType.REBUTTAL,
        confidence=0.95,
        payload=PropositionPayloadDTO(statement="Audit disproved margin expansion."),
        created_at=now,
    )
    assert node.confidence == 0.95

    match_dto = FalsifiedClaimMatch(
        rebuttal_id=node_id,
        invalidated_warrant_id=warrant_id,
        falsified_claim_id=claim_id,
        rebuttal_confidence=0.95,
        claim_statement="Margin expansion is sustainable.",
    )
    assert match_dto.falsified_claim_id == claim_id

    binary_dto = ReportBinaryPayloadDTO(
        report_id=report_id,
        pdf_bytes=b"%PDF-1.7 sample",
        size_bytes=15,
        created_at=now,
    )
    assert binary_dto.mime_type == "application/pdf"
    assert binary_dto.size_bytes == 15

    # Negative 1: PropositionNode and FalsifiedClaimMatch out-of-range confidence
    with pytest.raises(ValidationError):
        PropositionNode(
            node_id=node_id,
            run_id=run_id,
            node_type=PropositionNodeType.CLAIM,
            confidence=1.5,
            payload=PropositionPayloadDTO(statement="Invalid"),
            created_at=now,
        )

    with pytest.raises(ValidationError):
        FalsifiedClaimMatch(
            rebuttal_id=node_id,
            invalidated_warrant_id=warrant_id,
            falsified_claim_id=claim_id,
            rebuttal_confidence=-0.1,
            claim_statement="Claim",
        )

    # Negative 2: ReportBinaryPayloadDTO negative size_bytes
    with pytest.raises(ValidationError):
        ReportBinaryPayloadDTO(
            report_id=report_id,
            pdf_bytes=b"",
            size_bytes=-1,
            created_at=now,
        )

    # CycleDetectedError contract
    cycle_err = CycleDetectedError(run_id=run_id, cycle_path=(node_id, warrant_id, node_id))
    assert cycle_err.run_id == run_id
    assert cycle_err.cycle_path == (node_id, warrant_id, node_id)
    assert cycle_err.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
