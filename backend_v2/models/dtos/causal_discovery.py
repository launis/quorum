"""Causal discovery immutable Pydantic V2 DTO contracts.

Defines 9 strictly typed models for autonomous text DAG argument mining,
topological causal graphs, root-cause fault attribution, and fair scoring arithmetic.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BeforeValidator, ConfigDict, Field, field_validator, model_validator

from backend_v2.models.core_base import V2CoreBase, coerce_source_quotes_tuple
from backend_v2.models.domain.proposition_graph import FalsifiedClaimMatch
from backend_v2.models.enums import CausalRootCauseType, LaxCausalRootCauseType, LaxExecutionStatus

__all__ = [
    "AntiFluffAuditDTO",
    "CausalEdgeDTO",
    "CausalGraphPayloadDTO",
    "CausalNodeDTO",
    "CausalRootCauseDiagnosisDTO",
    "CausalTdaFusionResultDTO",
    "CounterfactualSimulationResultDTO",
    "FairScoringBreakdownDTO",
    "PrescriptiveRemediationDTO",
]


class CausalNodeDTO(V2CoreBase):
    """Node representation in an argument causal graph.

    Attributes:
        node_id: Unique identifier for the causal node.
        claim: Textual claim statement evaluated in the node.
        source_quotes: Exact verbatim source quote segments from document.
        paragraph_ref: Paragraph or block reference in source text.
        status: Execution and verification status.
        blame_parent_ids: IDs of upstream parent nodes contributing to failure.
        dependent_child_ids: IDs of downstream nodes affected by this node.
        tda_score: Evaluated TDA cognitive score.
        tda_level_key: TDA qualitative level key.
        source_input_key: Dynamic input key indicating source document provenance.
        short_circuited_by_claims: Human-readable prerequisite claims that short-circuited this causal node.
        falsified_warrant_claims: Formatted Toulmin rebuttal-warrant-claim falsification entries for this node.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    node_id: Annotated[str, Field(description="Unique identifier for the causal node.")]
    claim: Annotated[str, Field(description="Textual claim statement evaluated in the node.")]
    source_quotes: Annotated[
        tuple[str, ...] | None,
        BeforeValidator(coerce_source_quotes_tuple),
        Field(default=None, description="Exact verbatim source quote segments from document."),
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
    # Phase 3, Step 3.1: Node-level topological short-circuit and Toulmin falsification lineage
    short_circuited_by_claims: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Human-readable prerequisite claims that short-circuited this causal node.",
        ),
    ]
    falsified_warrant_claims: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Formatted Toulmin rebuttal-warrant-claim falsification entries for this node.",
        ),
    ]


