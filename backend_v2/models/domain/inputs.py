"""Domain model for workflow inputs (Payloads)."""

from __future__ import annotations

import logging
from typing import Annotated

from pydantic import ConfigDict, Field, field_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain import analyst as _analyst
from backend_v2.models.domain.archival import ArchivalPrecedentDTO
from backend_v2.models.domain.coach import CoachingPlan
from backend_v2.models.domain.evaluation import EvaluationResult
from backend_v2.models.domain.interaction import InteractionAnalysisDTO
from backend_v2.models.domain.judge import JudgeOutput
from backend_v2.models.domain.linguistics import LinguisticsResultDTO
from backend_v2.models.domain.logician import LogicianOutput
from backend_v2.models.domain.matrix import FlattenedAtom
from backend_v2.models.domain.metadata import MetadataHookPayloadDTO, MetadataHookResultDTO, StepMetadataDTO
from backend_v2.models.domain.metrics import ProfilerMetricsDTO, TextMetricsDTO
from backend_v2.models.domain.performativity import PerformativityOutput
from backend_v2.models.domain.references import BibliographyResultDTO
from backend_v2.models.domain.security import InputProcessingOutputDTO, SanitizationResultDTO
from backend_v2.models.domain.validation import GuttmanAtomItemDTO, ValidationResultDTO
from backend_v2.models.dtos.atom_evaluation import ReducedAtomDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.inputs import (
    Base64Attachment,
    GuidedReflectionInputDTO,
    IngressInputValue,
)
from backend_v2.models.dtos.lightweight_matrix import (
    LightweightMatrixOutput,
    MatrixAggregationStateDTO,
    ScoringResultDTO,
)
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.dtos.synthesis import SynthesisDistillationDTO
from backend_v2.models.dtos.trace import (
    StepTraceMetadataDTO,
    TraceMatrixPayloadDTO,
    TraceScoringPayloadDTO,
)
from backend_v2.models.llm import LLMProviderConfig

logger = logging.getLogger(__name__)

__all__ = [
    "Base64Attachment",
    "DLQAtomSchema",
    "DomainInputValue",
    "IngressInputValue",
    "WorkflowInputs",
    "WorkflowInputsBase",
    "WorkflowInputsIngress",
]


class DLQAtomSchema(V2CoreBase):
    """Strict schema for DLQ validation.

    Attributes:
        atom_id: Target atom identifier.
        tda_id: Target TDA identifier.
        status: DLQ status string.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    atom_id: Annotated[str | None, Field(default=None)] = None
    tda_id: Annotated[str | None, Field(default=None)] = None
    status: Annotated[str | None, Field(default=None)] = None


type DomainInputValue = Annotated[
    StepOutputDTO
    | list[StepOutputDTO]
    | AtomResultDTO
    | list[AtomResultDTO]
    | ReducedAtomDTO
    | list[ReducedAtomDTO]
    | FlattenedAtom
    | list[FlattenedAtom]
    | DLQAtomSchema
    | list[DLQAtomSchema]
    | HydratedAtomDTO
    | dict[str, HydratedAtomDTO]
    | LightweightMatrixOutput
    | MatrixAggregationStateDTO
    | ScoringResultDTO
    | TraceScoringPayloadDTO
    | TraceMatrixPayloadDTO
    | StepTraceMetadataDTO
    | dict[str, float]
    | dict[str, str]
    | GuttmanAtomItemDTO
    | list[GuttmanAtomItemDTO]
    | ValidationResultDTO
    | _analyst.Hypothesis
    | list[_analyst.Hypothesis]
    | _analyst.AnalystOutput
    | JudgeOutput
    | CoachingPlan
    | EvaluationResult
    | MetadataHookPayloadDTO
    | MetadataHookResultDTO
    | SynthesisDistillationDTO
    | ArchivalPrecedentDTO
    | list[ArchivalPrecedentDTO]
    | GuidedReflectionInputDTO
    | StepMetadataDTO
    | LinguisticsResultDTO
    | SanitizationResultDTO
    | InputProcessingOutputDTO
    | ProfilerMetricsDTO
    | TextMetricsDTO
    | BibliographyResultDTO
    | InteractionAnalysisDTO
    | LogicianOutput
    | PerformativityOutput
    | LLMProviderConfig
    | str
    | int
    | float
    | bool
    | list[str]
    | None,
    Field(description="Strict closed union of extracted domain inputs (Base64Attachment strictly excluded)"),
]


class WorkflowInputsBase(V2CoreBase):
    """Base schema for workflow inputs across ingress and domain boundaries.

    Attributes:
        organization_id: Tenant ID for multi-tenancy.
        user_id: User ID for audit trails.
        simulation_mode: If True, indicates a test/simulation run.
        language: Target language code.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    organization_id: Annotated[
        str | None, Field(default=None, min_length=1, description="Tenant ID for multi-tenancy.")
    ] = None
    user_id: Annotated[str | None, Field(default=None, min_length=1, description="User ID for audit trails.")] = None
    simulation_mode: Annotated[bool, Field(default=False, description="If True, indicates a test/simulation run.")] = (
        False
    )
    language: Annotated[
        str, Field(default="en", min_length=1, description="Target language code (e.g., 'en', 'fi').")
    ] = "en"


class WorkflowInputsIngress(WorkflowInputsBase):
    """API Ingress payload for the workflow (Content).

    Allows Base64 attachments during initial API routing, before Eager Extraction happens.

    Attributes:
        dynamic_inputs: Structured dictionary for dynamic workflow inputs.
    """

    dynamic_inputs: dict[str, IngressInputValue] = Field(
        default_factory=dict, description="Structured dictionary for dynamic workflow inputs."
    )


class WorkflowInputs(WorkflowInputsBase):
    """Strict Domain payload for the workflow (Content).

    This model defines the DATA content that the workflow processes.
    It rigorously BANS base64 payloads to protect the DB.

    Attributes:
        dynamic_inputs: Structured dictionary for domain inputs (Base64Attachment excluded).
    """

    dynamic_inputs: dict[str, DomainInputValue] = Field(
        default_factory=dict,
        description="Structured dictionary for domain inputs (Base64Attachment excluded).",
    )

    @field_validator("dynamic_inputs")
    @classmethod
    def validate_no_base64(cls, v: dict[str, DomainInputValue]) -> dict[str, DomainInputValue]:
        """Strictly ban base64 payloads from domain inputs.

        Args:
            v: Dictionary of dynamic domain inputs to validate.

        Returns:
            The validated dictionary of domain inputs.

        Raises:
            ValueError: If a Base64Attachment or content_base64 dictionary payload is present.
        """
        for val in v.values():
            if isinstance(val, Base64Attachment):
                raise ValueError("Base64Attachment is strictly forbidden in WorkflowInputs")
            if type(val) is dict and "content_base64" in val:
                raise ValueError("Base64 payloads are strictly forbidden in WorkflowInputs")
        return v
