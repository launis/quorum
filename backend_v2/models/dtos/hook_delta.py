"""Hook Delta DTOs and Projection Result Containers.

Strictly typed containers returned by hooks, projectors, and analytical services
for state reduction and DAG results without loose dictionaries.
"""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.metadata import MetadataHookPayloadDTO
from backend_v2.models.domain.references import BibliographyResultDTO
from backend_v2.models.domain.security import SanitizationResultDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.synthesis import SynthesisDistillationDTO
from backend_v2.models.state import StepOutputDTO

__all__ = [
    "HookDeltaDTO",
    "MatrixHookResultDTO",
    "MatrixProjectionResultDTO",
    "MissingContextDTO",
    "ProjectedResultsDTO",
]


class ProjectedResultsDTO(V2CoreBase):
    """Frozen DTO encapsulating projected atom execution results and references.

    Attributes:
        results: List of projected atom result DTOs.
        hydrated_references: Mapping of atom ID to hydrated atom reference DTO.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    results: Annotated[list[AtomResultDTO], Field(description="List of projected atom result DTOs.")]
    hydrated_references: Annotated[
        dict[str, HydratedAtomDTO],
        Field(description="Mapping of atom ID to hydrated atom reference DTO."),
    ]


class MissingContextDTO(V2CoreBase):
    """DTO representing missing atoms and context text in matrix projection.

    Attributes:
        missing_atoms: List of missing atom textual labels or descriptions.
        missing_context_text: Formatted context string detailing missing atoms.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    missing_atoms: Annotated[list[str], Field(description="List of missing atom textual labels or descriptions.")]
    missing_context_text: Annotated[
        str | None,
        Field(default=None, description="Formatted context string detailing missing atoms."),
    ] = None


class MatrixProjectionResultDTO(V2CoreBase):
    """Frozen DTO returned by ResultProjector.project_matrix_results.

    Attributes:
        results: List of evaluated atom results.
        matrix_output: Computed lightweight matrix scoring output.
        missing_context: Structured missing context DTO if any criteria missed.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    results: Annotated[list[AtomResultDTO], Field(description="List of evaluated atom results.")]
    matrix_output: Annotated[LightweightMatrixOutput, Field(description="Computed lightweight matrix scoring output.")]
    missing_context: Annotated[
        MissingContextDTO | None,
        Field(default=None, description="Structured missing context DTO if any criteria missed."),
    ] = None


class MatrixHookResultDTO(V2CoreBase):
    """Strongly typed analytical output payload emitted by matrix scoring hook.

    Attributes:
        matrix_outputs: Mapping of prompt block ID to computed matrix outputs.
        missing_contexts: Mapping of prompt block ID to missing criteria summary text.
        atom_quotes: Mapping of prompt block ID to list of extracted quote evidence DTOs.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    matrix_outputs: Annotated[
        dict[str, LightweightMatrixOutput],
        Field(description="Mapping of prompt block ID to computed matrix outputs."),
    ]
    missing_contexts: Annotated[
        dict[str, str],
        Field(description="Mapping of prompt block ID to missing criteria summary text."),
    ]
    atom_quotes: Annotated[
        dict[str, list[QuoteEvidenceDTO]],
        Field(description="Mapping of prompt block ID to list of extracted quote evidence DTOs."),
    ]


class HookDeltaDTO(V2CoreBase):
    """Strict state delta container returned by hooks for state reduction.

    Attributes:
        delta: Typed state delta payload to merge into execution context.
        metadata_updates: Optional metadata updates to merge into ExecutionMetadata.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    delta: Annotated[
        MatrixHookResultDTO
        | SynthesisDistillationDTO
        | StepOutputDTO
        | SanitizationResultDTO
        | BibliographyResultDTO
        | MetadataHookPayloadDTO
        | dict[str, Any]
        | None,
        Field(default=None, description="Typed state delta payload to merge into execution context."),
    ] = None
    metadata_updates: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Optional metadata updates to merge into ExecutionMetadata."),
    ] = None
