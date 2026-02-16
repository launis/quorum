"""Falsifier Agent Domain Models.

This module contains the schemas for the Falsifier Agent,
including stress tests and fidelity audits.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator

from backend.models.domain.base import ReasoningTrace
from backend.models.enums import FidelityLevel


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
    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("question", "observation")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class ReasoningFidelity(BaseModel):
    """Fidelity of reasoning."""

    fidelity_score: FidelityLevel = Field(
        ...,
        description="Fidelity level.",
        json_schema_extra={"x-ui-label": "Fidelity Score"},
    )
    fidelity_numeric: float = Field(
        ...,
        description="Numeric fidelity score (1-3).",
        json_schema_extra={"x-ui-label": "Fidelity Numeric"},
    )
    justification: str = Field(..., description="Justification.", json_schema_extra={"x-ui-label": "Justification"})
    quote: str | None = Field(default=None, description="Direct quote.", json_schema_extra={"x-ui-label": "Quote"})
    post_hoc_rationalization: bool = Field(
        default=False,
        description="Was reasoning constructed after the fact?",
        json_schema_extra={"x-ui-label": "Post-Hoc Rationalization"}
    )

    @field_validator("justification")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("quote")
    @classmethod
    def validate_quote(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Quote cannot be empty if provided.")
        return v.strip() if v else None



    @model_validator(mode="before")
    @classmethod
    def calc_fidelity(cls, data: Any) -> Any:
        if isinstance(data, dict):
            mapping = {
                FidelityLevel.WEAK: 1.0,
                FidelityLevel.UNCERTAIN: 2.0,
                FidelityLevel.HIGH: 3.0
            }

            val = data.get("fidelity_score")
            # Only calc if numeric missing
            if data.get("fidelity_numeric") is None and val:
                # Handle both Enum and String input
                try:
                    enum_val = val if isinstance(val, FidelityLevel) else FidelityLevel(val)
                    if enum_val in mapping:
                        data["fidelity_numeric"] = mapping[enum_val]
                except ValueError:
                    pass # Let Pydantic fail
        return data

    model_config = ConfigDict(frozen=True, strict=True)


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
    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("stress_test_findings")
    @classmethod
    def validate_list_not_empty(cls, v: list[WaltonStressTest]) -> list[WaltonStressTest]:
        if not v:
            raise ValueError("Stress test findings cannot be empty.")
        return v


class FalsifierOutput(ReasoningTrace):
    """Output schema for the Falsifier Agent."""

    falsifier_data: FalsifierData = Field(
        ...,
        description="Falsification audit result.",
        json_schema_extra={"x-ui-label": "Falsification Audit"},
    )
    model_config = ConfigDict(frozen=True, strict=True)
