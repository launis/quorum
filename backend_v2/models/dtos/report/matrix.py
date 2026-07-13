"""Matrix models and trace extractors."""

from typing import Annotated, Any

from pydantic import ConfigDict, Field

from backend_v2.models.dtos.base import BaseDTO


class MatrixFieldsMixin(BaseDTO):
    """Mixin capturing typical automated scoring assessment outcomes across matrices."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    justification: str | None = None
    normalized_score: float | None = None
    raw_score: float | None = None
    evaluated_atoms: dict[str, bool | str] | None = None
    extensions: dict[str, str] | None = None
    level_breakdown: dict[str, dict[str, int]] | None = None
    xai_log: dict[str, Any] | None = None


class MatrixObservabilityItem(BaseDTO):
    """Individual dimension tracking diagnostic item."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    normalized_score: float = 0.0
    justification: str = ""


class MatrixObservabilityDTO(BaseDTO):
    """Securely transmits only essential counts to prevent token explosions."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    true_atoms_count: Annotated[int, Field(description="Total number of true evaluation atoms.")] = 0
    false_atoms_count: Annotated[int, Field(description="Total number of false evaluation atoms.")] = 0
    matrices: Annotated[dict[str, MatrixObservabilityItem], Field(default_factory=dict)]


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
