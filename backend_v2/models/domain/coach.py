"""Coach Agent Domain Models.

This module contains the schemas for the Coach Agent,
including coaching plans and bibliography.
"""

# Import JudgeOutput for strict type checking if possible, otherwise use Dict
# To avoid potential circular imports (though judge doesn't import coach), we can use forward refs or just imports
# But let's check if we can import JudgeOutput from backend_v2.models.domain.judge

import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.judge import JudgeOutput


class CoachInput(BaseModel):
    """Strict input schema for CoachAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are allowed dynamically.
    """

    chat_log: str = Field(..., description="Mandatory chatlog.")
    step_judge: JudgeOutput | None = Field(
        default=None, description="The Verdict from Judge Agent.", json_schema_extra={"x-ui-label": "Judge Verdict"}
    )
    step_judge_cognitive: JudgeOutput | None = Field(
        default=None,
        description="The Verdict from Cognitive Judge Agent.",
        json_schema_extra={"x-ui-label": "Cognitive Verdict"},
    )
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    # --- Universal Routing Inputs ---
    step_analyst: Any | None = Field(default=None, description="Analyst hypotheses and RAG data.")
    step_profiler: Any | None = Field(default=None, description="Profiler cognitive bias data.")
    step_falsifier: Any | None = Field(default=None, description="Falsifier critical distance data.")
    step_logician: Any | None = Field(default=None, description="Logician Toulmin analysis data.")
    step_causal_analyst: Any | None = Field(
        default=None, description="Causal Analyst post-hoc and counterfactual data."
    )

    # Allow extra fields because Coach might receive step_judge, step_judge_cognitive etc.
    # Logic in agent iterates keys.
    model_config = ConfigDict(frozen=True, strict=True, extra="allow")

    @field_validator("chat_log")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str:
        if not v or not str(v).strip():
            msg = "chat_log cannot be empty or whitespace only."
            logger.error("[CoachModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return str(v).strip()


class BibliographyItem(BaseModel):
    """A single bibliographic reference."""

    source_id: str = Field(..., description="Unique source ID.", json_schema_extra={"x-ui-label": "Source ID"})
    title: str = Field(..., description="Title of the source.", json_schema_extra={"x-ui-label": "Title"})
    url: str | None = Field(default=None, description="URL if available.", json_schema_extra={"x-ui-label": "URL"})
    snippet: str | None = Field(
        default=None, description="Relevant snippet.", json_schema_extra={"x-ui-label": "Snippet"}
    )

    model_config = ConfigDict(frozen=True, extra="forbid")

    @field_validator("source_id", "title")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str:
        if not v or not str(v).strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[CoachModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return str(v).strip()


class BibliographyResult(BaseModel):
    """Result of the bibliography generation (Hook)."""

    references: list[BibliographyItem] = Field(
        ..., description="List of references.", json_schema_extra={"x-ui-label": "References"}
    )

    model_config = ConfigDict(frozen=True, extra="forbid")

    @model_validator(mode="after")
    def validate_references_exist(self) -> BibliographyResult:
        if not self.references:
            msg = "Bibliography references cannot be empty. Zero-Compromise Fail-Fast enforced."
            logger.error("[CoachModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return self


class CoachingPlanDTO(ReasoningTraceDTO):
    """DTO for Coaching Plan (Content Only)."""

    actionable_steps: list[str] = Field(
        ...,
        description="Concrete steps for improvement.",
        json_schema_extra={"x-ui-label": "Actionable Steps"},
    )
    bibliography: list[BibliographyItem] = Field(
        ...,
        description="Recommended reading.",
        json_schema_extra={"x-ui-label": "References"},
    )
    focus_areas: list[str] = Field(
        ...,
        description="Key areas to focus on.",
        json_schema_extra={"x-ui-label": "Focus Areas"},
    )
    model_config = ConfigDict(frozen=True, extra="forbid")

    @field_validator("actionable_steps", "focus_areas")
    @classmethod
    def validate_list_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            msg = "List cannot be empty."
            logger.error("[CoachModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        # Validate individual items
        cleaned = [item.strip() for item in v if item and item.strip()]
        if not cleaned:
            msg = "List cannot contain only empty strings."
            logger.error("[CoachModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return cleaned

    @field_validator("bibliography")
    @classmethod
    def validate_biblio_not_empty(cls, v: list[BibliographyItem]) -> list[BibliographyItem]:
        if not v:
            msg = "Bibliography cannot be empty. Zero-Compromise Fail-Fast enforced."
            logger.error("[CoachModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return v


class CoachingPlan(CoachingPlanDTO, ReasoningTrace):
    """Output schema for the Coach Agent (Domain Model)."""

    model_config = ConfigDict(frozen=True, extra="forbid")
