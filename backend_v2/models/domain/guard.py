"""Guard Agent Domain Models.

This module contains the strict schemas for the Guard Agent,
including input validation and security check results.
"""

from __future__ import annotations

import logging

from pydantic import Field, ValidationInfo, field_validator, model_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.enums import RiskLevel, SimulationType

logger = logging.getLogger(__name__)


class GuardInput(V2CoreBase):
    """Input schema for the Guard Agent, supporting strict validation.

    Attributes:
        chat_log: Mandatory chatlog to analyze.
        product_text: Product text to analyze.
        reflection_text: Reflection text to analyze.
        last_reasoning_trace: Previous reasoning trace.
    """

    chat_log: str = Field(..., min_length=1, pattern=r"\S", json_schema_extra={"x-ui-label": "INPUT_CHATLOG"})
    product_text: str | None = Field(
        None, min_length=1, pattern=r"\S", json_schema_extra={"x-ui-label": "INPUT_PRODUCT_TEXT"}
    )
    reflection_text: str | None = Field(
        default=None, min_length=1, pattern=r"\S", json_schema_extra={"x-ui-label": "INPUT_REFLECTION_TEXT"}
    )
    last_reasoning_trace: str | None = Field(default=None, json_schema_extra={"x-ui-label": "Last Reasoning Trace"})

    @model_validator(mode="after")
    def validate_banned_phrases(self, info: ValidationInfo) -> GuardInput:
        """Validates that no banned phrases are present in the input.

        Args:
            info: Validation context containing banned phrases.

        Returns:
            The validated GuardInput instance.

        Raises:
            AppException: If a banned phrase is detected (PERMISSION_DENIED).
        """
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
                        msg = f"SECURITY_BANNED_PHRASE_DETECTED: Found banned phrase in field '{key}'"
                        logger.error("[GuardModel] %s: %s", ErrorCodes.PERMISSION_DENIED.name, msg)
                        raise AppException(message=msg, details={"error_code": ErrorCodes.PERMISSION_DENIED})
        return self


class TaintedDataContent(V2CoreBase):
    """Raw input data wrapper.

    Attributes:
        chat_history: Chat history data.
        product_text: Product text data.
        reflection_text: Reflection text data.
        safe_data: Safe data marker.
    """

    chat_history: str = Field(
        ...,
        min_length=1,
        pattern=r"\S",
        description="Chat history.",
        json_schema_extra={"x-ui-label": "INPUT_CHAT_HISTORY"},
    )
    product_text: str | None = Field(
        None,
        min_length=1,
        pattern=r"\S",
        description="Product text.",
        json_schema_extra={"x-ui-label": "INPUT_PRODUCT_TEXT"},
    )
    reflection_text: str = Field(
        ...,
        min_length=1,
        pattern=r"\S",
        description="Reflection text.",
        json_schema_extra={"x-ui-label": "INPUT_REFLECTION_TEXT"},
    )
    safe_data: str = Field(
        ...,
        min_length=1,
        pattern=r"\S",
        description="Safe data marker.",
        json_schema_extra={"x-ui-label": "INPUT_SAFE_DATA"},
    )


class SecurityCheck(V2CoreBase):
    """Security check results.

    Attributes:
        threat_detected: Threat detected flag.
        risk_level: Risk level enum.
        risk_score: Numeric Risk score (1-3).
        simulation_score: Numeric Simulation score (1-3).
        simulation_result: Simulation result description.
        anonymized: Was anonymization performed?
        pii_findings: List of PII findings.
    """

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
    def validate_scores_range(cls, v: float) -> float:
        """Enforce strict score boundaries between 1.0 and 3.0.

        Args:
            v: The score to validate.

        Returns:
            Validated float amount.

        Raises:
            AppException: If score is out of bounds (VALIDATION_FAILED).
        """
        if not (1.0 <= v <= 3.0):
            msg = "Score must be between 1.0 and 3.0 inclusive."
            logger.error("[GuardModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v

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


class GuardDTO(ReasoningTraceDTO):
    """Data Transfer Object for Guard Agent (Content Only).

    Attributes:
        security_check: Security scan results.
    """

    security_check: SecurityCheck = Field(
        ...,
        description="Security scan results.",
        json_schema_extra={"x-ui-label": "Security Check"},
    )


class GuardOutput(GuardDTO, ReasoningTrace):
    """Output schema for the Guard Agent.

    Attributes:
        tainted_data: Raw input data (tainted).
    """

    tainted_data: TaintedDataContent = Field(
        ...,
        description="Raw input data (tainted).",
        json_schema_extra={"x-ui-label": "Input Data"},
    )


class SanitizationResult(V2CoreBase):
    """Result of the text sanitization process (Security Hook).

    Attributes:
        sanitized_inputs: Sanitized input text fields.
        pii_threats_detected: List of detected PII threats.
        banned_phrases_detected: List of detected banned phrases.
    """

    sanitized_inputs: dict[str, str] = Field(
        ..., description="Sanitized input text fields.", json_schema_extra={"x-ui-label": "Sanitized Inputs"}
    )
    pii_threats_detected: list[str] = Field(
        default_factory=list,
        description="List of detected PII threats.",
        json_schema_extra={"x-ui-label": "PII Threats"},
    )
    banned_phrases_detected: list[str] = Field(
        default_factory=list,
        description="List of detected banned phrases.",
        json_schema_extra={"x-ui-label": "Banned Phrases"},
    )
