from pydantic import BaseModel, ConfigDict, Field

from backend_v2.models.enums import XaiExtensionType


class OutputProfileConfig(BaseModel):
    """Configuration for Output Profile extensions."""

    visible_extensions: list[XaiExtensionType]

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class LightweightMatrixOutput(BaseModel):
    """Strict schema for the Lightweight Matrix Output."""

    raw_score: float
    normalized_score: float = Field(ge=0.0, le=100.0)
    level_breakdown: str
    justification: str
    evaluated_atoms: dict[str, bool]
    extensions: dict[XaiExtensionType, str]

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
