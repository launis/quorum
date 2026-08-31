"""Domain models for Knowledge Base, Banned Phrases, and Prompt Templates."""

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase


class BannedPhrase(V2CoreBase):
    """Model for a single banned phrase."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[str, Field(min_length=1, description="Unique ID for the banned phrase.")]
    phrase: Annotated[str, Field(min_length=1, description="The banned phrase string.")]
    language: Annotated[str, Field(default="en", description="Language code.")]


class PromptTemplateDTO(V2CoreBase):
    """Model for compiled system and user prompt template."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    system: Annotated[str, Field(description="System prompt instruction string.")]
    user: Annotated[str, Field(description="User prompt instruction string.")]


class Concept(V2CoreBase):
    """Model for a knowledge base concept."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[str, Field(min_length=1, description="Unique concept ID.")]
    name: Annotated[str | None, Field(default=None, description="Optional concept name.")] = None


class Reference(V2CoreBase):
    """Model for a knowledge base reference."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[str, Field(min_length=1, description="Unique reference ID.")]
    name: Annotated[str | None, Field(default=None, description="Optional reference name.")] = None


class Claim(V2CoreBase):
    """Model for a knowledge base claim."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[str, Field(min_length=1, description="Unique claim ID.")]
    name: Annotated[str | None, Field(default=None, description="Optional claim name.")] = None
