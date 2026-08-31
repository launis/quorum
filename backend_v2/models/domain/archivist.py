"""Archivist Agent Domain Models.

This module contains the schemas for the Archivist Agent,
including precedent analysis and compliance checks.
"""

import logging
from typing import Annotated, Any, Literal, Self

from pydantic import ConfigDict, Field, model_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO

logger = logging.getLogger(__name__)


class ArchiveCase(V2CoreBase):
    """A past case retrieved by the Archivist.

    Attributes:
        case_id: ID of the past case.
        similarity_score: Similarity to current case.
        verdict: Verdict of the past case.
        summary: Summary of the past case.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    case_id: Annotated[str, Field(min_length=1, description="ID of the past case.")]
    similarity_score: Annotated[float, Field(description="Similarity to current case.")]
    verdict: Annotated[str, Field(min_length=1, description="Verdict of the past case.")]
    summary: Annotated[str, Field(min_length=1, description="Summary of the past case.")]


class ArchivistInput(V2CoreBase):
    """Strict input schema for ArchivistAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are encapsulated dynamically.

    Attributes:
        chat_log: Mandatory chatlog to analyze.
        archivist_precedents: Retrieved precedents.
        last_reasoning_trace: Previous reasoning trace.
        dynamic_inputs: Structured dictionary for dynamic inputs.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    chat_log: Annotated[str, Field(description="Mandatory chatlog to analyze.")]
    archivist_precedents: Annotated[list[ArchiveCase] | None, Field(description="Retrieved precedents.")] = None
    last_reasoning_trace: Annotated[str | None, Field(description="Previous reasoning trace.")] = None

    dynamic_inputs: Annotated[dict[str, Any], Field(description="Structured dictionary for dynamic inputs.")] = {}


class ArchivistOutputDTO(ReasoningTraceDTO):
    """DTO for Archivist Agent (Content Only).

    Attributes:
        relevant_cases: Relevant past cases.
        consistency_analysis: Analysis of consistency with precedents.
        stare_decisis_adherence: Whether the decision follows precedent.
        compliance_analysis: Analysis of consistency with goals (Compliance).
        compliance_score: Numeric Compliance score (1-5).
        description_key: Localization key.
        description: Localized description.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    relevant_cases: Annotated[
        list[ArchiveCase],
        Field(min_length=1, description="Relevant past cases.", json_schema_extra={"x-ui-label": "Relevant Cases"}),
    ]
    consistency_analysis: Annotated[
        str,
        Field(
            min_length=1,
            description="Analysis of consistency with precedents.",
            json_schema_extra={"x-ui-label": "Consistency Analysis"},
        ),
    ]
    stare_decisis_adherence: Annotated[
        bool,
        Field(description="Whether the decision follows precedent.", json_schema_extra={"x-ui-label": "Stare Decisis"}),
    ]
    compliance_analysis: Annotated[
        Literal["Critically Misaligned", "Misaligned", "Neutral", "Aligned", "Strongly Aligned"],
        Field(
            description="Analysis of consistency with goals (Compliance).",
            json_schema_extra={"x-ui-label": "Compliance Analysis"},
        ),
    ]
    compliance_score: Annotated[
        float | None,
        Field(
            default=None,
            description="Numeric Compliance score (1-5).",
            json_schema_extra={"x-ui-label": "Compliance Score"},
        ),
    ] = None
    description_key: Annotated[
        str,
        Field(min_length=1, description="Localization key."),
    ] = "compliance_desc"
    description: Annotated[
        str,
        Field(description="Localized description.", json_schema_extra={"x-ui-label": "Description"}),
    ] = ""

    @model_validator(mode="after")
    def calc_compliance(self) -> Self:
        """Calculate numerical compliance score from literal.

        Returns:
            Validated instance with compliance_score updated.
        """
        mapping: dict[str, float] = {
            "Critically Misaligned": 1.0,
            "Misaligned": 2.0,
            "Neutral": 3.0,
            "Aligned": 4.0,
            "Strongly Aligned": 5.0,
        }

        if self.compliance_analysis in mapping:
            expected_score = mapping[self.compliance_analysis]
            if self.compliance_score != expected_score:
                return self.model_copy(update={"compliance_score": expected_score})

        return self


class ArchivistOutput(ArchivistOutputDTO, ReasoningTrace):
    """Domain model for Archivist Agent (Content + Metadata)."""

    model_config = ConfigDict(strict=True, extra="forbid")

    pass
