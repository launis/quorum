"""Falsifier Agent Domain Models.

This module contains the schemas for the Falsifier Agent,
including stress tests and fidelity audits.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
import logging
from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.logician import LogicianOutput
from backend_v2.models.enums import FidelityLevel


class FalsifierInput(BaseModel):
    """Strict input schema for LogicalFalsifierAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are allowed dynamically.
    """

    chat_log: str = Field(..., description="Mandatory chatlog to analyze.")
    step_analyst: AnalystOutput | LogicianOutput | None = Field(None, description="Analyst or Logician outputs.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    model_config = ConfigDict(frozen=True, extra="allow")


class WaltonStressTest(BaseModel):
    """Stress test using Walton's critical questions."""

    question: str = Field(
        ...,
        description="The critical question asked.",
        json_schema_extra={"x-ui-label": "Question"},
    )
    evidence_held: bool = Field(
        ...,
        description="Did the evidence hold up?",
        json_schema_extra={"x-ui-label": "Result"},
    )
    observation: str = Field(
        ...,
        description="Observation notes.",
        json_schema_extra={"x-ui-label": "Observation"},
    )
    model_config = ConfigDict(frozen=True, strict=False)

    @field_validator("question", "observation", mode="before")
    @classmethod
    def validate_non_empty(cls, v: Any) -> Any:
        return v


class ReasoningFidelity(BaseModel):
    """Fidelity of reasoning."""

    fidelity_score: FidelityLevel = Field(
        ...,
        description="Fidelity level.",
        json_schema_extra={"x-ui-label": "Fidelity Score"},
    )
    fidelity_numeric: float = Field(
        ...,
        ge=1.0,
        le=3.0,
        description="Numeric fidelity score (1.0 to 3.0), required 1-decimal precision. USE DECIMALS (e.g., 2.5) to reflect nuance.",
        json_schema_extra={"x-ui-label": "Fidelity Numeric"},
    )
    abductive_score: float = Field(
        ...,
        ge=1.0,
        le=3.0,
        description="Numeric abductive score (1.0 to 3.0), required 1-decimal precision. USE DECIMALS (e.g., 2.5) to reflect nuance.",
        json_schema_extra={"x-ui-label": "Abductive Score"},
    )
    plausibility_score: float = Field(
        ...,
        ge=1.0,
        le=3.0,
        description="Numeric plausibility score (1.0 to 3.0), required 1-decimal precision. USE DECIMALS (e.g., 2.5) to reflect nuance.",
        json_schema_extra={"x-ui-label": "Plausibility Score"},
    )
    justification: str = Field(..., description="Justification.", json_schema_extra={"x-ui-label": "Justification"})
    quote: str | None = Field(default=None, description="Direct quote.", json_schema_extra={"x-ui-label": "Quote"})
    post_hoc_rationalization: bool = Field(
        default=False,
        description="Was reasoning constructed after the fact?",
        json_schema_extra={"x-ui-label": "Post-Hoc Rationalization"},
    )
    is_post_hoc: bool = Field(
        default=False,
        description="Legacy flag for post-hoc rationalization (Validation Mirror).",
    )

    @field_validator("justification", mode="before")
    @classmethod
    def validate_non_empty(cls, v: Any) -> Any:
        return v

    @field_validator("fidelity_numeric", "abductive_score", "plausibility_score")
    @classmethod
    def validate_falsifier_scores(cls, v: float) -> float:
        if not (1.0 <= v <= 3.0):
            msg = "Score must be between 1.0 and 3.0."
            logger.error(f"[FalsifierModel] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v

    @field_validator("quote", mode="before")
    @classmethod
    def validate_quote(cls, v: Any) -> Any:
        return v

    @model_validator(mode="before")
    @classmethod
    def calc_fidelity(cls, data: Any) -> Any:
        if isinstance(data, dict):
            mapping = {FidelityLevel.WEAK: 1.0, FidelityLevel.UNCERTAIN: 2.0, FidelityLevel.HIGH: 3.0}

            val = data.get("fidelity_score")

            # Robust Enum Parsing (Handle "High", "high", "FIDELITY_HIGH")
            if val and isinstance(val, str):
                val_upper = val.upper()
                if not val_upper.startswith("FIDELITY_"):
                    # Try to map simple term to full enum
                    if val_upper == "WEAK":
                        data["fidelity_score"] = FidelityLevel.WEAK
                    elif val_upper == "UNCERTAIN":
                        data["fidelity_score"] = FidelityLevel.UNCERTAIN
                    elif val_upper == "HIGH":
                        data["fidelity_score"] = FidelityLevel.HIGH

            # Re-fetch potentially updated value
            val = data.get("fidelity_score")

            # Only calc if numeric missing
            if data.get("fidelity_numeric") is None and val:
                # Handle both Enum and String input
                try:
                    enum_val = val if isinstance(val, FidelityLevel) else FidelityLevel(val)
                    if enum_val in mapping:
                        data["fidelity_numeric"] = mapping[enum_val]
                except ValueError:
                    pass  # Let Pydantic fail
        return data

    model_config = ConfigDict(frozen=True, strict=False)


class FalsifierData(BaseModel):
    """Output from the Falsifier component."""

    stress_test_findings: list[WaltonStressTest] = Field(
        ...,
        description="Stress test results.",
        json_schema_extra={"x-ui-label": "Stress Test"},
    )
    fidelity_audit: ReasoningFidelity = Field(
        ...,
        description="Fidelity audit.",
        json_schema_extra={"x-ui-label": "Fidelity Audit"},
    )
    model_config = ConfigDict(frozen=True, strict=False)

    @field_validator("stress_test_findings", mode="before")
    @classmethod
    def validate_list_not_empty(cls, v: Any) -> Any:
        return v


class FalsifierDTO(ReasoningTraceDTO):
    """Falsifier DTO (Content Only)."""

    falsifier_data: FalsifierData = Field(
        ...,
        description="Falsification audit result.",
        json_schema_extra={"x-ui-label": "Falsification Audit"},
    )
    model_config = ConfigDict(frozen=True, strict=False)


class FalsifierOutput(FalsifierDTO, ReasoningTrace):
    """Output schema for the Falsifier Agent."""

    model_config = ConfigDict(frozen=True, strict=False)
