"""Falsifier Agent Domain Models.

This module contains the schemas for the Falsifier Agent,
including stress tests and fidelity audits.
"""

from __future__ import annotations

import logging

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase

logger = logging.getLogger(__name__)

from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.logician import LogicianOutput
from backend_v2.models.enums import FidelityLevel


class FalsifierInput(V2CoreBase):
    """Strict input schema for LogicalFalsifierAgent."""

    chat_log: str = Field(..., min_length=1, description="Mandatory chatlog to analyze.")
    step_analyst: AnalystOutput | LogicianOutput | None = Field(None, description="Analyst or Logician outputs.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")


class WaltonStressTest(V2CoreBase):
    """Stress test using Walton's critical questions."""

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
        description=(
            "Numeric fidelity score (1.0 to 3.0), required 1-decimal precision. "
            "USE DECIMALS (e.g., 2.5) to reflect nuance."
        ),
        json_schema_extra={"x-ui-label": "Fidelity Numeric"},
    )
    abductive_score: float = Field(
        ...,
        ge=1.0,
        le=3.0,
        description=(
            "Numeric abductive score (1.0 to 3.0), required 1-decimal precision. "
            "USE DECIMALS (e.g., 2.5) to reflect nuance."
        ),
        json_schema_extra={"x-ui-label": "Abductive Score"},
    )
    plausibility_score: float = Field(
        ...,
        ge=1.0,
        le=3.0,
        description=(
            "Numeric plausibility score (1.0 to 3.0), required 1-decimal precision. "
            "USE DECIMALS (e.g., 2.5) to reflect nuance."
        ),
        json_schema_extra={"x-ui-label": "Plausibility Score"},
    )
    justification: str = Field(
        ..., min_length=1, description="Justification.", json_schema_extra={"x-ui-label": "Justification"}
    )
    quote: str | None = Field(
        default=None, min_length=1, description="Direct quote.", json_schema_extra={"x-ui-label": "Quote"}
    )
    post_hoc_rationalization: bool = Field(
        default=False,
        description="Was reasoning constructed after the fact?",
        json_schema_extra={"x-ui-label": "Post-Hoc Rationalization"},
    )


class FalsifierData(V2CoreBase):
    """Output from the Falsifier component."""

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
    """Falsifier DTO (Content Only)."""

    falsifier_data: FalsifierData = Field(
        ...,
        description="Falsification audit result.",
        json_schema_extra={"x-ui-label": "Falsification Audit"},
    )


class FalsifierOutput(FalsifierDTO, ReasoningTrace):
    """Output schema for the Falsifier Agent."""
