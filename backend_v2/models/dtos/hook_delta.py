"""Hook Delta DTOs and Projection Result Containers.

Strictly typed containers returned by hooks, projectors, and analytical services
for state reduction and DAG results without loose dictionaries.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.archival import ArchivalPrecedentDTO
from backend_v2.models.domain.evaluation import EvaluationResult
from backend_v2.models.domain.interaction import InteractionAnalysisDTO
from backend_v2.models.domain.linguistics import LinguisticsResultDTO
from backend_v2.models.domain.matrix import FlattenedAtom
from backend_v2.models.domain.metadata import (
    MetadataHookPayloadDTO,
    MetadataHookResultDTO,
    StepMetadataDTO,
)
from backend_v2.models.domain.metrics import ProfilerMetricsDTO
from backend_v2.models.domain.references import BibliographyResultDTO
from backend_v2.models.domain.security import SanitizationResultDTO
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.validation import ValidationResultDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput, ScoringResultDTO
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.synthesis import SynthesisDistillationDTO
from backend_v2.models.dtos.trace import TraceScoringPayloadDTO
from backend_v2.models.enums import LLMProvider
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.models.state import StepOutputDTO

__all__ = [
    "AnomalyRetryResultDTO",
    "ArchivistPrecedentsResultDTO",
    "ExecutionInputsDTO",
    "ExecutionMetadataDeltaDTO",
    "ExternalEvidenceResultDTO",
    "FlatteningHookOutput",
    "HookDeltaDTO",
    "HookPayloadDTO",
    "InputControlRatioResultDTO",
    "MatrixHookResultDTO",
    "MatrixProjectionResultDTO",
    "MissingContextDTO",
    "PassivityDetectionResultDTO",
    "ProjectedResultsDTO",
    "StepContextMetadataDTO",
    "WorkerJobResultDTO",
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


class PassivityDetectionResultDTO(V2CoreBase):
    """Result payload emitted when passivity penalty is detected.

    Attributes:
        passivity_detected: Flag indicating whether passivity penalty was detected.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    passivity_detected: Annotated[
        bool,
        Field(default=True, description="Flag indicating whether passivity penalty was detected."),
    ] = True


class AnomalyRetryResultDTO(V2CoreBase):
    """Result payload requesting an LLM anomaly retry.

    Attributes:
        llm_anomaly_retry_requested: Flag indicating whether LLM anomaly retry was requested.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    llm_anomaly_retry_requested: Annotated[
        bool,
        Field(default=True, description="Flag indicating whether LLM anomaly retry was requested."),
    ] = True


class InputControlRatioResultDTO(V2CoreBase):
    """Result payload emitted by metrics hook with calculated input control ratio.

    Attributes:
        input_control_ratio: Calculated input control ratio value.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    input_control_ratio: Annotated[
        float,
        Field(ge=0.0, description="Calculated input control ratio value."),
    ]


class ExternalEvidenceResultDTO(V2CoreBase):
    """Result payload containing external evidence retrieved via search tools.

    Attributes:
        external_evidence: Consolidated external evidence XML string.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    external_evidence: Annotated[
        str,
        Field(description="Consolidated external evidence XML string."),
    ]


class ExecutionMetadataDeltaDTO(V2CoreBase):
    """Typed metadata updates container to merge into ExecutionMetadata.

    Attributes:
        matrix_sampling_strategy: Optional sampling strategy limit override.
        estimated_token_count: Optional estimated token proxy count.
        mcp_audit_traces: Optional audit traces from MCP external searches.
        provider_override: Optional execution-level LLM provider override.
        model_registry_id: Optional system config ID of attached model registry.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    matrix_sampling_strategy: Annotated[
        int | None,
        Field(default=None, ge=0, description="Sampling strategy limit override."),
    ] = None
    estimated_token_count: Annotated[
        int | None,
        Field(default=None, ge=0, description="Estimated token proxy count."),
    ] = None
    mcp_audit_traces: Annotated[
        list[MCPAuditTrace] | None,
        Field(default=None, description="MCP external search audit traces."),
    ] = None
    provider_override: Annotated[
        LLMProvider | None,
        Field(default=None, description="Execution-level LLM provider override."),
    ] = None
    model_registry_id: Annotated[
        str | None,
        Field(default=None, description="System config ID of the attached model registry."),
    ] = None


