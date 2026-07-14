"""Execution trace DTO schemas."""

from typing import Any

from pydantic import ConfigDict

from backend_v2.models.dtos.base import BaseDTO


class TraceMatrixPayloadDTO(BaseDTO):
    """Strict hydration schema for extracting matrix payloads from execution trace."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    raw_score: float | None = None
    normalized_score: float | None = None
    justification: str | None = None
    level_breakdown: dict[str, Any] | None = None
    extensions: dict[str, Any] | None = None
    evaluated_atoms: dict[str, bool | str] | None = None
    xai_log: dict[str, Any] | None = None
    allowed_extensions: list[str] | None = None


class TraceScoringPayloadDTO(BaseDTO):
    """Strict hydration schema for extracting scoring results in BlueprintTransformer."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    total_score: float | None = None
    final_score: float | None = None
    normalized_score: float | None = None
    penalties_applied: list[Any] | None = None
    aggregation_status: str | None = None
