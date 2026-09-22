"""Engine Data Transfer Objects.

Provides the strict Pydantic V2 schemas for engine execution.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Annotated, Any

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.matrix import ContrastivePairDTO, TheoryGrounding
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.state import TraceEvent

if TYPE_CHECKING:
    from backend_v2.services.orchestrator.strategies.base import StrategyContext

__all__ = [
    "ContrastivePairDTO",
    "EngineExecutionRequest",
    "EngineExecutionResult",
    "FlattenedAtom",
    "MatrixEvaluationContext",
]


from backend_v2.models.dtos.flattened_atom import FlattenedAtom as FlattenedAtom


class MatrixEvaluationContext(BaseModel):
    """Context for matrix evaluation.

    Attributes:
        theory_grounding: The theory grounding applied to the matrix.
        matrix_objective: The objective of the matrix.
        allow_contextual_override: Whether contextual override is allowed.
        matrix_assertions: Raw matrix constraints.
    """

    theory_grounding: Annotated[
        TheoryGrounding | None, Field(default=None, description="The theory grounding applied to the matrix.")
    ] = None
    matrix_objective: Annotated[str | None, Field(default=None, description="The objective of the matrix.")] = None
    allow_contextual_override: Annotated[
        bool, Field(default=False, description="Whether contextual override is allowed.")
    ] = False
    matrix_assertions: Annotated[
        list[FlattenedAtom] | None, Field(default=None, description="Raw matrix constraints.")
    ] = None

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)


class EngineExecutionRequest(BaseModel):
    """Request DTO for execution engines.

    Carries all required context, rules, and telemetry hooks for engine evaluation.

    Attributes:
        bound_client: The initialized LLM client.
        compiled_schema: Forward compatibility for SynthesisEngine schema.
        hydrated_messages: Strongly typed messages for SynthesisEngine / PromptEngine.
        system_prompt: The compiled system prompt.
        step: The step configuration.
        context: Immutable strategy context.
        global_source_text: The full source document text.
        target_locale: The target locale for the evaluation.
        semaphore: Concurrency limiter.
        running_event: Cancellation trigger.
        progress_callback: Progress reporting callback.
        trace_callback: Live telemetry flush callback.
        prompt_compiler: The prompt compiler instance.
        shuffled_atoms: The explicit matrix assertions for matrix evaluations.
        matrix_block_id: Optional ID of the matrix block for namespace isolation.
        matrix_context: Context for matrix evaluation.
    """

    bound_client: Annotated[LLMClient, Field(description="The initialized LLM client.")]
    compiled_schema: Annotated[
        type[BaseModel] | None, Field(default=None, description="Forward compatibility for SynthesisEngine schema.")
    ] = None
    hydrated_messages: Annotated[
        list[LLMMessageDTO] | None,
        Field(default=None, description="Strongly typed messages for SynthesisEngine / PromptEngine."),
    ] = None
    system_prompt: Annotated[str, Field(description="The compiled system prompt.")]
    step: Annotated[StepRule, Field(description="The step configuration.")]
    context: Annotated[StrategyContext, Field(description="Immutable strategy context.")]
    global_source_text: Annotated[str, Field(description="The full source document text.")]
    target_locale: Annotated[str | None, Field(default=None, description="The target locale for the evaluation.")] = (
        None
    )
    semaphore: Annotated[asyncio.Semaphore | None, Field(default=None, description="Concurrency limiter.")] = None
    running_event: Annotated[asyncio.Event | None, Field(default=None, description="Cancellation trigger.")] = None
    progress_callback: Annotated[
        Callable[[int, int], Awaitable[None]] | None, Field(default=None, description="Progress reporting callback.")
    ] = None
    trace_callback: Annotated[
        Callable[[TraceEvent], Awaitable[None]] | None,
        Field(default=None, description="Live telemetry flush callback."),
    ] = None
    prompt_compiler: Annotated[Any, Field(description="The prompt compiler instance.")]
    shuffled_atoms: Annotated[
        list[FlattenedAtom] | None,
        Field(default=None, description="The explicit matrix assertions for matrix evaluations."),
    ] = None
    matrix_block_id: Annotated[
        str | None, Field(default=None, description="Optional ID of the matrix block for namespace isolation.")
    ] = None
    matrix_context: Annotated[
        MatrixEvaluationContext | None, Field(default=None, description="Context for matrix evaluation.")
    ] = None

    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True, extra="forbid", frozen=True)

    @property
    def semaphore_cm(self) -> Any:
        """Context manager safely wrapping nullable semaphore with nullcontext.

        Returns:
            The semaphore or a nullcontext context manager.
        """
        import contextlib

        return self.semaphore if self.semaphore is not None else contextlib.nullcontext()


class EngineExecutionResult(BaseModel):
    """Result DTO for execution engines.

    Carries the final projected atom results and their hydrated references.

    Attributes:
        results: Projected atom results.
        hydrated_references: Hydrated atom references.
        synthesis_output: Optional typed structured synthesis DTO or dictionary.
        trace_events: Trace events recorded during engine execution.
        usage: Aggregated token usage for the engine execution.
    """

    results: Annotated[list[AtomResultDTO], Field(description="Projected atom results.")]
    hydrated_references: Annotated[dict[str, HydratedAtomDTO], Field(description="Hydrated atom references.")]
    synthesis_output: Annotated[
        BaseModel | None,
        Field(
            default=None,
            description="Typed structured synthesis DTO (specifically RenderedSynthesisCache).",
        ),
    ] = None
    trace_events: Annotated[
        list[TraceEvent], Field(default_factory=list, description="Trace events recorded during engine execution.")
    ] = Field(default_factory=list)
    usage: Annotated[
        TokenUsage | None, Field(default=None, description="Aggregated token usage for the engine execution.")
    ] = None

    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True, extra="forbid", frozen=True)
