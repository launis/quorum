"""Overseer Agent Domain Models.

This module contains the schemas for the Overseer Agent,
including fact checks and ethical observations.
"""

from __future__ import annotations

import logging
from typing import Annotated

from pydantic import ConfigDict, Field, computed_field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.logician import LogicianOutput
from backend_v2.models.enums import EthicalSeverity, LaxEthicalSeverity, LaxVerificationResult, VerificationResult

logger = logging.getLogger(__name__)


class OverseerInput(V2CoreBase):
    """Strict input schema for FactualOverseerAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are allowed dynamically.

    Attributes:
        chat_log: The mandatory conversation history to analyze.
        step_analyst: Analyst or Logician outputs.
        last_reasoning_trace: Previous reasoning trace.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    chat_log: Annotated[
        str,
        Field(
            min_length=1,
            description="The mandatory conversation history to analyze.",
            json_schema_extra={"x-ui-label": "Chatlog"},
        ),
    ]
    step_analyst: Annotated[
        AnalystOutput | LogicianOutput | None, Field(description="Analyst or Logician outputs.")
    ] = None
    last_reasoning_trace: Annotated[str | None, Field(description="Previous reasoning trace.")] = None


class FactCheckRFI(V2CoreBase):
    """Request for Information (Fact Check).

    Attributes:
        claim: Claim to check.
        verification_result: Result.
        source_or_reasoning: Source or reasoning.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    claim: Annotated[
        str,
        Field(
            description="Claim to check.",
            json_schema_extra={"x-ui-label": "Claim"},
        ),
    ]
    verification_result: Annotated[
        LaxVerificationResult,
        Field(
            description="Result.",
            json_schema_extra={"x-ui-label": "Result"},
        ),
    ]
    source_or_reasoning: Annotated[
        str,
        Field(
            description="Source or reasoning.",
            json_schema_extra={"x-ui-label": "Source/Reasoning"},
        ),
    ]

    @field_validator("claim", "source_or_reasoning")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Validate that the string is not empty or whitespace only.

        Args:
            v: The value to validate.

        Returns:
            The stripped string.

        Raises:
            AppException: If the string is empty or whitespace only.
        """
        if not v or not v.strip():
            msg = "Field cannot be empty"
            logger.error("[OverseerModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v.strip()

    @computed_field  # type: ignore[prop-decorator]  # Pydantic computed_field with @property
    @property
    def is_verified(self) -> bool:
        """Boolean verification status."""
        return self.verification_result == VerificationResult.VERIFIED


class EthicalObservation(V2CoreBase):
    """Ethical Observation.

    Attributes:
        issue_type: Type of ethical issue.
        severity: Severity level.
        description: Description.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    issue_type: Annotated[
        str,
        Field(
            description="Type of ethical issue.",
            json_schema_extra={"x-ui-label": "Issue Type"},
        ),
    ]
    severity: Annotated[
        LaxEthicalSeverity,
        Field(
            description="Severity level.",
            json_schema_extra={"x-ui-label": "Severity"},
        ),
    ]
    description: Annotated[
        str,
        Field(
            description="Description.",
            json_schema_extra={"x-ui-label": "Description"},
        ),
    ]

    @field_validator("issue_type", "description")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Validate that the string is not empty or whitespace only.

        Args:
            v: The value to validate.

        Returns:
            The stripped string.

        Raises:
            AppException: If the string is empty or whitespace only.
        """
        if not v or not v.strip():
            msg = "Field cannot be empty"
            logger.error("[OverseerModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v.strip()

    @computed_field  # type: ignore[prop-decorator]  # Pydantic computed_field with @property
    @property
    def is_critical(self) -> bool:
        """Is the issue critical?"""
        return self.severity == EthicalSeverity.CRITICAL


class OverseerData(V2CoreBase):
    """Output from the Overseer component.

    Attributes:
        fact_checks: Fact check report.
        ethical_issues: Ethical audit report.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    fact_checks: Annotated[
        list[FactCheckRFI],
        Field(
            description="Fact check report.",
            json_schema_extra={"x-ui-label": "Fact Checks"},
        ),
    ] = Field(default_factory=list)
    ethical_issues: Annotated[
        list[EthicalObservation],
        Field(
            description="Ethical audit report.",
            json_schema_extra={"x-ui-label": "Ethical Issues"},
        ),
    ]

    @field_validator("ethical_issues")
    @classmethod
    def validate_ethical_issues(cls, v: list[EthicalObservation]) -> list[EthicalObservation]:
        """Validate that the ethical issues list is not empty.

        Args:
            v: The list of ethical issues.

        Returns:
            The validated list.

        Raises:
            AppException: If the list is empty.
        """
        if not v:
            msg = "Ethical issues list cannot be empty"
            logger.error("[OverseerModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v


class OverseerDTO(ReasoningTraceDTO):
    """Overseer DTO (Content Only).

    Attributes:
        overseer_data: Ethics audit result.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    overseer_data: Annotated[
        OverseerData,
        Field(
            description="Ethics audit result.",
            json_schema_extra={"x-ui-label": "Ethics Audit"},
        ),
    ]


class OverseerOutput(OverseerDTO, ReasoningTrace):
    """Output schema for the Overseer Agent.

    Attributes:
        No additional attributes.
    """

    model_config = ConfigDict(strict=True, extra="forbid")
