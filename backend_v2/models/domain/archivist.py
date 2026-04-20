"""Archivist Agent Domain Models.

This module contains the schemas for the Archivist Agent,
including precedent analysis and compliance checks.
"""

import logging
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO


class ArchivistInput(BaseModel):
    """Strict input schema for ArchivistAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are allowed dynamically.
    """

    chat_log: str = Field(..., description="Mandatory chatlog to analyze.")
    archivist_precedents: list[dict[str, Any]] | None = Field(None, description="Retrieved precedents.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    model_config = ConfigDict(frozen=True, extra="allow")


class ArchiveCase(BaseModel):
    """A past case retrieved by the Archivist."""

    case_id: str = Field(..., description="ID of the past case.")
    similarity_score: float = Field(..., description="Similarity to current case.")
    verdict: str = Field(..., description="Verdict of the past case.")
    summary: str = Field(..., description="Summary of the past case.")

    model_config = ConfigDict(frozen=True, extra="forbid")

    @field_validator("case_id", "verdict", "summary")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str:
        if not v or not str(v).strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[ArchivistModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return str(v).strip()


class ArchivistOutputDTO(ReasoningTraceDTO):
    """DTO for Archivist Agent (Content Only)."""

    relevant_cases: list[ArchiveCase] = Field(
        ...,
        description="Relevant past cases.",
        json_schema_extra={"x-ui-label": "Relevant Cases"},
    )
    consistency_analysis: str = Field(
        ...,
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
        description="Localization key.",
    )
    description: str = Field(
        default="", description="Localized description.", json_schema_extra={"x-ui-label": "Description"}
    )

    @field_validator("consistency_analysis", "description_key")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str:
        if not v or not str(v).strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[ArchivistModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return str(v).strip()

    @model_validator(mode="before")
    @classmethod
    def calc_compliance(cls, data: Any) -> Any:
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
                raise AppException(
                    message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                )

            if val and "compliance_score" not in data:
                data["compliance_score"] = mapping[val]

        return data

    model_config = ConfigDict(frozen=True, extra="forbid")


class ArchivistOutput(ArchivistOutputDTO, ReasoningTrace):
    """Domain model for Archivist Agent (Content + Metadata)."""

    model_config = ConfigDict(frozen=True, extra="forbid")