class ArchivistPrecedentsResultDTO(V2CoreBase):
    """Encapsulates historical archivist precedents retrieved from prior executions.

    Attributes:
        archivist_precedents: List of archival precedent DTOs.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    archivist_precedents: Annotated[
        list[ArchivalPrecedentDTO],
        Field(default_factory=list, description="List of archival precedent DTOs."),
    ]


class FlatteningHookOutput(V2CoreBase):
    """Strict schema for matrix atom flattening hook state delta payload.

    Attributes:
        shuffled_atoms: List of selected and randomized extraction items.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    shuffled_atoms: Annotated[
        list[FlattenedAtom],
        Field(description="List of selected and randomized extraction items."),
    ]


class StepContextMetadataDTO(V2CoreBase):
    """Encapsulates extracted step context metadata for LLM prompt compiler execution.

    Attributes:
        gvars: Global context variables dictionary.
        doc_aliases: Document aliases available in the step context.
        dag_results: Mapping of atom ID to evaluated AtomResultDTO.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    gvars: Annotated[
        dict[str, object],
        Field(default_factory=dict, description="Global context variables dictionary."),
    ]
    doc_aliases: Annotated[
        list[str],
        Field(default_factory=list, description="Document aliases available in context."),
    ]
    dag_results: Annotated[
        dict[str, AtomResultDTO],
        Field(default_factory=dict, description="Mapping of atom ID to evaluated atom result."),
    ]


class WorkerJobResultDTO(V2CoreBase):
    """Data Transfer Object representing the result of a background worker job.

    Attributes:
        status: Execution status of the job (e.g., COMPLETED, FAILED/DLQ).
        execution_id: ID of the execution record if available.
        workflow_id: ID of the workflow configuration if available.
        duration_ms: Duration of the job execution in milliseconds.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    status: Annotated[str, Field(description="Execution status of the job.")]
    execution_id: Annotated[
        str | None,
        Field(default=None, description="ID of the execution record."),
    ] = None
    workflow_id: Annotated[
        str | None,
        Field(default=None, description="ID of the workflow configuration."),
    ] = None
    duration_ms: Annotated[
        int,
        Field(default=0, ge=0, description="Duration in milliseconds."),
    ] = 0


# NOTE: Code-path-instantiated union — no JSON deserialization, no discriminator needed.
type HookPayloadDTO = (
    GlobalContextVarsDTO
    | MatrixHookResultDTO
    | SynthesisDistillationDTO
    | StepOutputDTO
    | SanitizationResultDTO
    | BibliographyResultDTO
    | AnalystOutput
    | EvaluationResult
    | MetadataHookPayloadDTO
    | MetadataHookResultDTO
    | StepMetadataDTO
    | PassivityDetectionResultDTO
    | AnomalyRetryResultDTO
    | InputControlRatioResultDTO
    | ProfilerMetricsDTO
    | ExternalEvidenceResultDTO
    | FlatteningHookOutput
    | ScoringResultDTO
    | TraceScoringPayloadDTO
    | InteractionAnalysisDTO
    | LinguisticsResultDTO
    | LLMProviderConfig
    | ValidationResultDTO
    | ExecutionInputsDTO
    | ArchivistPrecedentsResultDTO
)


class HookDeltaDTO(V2CoreBase):
    """Strict state delta container returned by hooks for state reduction.

    Attributes:
        delta: Typed state delta payload to merge into execution context.
        metadata_updates: Optional metadata updates to merge into ExecutionMetadata.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    delta: Annotated[
        HookPayloadDTO | None,
        Field(default=None, description="Typed state delta payload to merge into execution context."),
    ] = None
    metadata_updates: Annotated[
        ExecutionMetadataDeltaDTO | None,
        Field(default=None, description="Optional metadata updates to merge into ExecutionMetadata."),
    ] = None
