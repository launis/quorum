"""Immutable Pydantic V2 Proposition Graph & Report Binary Domain Models.

Defines Draft and Persisted Toulmin/Causal proposition graph entities
(PropositionPayloadDTO, NodeDraft, EdgeDraft, PropositionNode, DependencyEdge,
FalsifiedClaimMatch), ReportBinaryPayloadDTO for PostgreSQL 19 TOAST binary storage,
and CycleDetectedError for fail-fast DAG cycle enforcement.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Annotated, Self

from fastapi import status
from pydantic import ConfigDict, Field, field_validator, model_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, V2CoreBase
from backend_v2.models.enums import DependencyRelationType, PropositionNodeType

__all__ = [
    "CycleDetectedError",
    "DependencyEdge",
    "EdgeDraft",
    "FalsifiedClaimMatch",
    "NodeDraft",
    "PropositionNode",
    "PropositionPayloadDTO",
    "ReportBinaryPayloadDTO",
]

logger = logging.getLogger(__name__)


def _validate_probability_bounds(value: float, field_name: str) -> float:
    """Validate that a floating-point confidence score lies within [0.0, 1.0].

    Args:
        value: Candidate float score.
        field_name: Name of the validated field for error reporting.

    Returns:
        Validated float in [0.0, 1.0].

    Raises:
        ValueError: If value is less than 0.0 or greater than 1.0.
    """
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{field_name} must be within [0.0, 1.0], got {value}.")
    return value


def _validate_causal_weight_bounds(value: float) -> float:
    """Validate that a floating-point causal edge weight lies within [-1.0, 1.0].

    Args:
        value: Candidate float weight.

    Returns:
        Validated float in [-1.0, 1.0].

    Raises:
        ValueError: If value is less than -1.0 or greater than 1.0.
    """
    if value < -1.0 or value > 1.0:
        raise ValueError(f"causal_weight must be within [-1.0, 1.0], got {value}.")
    return value


# Step 2: Immutable Pydantic V2 Draft and Persisted Proposition Graph Models
class PropositionPayloadDTO(V2CoreBase):
    """Structured JSONB payload for a Toulmin or SCM proposition node.

    Attributes:
        statement: Canonical proposition statement or claim text.
        source_atom_id: Optional originating Opaque Stripe atom identifier.
        source_quotes: Immutable tuple of exact lexical evidence quotes.
        metadata: Flat typed primitive telemetry attributes.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    statement: Annotated[
        str,
        Field(min_length=1, description="Canonical proposition statement or claim text."),
    ]
    source_atom_id: Annotated[
        str | None,
        Field(
            default=None,
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="Optional originating atom ID.",
        ),
    ] = None
    source_quotes: Annotated[
        tuple[str, ...],
        Field(default=(), description="Exact lexical evidence quotes."),
    ] = ()
    metadata: Annotated[
        dict[str, str | int | float | bool],
        Field(default_factory=dict, description="Flat typed primitive telemetry attributes."),
    ]


class NodeDraft(V2CoreBase):
    """In-memory symbolic proposition node draft produced during a Kahn topological wave.

    Attributes:
        local_key: Wave-local symbolic identifier resolved to a UUIDv7 key by PostgreSQL 19.
        node_type: Toulmin or SCM node classification.
        confidence: Confidence score in [0.0, 1.0].
        payload: Strictly validated proposition payload DTO.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    local_key: Annotated[
        str,
        Field(min_length=1, max_length=128, description="Wave-local symbolic identifier."),
    ]
    node_type: Annotated[
        PropositionNodeType,
        Field(description="Toulmin or SCM node classification."),
    ]
    confidence: Annotated[
        float,
        Field(description="Confidence score in [0.0, 1.0]."),
    ]
    payload: Annotated[
        PropositionPayloadDTO,
        Field(description="Strictly validated proposition payload DTO."),
    ]

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Enforce [0.0, 1.0] bounds on confidence via validator per Vertex grammar rules.

        Args:
            v: Candidate confidence value.

        Returns:
            Validated confidence float.

        Raises:
            ValueError: If v is outside [0.0, 1.0].
        """
        return _validate_probability_bounds(v, "confidence")


