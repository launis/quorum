"""Domain models for References hook."""

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase


class ReferencesInputsDTO(V2CoreBase):
    """Strict schema for inputs destined for reference generation.

    Attributes:
        root: The underlying dictionary containing the raw reference payload data.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    root: Annotated[dict[str, str | int | float | bool | list[str]], Field(default_factory=dict)]


class ReferenceDTO(V2CoreBase):
    """Domain model for a single reference citation.

    Attributes:
        source_id: Unique identifier string pointing to the original source.
        title: Title of the reference.
        snippet: Selected excerpt supporting the citation.
        url: Optional URL pointing to the external source location.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    source_id: Annotated[str, Field(min_length=1)]
    title: Annotated[str, Field(min_length=1)]
    snippet: Annotated[str, Field(min_length=1)]
    url: str | None = None


class ReferencesContextDTO(V2CoreBase):
    """Schema for safely parsing global_context_vars in Reference hook.

    Attributes:
        step_coach: Optional scalar dictionary configuration for step coaching logic.
        knowledge_base: Optional scalar dictionary configuration for KB interactions.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    step_coach: Annotated[dict[str, str | int | float | bool | list[str]] | None, Field(default=None)] = None
    knowledge_base: Annotated[dict[str, str | int | float | bool | list[str]] | None, Field(default=None)] = None


class BibliographyResultDTO(V2CoreBase):
    """Strict payload for injecting bibliography into state.

    Attributes:
        references: List of explicit ReferenceDTO objects forming the bibliography.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    references: list[ReferenceDTO]
