"""Quote evidence DTOs and alias validation models."""

import logging
import re
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.prompts.common import DESC_EXACT_QUOTE_TEXT
from backend_v2.utils.alias_engine import AliasEngine

logger = logging.getLogger(__name__)

__all__ = [
    "BaseSourceId",
    "GateMatchResultDTO",
    "LLMExtractedQuote",
    "QuoteEvidenceDTO",
    "SourceDocumentContext",
]


class GateMatchResultDTO(BaseModel):
    """Result of lexical gate matching containing verification status and character boundaries.

    Attributes:
        is_valid: True if match was confirmed within gate tolerances.
        start_idx: Starting character index of matched segment in normalized corpus.
        end_idx: Ending character index of matched segment in normalized corpus.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    is_valid: Annotated[bool, Field(description="True if match was confirmed within gate tolerances.")]
    start_idx: Annotated[int, Field(description="Starting character index of matched segment in normalized corpus.")]
    end_idx: Annotated[int, Field(description="Ending character index of matched segment in normalized corpus.")]

    def __bool__(self) -> bool:
        """Returns True if the gate match was valid."""
        return self.is_valid


class SourceDocumentContext(BaseModel):
    """Typed context representing source document text and metadata during validation.

    Attributes:
        opaque_id: Opaque Stripe ID or static input key of the source document.
        text_content: The extracted raw text content of the document.
        display_name: User-facing display name or label of the document.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    opaque_id: Annotated[str, Field(description="Opaque Stripe ID or static input key of the source document.")]
    text_content: Annotated[str, Field(description="The extracted raw text content of the document.")]
    display_name: Annotated[str, Field(description="User-facing display name or label of the document.")]


class BaseSourceId(BaseModel):
    """Base class to force source_id to appear first in the JSON schema.

    Attributes:
        source_id: Auto-resolved document ID (e.g. doc0, a1).
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    source_id: Annotated[str | None, Field(default=None, description="Auto-resolved document ID (e.g. doc0, a1)")] = (
        None
    )


class LLMExtractedQuote(BaseSourceId):
    """Schema for quotes extracted by the LLM, tracking their resolved document ID.

    Attributes:
        text: Exact extracted quote from source text.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    text: Annotated[str, Field(description=DESC_EXACT_QUOTE_TEXT)]

    @model_validator(mode="before")
    @classmethod
    def resolve_source_id(cls, data: Any, info: ValidationInfo) -> Any:
        """Resolves source_id alias to its opaque identifier.

        Args:
            data: Raw input dictionary.
            info: Pydantic validation info containing alias context.

        Returns:
            Dictionary with resolved source_id.

        Raises:
            ValueError: If source_id is invalid or hallucinated.
        """
        if isinstance(data, BaseModel):
            d = data.model_dump()
        elif type(data) is dict:
            d = dict(data)
        else:
            raise ValueError(f"Expected dictionary input for validation, got {type(data).__name__}")

        source_id = None
        if "source_id" in d:
            source_id = d["source_id"]
        if not source_id or not isinstance(source_id, str):
            return d

        if info.context is None:
            return d

        alias_map = {}
        if "alias_map" in info.context:
            alias_map = info.context["alias_map"]
        allowed_dynamic_keys = []
        if "allowed_dynamic_keys" in info.context:
            allowed_dynamic_keys = info.context["allowed_dynamic_keys"]
        allowed_mcp_prefixes = []
        if "allowed_mcp_prefixes" in info.context:
            allowed_mcp_prefixes = info.context["allowed_mcp_prefixes"]

        if not alias_map and not allowed_dynamic_keys and not allowed_mcp_prefixes:
            return d

        engine = AliasEngine(alias_map=alias_map)

        if not engine.is_valid_source_id(source_id, allowed_dynamic_keys, allowed_mcp_prefixes):
            msg = f"Hallucinated source_id '{source_id}'. Must be one of valid keys: {list(alias_map.keys())}"
            logger.warning(f"[SYSTEM] | backend_v2.models.dtos.quote_evidence | Pydantic Validation Error: {msg}")
            raise ValueError(msg)

        resolved = engine.resolve_alias(source_id)
        if resolved:
            d["source_id"] = resolved

        return d


class QuoteEvidenceDTO(V2CoreBase):
    """Headless DTO for storing quote evidence with strict deterministic alias resolution.

    Attributes:
        quote: The exact text of the quote.
        verified_source_ids: Resolved Opaque IDs.
        unverified_aliases: Aliases that could not be verified.
        is_verified: True if there are verified aliases and no unverified aliases.
        source_alias: Excluded raw alias field.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    quote: Annotated[str, Field(description="The exact text of the quote.")]
    verified_source_ids: list[str] = Field(default_factory=list, description="Resolved Opaque IDs.")
    unverified_aliases: list[str] = Field(default_factory=list, description="Aliases that could not be verified.")
    is_verified: Annotated[
        bool, Field(default=False, description="True if there are verified aliases and no unverified aliases.")
    ] = False
    source_alias: Annotated[list[str] | str | None, Field(default=None, exclude=True)] = None

    def get_quotes(self) -> tuple[str, ...]:
        """Extracts available quotes as an immutable tuple without reflection.

        Returns:
            Immutable tuple containing the quote string if non-empty, or an empty tuple.
        """
        if self.quote and self.quote.strip():
            return (self.quote,)
        return ()

    @model_validator(mode="before")
    @classmethod
    def resolve_and_verify_aliases(cls, data: Any, info: ValidationInfo) -> Any:
        """Resolves and verifies source document aliases against the context registry.

        Args:
            data: Raw input dictionary.
            info: Pydantic validation info containing alias registry context.

        Returns:
            Dictionary with verified and unverified source aliases.

        Raises:
            RuntimeError: If validation context is missing when source aliases are provided.
            ValueError: If input data cannot be parsed as a dictionary.
        """
        if isinstance(data, BaseModel):
            d = data.model_dump()
        elif type(data) is dict:
            d = dict(data)
        else:
            raise ValueError(f"Expected dictionary input for validation, got {type(data).__name__}")

        has_source_alias = "source_alias" in d and d["source_alias"] is not None
        if info.context is None:
            if has_source_alias and not ("verified_source_ids" in d or "unverified_aliases" in d):
                raise RuntimeError("ValidationInfo.context is missing. Cannot resolve aliases without context.")
            return d

        registry = {}
        if "alias_registry" in info.context:
            registry = info.context["alias_registry"]

        raw_aliases: list[str] = []
        raw_input = None
        if "source_alias" in d:
            raw_input = d["source_alias"]
        if isinstance(raw_input, str):
            if raw_input.strip():
                matches = re.findall(r"DOC-\d+", raw_input)
                if matches:
                    raw_aliases = matches
                else:
                    raw_aliases = [raw_input]
        elif isinstance(raw_input, list):
            extracted: list[str] = []
            for item in raw_input:
                if isinstance(item, str):
                    matches = re.findall(r"DOC-\d+", item)
                    if matches:
                        extracted.extend(matches)
                    else:
                        extracted.append(item)
                else:
                    extracted.append(str(item))
            raw_aliases = extracted

        verified: list[str] = []
        unverified: list[str] = []

        for alias in raw_aliases:
            if registry is not None and alias in registry:
                verified.append(str(registry[alias]))
            else:
                unverified.append(str(alias))

        d["verified_source_ids"] = verified
        d["unverified_aliases"] = unverified
        d["is_verified"] = len(unverified) == 0

        if "source_alias" in d:
            del d["source_alias"]

        return d
