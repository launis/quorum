"""Step telemetry DTO.

Defines immutable Pydantic V2 schema for step-level telemetry entries
accumulated during execution trace evaluation in execution worker.
"""

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase


class StepTelemetryEntryDTO(V2CoreBase):
    """Immutable telemetry entry for an execution step.

    Attributes:
        model_strategy: Strategy name used for LLM invocation.
        physical_model: Concrete provider model identifier if reported.
        system_fingerprint: System fingerprint returned by model backend.
        prompt_tokens: Number of prompt/input tokens consumed.
        completion_tokens: Number of completion/output tokens consumed.
        cached_tokens: Number of cached prompt tokens reused.
        reasoning_tokens: Number of reasoning/thinking tokens consumed.
        cost_usd: Total monetary cost incurred in USD.
        chunk_count: Number of chunks or batched sub-steps processed.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    model_strategy: Annotated[str, Field(description="Strategy name used for LLM invocation")]
    physical_model: Annotated[str | None, Field(default=None, description="Concrete provider model identifier")] = None
    system_fingerprint: Annotated[
        str | None, Field(default=None, description="System fingerprint returned by backend")
    ] = None
    prompt_tokens: Annotated[int, Field(default=0, ge=0, description="Prompt tokens consumed")] = 0
    completion_tokens: Annotated[int, Field(default=0, ge=0, description="Completion tokens consumed")] = 0
    cached_tokens: Annotated[int, Field(default=0, ge=0, description="Cached tokens reused")] = 0
    reasoning_tokens: Annotated[int, Field(default=0, ge=0, description="Reasoning tokens consumed")] = 0
    cost_usd: Annotated[float, Field(default=0.0, ge=0.0, description="Monetary cost in USD")] = 0.0
    chunk_count: Annotated[int, Field(default=0, ge=0, description="Number of chunks processed")] = 0
