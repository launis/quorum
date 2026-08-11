"""Coach Agent Domain Models.

This module contains the schemas for the Coach Agent,
including coaching plans and bibliography.
"""

from typing import Annotated, Any

from pydantic import ConfigDict, Field

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

    model_config = ConfigDict(strict=True, extra="forbid")

    chat_log: Annotated[str, Field(min_length=1, description="Mandatory chatlog.")]
    step_judge: Annotated[
        JudgeOutput | None,
        Field(description="The Verdict from Judge Agent.", json_schema_extra={"x-ui-label": "Judge Verdict"}),
    ] = None
    step_judge_cognitive: Annotated[
        JudgeOutput | None,
        Field(
            description="The Verdict from Cognitive Judge Agent.",
            json_schema_extra={"x-ui-label": "Cognitive Verdict"},
        ),
    ] = None
    last_reasoning_trace: Annotated[str | None, Field(description="Previous reasoning trace.")] = None

    # --- Universal Routing Inputs ---
    step_analyst: Annotated[Any | None, Field(description="Analyst hypotheses and RAG data.")] = None
    step_profiler: Annotated[Any | None, Field(description="Profiler cognitive bias data.")] = None
    step_falsifier: Annotated[Any | None, Field(description="Falsifier critical distance data.")] = None
    step_logician: Annotated[Any | None, Field(description="Logician Toulmin analysis data.")] = None
    step_causal_analyst: Annotated[
        Any | None, Field(description="Causal Analyst post-hoc and counterfactual data.")
    ] = None


class BibliographyItem(V2CoreBase):
    """A single bibliographic reference.

    Attributes:
        source_id: Unique source ID for L10n or tracing.
        title: Title of the source.
        url: URL of the reference source if available.
        snippet: Extracted relevant text segment.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    source_id: Annotated[
        str, Field(min_length=1, description="Unique source ID.", json_schema_extra={"x-ui-label": "Source ID"})
    ]
    title: Annotated[
        str, Field(min_length=1, description="Title of the source.", json_schema_extra={"x-ui-label": "Title"})
    ]
    url: Annotated[str | None, Field(description="URL if available.", json_schema_extra={"x-ui-label": "URL"})] = None
    snippet: Annotated[
        str | None, Field(description="Relevant snippet.", json_schema_extra={"x-ui-label": "Snippet"})
    ] = None


class BibliographyResult(V2CoreBase):
    """Result of the bibliography generation (Hook).

    Attributes:
        references: List of reference objects.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    references: Annotated[
        list[BibliographyItem],
        Field(min_length=1, description="List of references.", json_schema_extra={"x-ui-label": "References"}),
    ]


class CoachingPlanDTO(ReasoningTraceDTO):
    """DTO for Coaching Plan (Content Only).

    Attributes:
        actionable_steps: Concrete steps for development or optimization.
        bibliography: Curated resources mapped to the findings.
        focus_areas: Critical areas highlighted for growth.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    actionable_steps: Annotated[
        list[str],
        Field(
            min_length=1,
            description="Concrete steps for improvement.",
            json_schema_extra={"x-ui-label": "Actionable Steps"},
        ),
    ]
    bibliography: Annotated[
        list[BibliographyItem],
        Field(
            min_length=1,
            description="Recommended reading.",
            json_schema_extra={"x-ui-label": "References"},
        ),
    ]
    focus_areas: Annotated[
        list[str],
        Field(
            min_length=1,
            description="Key areas to focus on.",
            json_schema_extra={"x-ui-label": "Focus Areas"},
        ),
    ]


class CoachingPlan(CoachingPlanDTO, ReasoningTrace):
    """Output schema for the Coach Agent (Domain Model).

    Integrates DTO data alongside standard AI Reasoning trace telemetry.

    Attributes:
        actionable_steps: Inherited from CoachingPlanDTO.
        bibliography: Inherited from CoachingPlanDTO.
        focus_areas: Inherited from CoachingPlanDTO.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    pass
