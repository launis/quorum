"""Domain models for References hook."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, RootModel


class ReferenceDTO(BaseModel):
    """Domain model for a single reference citation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    snippet: str = Field(..., min_length=1)
    url: str | None = Field(default=None)


class ReferencesContextDTO(BaseModel):
    """Schema for safely parsing global_context_vars in Reference hook."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    step_coach: dict[str, Any] | None = None
    knowledge_base: dict[str, Any] | None = None


class ReferencesInputsDTO(RootModel[dict[str, Any]]):
    """Strict schema for inputs destined for reference generation."""

    model_config = ConfigDict(frozen=True)


class BibliographyResultDTO(BaseModel):
    """Strict payload for injecting bibliography into state."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    references: list[ReferenceDTO]
