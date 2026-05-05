"""Overseer Agent Domain Models.

This module contains the schemas for the Overseer Agent,
including fact checks and ethical observations.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import Field, model_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import EthicalSeverity, VerificationResult, LaxEthicalSeverity, LaxVerificationResult

from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.logician import LogicianOutput

logger = logging.getLogger(__name__)


class OverseerInput(V2CoreBase):
    """Strict input schema for FactualOverseerAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are allowed dynamically.
    """

    chat_log: str = Field(
        ...,
        min_length=1,
        description="The mandatory conversation history to analyze.",
        json_schema_extra={"x-ui-label": "Chatlog"},
    )
    step_analyst: AnalystOutput | LogicianOutput | None = Field(None, description="Analyst or Logician outputs.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")


class FactCheckRFI(V2CoreBase):
    """Request for Information (Fact Check)."""

    claim: str = Field(
        ...,
        min_length=1,
        description="Claim to check.",
        json_schema_extra={"x-ui-label": "Claim"},
    )
    verification_result: LaxVerificationResult = Field(
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
        min_length=1,
        description="Source or reasoning.",
        json_schema_extra={"x-ui-label": "Source/Reasoning"},
    )

    @model_validator(mode="before")
    @classmethod
    def calc_verification(cls, data: Any) -> Any:
        if isinstance(data, dict):
            val = data.get("verification_result")
            data["is_verified"] = val in (VerificationResult.VERIFIED, "RESULT_VERIFIED")
        return data


class EthicalObservation(V2CoreBase):
    """Ethical Observation."""

    issue_type: str = Field(
        ...,
        min_length=1,
        description="Type of ethical issue.",
        json_schema_extra={"x-ui-label": "Issue Type"},
    )
    severity: LaxEthicalSeverity = Field(
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
        min_length=1,
        description="Description.",
        json_schema_extra={"x-ui-label": "Description"},
    )

    @model_validator(mode="before")
    @classmethod
    def calc_ethics(cls, data: Any) -> Any:
        if isinstance(data, dict):
            val = data.get("severity")
            data["is_critical"] = val in (EthicalSeverity.CRITICAL, "SEVERITY_CRITICAL")
        return data


class OverseerData(V2CoreBase):
    """Output from the Overseer component."""

    fact_checks: list[FactCheckRFI] = Field(
        default_factory=list,
        description="Fact check report.",
        json_schema_extra={"x-ui-label": "Fact Checks"},
    )
    ethical_issues: list[EthicalObservation] = Field(
        ...,
        min_length=1,
        description="Ethical audit report.",
        json_schema_extra={"x-ui-label": "Ethical Issues"},
    )


class OverseerDTO(ReasoningTraceDTO):
    """Overseer DTO (Content Only)."""

    overseer_data: OverseerData = Field(
        ...,
        description="Ethics audit result.",
        json_schema_extra={"x-ui-label": "Ethics Audit"},
    )


class OverseerOutput(OverseerDTO, ReasoningTrace):
    """Output schema for the Overseer Agent."""
