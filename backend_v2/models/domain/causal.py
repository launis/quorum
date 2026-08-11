"""Causal Agent Domain Models.

This module contains the schemas for the Causal Agent,
including counterfactual testing and abductive reasoning.
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
from backend_v2.models.enums import LaxAbductiveConclusion, LaxPlausibilityLevel

logger = logging.getLogger(__name__)


class CausalInput(V2CoreBase):
    """Strict input schema for CausalAnalystAgent.

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


class CausalAnalysisData(V2CoreBase):
    """Data from Causal Audit.

    Attributes:
        timeline_valid: Is the timeline valid?
        observation: General observations.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    timeline_valid: Annotated[
        bool,
        Field(description="Is the timeline valid?", json_schema_extra={"x-ui-label": "Timeline Valid"}),
    ]
    observation: Annotated[
        str,
        Field(min_length=1, description="General observations.", json_schema_extra={"x-ui-label": "Observations"}),
    ]


class CounterfactualTest(V2CoreBase):
    """Counterfactual test result.

    Attributes:
        plausibility_score: Plausibility score.
        plausibility_numeric: Numeric plausibility (1.0 to 3.0), required 1-decimal precision.
        actual_scenario: Actual outcome.
        simulation_result: Simulation outcome.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    plausibility_score: Annotated[
        LaxPlausibilityLevel,
        Field(description="Plausibility score.", json_schema_extra={"x-ui-label": "Plausibility Score"}),
    ]
    plausibility_numeric: Annotated[
        float,
        Field(
            description=(
                "Numeric plausibility (1.0 to 3.0), required 1-decimal precision. "
                "USE DECIMALS (e.g., 2.5) to reflect nuance."
            ),
            json_schema_extra={"x-ui-label": "Plausibility Numeric"},
        ),
    ]

    @field_validator("plausibility_numeric")
    @classmethod
    def validate_plausibility_numeric(cls, v: float) -> float:
        """Enforce strict plausibility score boundaries between 1.0 and 3.0.

        Args:
            v: Plausibility score to validate.

        Returns:
            Validated float amount.

        Raises:
            AppException: If score is out of bounds (VALIDATION_FAILED).
        """
        if not (1.0 <= v <= 3.0):
            msg = "plausibility_numeric must be between 1.0 and 3.0 inclusive"
            logger.error("[CausalModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v

    actual_scenario: Annotated[
        str, Field(min_length=1, description="Actual outcome.", json_schema_extra={"x-ui-label": "Actual Scenario"})
    ]
    simulation_result: Annotated[
        str,
        Field(min_length=1, description="Simulation outcome.", json_schema_extra={"x-ui-label": "Simulation Result"}),
    ]


class CausalAnalysis(V2CoreBase):
    """Causal analysis result.

    Attributes:
        abductive_conclusion: Abductive conclusion type.
        abductive_score: Numeric abductive score (1.0 to 3.0), required 1-decimal precision.
        counterfactual_test: Counterfactual analysis.
        observation: Observation.
        hypothesis: Hypothesis.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    abductive_conclusion: Annotated[
        LaxAbductiveConclusion,
        Field(description="Abductive conclusion type.", json_schema_extra={"x-ui-label": "Abductive Conclusion"}),
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

    @field_validator("abductive_score")
    @classmethod
    def validate_abductive_score(cls, v: float) -> float:
        """Enforce strict abductive score boundaries between 1.0 and 3.0.

        Args:
            v: Abductive score to validate.

        Returns:
            Validated float amount.

        Raises:
            AppException: If score is out of bounds (VALIDATION_FAILED).
        """
        if not (1.0 <= v <= 3.0):
            msg = "abductive_score must be between 1.0 and 3.0 inclusive"
            logger.error("[CausalModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v

    counterfactual_test: Annotated[
        CounterfactualTest,
        Field(description="Counterfactual analysis.", json_schema_extra={"x-ui-label": "Counterfactual Test"}),
    ]
    observation: Annotated[
        str, Field(min_length=1, description="Observation.", json_schema_extra={"x-ui-label": "Observation"})
    ]
    hypothesis: Annotated[
        str, Field(min_length=1, description="Hypothesis.", json_schema_extra={"x-ui-label": "Hypothesis"})
    ]


class CausalDTO(ReasoningTraceDTO):
    """Causal DTO (Content Only).

    Attributes:
        causal_analysis: Causal audit result.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    causal_analysis: Annotated[
        CausalAnalysis,
        Field(description="Causal audit result.", json_schema_extra={"x-ui-label": "Causal Audit"}),
    ]


class CausalOutput(CausalDTO, ReasoningTrace):
    """Output schema for the Causal Agent.

    Attributes:
        causal_analysis: Causal audit result inherited from CausalDTO.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    pass
