"""Domain models for Knowledge Base, Banned Phrases, and Prompt Templates."""

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.dtos.base import BaseDTO

__all__ = [
    "BannedPhrase",
    "Claim",
    "ClaimCreateDTO",
    "Concept",
    "ConceptCreateDTO",
    "PromptTemplateDTO",
    "Reference",
    "ReferenceCreateDTO",
]


class ConceptCreateDTO(BaseDTO):
    """DTO for adding a concept to the knowledge base.

    Attributes:
        name: Concept name.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    name: Annotated[str, Field(min_length=1, description="Concept name")]


class ReferenceCreateDTO(BaseDTO):
    """DTO for adding a reference to the knowledge base.

    Attributes:
        name: Reference name.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    name: Annotated[str, Field(min_length=1, description="Reference name")]


class ClaimCreateDTO(BaseDTO):
    """DTO for adding a claim to the knowledge base.

    Attributes:
        name: Claim name.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    name: Annotated[str, Field(min_length=1, description="Claim name")]


class BannedPhrase(V2CoreBase):
    """Model for a single banned phrase.

    Attributes:
        id: Unique ID for the banned phrase.
        phrase: The banned phrase string.
        language: Language code.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[str, Field(min_length=1, description="Unique ID for the banned phrase.")]
    phrase: Annotated[str, Field(min_length=1, description="The banned phrase string.")]
    language: Annotated[str, Field(default="en", description="Language code.")]


class PromptTemplateDTO(V2CoreBase):
    """Model for compiled system and user prompt template.

    Attributes:
        system: System prompt instruction string.
        user: User prompt instruction string.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    system: Annotated[str, Field(description="System prompt instruction string.")]
    user: Annotated[str, Field(description="User prompt instruction string.")]


class Concept(V2CoreBase):
    """Model for a knowledge base concept.

    Attributes:
        id: Unique concept ID.
        name: Optional concept name.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[str, Field(min_length=1, description="Unique concept ID.")]
    name: Annotated[str | None, Field(default=None, description="Optional concept name.")] = None


class Reference(V2CoreBase):
    """Model for a knowledge base reference.

    Attributes:
        id: Unique reference ID.
        name: Optional reference name.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[str, Field(min_length=1, description="Unique reference ID.")]
    name: Annotated[str | None, Field(default=None, description="Optional reference name.")] = None


class Claim(V2CoreBase):
    """Model for a knowledge base claim.

    Attributes:
        id: Unique claim ID.
        name: Optional claim name.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[str, Field(min_length=1, description="Unique claim ID.")]
    name: Annotated[str | None, Field(default=None, description="Optional claim name.")] = None