class EdgeDraft(V2CoreBase):
    """In-memory symbolic dependency edge draft linking two NodeDraft local keys.

    Attributes:
        source_key: Source NodeDraft local_key.
        target_key: Target NodeDraft local_key.
        relation_type: Causal or Toulmin relation type.
        causal_weight: Edge weight in [-1.0, 1.0].
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    source_key: Annotated[
        str,
        Field(min_length=1, max_length=128, description="Source NodeDraft local_key."),
    ]
    target_key: Annotated[
        str,
        Field(min_length=1, max_length=128, description="Target NodeDraft local_key."),
    ]
    relation_type: Annotated[
        DependencyRelationType,
        Field(description="Causal or Toulmin relation type."),
    ]
    causal_weight: Annotated[
        float,
        Field(default=1.0, description="Edge weight in [-1.0, 1.0]."),
    ] = 1.0

    @field_validator("causal_weight")
    @classmethod
    def validate_causal_weight(cls, v: float) -> float:
        """Enforce [-1.0, 1.0] bounds on causal_weight via validator.

        Args:
            v: Candidate causal_weight value.

        Returns:
            Validated causal_weight float.

        Raises:
            ValueError: If v is outside [-1.0, 1.0].
        """
        return _validate_causal_weight_bounds(v)

    @model_validator(mode="after")
    def validate_no_self_loop(self) -> Self:
        """Reject self-referential draft edges where source_key equals target_key.

        Returns:
            Validated EdgeDraft instance.

        Raises:
            ValueError: If source_key == target_key.
        """
        if self.source_key == self.target_key:
            raise ValueError(f"EdgeDraft self-loop prohibited: source_key == target_key ('{self.source_key}').")
        return self


class PropositionNode(V2CoreBase):
    """Persisted proposition node hydrated from PostgreSQL 19 quorum_nodes.

    Attributes:
        node_id: Persisted nod_<uuid7_hex> identifier.
        run_id: Parent exe_<uuid7_hex> identifier.
        node_type: Toulmin or SCM node classification.
        confidence: Confidence score in [0.0, 1.0].
        payload: Validated proposition payload.
        created_at: Timestamp extracted from PostgreSQL 19 VIRTUAL column.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    node_id: Annotated[
        str,
        Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Persisted nod_<uuid7_hex> identifier."),
    ]
    run_id: Annotated[
        str,
        Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Parent exe_<uuid7_hex> identifier."),
    ]
    node_type: Annotated[
        PropositionNodeType,
        Field(description="Toulmin or SCM node classification."),
    ]
    confidence: Annotated[
        float,
        Field(description="Confidence score in [0.0, 1.0]."),
    ]
    payload: Annotated[
        PropositionPayloadDTO,
        Field(description="Validated proposition payload."),
    ]
    created_at: Annotated[
        datetime,
        Field(description="Timestamp extracted from PostgreSQL 19 VIRTUAL column."),
    ]

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Enforce [0.0, 1.0] bounds on confidence.

        Args:
            v: Candidate confidence value.

        Returns:
            Validated confidence float.

        Raises:
            ValueError: If v is outside [0.0, 1.0].
        """
        return _validate_probability_bounds(v, "confidence")


class DependencyEdge(V2CoreBase):
    """Persisted directed dependency edge hydrated from PostgreSQL 19 quorum_edges.

    Attributes:
        edge_id: Persisted edg_<uuid7_hex> identifier.
        run_id: Parent exe_<uuid7_hex> identifier.
        source_id: Source nod_<uuid7_hex> identifier.
        target_id: Target nod_<uuid7_hex> identifier.
        relation_type: Relation classification.
        causal_weight: Edge weight in [-1.0, 1.0].
        created_at: Timestamp extracted from PostgreSQL 19 VIRTUAL column.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    edge_id: Annotated[
        str,
        Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Persisted edg_<uuid7_hex> identifier."),
    ]
    run_id: Annotated[
        str,
        Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Parent exe_<uuid7_hex> identifier."),
    ]
    source_id: Annotated[
        str,
        Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Source nod_<uuid7_hex> identifier."),
    ]
    target_id: Annotated[
        str,
        Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Target nod_<uuid7_hex> identifier."),
    ]
    relation_type: Annotated[
        DependencyRelationType,
        Field(description="Relation classification."),
    ]
    causal_weight: Annotated[
        float,
        Field(default=1.0, description="Edge weight in [-1.0, 1.0]."),
    ] = 1.0
    created_at: Annotated[
        datetime,
        Field(description="Timestamp extracted from PostgreSQL 19 VIRTUAL column."),
    ]

    @field_validator("causal_weight")
    @classmethod
    def validate_causal_weight(cls, v: float) -> float:
        """Enforce [-1.0, 1.0] bounds on causal_weight.

        Args:
            v: Candidate causal_weight value.

        Returns:
            Validated causal_weight float.

        Raises:
            ValueError: If v is outside [-1.0, 1.0].
        """
        return _validate_causal_weight_bounds(v)

    @model_validator(mode="after")
    def validate_no_self_loop(self) -> Self:
        """Reject self-referential persisted edges where source_id equals target_id.

        Returns:
            Validated DependencyEdge instance.

        Raises:
            ValueError: If source_id == target_id.
        """
        if self.source_id == self.target_id:
            raise ValueError(f"DependencyEdge self-loop prohibited: source_id == target_id ('{self.source_id}').")
        return self


