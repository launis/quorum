"""Execution trace DTO schemas."""

from typing import Annotated, Any

from pydantic import ConfigDict, Field

from backend_v2.models.dtos.base import BaseDTO


class TraceMatrixPayloadDTO(BaseDTO):
    """Strict hydration schema for extracting matrix payloads from execution trace."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    raw_score: Annotated[float | None, Field(description="The raw score calculated")] = None
    normalized_score: Annotated[float | None, Field(description="The normalized score")] = None
    justification: Annotated[str | None, Field(description="The justification text")] = None
    level_breakdown: Annotated[dict[str, Any] | None, Field(description="Breakdown of levels")] = None
    extensions: Annotated[dict[str, Any] | None, Field(description="Additional extensions")] = None
    evaluated_atoms: Annotated[dict[str, bool | str] | None, Field(description="Evaluated atoms mapping")] = None
    xai_log: Annotated[dict[str, Any] | None, Field(description="XAI audit log")] = None
    allowed_extensions: Annotated[list[str] | None, Field(description="List of allowed extensions")] = None


class TraceScoringPayloadDTO(BaseDTO):
    """Strict hydration schema for extracting scoring results in BlueprintTransformer."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    total_score: Annotated[float | None, Field(description="The total score")] = None
    final_score: Annotated[float | None, Field(description="The final computed score")] = None
    normalized_score: Annotated[float | None, Field(description="The normalized score projection")] = None
    penalties_applied: Annotated[list[Any] | None, Field(description="List of applied penalties")] = None
    aggregation_status: Annotated[str | None, Field(description="Status of aggregation")] = None