class CausalEdgeDTO(V2CoreBase):
    """Directed causal dependency edge between two argument nodes.

    Attributes:
        source_id: Source/parent node ID in the causal dependency.
        target_id: Target/dependent node ID in the causal dependency.
        reasoning: Logical reasoning explaining the dependency relationship.
        warrant_quotes: Verbatim source quotes grounding the Toulmin inferential warrant.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    source_id: Annotated[str, Field(description="Source/parent node ID in the causal dependency.")]
    target_id: Annotated[str, Field(description="Target/dependent node ID in the causal dependency.")]
    reasoning: Annotated[str, Field(description="Logical reasoning explaining the dependency relationship.")]
    warrant_quotes: Annotated[
        tuple[str, ...] | None,
        BeforeValidator(coerce_source_quotes_tuple),
        Field(
            default=None,
            description="Verbatim source quotes grounding the Toulmin inferential warrant.",
        ),
    ] = None


class CausalGraphPayloadDTO(V2CoreBase):
    """Full causal argument graph payload.

    Attributes:
        nodes: List of causal argument nodes.
        edges: List of directed dependency edges.
        root_cause_node_ids: IDs of identified root cause failure nodes.
        cycle_detected: Flag indicating if cycle was detected during traversal.
        isolated_node_ids: IDs of isolated claims lacking inbound/outbound links.
        partition_node_ids: Mapping of dynamic input_key to list of contained causal node IDs.
        edge_root_causes: List of serialized edge IDs failing warrant grounding or validation.
    """

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
            description=(
                "List of serialized edge IDs ('source_id->target_id') failing warrant grounding "
                "or precondition validation."
            ),
        ),
    ]

    @model_validator(mode="after")
    def validate_referential_integrity(self) -> CausalGraphPayloadDTO:
        """Verify that all edge endpoints, root cause IDs, and isolated node IDs exist in nodes.

        Returns:
            The validated CausalGraphPayloadDTO instance.

        Raises:
            ValueError: If an unextracted node or edge reference is detected.
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
    """Root cause diagnostic detail for an argument failure.

    Attributes:
        failing_node_id: ID of the failing dependent node.
        root_cause_parent_id: ID of the upstream root cause parent.
        paragraph_ref: Source paragraph reference.
        explanation: Causal chain explanation of why the root cause led to failure.
        penalty_points: Attributed penalty points.
        root_cause_type: Categorization of failure as node, warrant, or precondition failure.
        root_cause_claim: Human-readable claim statement of the upstream root cause parent.
        failing_node_claim: Human-readable claim statement of the failing dependent node.
        warrant_relation: Toulmin inferential relation type on the dependency edge.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    failing_node_id: Annotated[str, Field(description="ID of the failing dependent node.")]
    root_cause_parent_id: Annotated[str, Field(description="ID of the upstream root cause parent.")]
    paragraph_ref: Annotated[str, Field(description="Source paragraph reference.")]
    explanation: Annotated[str, Field(description="Causal chain explanation of why the root cause led to failure.")]
    penalty_points: Annotated[float, Field(description="Attributed penalty points.")]
    root_cause_type: Annotated[
        LaxCausalRootCauseType,
        Field(
            default=CausalRootCauseType.NODE_FAILURE,
            description=(
                "Categorization of failure as node claim flaw, warrant grounding failure, or precondition mismatch."
            ),
        ),
    ] = CausalRootCauseType.NODE_FAILURE
    # Resolved claim texts and warrant relation for self-contained root-cause diagnostics
    root_cause_claim: Annotated[
        str,
        Field(
            default="",
            description="Human-readable claim statement of the upstream root cause parent node.",
        ),
    ] = ""
    failing_node_claim: Annotated[
        str,
        Field(
            default="",
            description="Human-readable claim statement of the failing dependent node.",
        ),
    ] = ""
    warrant_relation: Annotated[
        Literal["supports", "rebuts", "warrants"],
        Field(
            default="warrants",
            description="Toulmin inferential relation type on the dependency edge.",
        ),
    ] = "warrants"


class AntiFluffAuditDTO(V2CoreBase):
    """Audit summary detecting hollow concepts, ungrounded claims, and logical cohesion.

    Attributes:
        isolated_concept_count: Number of isolated unlinked claims.
        cycle_detected: Whether causal loops or circular reasoning occurred.
        unsupported_claims_count: Count of claims lacking evidentiary foundation.
        logical_cohesion_score: Overall structural cohesion score (0.0 - 1.0).
        largest_component_ratio: Fraction of deliverable claims in the largest weakly connected component (0.0 - 1.0).
        branch_convergence_ratio: Fraction of deliverable claims with in-degree >= 2 (0.0 - 1.0).
        steering_coupling_ratio: Fraction of deliverable root claims anchored by dialogue directives (0.0 - 1.0).
        detected_hollow_terms: Detected hollow or performative buzzwords.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    isolated_concept_count: Annotated[int, Field(description="Number of isolated unlinked claims.")]
    cycle_detected: Annotated[bool, Field(description="Whether causal loops or circular reasoning occurred.")]
    unsupported_claims_count: Annotated[int, Field(description="Count of claims lacking evidentiary foundation.")]
    logical_cohesion_score: Annotated[float, Field(description="Overall structural cohesion score (0.0 - 1.0).")]
    largest_component_ratio: Annotated[
        float,
        Field(
            default=1.0,
            description="Fraction of deliverable claims in the largest weakly connected component (0.0 - 1.0).",
        ),
    ] = 1.0
    branch_convergence_ratio: Annotated[
        float,
        Field(
            default=0.0,
            description="Fraction of deliverable claims synthesizing multi-premise warrants with in-degree >= 2 (0.0 - 1.0).",
        ),
    ] = 0.0
    steering_coupling_ratio: Annotated[
        float,
        Field(
            default=0.0,
            description="Fraction of deliverable foundational root claims anchored by upstream dialogue directives (0.0 - 1.0).",
        ),
    ] = 0.0
    detected_hollow_terms: Annotated[
        list[str],
        Field(default_factory=list, description="Detected hollow or performative buzzwords."),
    ]

    # Enforce topological ratio bounds [0.0, 1.0] via @field_validator per vertex_serving_grammar_fix
    @field_validator(
        "largest_component_ratio",
        "branch_convergence_ratio",
        "steering_coupling_ratio",
    )
    @classmethod
    def validate_ratio_bounds(cls, value: float) -> float:
        """Validate that topological ratios reside strictly within [0.0, 1.0].

        Args:
            value: Candidate ratio float value.

        Returns:
            Validated ratio float value.

        Raises:
            ValueError: If value is outside [0.0, 1.0].
        """
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Topological ratio must be within [0.0, 1.0], got {value}.")
        return value


