"""Archivist Agent Domain Models.

This module contains the schemas for the Archivist Agent,
including precedent analysis and compliance checks.
"""

import logging
from typing import Annotated, Any, Literal

from pydantic import ConfigDict, Field, model_validator

from backend_v2.exceptions import AppException, ErrorCodes
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
        float,
        Field(description="Numeric Compliance score (1-5).", json_schema_extra={"x-ui-label": "Compliance Score"}),
    ]
    description_key: Annotated[
        str,
        Field(min_length=1, description="Localization key."),
    ] = "compliance_desc"
    description: Annotated[
        str,
        Field(description="Localized description.", json_schema_extra={"x-ui-label": "Description"}),
    ] = ""

    @model_validator(mode="before")
    @classmethod
    def calc_compliance(cls, data: Any) -> Any:
        """Calculate numerical compliance score from literal.

        Args:
            data: Raw input dictionary.

        Returns:
            Mutated dictionary with compliance_score.

        Raises:
            AppException: If compliance_analysis is invalid (ErrorCodes.VALIDATION_FAILED).
        """
        if isinstance(data, dict):
            # Map Literal to Score
            mapping = {
                "Critically Misaligned": 1.0,
                "Misaligned": 2.0,
                "Neutral": 3.0,
                "Aligned": 4.0,
                "Strongly Aligned": 5.0,
            }

            # Access the raw string value
            val = data.get("compliance_analysis")
            if val and val not in mapping:
                # STRICT VALIDATION: No fallback allowed.
                msg = f"Invalid compliance_analysis: {val}. Must be one of {list(mapping.keys())}"
                logger.error("[ArchivistModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED})

            if val:
                data.setdefault("compliance_score", mapping[val])

        return data


class ArchivistOutput(ArchivistOutputDTO, ReasoningTrace):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Domain model for Archivist Agent (Content + Metadata)."""

    pass
