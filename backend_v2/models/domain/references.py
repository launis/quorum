"""Domain models for References hook."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

_dict_adapter = TypeAdapter(dict[str, Any])


class ReferencesInputsDTO:
    """Strict schema for inputs destined for reference generation.

    By utilizing a TypeAdapter wrapper (RootModel is broken in Python 3.14),
    we strictly enforce that the incoming state payload is explicitly a dictionary
    before any iterative logic executes, satisfying the Phase 9 Zero-Compromise mandate.
    """

    def __init__(self, root: dict[str, Any]) -> None:
        self.root = root

    @classmethod
    def model_validate(cls, data: Any) -> ReferencesInputsDTO:
        """Validate using strict Pydantic TypeAdapter."""
        validated = _dict_adapter.validate_python(data)
        return cls(root=validated)


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


class BibliographyResultDTO(BaseModel):
    """Strict payload for injecting bibliography into state."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    references: list[ReferenceDTO]
