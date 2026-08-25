"""Engine Data Transfer Objects.

Provides the strict Pydantic V2 schemas for engine execution.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Annotated, Any

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import CausalEdge
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import AtomResultDTO, HydratedAtomDTO, StepRule, TheoryGrounding

if TYPE_CHECKING:
    from backend_v2.services.orchestrator.strategies.base import StrategyContext


class FlattenedAtom(BaseModel):
    """Strict Pydantic schema for individual shuffled items (No Naked Dicts rule).

    Attributes:
        atom_id: Opaque hashed ID for the extracted atom.
        question: The text content evaluated blindly.
        extraction_rule: The specific validation rule.
        anchor_target: Semantic bounding box target.
        is_inverse: True if this is an inverse assertion.
        depends_on: Causal dependencies attached to this atom.
    """

    atom_id: Annotated[str, Field(description="Opaque hashed ID for the extracted atom.")]
    question: Annotated[str, Field(description="The text content evaluated blindly.")]
    extraction_rule: Annotated[str, Field(default="", description="The specific validation rule.")]
    anchor_target: Annotated[str, Field(default="", description="Semantic bounding box target.")]
    is_inverse: Annotated[bool, Field(default=False, description="True if this is an inverse assertion.")]
    depends_on: Annotated[
        tuple[CausalEdge, ...],
        Field(
            default_factory=tuple,
            description="Causal dependencies attached to this atom.",
        ),
    ]

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")


class MatrixEvaluationContext(BaseModel):
    """Context for matrix evaluation.

    Attributes:
        theory_grounding: The theory grounding applied to the matrix.
        matrix_objective: The objective of the matrix.
        allow_contextual_override: Whether contextual override is allowed.
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
        hydrated_messages: Forward compatibility for SynthesisEngine messages.
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
    """

    bound_client: LLMClient
    compiled_schema: type[BaseModel] | None
    hydrated_messages: list[dict[str, str]] | None
    system_prompt: str
    step: StepRule
    context: StrategyContext
    global_source_text: str
    target_locale: str | None
    semaphore: asyncio.Semaphore | None = None
    running_event: asyncio.Event | None = None
    progress_callback: Callable[[int, int], Awaitable[None]] | None = None
    trace_callback: Callable[[TraceEvent], Awaitable[None]] | None = None
    prompt_compiler: Any
    shuffled_atoms: list[FlattenedAtom] | None = None
    matrix_block_id: str | None = None
    matrix_context: Annotated[
        MatrixEvaluationContext | None, Field(default=None, description="Context for matrix evaluation")
    ] = None

    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True, extra="forbid", frozen=True)

    @property
    def semaphore_cm(self) -> Any:
        """Context manager safely wrapping nullable semaphore with nullcontext."""
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

    results: list[AtomResultDTO]
    hydrated_references: dict[str, HydratedAtomDTO]
    synthesis_output: Annotated[
        dict[str, Any] | BaseModel | None,
        Field(
            default=None,
            description="Typed structured synthesis DTO or dictionary (specifically RenderedSynthesisCache).",
        ),
    ] = None
    trace_events: list[TraceEvent] = Field(default_factory=list)
    usage: TokenUsage | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True, extra="forbid", frozen=True)
