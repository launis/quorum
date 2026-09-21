"""Domain model for workflow inputs (Payloads)."""

from __future__ import annotations

import logging
from typing import Annotated

from pydantic import ConfigDict, Field, field_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.analyst import Hypothesis
from backend_v2.models.domain.interaction import InteractionAnalysisDTO
from backend_v2.models.domain.linguistics import LinguisticsResultDTO
from backend_v2.models.domain.matrix import FlattenedAtom
from backend_v2.models.domain.metadata import StepMetadataDTO
from backend_v2.models.domain.metrics import TextMetricsDTO
from backend_v2.models.domain.references import BibliographyResultDTO
from backend_v2.models.domain.security import SanitizationResultDTO
from backend_v2.models.domain.validation import GuttmanAtomItemDTO, ValidationResultDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.inputs import GuidedReflectionInputDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput, ScoringResultDTO
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.dtos.trace import TraceScoringPayloadDTO
from backend_v2.models.llm import LLMProviderConfig

logger = logging.getLogger(__name__)


class Base64Attachment(V2CoreBase):
    """Strict DTO for handling binary base64 file uploads.

    Attributes:
        filename: The name of the uploaded file.
        content_base64: The base64 encoded binary content.
        content_type: Optional MIME type.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    filename: Annotated[str, Field(description="The name of the uploaded file")]
    content_base64: Annotated[str, Field(description="The base64 encoded binary content")]
    content_type: Annotated[str | None, Field(default=None, description="Optional MIME type")] = None


class DLQAtomSchema(V2CoreBase):
    """Strict schema for DLQ validation."""

    model_config = ConfigDict(strict=True, extra="forbid")

    atom_id: Annotated[str | None, Field(default=None)] = None
    tda_id: Annotated[str | None, Field(default=None)] = None
    status: Annotated[str | None, Field(default=None)] = None


type IngressInputValue = Annotated[
    Base64Attachment | GuidedReflectionInputDTO | str | int | float | bool | list[str],
    Field(description="Strict closed union of allowed ingress workflow input values"),
]

type DomainInputValue = Annotated[
    StepOutputDTO
    | list[StepOutputDTO]
    | AtomResultDTO
    | list[AtomResultDTO]
    | FlattenedAtom
    | list[FlattenedAtom]
    | DLQAtomSchema
    | list[DLQAtomSchema]
    | HydratedAtomDTO
    | dict[str, HydratedAtomDTO]
    | LightweightMatrixOutput
    | ScoringResultDTO
    | TraceScoringPayloadDTO
    | dict[str, float]
    | dict[str, str]
    | GuttmanAtomItemDTO
    | list[GuttmanAtomItemDTO]
    | ValidationResultDTO
    | Hypothesis
    | list[Hypothesis]
    | GuidedReflectionInputDTO
    | StepMetadataDTO
    | LinguisticsResultDTO
    | SanitizationResultDTO
    | TextMetricsDTO
    | BibliographyResultDTO
    | InteractionAnalysisDTO
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

    dynamic_inputs: Annotated[
        dict[str, IngressInputValue],
        Field(default_factory=dict, description="Structured dictionary for dynamic workflow inputs."),
    ] = Field(default_factory=dict)


class WorkflowInputs(WorkflowInputsBase):
    """Strict Domain payload for the workflow (Content).

    This model defines the DATA content that the workflow processes.
    It rigorously BANS base64 payloads to protect the DB.

    Attributes:
        dynamic_inputs: Structured dictionary for domain inputs (Base64Attachment excluded).
    """

    dynamic_inputs: Annotated[
        dict[str, DomainInputValue],
        Field(
            default_factory=dict,
            description="Structured dictionary for domain inputs (Base64Attachment excluded).",
        ),
    ] = Field(default_factory=dict)

    @field_validator("dynamic_inputs")
    @classmethod
    def validate_no_base64(cls, v: dict[str, DomainInputValue]) -> dict[str, DomainInputValue]:
        """Strictly ban base64 payloads from domain inputs."""
        for val in v.values():
            if isinstance(val, Base64Attachment):
                raise ValueError("Base64Attachment is strictly forbidden in WorkflowInputs")
            if type(val) is dict and "content_base64" in val:
                raise ValueError("Base64 payloads are strictly forbidden in WorkflowInputs")
        return v
