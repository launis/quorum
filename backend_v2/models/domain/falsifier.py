"""Falsifier Agent Domain Models.

This module contains the schemas for the Falsifier Agent,
including stress tests and fidelity audits.
"""

from __future__ import annotations

import logging

from pydantic import Field, field_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.logician import LogicianOutput
from backend_v2.models.enums import LaxFidelityLevel

logger = logging.getLogger(__name__)


class FalsifierInput(V2CoreBase):
    """Strict input schema for LogicalFalsifierAgent.

    Attributes:
        chat_log: Mandatory chatlog to analyze.
        step_analyst: Analyst or Logician outputs.
        last_reasoning_trace: Previous reasoning trace.
    """

    chat_log: str = Field(..., min_length=1, description="Mandatory chatlog to analyze.")
    step_analyst: AnalystOutput | LogicianOutput | None = Field(None, description="Analyst or Logician outputs.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")


class WaltonStressTest(V2CoreBase):
    """Stress test using Walton's critical questions.

    Attributes:
        question: The critical question asked.
        evidence_held: Did the evidence hold up?
        observation: Observation notes.
    """

    question: str = Field(
        ...,
        min_length=1,
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
        min_length=1,
        description="Observation notes.",
        json_schema_extra={"x-ui-label": "Observation"},
    )


class ReasoningFidelity(V2CoreBase):
    """Fidelity of reasoning metrics and evaluation results.

    Attributes:
        fidelity_score: Fidelity level enum.
        fidelity_numeric: Numeric fidelity score (1.0 to 3.0), required 1-decimal precision.
        abductive_score: Numeric abductive score (1.0 to 3.0), required 1-decimal precision.
        plausibility_score: Numeric plausibility score (1.0 to 3.0), required 1-decimal precision.
        justification: Justification for scores.
        quote: Direct quote from sources.
        post_hoc_rationalization: True if reasoning was constructed after the fact.
    """

    fidelity_score: LaxFidelityLevel = Field(
        ...,
        description="Fidelity level.",
        json_schema_extra={"x-ui-label": "Fidelity Score"},
    )
    fidelity_numeric: float = Field(
        ...,
        description=(
            "Numeric fidelity score (1.0 to 3.0), required 1-decimal precision. "
            "USE DECIMALS (e.g., 2.5) to reflect nuance."
        ),
        json_schema_extra={"x-ui-label": "Fidelity Numeric"},
    )
    abductive_score: float = Field(
        ...,
        description=(
            "Numeric abductive score (1.0 to 3.0), required 1-decimal precision. "
            "USE DECIMALS (e.g., 2.5) to reflect nuance."
        ),
        json_schema_extra={"x-ui-label": "Abductive Score"},
    )
    plausibility_score: float = Field(
        ...,
        description=(
            "Numeric plausibility score (1.0 to 3.0), required 1-decimal precision. "
            "USE DECIMALS (e.g., 2.5) to reflect nuance."
        ),
        json_schema_extra={"x-ui-label": "Plausibility Score"},
    )

    @field_validator("fidelity_numeric", "abductive_score", "plausibility_score")
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
            logger.error("[FalsifierModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise ValueError(msg)
        return v

    justification: str = Field(
        ..., min_length=1, description="Justification.", json_schema_extra={"x-ui-label": "Justification"}
    )
    quote: str | None = Field(default=None, description="Direct quote.", json_schema_extra={"x-ui-label": "Quote"})
    post_hoc_rationalization: bool = Field(
        default=False,
        description="Was reasoning constructed after the fact?",
        json_schema_extra={"x-ui-label": "Post-Hoc Rationalization"},
    )


class FalsifierData(V2CoreBase):
    """Output data structured by the Falsifier component.

    Attributes:
        stress_test_findings: Stress test results using Walton critical questions.
        fidelity_audit: Comprehensive reasoning fidelity results.
    """

    stress_test_findings: list[WaltonStressTest] = Field(
        ...,
        min_length=1,
        description="Stress test results.",
        json_schema_extra={"x-ui-label": "Stress Test"},
    )
    fidelity_audit: ReasoningFidelity = Field(
        ...,
        description="Fidelity audit.",
        json_schema_extra={"x-ui-label": "Fidelity Audit"},
    )


class FalsifierDTO(ReasoningTraceDTO):
    """Falsifier Data Transfer Object carrying structural evaluation findings.

    Attributes:
        falsifier_data: Falsification audit result containing stress tests and fidelity.
    """

    falsifier_data: FalsifierData = Field(
        ...,
        description="Falsification audit result.",
        json_schema_extra={"x-ui-label": "Falsification Audit"},
    )


class FalsifierOutput(FalsifierDTO, ReasoningTrace):
    """Final output schema for the Falsifier Agent combining telemetry and audit payload.

    Attributes:
        falsifier_data: Falsification audit result containing stress tests and fidelity.
    """

    pass
