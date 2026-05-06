"""Logician Agent Domain Models.

This module contains the schemas for the Logician Agent,
including Toulmin argumentation analysis and Walton schemes.
"""

import logging
from typing import Any

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.enums import LaxBloomLevel, LaxStrategicDepth

logger = logging.getLogger(__name__)


class LogicianInput(V2CoreBase):
    """Strict input schema for LogicianAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are encapsulated dynamically.
    """

    chat_log: str = Field(
        ...,
        min_length=1,
        description="The mandatory conversation history to analyze.",
        json_schema_extra={"x-ui-label": "Chatlog"},
    )
    step_analyst: AnalystOutput | None = Field(None, description="Analyst hypotheses/timeline.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    dynamic_inputs: dict[str, Any] = Field(
        default_factory=dict, description="Structured dictionary for dynamic inputs."
    )


class ToulminComponent(V2CoreBase):
    """Component of the Toulmin Argumentation Model."""

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
    """Assessment of cognitive depth."""

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
        ge=0.0,
        le=6.0,
        description=(
            "Numeric Bloom score (0.0 to 6.0), required 1-decimal precision. "
            "USE DECIMALS (e.g., 4.5) to reflect nuance."
        ),
        json_schema_extra={"x-ui-label": "Bloom Score"},
    )
    strategic_score: float = Field(
        ...,
        ge=1.0,
        le=4.0,
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


class WaltonScheme(V2CoreBase):
    """Walton's Argumentation Scheme."""

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
    """The core data payload of Logician analysis."""

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
        ge=0.0,
        le=6.0,
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


class LogicianOutputDTO(ReasoningTraceDTO):
    """Logician Output DTO (Content Only)."""

    logician_data: LogicianData = Field(
        ...,
        description="Logic analysis results.",
        json_schema_extra={"x-ui-label": "Logic Analysis"},
    )


class LogicianOutput(LogicianOutputDTO, ReasoningTrace):
    """Output schema for the Logician Agent (Domain Authority)."""
