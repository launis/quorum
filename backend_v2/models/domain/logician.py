"""Logician Agent Domain Models.

This module contains the schemas for the Logician Agent,
including Toulmin argumentation analysis and Walton schemes.
"""

import logging
from typing import Any

from pydantic import Field, field_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.enums import LaxBloomLevel, LaxStrategicDepth

logger = logging.getLogger(__name__)


class LogicianInput(V2CoreBase):
    """Strict input schema for LogicianAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are encapsulated dynamically.

    Attributes:
        chat_log: The mandatory conversation history to analyze.
        step_analyst: Analyst hypotheses/timeline.
        last_reasoning_trace: Previous reasoning trace.
        dynamic_inputs: Structured dictionary for dynamic inputs.
    """

    chat_log: str = Field(
        ...,
        min_length=1,
        description="The mandatory conversation history to analyze.",
        json_schema_extra={"x-ui-label": "Chatlog"},
    )
    step_analyst: AnalystOutput | None = Field(default=None, description="Analyst hypotheses/timeline.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")
    dynamic_inputs: dict[str, Any] = Field(
        default_factory=dict, description="Structured dictionary for dynamic inputs."
    )


class ToulminComponent(V2CoreBase):
    """Component of the Toulmin Argumentation Model.

    Attributes:
        id: Reference ID.
        claim: The conclusion.
        data: The evidence.
        warrant: The logical bridge.
        backing: Support for the warrant.
        rebuttal: Counter-arguments.
        qualifier: Degree of certainty.
    """

    id: str = Field(
        ...,
        min_length=1,
        description="Reference ID.",
        json_schema_extra={"x-ui-label": "ID"},
    )
    claim: str = Field(
        ...,
        min_length=1,
        description="The conclusion.",
        json_schema_extra={"x-ui-label": "Claim"},
    )
    data: str = Field(
        ...,
        min_length=1,
        description="The evidence.",
        json_schema_extra={"x-ui-label": "Data"},
    )
    warrant: str = Field(
        ...,
        min_length=1,
        description="The logical bridge.",
        json_schema_extra={"x-ui-label": "Warrant"},
    )
    backing: str | None = Field(
        default=None,
        description="Support for the warrant.",
        json_schema_extra={"x-ui-label": "Backing"},
    )
    rebuttal: str | None = Field(
        default=None,
        description="Counter-arguments.",
        json_schema_extra={"x-ui-label": "Rebuttal"},
    )
    qualifier: str | None = Field(
        default=None,
        description="Degree of certainty.",
        json_schema_extra={"x-ui-label": "Qualifier"},
    )


class CognitiveLevel(V2CoreBase):
    """Assessment of cognitive depth.

    Attributes:
        bloom_level: Bloom's Taxonomy Level.
        strategic_depth: Strategic depth analysis.
        bloom_score: Numeric Bloom score (0.0 to 6.0), required 1-decimal precision.
        strategic_score: Numeric Strategic score (1.0 to 4.0), required 1-decimal precision.
        description_key: Localization key for help text.
        description: Localized description.
    """

    bloom_level: LaxBloomLevel = Field(
        ...,
        description="Bloom's Taxonomy Level.",
        json_schema_extra={"x-ui-label": "Bloom Level"},
    )
    strategic_depth: LaxStrategicDepth = Field(
        ...,
        description="Strategic depth analysis.",
        json_schema_extra={"x-ui-label": "Strategic Depth"},
    )
    bloom_score: float = Field(
        ...,
        description=(
            "Numeric Bloom score (0.0 to 6.0), required 1-decimal precision. "
            "USE DECIMALS (e.g., 4.5) to reflect nuance."
        ),
        json_schema_extra={"x-ui-label": "Bloom Score"},
    )
    strategic_score: float = Field(
        ...,
        description=(
            "Numeric Strategic score (1.0 to 4.0), required 1-decimal precision. "
            "USE DECIMALS (e.g., 2.5) to reflect nuance."
        ),
        json_schema_extra={"x-ui-label": "Strategic Score"},
    )
    description_key: str = Field(
        default="bloom_desc",
        description="Localization key for help text.",
    )
    description: str = Field(
        default="", description="Localized description.", json_schema_extra={"x-ui-label": "Description"}
    )

    @field_validator("bloom_score")
    @classmethod
    def validate_bloom_score(cls, v: float) -> float:
        """Enforce limits locally to bypass Vertex AI 400 Field schema constraint parser rules.

        Args:
            v: The validation candidate float score.

        Returns:
            The validated float score if within bounds.

        Raises:
            ValueError: If bloom_score is not between 0.0 and 6.0.
        """
        if not (0.0 <= v <= 6.0):
            raise ValueError("bloom_score must be between 0.0 and 6.0")
        return v

    @field_validator("strategic_score")
    @classmethod
    def validate_strategic_score(cls, v: float) -> float:
        """Enforce limits locally to bypass Vertex AI 400 Field schema constraint parser rules.

        Args:
            v: The validation candidate float score.

        Returns:
            The validated float score if within bounds.

        Raises:
            ValueError: If strategic_score is not between 1.0 and 4.0.
        """
        if not (1.0 <= v <= 4.0):
            raise ValueError("strategic_score must be between 1.0 and 4.0")
        return v


