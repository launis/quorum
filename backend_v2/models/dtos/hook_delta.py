"""Hook Delta DTOs and Projection Result Containers.

Strictly typed containers returned by hooks, projectors, and analytical services
for state reduction and DAG results without loose dictionaries.
"""

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
    """Frozen DTO encapsulating projected atom execution results and references."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    results: list[AtomResultDTO]
    hydrated_references: dict[str, HydratedAtomDTO]


class MissingContextDTO(V2CoreBase):
    """DTO representing missing atoms and context text in matrix projection."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    missing_atoms: list[str]
    missing_context_text: str | None = None


class MatrixProjectionResultDTO(V2CoreBase):
    """Frozen DTO returned by ResultProjector.project_matrix_results."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    results: list[AtomResultDTO]
    matrix_output: LightweightMatrixOutput
    missing_context: MissingContextDTO | None = None


class MatrixHookResultDTO(V2CoreBase):
    """Strongly typed analytical output payload emitted by matrix scoring hook."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    matrix_outputs: dict[str, LightweightMatrixOutput]
    missing_contexts: dict[str, str]
    atom_quotes: dict[str, list[QuoteEvidenceDTO]]


class HookDeltaDTO(V2CoreBase):
    """Strict state delta container returned by hooks for state reduction."""

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
