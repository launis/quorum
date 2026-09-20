"""Step Output DTO for execution traces and domain inputs."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase

__all__ = ["StepOutputDTO"]


class StepOutputDTO(V2CoreBase):
    """Strict execution trace payload format."""

    model_config = ConfigDict(strict=True, extra="forbid")

    step_id: str = Field(description="The opaque DAG Step ID.")
    block_id: str = Field(description="The opaque PromptBlock ID.")
    data_type: Literal["text", "matrix", "unknown"] = Field(
        description="Inferred or explicitly parsed data type (e.g. matrix, text)."
    )
    payload: Any = Field(description="The actual data payload.")
