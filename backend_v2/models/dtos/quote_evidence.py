"""Quote evidence DTOs and alias validation models."""

import logging
import re
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.utils.alias_engine import AliasEngine

logger = logging.getLogger(__name__)


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

    text: Annotated[str, Field(description="Tarkka lainaus tekstistä")]

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
        try:
            d = dict(data)
        except TypeError, ValueError:
            return data

        source_id = d.get("source_id")
        if not source_id:
            return d

        if info.context is None:
            return d

        try:
            alias_map = info.context.get("alias_map") or {}
            allowed_dynamic_keys = info.context.get("allowed_dynamic_keys") or []
            allowed_mcp_prefixes = info.context.get("allowed_mcp_prefixes") or []
        except AttributeError, TypeError:
            return d

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

    quote: str = Field(..., description="The exact text of the quote.")
    verified_source_ids: list[str] = Field(default_factory=list, description="Resolved Opaque IDs.")
    unverified_aliases: list[str] = Field(default_factory=list, description="Aliases that could not be verified.")
    is_verified: bool = Field(
        default=False, description="True if there are verified aliases and no unverified aliases."
    )
    source_alias: list[str] | str | None = Field(default=None, exclude=True)

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
        """
        try:
            d = dict(data)
        except TypeError, ValueError:
            return data

        if info.context is None:
            if "verified_source_ids" in d or "unverified_aliases" in d:
                return d
            raise RuntimeError("ValidationInfo.context is missing. Cannot resolve aliases without context.")

        try:
            registry = info.context.get("alias_registry") or {}
        except AttributeError, TypeError:
            registry = {}

        raw_aliases = d.get("source_alias")
        if raw_aliases is None:
            raw_aliases = []
        elif isinstance(raw_aliases, str):
            if not raw_aliases.strip():
                raw_aliases = []
            else:
                raw_aliases = re.findall(r"DOC-\d+", raw_aliases) or [raw_aliases]
        elif isinstance(raw_aliases, list):
            extracted: list[str] = []
            for item in raw_aliases:
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
            try:
                opaque_id = registry.get(alias)
            except AttributeError, TypeError:
                opaque_id = None

            if opaque_id is not None:
                verified.append(str(opaque_id))
            else:
                unverified.append(str(alias))

        d["verified_source_ids"] = verified
        d["unverified_aliases"] = unverified
        d["is_verified"] = len(unverified) == 0

        if "source_alias" in d:
            del d["source_alias"]

        return d
