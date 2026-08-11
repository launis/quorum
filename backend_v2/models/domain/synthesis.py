"""Synthesis Hook Domain Models.

Provides strict Pydantic V2 validation schemas for the synthesis pipeline
to eliminate legacy dictionary-based parsing.
"""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.state import StepExecutionEnvelope, StepOutputDTO


class SynthesisMetadataDTO(V2CoreBase):
    """Strict schema for execution metadata used during synthesis.

    Attributes:
        target_locale: Target localization code.
        token_usage: Comprehensive tracker for LLM token usage metrics.
        step_results: Completed step outputs mapped during parsing.
        profile_id: Identifier of user persona profile.
        target_profile_id: ID of the targeted evaluation profile.
        matrix_sampling_strategy: Index defining sampling patterns.
        workflow_version: Tracked version of execution state flow.
        total_tokens: Total tokens consumed across all steps.
        prompt_tokens: Cumulative tokens consumed via prompt inputs.
        completion_tokens: Cumulative tokens returned by upstream APIs.
        cost_estimate: Estimate representing financial metrics.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    target_locale: Annotated[str, Field(min_length=1)]
    token_usage: Annotated[TokenUsage, Field()] = Field(
        default_factory=lambda: TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
    )
    step_results: Annotated[list[StepOutputDTO], Field()] = Field(default_factory=list)
    profile_id: Annotated[str | None, Field()] = None
    target_profile_id: Annotated[str | None, Field()] = None
    matrix_sampling_strategy: Annotated[int | None, Field()] = None
    workflow_version: Annotated[int | None, Field()] = None

    # Injected by worker.py during execution trace iterations for token usage tracking
    total_tokens: Annotated[int | None, Field()] = None
    prompt_tokens: Annotated[int | None, Field()] = None
    completion_tokens: Annotated[int | None, Field()] = None
    cost_estimate: Annotated[float | None, Field()] = None
    synthesis_cost_usd: Annotated[float | None, Field()] = None
    dag_cost_usd: Annotated[float | None, Field()] = None

    # Injected by System 2 Reliability Tracker in worker.py
    global_context_vars: Annotated[dict[str, Any] | None, Field()] = None
    execution_summary: Annotated[dict[str, Any] | None, Field()] = None
    step_metrics: Annotated[dict[str, Any] | None, Field()] = None

    # Injected by output quality scanner
    has_slop_warning: Annotated[bool | None, Field()] = None


class SynthesisStepDataDTO(StepExecutionEnvelope):
    """Schema to safely extract required synthesis flags from generic step outputs.

    Attributes:
        reasoning_trace: Captured step-specific agent reasoning parameters.
        token_usage: Usage statistics for this execution iteration.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    reasoning_trace: Annotated[ReasoningTrace | None, Field()] = None
    token_usage: Annotated[TokenUsage, Field()] = Field(
        default_factory=lambda: TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
    )
