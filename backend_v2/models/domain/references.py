"""Domain models for References hook."""

from typing import Annotated, Any

from pydantic import ConfigDict, Field, TypeAdapter

from backend_v2.models.core_base import V2CoreBase

_dict_adapter = TypeAdapter(dict[str, Any])


class ReferencesInputsDTO:
    """Strict schema for inputs destined for reference generation.

    By utilizing a TypeAdapter wrapper (RootModel is broken in Python 3.14),
    we strictly enforce that the incoming state payload is explicitly a dictionary
    before any iterative logic executes, satisfying the Phase 9 Zero-Compromise mandate.

    Attributes:
        root: The underlying dictionary containing the raw reference payload data.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    def __init__(self, root: dict[str, Any]) -> None:
        """Initialize the DTO with the underlying dictionary.

        Args:
            root: The raw reference payload data.
        """
        self.root = root

    @classmethod
    def model_validate(cls, data: Any) -> ReferencesInputsDTO:
        """Validate using strict Pydantic TypeAdapter.

        Args:
            data: Arbitrary input data to validate.

        Returns:
            A validated ReferencesInputsDTO.

        Raises:
            ValidationError: If validation fails.
        """
        validated = _dict_adapter.validate_python(data)
        return cls(root=validated)


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
        step_coach: Optional generic dictionary configuration for step coaching logic.
        knowledge_base: Optional generic dictionary configuration for KB interactions.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    step_coach: dict[str, Any] | None = None
    knowledge_base: dict[str, Any] | None = None


class BibliographyResultDTO(V2CoreBase):
    """Strict payload for injecting bibliography into state.

    Attributes:
        references: List of explicit ReferenceDTO objects forming the bibliography.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    references: list[ReferenceDTO]
