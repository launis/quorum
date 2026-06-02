"""Coach Agent Domain Models.

This module contains the schemas for the Coach Agent,
including coaching plans and bibliography.
"""

from typing import Any

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.judge import JudgeOutput


class CoachInput(V2CoreBase):
    """Strict input schema for CoachAgent.

    Attributes:
        chat_log: Mandatory chatlog string.
        step_judge: The Verdict from Judge Agent.
        step_judge_cognitive: The Verdict from Cognitive Judge Agent.
        last_reasoning_trace: Previous reasoning trace if present.
        step_analyst: Analyst hypotheses and RAG data.
        step_profiler: Profiler cognitive bias data.
        step_falsifier: Falsifier critical distance data.
        step_logician: Logician Toulmin analysis data.
        step_causal_analyst: Causal Analyst post-hoc and counterfactual data.
    """

    chat_log: str = Field(..., min_length=1, description="Mandatory chatlog.")
    step_judge: JudgeOutput | None = Field(
        default=None, description="The Verdict from Judge Agent.", json_schema_extra={"x-ui-label": "Judge Verdict"}
    )
    step_judge_cognitive: JudgeOutput | None = Field(
        default=None,
        description="The Verdict from Cognitive Judge Agent.",
        json_schema_extra={"x-ui-label": "Cognitive Verdict"},
    )
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    # --- Universal Routing Inputs ---
    step_analyst: Any | None = Field(default=None, description="Analyst hypotheses and RAG data.")
    step_profiler: Any | None = Field(default=None, description="Profiler cognitive bias data.")
    step_falsifier: Any | None = Field(default=None, description="Falsifier critical distance data.")
    step_logician: Any | None = Field(default=None, description="Logician Toulmin analysis data.")
    step_causal_analyst: Any | None = Field(
        default=None, description="Causal Analyst post-hoc and counterfactual data."
    )


class BibliographyItem(V2CoreBase):
    """A single bibliographic reference.

    Attributes:
        source_id: Unique source ID for L10n or tracing.
        title: Title of the source.
        url: URL of the reference source if available.
        snippet: Extracted relevant text segment.
    """

    source_id: str = Field(
        ..., min_length=1, description="Unique source ID.", json_schema_extra={"x-ui-label": "Source ID"}
    )
    title: str = Field(..., min_length=1, description="Title of the source.", json_schema_extra={"x-ui-label": "Title"})
    url: str | None = Field(default=None, description="URL if available.", json_schema_extra={"x-ui-label": "URL"})
    snippet: str | None = Field(
        default=None, description="Relevant snippet.", json_schema_extra={"x-ui-label": "Snippet"}
    )


class BibliographyResult(V2CoreBase):
    """Result of the bibliography generation (Hook).

    Attributes:
        references: List of reference objects.
    """

    references: list[BibliographyItem] = Field(
        ..., min_length=1, description="List of references.", json_schema_extra={"x-ui-label": "References"}
    )


class CoachingPlanDTO(ReasoningTraceDTO):
    """DTO for Coaching Plan (Content Only).

    Attributes:
        actionable_steps: Concrete steps for development or optimization.
        bibliography: Curated resources mapped to the findings.
        focus_areas: Critical areas highlighted for growth.
    """

    actionable_steps: list[str] = Field(
        ...,
        min_length=1,
        description="Concrete steps for improvement.",
        json_schema_extra={"x-ui-label": "Actionable Steps"},
    )
    bibliography: list[BibliographyItem] = Field(
        ...,
        min_length=1,
        description="Recommended reading.",
        json_schema_extra={"x-ui-label": "References"},
    )
    focus_areas: list[str] = Field(
        ...,
        min_length=1,
        description="Key areas to focus on.",
        json_schema_extra={"x-ui-label": "Focus Areas"},
    )


class CoachingPlan(CoachingPlanDTO, ReasoningTrace):
    """Output schema for the Coach Agent (Domain Model).

    Integrates DTO data alongside standard AI Reasoning trace telemetry.
    """
