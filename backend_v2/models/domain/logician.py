"""Logician Agent Domain Models.

This module contains the schemas for the Logician Agent,
including Toulmin argumentation analysis and Walton schemes.
"""

import logging
from typing import Any

from pydantic import Field, model_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.enums import BloomLevel, StrategicDepth, LaxBloomLevel, LaxStrategicDepth
from backend_v2.services.localization import LocalizationService

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

    @model_validator(mode="before")
    @classmethod
    def calculate_scores(cls, data: Any) -> Any:
        """Calculate numeric scores and populate descriptions."""
        if isinstance(data, dict):
            # Populate Description (Context-Aware)
            key = data.get("description_key", "bloom_desc")
            if not data.get("description"):
                data["description"] = LocalizationService.translate(key)

            bloom_map = {
                BloomLevel.REMEMBERING: 1.0,
                BloomLevel.UNDERSTANDING: 2.0,
                BloomLevel.APPLYING: 3.0,
                BloomLevel.ANALYZING: 4.0,
                BloomLevel.EVALUATING: 5.0,
                BloomLevel.CREATING: 6.0,
                BloomLevel.REMEMBERING.value: 1.0,
                BloomLevel.UNDERSTANDING.value: 2.0,
                BloomLevel.APPLYING.value: 3.0,
                BloomLevel.ANALYZING.value: 4.0,
                BloomLevel.EVALUATING.value: 5.0,
                BloomLevel.CREATING.value: 6.0,
            }

            current_bloom_score = data.get("bloom_score")
            if current_bloom_score is None:
                b_val = data.get("bloom_level")
                if b_val in bloom_map:
                    data["bloom_score"] = bloom_map[b_val]

            strat_map = {
                StrategicDepth.LOW: 1.0,
                StrategicDepth.MEDIUM: 2.0,
                StrategicDepth.HIGH: 3.0,
                StrategicDepth.VISIONARY: 4.0,
                StrategicDepth.LOW.value: 1.0,
                StrategicDepth.MEDIUM.value: 2.0,
                StrategicDepth.HIGH.value: 3.0,
                StrategicDepth.VISIONARY.value: 4.0,
            }

            current_strat_score = data.get("strategic_score")
            if current_strat_score is None:
                s_val = data.get("strategic_depth")
                if s_val in strat_map:
                    data["strategic_score"] = strat_map[s_val]

        return data


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

    @model_validator(mode="before")
    @classmethod
    def pop_desc(cls, data: Any) -> Any:
        if isinstance(data, dict):
            key = data.get("description_key", "toulmin_desc")
            if not data.get("description"):
                data["description"] = LocalizationService.translate(key)
        return data


class LogicianOutputDTO(ReasoningTraceDTO):
    """Logician Output DTO (Content Only)."""

    logician_data: LogicianData = Field(
        ...,
        description="Logic analysis results.",
        json_schema_extra={"x-ui-label": "Logic Analysis"},
    )


class LogicianOutput(LogicianOutputDTO, ReasoningTrace):
    """Output schema for the Logician Agent (Domain Authority)."""
