"""Overseer Agent Domain Models.

This module contains the schemas for the Overseer Agent,
including fact checks and ethical observations.
"""


from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator

from backend.models.domain.base import ReasoningTrace


from typing import TYPE_CHECKING
from backend.models.domain.analyst import AnalystOutput


class OverseerInput(BaseModel):
    """Strict input schema for FactualOverseerAgent."""
    history_text: str = Field(..., description="Chat history to analyze.")
    step_analyst: Optional[AnalystOutput] = Field(None, description="Analyst hypotheses/timeline.")
    last_reasoning_trace: Optional[str] = Field(default=None, description="Previous reasoning trace.")
    
    model_config = ConfigDict(frozen=True, extra="ignore")


class FactCheckRFI(BaseModel):
    """Request for Information (Fact Check)."""

    claim: str = Field(
        ...,
        description="Claim to check.",
        json_schema_extra={"x-ui-label": "Claim"},
    )
    verification_result: Literal["Verified", "Debunked", "Unverified"] = Field(
        ...,
        description="Result.",
        json_schema_extra={"x-ui-label": "Result"},
    )
    is_verified: bool = Field(
        default=False,
        description="Boolean verification status.",
    )
    source_or_reasoning: str = Field(
        ...,
        description="Source or reasoning.",
        json_schema_extra={"x-ui-label": "Source/Reasoning"},
    )

    @field_validator("claim", "source_or_reasoning")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @model_validator(mode="before")
    @classmethod
    def calc_verification(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Derive boolean from Literal
            val = data.get("verification_result")
            data["is_verified"] = val == "Verified"
        return data

    model_config = ConfigDict(frozen=True, strict=True)


class EthicalObservation(BaseModel):
    """Ethical Observation."""

    issue_type: str = Field(
        ...,
        description="Type of ethical issue.",
        json_schema_extra={"x-ui-label": "Issue Type"},
    )
    severity: Literal["None", "Warning", "Critical"] = Field(
        ...,
        description="Severity level.",
        json_schema_extra={"x-ui-label": "Severity"},
    )
    is_critical: bool = Field(
        default=False,
        description="Is the issue critical?",
    )
    description: str = Field(
        ...,
        description="Description.",
        json_schema_extra={"x-ui-label": "Description"},
    )

    @field_validator("issue_type", "description")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @model_validator(mode="before")
    @classmethod
    def calc_ethics(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Strictly derive booleans from Literal
            val = data.get("severity")
            data["is_critical"] = val == "Critical"
        return data

    model_config = ConfigDict(frozen=True, strict=True)


class OverseerData(BaseModel):
    """Output from the Overseer component."""

    fact_checks: list[FactCheckRFI] = Field(
        default_factory=list,
        description="Fact check report.",
        json_schema_extra={"x-ui-label": "Fact Checks"},
    )
    ethical_issues: list[EthicalObservation] = Field(
        ...,
        description="Ethical audit report.",
        json_schema_extra={"x-ui-label": "Ethical Issues"},
    )
    model_config = ConfigDict(frozen=True, strict=True)


class OverseerOutput(ReasoningTrace):
    """Output schema for the Overseer Agent."""

    overseer_data: OverseerData = Field(
        ...,
        description="Ethics audit result.",
        json_schema_extra={"x-ui-label": "Ethics Audit"},
    )
    model_config = ConfigDict(frozen=True, strict=True)