class FalsifiedClaimMatch(V2CoreBase):
    """Result DTO representing a claim falsified by a high-confidence rebuttal of its warrant.

    Attributes:
        rebuttal_id: Rebuttal nod_<uuid7_hex> identifier.
        invalidated_warrant_id: Invalidated warrant nod_<uuid7_hex> identifier.
        falsified_claim_id: Falsified claim nod_<uuid7_hex> identifier.
        rebuttal_confidence: Confidence of the rebuttal node in [0.0, 1.0].
        claim_statement: Statement text of the falsified claim.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    rebuttal_id: Annotated[
        str,
        Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Rebuttal nod_<uuid7_hex>."),
    ]
    invalidated_warrant_id: Annotated[
        str,
        Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Invalidated warrant nod_<uuid7_hex>."),
    ]
    falsified_claim_id: Annotated[
        str,
        Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Falsified claim nod_<uuid7_hex>."),
    ]
    rebuttal_confidence: Annotated[
        float,
        Field(description="Confidence of the rebuttal node."),
    ]
    claim_statement: Annotated[
        str,
        Field(min_length=1, description="Statement text of the falsified claim."),
    ]

    @field_validator("rebuttal_confidence")
    @classmethod
    def validate_rebuttal_confidence(cls, v: float) -> float:
        """Enforce [0.0, 1.0] bounds on rebuttal_confidence.

        Args:
            v: Candidate rebuttal_confidence value.

        Returns:
            Validated rebuttal_confidence float.

        Raises:
            ValueError: If v is outside [0.0, 1.0].
        """
        return _validate_probability_bounds(v, "rebuttal_confidence")


class ReportBinaryPayloadDTO(V2CoreBase):
    """Immutable binary payload DTO for PostgreSQL 19 lz4-compressed TOAST report storage.

    Attributes:
        report_id: Parent rep_<uuid7_hex> identifier.
        mime_type: MIME type of binary payload.
        pdf_bytes: Raw binary PDF bytes stored in TOAST table.
        size_bytes: Exact byte length.
        created_at: Creation timestamp.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    report_id: Annotated[
        str,
        Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Parent rep_<uuid7_hex> identifier."),
    ]
    mime_type: Annotated[
        str,
        Field(default="application/pdf", min_length=1, description="MIME type of binary payload."),
    ] = "application/pdf"
    pdf_bytes: Annotated[
        bytes,
        Field(description="Raw binary PDF bytes stored in TOAST table."),
    ]
    size_bytes: Annotated[
        int,
        Field(ge=0, description="Exact byte length."),
    ]
    created_at: Annotated[
        datetime,
        Field(description="Creation timestamp."),
    ]


class CycleDetectedError(AppException):
    """Domain exception raised when a cycle is detected in the proposition graph DAG.

    Attributes:
        run_id: Parent execution identifier where the cycle occurred.
        cycle_path: Immutable tuple of node identifiers forming the cycle.
    """

    def __init__(self, run_id: str, cycle_path: tuple[str, ...]) -> None:
        """Initialize CycleDetectedError with RFC 7807 structured details.

        Args:
            run_id: Parent exe_<uuid7_hex> identifier.
            cycle_path: Ordered sequence of node IDs forming the cycle.
        """
        self.run_id = run_id
        self.cycle_path = tuple(cycle_path)
        cycle_display = " -> ".join(self.cycle_path)
        msg = f"Cycle detected in proposition graph for run '{run_id}': {cycle_display}"
        logger.error(
            "[PropositionGraph] %s: %s",
            ErrorCodes.VALIDATION_FAILED.name,
            msg,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "run_id": run_id},
        )
        super().__init__(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "error_code": ErrorCodes.VALIDATION_FAILED.value,
                "run_id": run_id,
                "cycle_path": list(self.cycle_path),
            },
        )
