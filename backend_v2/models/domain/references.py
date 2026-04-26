"""Domain models for References hook."""

from typing import Any

from pydantic import BaseModel, ConfigDict, RootModel


class ReferenceDTO(BaseModel):
    """Domain model for a single reference citation."""

    model_config = ConfigDict(frozen=True)

    source_id: str
    title: str
    snippet: str
    url: str | None = None


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

    model_config = ConfigDict(frozen=True)

    references: list[ReferenceDTO]
