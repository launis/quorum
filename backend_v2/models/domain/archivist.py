"""Archivist Agent Domain Models.

This module contains the schemas for the Archivist Agent,
including precedent analysis and compliance checks.
"""

import logging
from typing import Any, Literal

from pydantic import Field, model_validator

from backend_v2.exceptions import ErrorCodes
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

    case_id: str = Field(..., min_length=1, description="ID of the past case.")
    similarity_score: float = Field(..., description="Similarity to current case.")
    verdict: str = Field(..., min_length=1, description="Verdict of the past case.")
    summary: str = Field(..., min_length=1, description="Summary of the past case.")


class ArchivistInput(V2CoreBase):
    """Strict input schema for ArchivistAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are encapsulated dynamically.

    Attributes:
        chat_log: Mandatory chatlog to analyze.
        archivist_precedents: Retrieved precedents.
        last_reasoning_trace: Previous reasoning trace.
        dynamic_inputs: Structured dictionary for dynamic inputs.
    """

    chat_log: str = Field(..., description="Mandatory chatlog to analyze.")
    archivist_precedents: list[ArchiveCase] | None = Field(None, description="Retrieved precedents.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    dynamic_inputs: dict[str, Any] = Field(
        default_factory=dict, description="Structured dictionary for dynamic inputs."
    )


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

    relevant_cases: list[ArchiveCase] = Field(
        ...,
        min_length=1,
        description="Relevant past cases.",
        json_schema_extra={"x-ui-label": "Relevant Cases"},
    )
    consistency_analysis: str = Field(
        ...,
        min_length=1,
        description="Analysis of consistency with precedents.",
        json_schema_extra={"x-ui-label": "Consistency Analysis"},
    )
    stare_decisis_adherence: bool = Field(
        ...,
        description="Whether the decision follows precedent.",
        json_schema_extra={"x-ui-label": "Stare Decisis"},
    )
    compliance_analysis: Literal["Critically Misaligned", "Misaligned", "Neutral", "Aligned", "Strongly Aligned"] = (
        Field(
            ...,
            description="Analysis of consistency with goals (Compliance).",
            json_schema_extra={"x-ui-label": "Compliance Analysis"},
        )
    )
    compliance_score: float = Field(
        ...,
        description="Numeric Compliance score (1-5).",
        json_schema_extra={"x-ui-label": "Compliance Score"},
    )
    description_key: str = Field(
        default="compliance_desc",
        min_length=1,
        description="Localization key.",
    )
    description: str = Field(
        default="", description="Localized description.", json_schema_extra={"x-ui-label": "Description"}
    )

    @model_validator(mode="before")
    @classmethod
    def calc_compliance(cls, data: Any) -> Any:
        """Calculate numerical compliance score from literal.

        Args:
            data: Raw input dictionary.

        Returns:
            Mutated dictionary with compliance_score.

        Raises:
            ValueError: If compliance_analysis is invalid.
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
                raise ValueError(msg)

            if val and "compliance_score" not in data:
                data["compliance_score"] = mapping[val]

        return data


class ArchivistOutput(ArchivistOutputDTO, ReasoningTrace):
    """Domain model for Archivist Agent (Content + Metadata)."""

    pass