class WaltonScheme(V2CoreBase):
    """Walton's Argumentation Scheme.

    Attributes:
        identified_scheme: Identified Argumentation Scheme.
        critical_questions: Critical Questions posed.
    """

    identified_scheme: str = Field(
        ...,
        min_length=1,
        description="Identified Argumentation Scheme.",
        json_schema_extra={"x-ui-label": "Identified Scheme"},
    )
    critical_questions: list[str] = Field(
        ...,
        min_length=1,
        description="Critical Questions posed.",
        json_schema_extra={"x-ui-label": "Critical Questions"},
    )


class LogicianData(V2CoreBase):
    """The core data payload of Logician analysis.

    Attributes:
        toulmin_analysis: Toulmin analysis breakdown.
        cognitive_level: Cognitive level assessment.
        walton_scheme: Argumentation scheme analysis.
        toulmin_score: Calculated score based on components.
        description_key: Localization key for help text.
        description: Localized description.
    """

    toulmin_analysis: list[ToulminComponent] = Field(
        ...,
        min_length=1,
        description="Toulmin analysis breakdown.",
        json_schema_extra={"x-ui-label": "Toulmin Analysis"},
    )
    cognitive_level: CognitiveLevel = Field(
        ...,
        description="Cognitive level assessment.",
        json_schema_extra={"x-ui-label": "Cognitive Level"},
    )
    walton_scheme: WaltonScheme = Field(
        ...,
        description="Argumentation scheme analysis.",
        json_schema_extra={"x-ui-label": "Argumentation Scheme"},
    )
    toulmin_score: float = Field(
        ...,
        description=(
            "Calculated score based on components (0.0 to 6.0), required 1-decimal precision. "
            "USE DECIMALS (e.g., 5.5) to reflect nuance."
        ),
        json_schema_extra={"x-ui-label": "Toulmin Score"},
    )
    description_key: str = Field(
        default="toulmin_desc",
        description="Localization key for help text.",
    )
    description: str = Field(
        default="", description="Localized description.", json_schema_extra={"x-ui-label": "Description"}
    )

    @field_validator("toulmin_score")
    @classmethod
    def validate_toulmin_score(cls, v: float) -> float:
        """Enforce limits locally to bypass Vertex AI 400 Field schema constraint parser rules.

        Args:
            v: The validation candidate float score.

        Returns:
            The validated float score if within bounds.

        Raises:
            ValueError: If toulmin_score is not between 0.0 and 6.0.
        """
        if not (0.0 <= v <= 6.0):
            raise ValueError("toulmin_score must be between 0.0 and 6.0")
        return v


class LogicianOutputDTO(ReasoningTraceDTO):
    """Logician Output DTO (Content Only).

    Attributes:
        logician_data: Logic analysis results.
    """

    logician_data: LogicianData = Field(
        ...,
        description="Logic analysis results.",
        json_schema_extra={"x-ui-label": "Logic Analysis"},
    )


class LogicianOutput(LogicianOutputDTO, ReasoningTrace):
    """Output schema for the Logician Agent (Domain Authority)."""
