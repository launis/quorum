"""Falsifier Agent Domain Models.

This module contains the schemas for the Falsifier Agent,
including stress tests and fidelity audits.
"""

from __future__ import annotations

import logging
from typing import Annotated

from pydantic import ConfigDict, Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
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
    model_config = ConfigDict(strict=True, extra="forbid")

    chat_log: Annotated[str, Field(min_length=1, description="Mandatory chatlog to analyze.")]
    step_analyst: Annotated[
        AnalystOutput | LogicianOutput | None, Field(description="Analyst or Logician outputs.")
    ] = None
    last_reasoning_trace: Annotated[str | None, Field(description="Previous reasoning trace.")] = None


class WaltonStressTest(V2CoreBase):
    """Stress test using Walton's critical questions.

    Attributes:
        question: The critical question asked.
        evidence_held: Did the evidence hold up?
        observation: Observation notes.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    question: Annotated[
        str,
        Field(
            min_length=1,
            description="The critical question asked.",
            json_schema_extra={"x-ui-label": "Question"},
        ),
    ]
    evidence_held: Annotated[
        bool,
        Field(
            description="Did the evidence hold up?",
            json_schema_extra={"x-ui-label": "Result"},
        ),
    ]
    observation: Annotated[
        str,
        Field(
            min_length=1,
            description="Observation notes.",
            json_schema_extra={"x-ui-label": "Observation"},
        ),
    ]


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
    model_config = ConfigDict(strict=True, extra="forbid")

    fidelity_score: Annotated[
        LaxFidelityLevel,
        Field(
            description="Fidelity level.",
            json_schema_extra={"x-ui-label": "Fidelity Score"},
        ),
    ]
    fidelity_numeric: Annotated[
        float,
        Field(
            description=(
                "Numeric fidelity score (1.0 to 3.0), required 1-decimal precision. "
                "USE DECIMALS (e.g., 2.5) to reflect nuance."
            ),
            json_schema_extra={"x-ui-label": "Fidelity Numeric"},
        ),
    ]
    abductive_score: Annotated[
        float,
        Field(
            description=(
                "Numeric abductive score (1.0 to 3.0), required 1-decimal precision. "
                "USE DECIMALS (e.g., 2.5) to reflect nuance."
            ),
            json_schema_extra={"x-ui-label": "Abductive Score"},
        ),
    ]
    plausibility_score: Annotated[
        float,
        Field(
            description=(
                "Numeric plausibility score (1.0 to 3.0), required 1-decimal precision. "
                "USE DECIMALS (e.g., 2.5) to reflect nuance."
            ),
            json_schema_extra={"x-ui-label": "Plausibility Score"},
        ),
    ]

    justification: Annotated[
        str, Field(min_length=1, description="Justification.", json_schema_extra={"x-ui-label": "Justification"})
    ]
    quote: Annotated[str | None, Field(description="Direct quote.", json_schema_extra={"x-ui-label": "Quote"})] = None
    post_hoc_rationalization: Annotated[
        bool,
        Field(
            description="Was reasoning constructed after the fact?",
            json_schema_extra={"x-ui-label": "Post-Hoc Rationalization"},
        ),
    ] = False

    @field_validator("fidelity_numeric", "abductive_score", "plausibility_score")
    @classmethod
    def validate_scores_bounds(cls, v: float) -> float:
        """Validate that score is between 1.0 and 3.0.

        Args:
            v: Input score.

        Returns:
            Validated score.

        Raises:
            AppException: If score is out of bounds.
        """
        if not (1.0 <= v <= 3.0):
            msg = "Score must be between 1.0 and 3.0"
            logger.error("[FalsifierModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v


class FalsifierData(V2CoreBase):
    """Output data structured by the Falsifier component.

    Attributes:
        stress_test_findings: Stress test results using Walton critical questions.
        fidelity_audit: Comprehensive reasoning fidelity results.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    stress_test_findings: Annotated[
        list[WaltonStressTest],
        Field(
            min_length=1,
            description="Stress test results.",
            json_schema_extra={"x-ui-label": "Stress Test"},
        ),
    ]
    fidelity_audit: Annotated[
        ReasoningFidelity,
        Field(
            description="Fidelity audit.",
            json_schema_extra={"x-ui-label": "Fidelity Audit"},
        ),
    ]


class FalsifierDTO(ReasoningTraceDTO):
    """Falsifier Data Transfer Object carrying structural evaluation findings.

    Attributes:
        falsifier_data: Falsification audit result containing stress tests and fidelity.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    falsifier_data: Annotated[
        FalsifierData,
        Field(
            description="Falsification audit result.",
            json_schema_extra={"x-ui-label": "Falsification Audit"},
        ),
    ]


class FalsifierOutput(FalsifierDTO, ReasoningTrace):
    """Final output schema for the Falsifier Agent combining telemetry and audit payload.

    Attributes:
        falsifier_data: Falsification audit result containing stress tests and fidelity.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    pass
