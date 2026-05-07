"""Synthesis Hook Domain Models.

Provides strict Pydantic V2 validation schemas for the synthesis pipeline
to eliminate legacy dictionary-based parsing.
"""

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.state import StepExecutionEnvelope, StepOutputDTO


class SynthesisMetadataDTO(V2CoreBase):
    """Strict schema for execution metadata used during synthesis."""

    target_locale: str = Field(..., min_length=1)
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    step_results: list[StepOutputDTO] = Field(default_factory=list)
    profile_id: str | None = Field(default=None)
    target_profile_id: str | None = Field(default=None)
    matrix_sampling_strategy: int | None = Field(default=None)

    # Injected by worker.py during execution trace iterations for token usage tracking
    total_tokens: int | None = Field(default=None)
    prompt_tokens: int | None = Field(default=None)
    completion_tokens: int | None = Field(default=None)
    cost_estimate: float | None = Field(default=None)


class SynthesisStepDataDTO(StepExecutionEnvelope):
    """Schema to safely extract required synthesis flags from generic step outputs."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    reasoning_trace: ReasoningTrace | None = Field(default=None)
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
