"""Guard Agent Domain Models.

This module contains the strict schemas for the Guard Agent,
including input validation and security check results.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator, field_validator

from backend.models.domain.base import ReasoningTrace
from backend.models.enums import RiskLevel, SimulationType


class GuardInput(BaseModel):
    """Input schema for the Guard Agent, supporting strict validation."""
    history_text: str = Field(..., json_schema_extra={"x-ui-label": "INPUT_HISTORY_TEXT"})
    product_text: str = Field(..., json_schema_extra={"x-ui-label": "INPUT_PRODUCT_TEXT"})
    reflection_text: str | None = Field(default=None, json_schema_extra={"x-ui-label": "INPUT_REFLECTION_TEXT"})
    last_reasoning_trace: str | None = Field(default=None, json_schema_extra={"x-ui-label": "Last Reasoning Trace"})

    @field_validator("history_text", "product_text")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("reflection_text")
    @classmethod
    def validate_reflection(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
             raise ValueError("Reflection text cannot be empty if provided.")
        return v.strip() if v else None

    @model_validator(mode="after")
    def validate_banned_phrases(self, info: ValidationInfo) -> GuardInput:
        """Validates that no banned phrases are present in the input."""
        context = info.context
        if not context or "banned_phrases" not in context:
            return self

        banned_phrases = context["banned_phrases"]
        if not banned_phrases:
            return self

        # Check all string fields
        data_dict = self.model_dump()
        for key, value in data_dict.items():
            if isinstance(value, str):
                for phrase in banned_phrases:
                    if phrase.lower() in value.lower():
                        raise ValueError(f"SECURITY_BANNED_PHRASE_DETECTED: Found '{phrase}' in field '{key}'")
        return self


class TaintedDataContent(BaseModel):
    """Raw input data wrapper."""

    chat_history: str = Field(..., description="Chat history.", json_schema_extra={"x-ui-label": "INPUT_CHAT_HISTORY"})
    product_text: str = Field(..., description="Product text.", json_schema_extra={"x-ui-label": "INPUT_PRODUCT_TEXT"})
    reflection_text: str = Field(..., description="Reflection text.", json_schema_extra={"x-ui-label": "INPUT_REFLECTION_TEXT"})
    safe_data: str = Field(..., description="Safe data marker.", json_schema_extra={"x-ui-label": "INPUT_SAFE_DATA"})

    @field_validator("chat_history", "product_text", "reflection_text", "safe_data")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class SecurityCheck(BaseModel):
    """Security check results."""

    threat_detected: bool = Field(
        ...,
        description="Threat detected flag.",
        json_schema_extra={"x-ui-label": "Threat Detected"},
    )
    risk_level: RiskLevel = Field(
        ...,
        description="Risk level.",
        json_schema_extra={"x-ui-label": "Risk Level"},
    )
    risk_score: float = Field(
        ...,
        description="Numeric Risk score (1-3).",
        json_schema_extra={"x-ui-label": "Risk Score"},
    )
    simulation_score: float = Field(
        ...,
        description="Numeric Simulation score (1-3).",
        json_schema_extra={"x-ui-label": "Simulation Score"},
    )

    @field_validator("risk_score", "simulation_score")
    @classmethod
    def validate_score_range(cls, v: float) -> float:
        if not (1.0 <= v <= 3.0):
            raise ValueError("Score must be between 1.0 and 3.0.")
        return v

    @model_validator(mode="before")
    @classmethod
    def calc_scores(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # 1. Calc Risk
            # Map Enum -> Score directly (Strict)
            risk_map = {
                RiskLevel.LOW: 1.0,
                RiskLevel.MEDIUM: 2.0,
                RiskLevel.HIGH: 3.0
            }

            risk_score = data.get("risk_score")
            risk_level = data.get("risk_level")

            # Only calculate if not present
            if risk_score is None and risk_level:
                # If incoming data is already an Enum member (during object construction)
                if isinstance(risk_level, RiskLevel):
                     data["risk_score"] = risk_map[risk_level]
                # If incoming data is a raw string (from JSON/LLM)
                elif isinstance(risk_level, str):
                     try:
                         # Try to convert string to Enum
                         risk_enum = RiskLevel(risk_level)
                         data["risk_score"] = risk_map[risk_enum]
                     except ValueError:
                         pass

            # 2. Calc Simulation
            sim_map = {
                SimulationType.PASSIVE: 1.0,
                SimulationType.ACTIVE: 2.0,
                SimulationType.MALICIOUS: 3.0
            }

            sim_score = data.get("simulation_score")
            sim_res = data.get("simulation_result")

            # Only calculate if not present
            if sim_score is None and sim_res:
                try:
                    sim_enum = SimulationType(sim_res)
                    data["simulation_score"] = sim_map[sim_enum]
                except ValueError:
                    pass

        return data

    simulation_result: SimulationType | None = Field(
         default=None,
         description="Simulation result description.",
         json_schema_extra={"x-ui-label": "Simulation Result"},
    )
    anonymized: bool = Field(
        ...,
        description="Was anonymization performed?",
        json_schema_extra={"x-ui-label": "Anonymized"},
    )
    pii_findings: list[str] = Field(
        default_factory=list,
        description="PII findings.",
        json_schema_extra={"x-ui-label": "PII Findings"},
    )
    model_config = ConfigDict(frozen=True)


class GuardOutput(ReasoningTrace):
    """Output schema for the Guard Agent."""

    security_check: SecurityCheck = Field(
        ...,
        description="Security scan results.",
        json_schema_extra={"x-ui-label": "Security Check"},
    )
    tainted_data: TaintedDataContent = Field(
        ...,
        description="Raw input data (tainted).",
        json_schema_extra={"x-ui-label": "Input Data"},
    )
    model_config = ConfigDict(frozen=True)


class SanitizationResult(BaseModel):
    """Result of the text sanitization process (Security Hook)."""
    sanitized_inputs: dict[str, str] = Field(
        ...,
        description="Sanitized input text fields.",
        json_schema_extra={"x-ui-label": "Sanitized Inputs"}
    )
    pii_threats_detected: list[str] = Field(
        default_factory=list,
        description="List of detected PII threats.",
        json_schema_extra={"x-ui-label": "PII Threats"}
    )
    banned_phrases_detected: list[str] = Field(
        default_factory=list,
        description="List of detected banned phrases.",
        json_schema_extra={"x-ui-label": "Banned Phrases"}
    )
    banned_phrases_error: str | None = Field(
        default=None,
        description="Error message if banned phrases fetch failed.",
        json_schema_extra={"x-ui-label": "Banned Phrases Error"}
    )

    model_config = ConfigDict(frozen=True, strict=True)
