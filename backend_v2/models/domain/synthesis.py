"""Synthesis Hook Domain Models.

Provides strict Pydantic V2 validation schemas for the synthesis pipeline
to eliminate legacy dictionary-based parsing.
"""

from __future__ import annotations

from typing import Any

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

    target_locale: str = Field(..., min_length=1)
    token_usage: TokenUsage = Field(
        default_factory=lambda: TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
    )
    step_results: list[StepOutputDTO] = Field(default_factory=list)
    profile_id: str | None = Field(default=None)
    target_profile_id: str | None = Field(default=None)
    matrix_sampling_strategy: int | None = Field(default=None)
    workflow_version: int | None = Field(default=None)

    # Injected by worker.py during execution trace iterations for token usage tracking
    total_tokens: int | None = Field(default=None)
    prompt_tokens: int | None = Field(default=None)
    completion_tokens: int | None = Field(default=None)
    cost_estimate: float | None = Field(default=None)
    synthesis_cost_usd: float | None = Field(default=None)
    dag_cost_usd: float | None = Field(default=None)

    # Injected by System 2 Reliability Tracker in worker.py
    global_context_vars: dict[str, Any] | None = Field(default=None)
    execution_summary: dict[str, Any] | None = Field(default=None)
    step_metrics: dict[str, Any] | None = Field(default=None)


class SynthesisStepDataDTO(StepExecutionEnvelope):
    """Schema to safely extract required synthesis flags from generic step outputs.

    Attributes:
        reasoning_trace: Captured step-specific agent reasoning parameters.
        token_usage: Usage statistics for this execution iteration.
    """

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    reasoning_trace: ReasoningTrace | None = Field(default=None)
    token_usage: TokenUsage = Field(
        default_factory=lambda: TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
    )
