"""Sensor validation context and ensemble call result DTOs for extractive sensor services."""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import AtomEvaluationResultDTO

__all__ = ["EnsembleCallResultDTO", "SensorValidationContextDTO"]


class SensorValidationContextDTO(V2CoreBase):
    """Encapsulates context parameters for sensor evaluation and anchor validation.

    Attributes:
        sub_task: Subtask identifier or category.
        execution_id: Parent execution ID.
        step_id: Current step ID.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    sub_task: Annotated[str, Field(description="Subtask identifier or category")]
    execution_id: Annotated[str | None, Field(default=None, description="Parent execution ID")] = None
    step_id: Annotated[str | None, Field(default=None, description="Current step ID")] = None


class EnsembleCallResultDTO(V2CoreBase):
    """Encapsulates the result of a single ensemble call in Best-of-3 evaluation.

    Attributes:
        evaluations: Mapping of atom ID to evaluation result, or None if transient failure occurred.
        usage: Token usage incurred by this call.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    evaluations: Annotated[
        dict[str, AtomEvaluationResultDTO] | None,
        Field(default=None, description="Atom evaluation results mapping, or None if transient failure"),
    ] = None
    usage: Annotated[
        TokenUsage,
        Field(
            default_factory=lambda: TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            description="Token usage for the call",
        ),
    ]
