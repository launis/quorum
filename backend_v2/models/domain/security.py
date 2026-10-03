"""Security Domain Models.

Provides strict Pydantic V2 validation schemas for the security hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

import logging
from typing import Annotated, Any

from pydantic import ConfigDict, Field, field_validator, model_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTraceDTO
from backend_v2.models.enums import LaxRiskLevel, LaxSimulationType

logger = logging.getLogger(__name__)


class SecurityPayloadDTO(V2CoreBase):
    """Strict schema for inputs destined for text sanitization.

    Attributes:
        root: Raw state inputs.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    root: Annotated[dict[str, Any], Field(default_factory=dict)]

    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
        extra: Any | None = None,
    ) -> SecurityPayloadDTO:
        if type(obj) is dict:
            return cls(root=obj)
        return super().model_validate(
            obj,
            strict=strict,
            from_attributes=from_attributes,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
            extra=extra,
        )


class SanitizationResultDTO(V2CoreBase):
    """Result payload for text sanitization.

    Attributes:
        sanitized_inputs: Original keys mapped to sanitized values.
        security_status: Overall status of the security check.
        threat_detected: Flag indicating if a threat was detected.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    sanitized_inputs: Annotated[dict[str, str], Field(description="The inputs after sanitization")]
    security_status: Annotated[str, Field(min_length=1, description="Status of the security check")]
    threat_detected: Annotated[bool, Field(description="Whether a threat was detected")]


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

    model_config = ConfigDict(strict=True, extra="forbid")

    threat_detected: Annotated[
        bool,
        Field(
            description="Threat detected flag.",
            json_schema_extra={"x-ui-label": "Threat Detected"},
        ),
    ]
    risk_level: Annotated[
        LaxRiskLevel,
        Field(
            description="Risk level.",
            json_schema_extra={"x-ui-label": "Risk Level"},
        ),
    ]
    risk_score: Annotated[
        float,
        Field(
            description="Numeric Risk score (1-3).",
            json_schema_extra={"x-ui-label": "Risk Score"},
        ),
    ]
    simulation_score: Annotated[
        float,
        Field(
            description="Numeric Simulation score (1-3).",
            json_schema_extra={"x-ui-label": "Simulation Score"},
        ),
    ]

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

    simulation_result: Annotated[
        LaxSimulationType | None,
        Field(
            description="Simulation result description.",
            json_schema_extra={"x-ui-label": "Simulation Result"},
        ),
    ] = None
    anonymized: Annotated[
        bool,
        Field(
            description="Was anonymization performed?",
            json_schema_extra={"x-ui-label": "Anonymized"},
        ),
    ]
    pii_findings: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="PII findings.",
            json_schema_extra={"x-ui-label": "PII Findings"},
        ),
    ]


class InputProcessingOutputDTO(ReasoningTraceDTO):
    """Data Transfer Object for Unified Input Processing and Security Hook.

    Attributes:
        is_safe: Whether the input is considered safe.
        rejection_reason: Reason for rejection if unsafe.
        security_check: Nested security check details.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    is_safe: Annotated[
        bool,
        Field(
            description="Whether the input is considered safe.",
            json_schema_extra={"x-ui-label": "Is Safe"},
        ),
    ]
    rejection_reason: Annotated[
        str | None,
        Field(
            description="Reason for rejection if unsafe.",
            json_schema_extra={"x-ui-label": "Rejection Reason"},
        ),
    ] = None
    security_check: Annotated[
        SecurityCheck | None,
        Field(
            description="Security scan results.",
            json_schema_extra={"x-ui-label": "Security Check"},
        ),
    ] = None

    @model_validator(mode="after")
    def validate_safety_reason(self) -> InputProcessingOutputDTO:
        """Validates that a rejection reason is provided if is_safe is False.

        Returns:
            The validated InputProcessingOutputDTO instance.

        Raises:
            ValueError: If is_safe is False and rejection_reason is missing.
        """
        if not self.is_safe and not self.rejection_reason:
            raise ValueError("rejection_reason must be provided if is_safe is False")
        return self
