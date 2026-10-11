"""Global Context Variables DTO.

Strongly typed container for global context variables across hook pipelines,
eliminating loose dictionaries and permissive typing.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.archival import PrecedentDTO
from backend_v2.models.domain.evaluation import EvaluationResult
from backend_v2.models.domain.hydration import HydrationInputSourceDTO
from backend_v2.models.domain.interaction import InteractionAnalysisDTO
from backend_v2.models.domain.linguistics import LinguisticsResultDTO
from backend_v2.models.domain.matrix import FlattenedAtom
from backend_v2.models.domain.metadata import StepMetadataDTO
from backend_v2.models.domain.metrics import ProfilerMetricsDTO
from backend_v2.models.domain.references import BibliographyResultDTO
from backend_v2.models.domain.security import SanitizationResultDTO
from backend_v2.models.dtos.lightweight_matrix import ScoringResultDTO
from backend_v2.models.dtos.synthesis import SynthesisDistillationDTO
from backend_v2.models.dtos.trace import TraceScoringPayloadDTO

__all__ = ["GlobalContextVarsDTO"]


class GlobalContextVarsDTO(V2CoreBase):
    """Strictly typed global context variables container.

    Attributes:
        language: Target translation or execution language.
        target_locale: Client localized language code.
        system_locale: System runtime default locale.
        profile_id: Active output profile identifier.
        organization_id: Multi-tenant organization identifier.
        initiator_id: Execution initiator user identifier.
        step_coach: Coach stage execution telemetry payload.
        knowledge_base: Grounding knowledge context attributes.
        hydration_results: Upstream hydrated input source payloads.
        step_linguistics: Evaluated linguistic statistics and metrics.
        external_evidence: Aggregated external search evidence.
        evaluative_matrices: Dynamic prompt block scores.
        passivity_detected: Whether passivity was detected.
        archivist_precedents: Historical archivist precedents retrieved from prior executions.
        shuffled_atoms: Shuffled flattened atoms for matrix evaluation.
        profiler_metrics: Profiler telemetry metrics.
        distillation: Synthesis distillation payload.
        scoring: Scoring result payload.
        interaction_analysis: Interaction analysis payload.
        bibliography: Bibliography citations payload.
        sanitization: Sanitization payload.
        llm_anomaly_retry_requested: Whether LLM anomaly retry was requested.
        input_control_ratio: Input control ratio metric.
        integrity_verified_output: Integrity verified analyst output or evaluation result.
        step_metadata: Step metadata payload.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    language: Annotated[str | None, Field(default=None, description="Target translation or execution language.")] = None
    target_locale: Annotated[str | None, Field(default=None, description="Client localized language code.")] = None
    system_locale: Annotated[str | None, Field(default=None, description="System runtime default locale.")] = None
    profile_id: Annotated[str | None, Field(default=None, description="Active output profile identifier.")] = None
    organization_id: Annotated[str | None, Field(default=None, description="Multi-tenant organization identifier.")] = (
        None
    )
    initiator_id: Annotated[
        str | None,
        Field(default=None, alias="_sys_initiator_id", description="Execution initiator user identifier."),
    ] = None
    step_coach: Annotated[
        dict[str, str | int | float | bool | list[str]] | None,
        Field(default=None, description="Coach stage execution telemetry payload."),
    ] = None
    knowledge_base: Annotated[
        dict[str, str | int | float | bool | list[str]] | None,
        Field(default=None, description="Grounding knowledge context attributes."),
    ] = None
    hydration_results: Annotated[
        HydrationInputSourceDTO | None,
        Field(default=None, description="Upstream hydrated input source payloads."),
    ] = None
    step_linguistics: Annotated[
        LinguisticsResultDTO | None,
        Field(default=None, description="Evaluated linguistic statistics and metrics."),
    ] = None
    external_evidence: Annotated[
        str | None,
        Field(default=None, description="Aggregated external search evidence."),
    ] = None
    evaluative_matrices: Annotated[
        dict[str, float] | None,
        Field(default=None, description="Dynamic prompt block scores."),
    ] = None
    passivity_detected: Annotated[
        bool | None,
        Field(default=None, description="Whether passivity was detected."),
    ] = None
    archivist_precedents: Annotated[
        list[PrecedentDTO] | None,
        Field(default=None, description="Historical archivist precedents retrieved from prior executions."),
    ] = None
    shuffled_atoms: Annotated[
        list[FlattenedAtom] | None,
        Field(default=None, description="Shuffled flattened atoms for matrix evaluation."),
    ] = None
    profiler_metrics: Annotated[
        ProfilerMetricsDTO | None,
        Field(default=None, description="Profiler telemetry metrics."),
    ] = None
    distillation: Annotated[
        SynthesisDistillationDTO | None,
        Field(default=None, description="Synthesis distillation payload."),
    ] = None
    scoring: Annotated[
        ScoringResultDTO | TraceScoringPayloadDTO | None,
        Field(default=None, description="Scoring result payload."),
    ] = None
    interaction_analysis: Annotated[
        InteractionAnalysisDTO | None,
        Field(default=None, description="Interaction analysis payload."),
    ] = None
    bibliography: Annotated[
        BibliographyResultDTO | None,
        Field(default=None, description="Bibliography citations payload."),
    ] = None
    sanitization: Annotated[
        SanitizationResultDTO | None,
        Field(default=None, description="Sanitization payload."),
    ] = None
    llm_anomaly_retry_requested: Annotated[
        bool | None,
        Field(default=None, description="Whether LLM anomaly retry was requested."),
    ] = None
    input_control_ratio: Annotated[
        float | None,
        Field(default=None, description="Input control ratio metric."),
    ] = None
    integrity_verified_output: Annotated[
        AnalystOutput | EvaluationResult | None,
        Field(default=None, description="Integrity verified analyst output or evaluation result."),
    ] = None
    step_metadata: Annotated[
        StepMetadataDTO | None,
        Field(default=None, description="Step metadata payload."),
    ] = None