class PrescriptiveRemediationDTO(V2CoreBase):
    """Actionable prescriptive remediation unlocking downstream score improvements.

    Attributes:
        target_node_id: Target node requiring remediation.
        required_action: Concrete action required to rectify the logical flaw.
        unlocks_node_ids: Downstream nodes unlocked if this node is fixed.
        potential_score_impact: Estimated positive impact on total evaluation score.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    target_node_id: Annotated[str, Field(description="Target node requiring remediation.")]
    required_action: Annotated[str, Field(description="Concrete action required to rectify the logical flaw.")]
    unlocks_node_ids: Annotated[
        list[str],
        Field(default_factory=list, description="Downstream nodes unlocked if this node is fixed."),
    ]
    potential_score_impact: Annotated[float, Field(description="Estimated positive impact on total evaluation score.")]


class FairScoringBreakdownDTO(V2CoreBase):
    """Fair scoring breakdown attributing penalties and savings across causal chains.

    Attributes:
        independent_error_count: Count of independent, non-cascading errors.
        cascading_fault_count: Count of secondary cascading faults.
        raw_penalty_points: Raw unpenalized deduction points.
        deduplicated_penalty_points: Penalty points after deduplicating cascading faults.
        dampened_savings_points: Points saved via secondary fault dampening.
    """

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
        """Verify mathematical identity raw == deduplicated + dampened_savings.

        Returns:
            The validated FairScoringBreakdownDTO instance.

        Raises:
            ValueError: If the scoring identity is violated beyond tolerance (1e-4).
        """
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
    """Composite fusion result combining causal graph discovery and TDA evaluation.

    Attributes:
        graph: Complete causal argument graph.
        root_cause_diagnoses: Root cause diagnostics for all cascade failures.
        anti_fluff_audit: Anti-fluff and cohesion audit metrics.
        prescriptive_remediations: Prescriptive remediation steps to unlock performance.
        fair_scoring: Fair scoring arithmetic breakdown.
        total_deliverable_nodes: Total node count in deliverable subgraph.
        falsified_claims: Toulmin falsified claims resolved via 3-way rebuttal-warrant-claim join.
    """

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
    # Toulmin 3-way rebuttal-warrant-claim falsified claim matches
    falsified_claims: Annotated[
        list[FalsifiedClaimMatch],
        Field(
            default_factory=list,
            description="Toulmin falsified claims resolved via 3-way rebuttal-warrant-claim join.",
        ),
    ]


class CounterfactualSimulationResultDTO(V2CoreBase):
    """Result contract for Algorithm 1 discrete counterfactual premise retraction simulation.

    Attributes:
        retracted_root_id: ID of the retracted root proposition node.
        collapsed_node_ids: Downstream node IDs that collapsed into BLOCKED state during cascade.
        surviving_node_ids: Node IDs that survived the counterfactual retraction.
        collapse_ratio: Fraction of graph nodes invalidated by the retraction cascade (0.0 - 1.0).
        max_cascade_depth: Maximum topological hop depth reached by the collapse cascade.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    retracted_root_id: Annotated[str, Field(description="ID of the retracted root proposition node.")]
    collapsed_node_ids: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Downstream node IDs that collapsed into BLOCKED state during counterfactual cascade.",
        ),
    ]
    surviving_node_ids: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Node IDs that survived the counterfactual retraction.",
        ),
    ]
    collapse_ratio: Annotated[
        float,
        Field(
            default=0.0,
            description="Fraction of graph nodes invalidated by the retraction cascade (0.0 - 1.0).",
        ),
    ] = 0.0
    max_cascade_depth: Annotated[
        int,
        Field(
            ge=0,
            default=0,
            description="Maximum topological hop depth reached by the counterfactual collapse cascade.",
        ),
    ] = 0

    @field_validator("collapse_ratio")
    @classmethod
    def validate_collapse_ratio_bounds(cls, value: float) -> float:
        """Validate that collapse_ratio resides strictly within [0.0, 1.0].

        Args:
            value: Candidate collapse_ratio float value.

        Returns:
            Validated collapse_ratio float value.

        Raises:
            ValueError: If value is outside [0.0, 1.0].
        """
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"collapse_ratio must be within [0.0, 1.0], got {value}.")
        return value
