"""Causal discovery immutable Pydantic V2 DTO contracts.

Defines 8 strictly typed models for autonomous text DAG argument mining,
topological causal graphs, root-cause fault attribution, and fair scoring arithmetic.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field, model_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import CausalRootCauseType, LaxExecutionStatus

__all__ = [
    "AntiFluffAuditDTO",
    "CausalEdgeDTO",
    "CausalGraphPayloadDTO",
    "CausalNodeDTO",
    "CausalRootCauseDiagnosisDTO",
    "CausalTdaFusionResultDTO",
    "FairScoringBreakdownDTO",
    "PrescriptiveRemediationDTO",
]


class CausalNodeDTO(V2CoreBase):
    """Node representation in an argument causal graph."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    node_id: Annotated[str, Field(description="Unique identifier for the causal node.")]
    claim: Annotated[str, Field(description="Textual claim statement evaluated in the node.")]
    source_quote: Annotated[
        str | None, Field(default=None, description="Exact verbatim source quote from document.")
    ] = None
    paragraph_ref: Annotated[
        str | None, Field(default=None, description="Paragraph or block reference in source text.")
    ] = None
    status: Annotated[LaxExecutionStatus, Field(description="Execution and verification status.")]
    blame_parent_ids: Annotated[
        list[str],
        Field(default_factory=list, description="IDs of upstream parent nodes contributing to failure."),
    ]
    dependent_child_ids: Annotated[
        list[str],
        Field(default_factory=list, description="IDs of downstream nodes affected by this node."),
    ]
    tda_score: Annotated[float | None, Field(default=None, description="Evaluated TDA cognitive score.")] = None
    tda_level_key: Annotated[str | None, Field(default=None, description="TDA qualitative level key.")] = None
    source_input_key: Annotated[
        str | None, Field(default=None, description="Dynamic input key indicating source document provenance.")
    ] = None


class CausalEdgeDTO(V2CoreBase):
    """Directed causal dependency edge between two argument nodes."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    source_id: Annotated[str, Field(description="Source/parent node ID in the causal dependency.")]
    target_id: Annotated[str, Field(description="Target/dependent node ID in the causal dependency.")]
    reasoning: Annotated[str, Field(description="Logical reasoning explaining the dependency relationship.")]


class CausalGraphPayloadDTO(V2CoreBase):
    """Full causal argument graph payload."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    nodes: Annotated[list[CausalNodeDTO], Field(description="List of causal argument nodes.")]
    edges: Annotated[
        list[CausalEdgeDTO],
        Field(default_factory=list, description="List of directed dependency edges."),
    ]
    root_cause_node_ids: Annotated[
        list[str],
        Field(default_factory=list, description="IDs of identified root cause failure nodes."),
    ]
    cycle_detected: Annotated[
        bool, Field(default=False, description="Flag indicating if cycle was detected during traversal.")
    ] = False
    isolated_node_ids: Annotated[
        list[str],
        Field(default_factory=list, description="IDs of isolated claims lacking inbound/outbound links."),
    ]
    partition_node_ids: Annotated[
        dict[str, list[str]],
        Field(default_factory=dict, description="Mapping of dynamic input_key to list of contained causal node IDs."),
    ]
    edge_root_causes: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="List of serialized edge IDs ('source_id->target_id') failing warrant grounding or precondition validation.",
        ),
    ]

    @model_validator(mode="after")
    def validate_referential_integrity(self) -> CausalGraphPayloadDTO:
        """Verifies that all edge endpoints, root cause IDs, and isolated node IDs exist in nodes.

        Raises:
            ValueError: If an unextracted node reference is detected.

        Returns:
            The validated CausalGraphPayloadDTO instance.
        """
        valid_node_ids = {node.node_id for node in self.nodes}
        for edge in self.edges:
            if edge.source_id not in valid_node_ids:
                raise ValueError(f"Edge source_id '{edge.source_id}' does not exist in graph nodes.")
            if edge.target_id not in valid_node_ids:
                raise ValueError(f"Edge target_id '{edge.target_id}' does not exist in graph nodes.")
        for root_id in self.root_cause_node_ids:
            if root_id not in valid_node_ids:
                raise ValueError(f"Root cause node_id '{root_id}' does not exist in graph nodes.")
        for isolated_id in self.isolated_node_ids:
            if isolated_id not in valid_node_ids:
                raise ValueError(f"Isolated node_id '{isolated_id}' does not exist in graph nodes.")
        for doc_key, part_node_ids in self.partition_node_ids.items():
            for p_node_id in part_node_ids:
                if p_node_id not in valid_node_ids:
                    raise ValueError(
                        f"Partition '{doc_key}' references node_id '{p_node_id}' that does not exist in graph nodes."
                    )
        valid_edge_ids = {f"{edge.source_id}->{edge.target_id}" for edge in self.edges}
        for edge_id in self.edge_root_causes:
            if edge_id not in valid_edge_ids:
                raise ValueError(f"Edge root cause '{edge_id}' does not match any active edge in graph edges.")
        return self


class CausalRootCauseDiagnosisDTO(V2CoreBase):
    """Root cause diagnostic detail for an argument failure."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    failing_node_id: Annotated[str, Field(description="ID of the failing dependent node.")]
    root_cause_parent_id: Annotated[str, Field(description="ID of the upstream root cause parent.")]
    paragraph_ref: Annotated[str, Field(description="Source paragraph reference.")]
    explanation: Annotated[str, Field(description="Causal chain explanation of why the root cause led to failure.")]
    penalty_points: Annotated[float, Field(description="Attributed penalty points.")]
    root_cause_type: Annotated[
        CausalRootCauseType,
        Field(
            default=CausalRootCauseType.NODE_FAILURE,
            description="Categorization of failure as node claim flaw, warrant grounding failure, or precondition mismatch.",
        ),
    ] = CausalRootCauseType.NODE_FAILURE


class AntiFluffAuditDTO(V2CoreBase):
    """Audit summary detecting hollow concepts, ungrounded claims, and logical cohesion."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    isolated_concept_count: Annotated[int, Field(description="Number of isolated unlinked claims.")]
    cycle_detected: Annotated[bool, Field(description="Whether causal loops or circular reasoning occurred.")]
    unsupported_claims_count: Annotated[int, Field(description="Count of claims lacking evidentiary foundation.")]
    logical_cohesion_score: Annotated[float, Field(description="Overall structural cohesion score (0.0 - 1.0).")]
    detected_hollow_terms: Annotated[
        list[str],
        Field(default_factory=list, description="Detected hollow or performative buzzwords."),
    ]


class PrescriptiveRemediationDTO(V2CoreBase):
    """Actionable prescriptive remediation unlocking downstream score improvements."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    target_node_id: Annotated[str, Field(description="Target node requiring remediation.")]
    required_action: Annotated[str, Field(description="Concrete action required to rectify the logical flaw.")]
    unlocks_node_ids: Annotated[
        list[str],
        Field(default_factory=list, description="Downstream nodes unlocked if this node is fixed."),
    ]
    potential_score_impact: Annotated[float, Field(description="Estimated positive impact on total evaluation score.")]


class FairScoringBreakdownDTO(V2CoreBase):
    """Fair scoring breakdown attributing penalties and savings across causal chains."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    independent_error_count: Annotated[int, Field(ge=0, description="Count of independent, non-cascading errors.")]
    cascading_fault_count: Annotated[int, Field(ge=0, description="Count of secondary cascading faults.")]
    raw_penalty_points: Annotated[float, Field(ge=0.0, description="Raw unpenalized deduction points.")]
    deduplicated_penalty_points: Annotated[
        float, Field(ge=0.0, description="Penalty points after deduplicating cascading faults.")
    ]
    dampened_savings_points: Annotated[float, Field(ge=0.0, description="Points saved via secondary fault dampening.")]

    @model_validator(mode="after")
    def validate_scoring_identity(self) -> FairScoringBreakdownDTO:
        """Verifies mathematical identity raw == deduplicated + dampened_savings.

        Raises:
            ValueError: If identity is violated or penalty values are negative.

        Returns:
            The validated FairScoringBreakdownDTO instance.
        """
        if self.independent_error_count < 0:
            raise ValueError(f"independent_error_count must be non-negative: {self.independent_error_count}")
        if self.cascading_fault_count < 0:
            raise ValueError(f"cascading_fault_count must be non-negative: {self.cascading_fault_count}")
        if self.raw_penalty_points < 0.0:
            raise ValueError(f"raw_penalty_points must be non-negative: {self.raw_penalty_points}")
        if self.deduplicated_penalty_points < 0.0:
            raise ValueError(f"deduplicated_penalty_points must be non-negative: {self.deduplicated_penalty_points}")
        if self.dampened_savings_points < 0.0:
            raise ValueError(f"dampened_savings_points must be non-negative: {self.dampened_savings_points}")

        expected_sum = self.deduplicated_penalty_points + self.dampened_savings_points
        if abs(self.raw_penalty_points - expected_sum) >= 1e-4:
            raise ValueError(
                f"Scoring identity violated: raw_penalty_points ({self.raw_penalty_points}) "
                f"!= deduplicated_penalty_points ({self.deduplicated_penalty_points}) "
                f"+ dampened_savings_points ({self.dampened_savings_points}) "
                f"(diff: {abs(self.raw_penalty_points - expected_sum):.6f} >= 1e-4)."
            )
        return self


class CausalTdaFusionResultDTO(V2CoreBase):
    """Composite fusion result combining causal graph discovery and TDA evaluation."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    graph: Annotated[CausalGraphPayloadDTO, Field(description="Complete causal argument graph.")]
    root_cause_diagnoses: Annotated[
        list[CausalRootCauseDiagnosisDTO],
        Field(default_factory=list, description="Root cause diagnostics for all cascade failures."),
    ]
    anti_fluff_audit: Annotated[AntiFluffAuditDTO, Field(description="Anti-fluff and cohesion audit metrics.")]
    prescriptive_remediations: Annotated[
        list[PrescriptiveRemediationDTO],
        Field(default_factory=list, description="Prescriptive remediation steps to unlock performance."),
    ]
    fair_scoring: Annotated[FairScoringBreakdownDTO, Field(description="Fair scoring arithmetic breakdown.")]
    total_deliverable_nodes: Annotated[
        int, Field(ge=0, default=0, description="Total node count in deliverable subgraph.")
    ] = 0
