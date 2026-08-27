import logging
import re
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.utils.alias_engine import AliasEngine

logger = logging.getLogger(__name__)


class SourceDocumentContext(BaseModel):
    """Typed context representing source document text and metadata during validation."""

    opaque_id: Annotated[str, Field(description="Opaque Stripe ID or static input key of the source document.")]
    text_content: Annotated[str, Field(description="The extracted raw text content of the document.")]
    display_name: Annotated[str, Field(description="User-facing display name or label of the document.")]
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


class BaseSourceId(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Base class to force source_id to appear first in the JSON schema."""

    source_id: Annotated[str | None, Field(default=None, description="Auto-resolved document ID (e.g. doc0, a1)")]


class LLMExtractedQuote(BaseSourceId):
    """Schema for quotes extracted by the LLM, tracking their resolved document ID."""

    text: Annotated[str, Field(description="Tarkka lainaus tekstistä")]
    model_config = ConfigDict(strict=True, extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def resolve_source_id(cls, data: Any, info: ValidationInfo) -> Any:
        if not isinstance(data, dict):
            return data

        source_id = data.get("source_id")
        if not source_id:
            return data

        if info.context is None:
            raise RuntimeError("ValidationInfo.context is missing. Cannot resolve source_id without context.")

        alias_map = info.context.get("alias_map", {})
        allowed_dynamic_keys = info.context.get("allowed_dynamic_keys", [])
        allowed_mcp_prefixes = info.context.get("allowed_mcp_prefixes", [])

        if not alias_map and not allowed_dynamic_keys and not allowed_mcp_prefixes:
            return data

        engine = AliasEngine(alias_map=alias_map)

        if not engine.is_valid_source_id(source_id, allowed_dynamic_keys, allowed_mcp_prefixes):
            msg = f"Hallucinated source_id '{source_id}'. Must be one of valid keys: {list(alias_map.keys())}"
            logger.warning(f"[SYSTEM] | backend_v2.models.dtos.quote_evidence | Pydantic Validation Error: {msg}")
            raise ValueError(msg)

        resolved = engine.resolve_alias(source_id)
        if resolved:
            data["source_id"] = resolved

        return data


class QuoteEvidenceDTO(V2CoreBase):
    """Headless DTO for storing quote evidence with strict deterministic alias resolution.

    Attributes:
        quote: The exact text of the quote.
        verified_source_ids: Resolved Opaque IDs.
        unverified_aliases: Aliases that could not be verified.
        is_verified: True if there are verified aliases and no unverified aliases.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    quote: str = Field(..., description="The exact text of the quote.")
    verified_source_ids: list[str] = Field(default=[], description="Resolved Opaque IDs.")
    unverified_aliases: list[str] = Field(default=[], description="Aliases that could not be verified.")
    is_verified: bool = Field(
        default=False, description="True if there are verified aliases and no unverified aliases."
    )
    source_alias: list[str] | str | None = Field(default=None, exclude=True)

    @model_validator(mode="before")
    @classmethod
    def resolve_and_verify_aliases(cls, data: Any, info: ValidationInfo) -> Any:
        if not isinstance(data, dict):
            return data

        if info.context is None:
            if "verified_source_ids" in data or "unverified_aliases" in data:
                return data
            raise RuntimeError("ValidationInfo.context is missing. Cannot resolve aliases without context.")

        registry = info.context.get("alias_registry", {})

        # Original input could be in 'source_alias' string or list
        raw_aliases = data.get("source_alias")
        if raw_aliases is None:
            raw_aliases = []
        elif isinstance(raw_aliases, str):
            if not raw_aliases.strip():
                raw_aliases = []
            else:
                raw_aliases = re.findall(r"DOC-\d+", raw_aliases) or [raw_aliases]
        elif isinstance(raw_aliases, list):
            extracted = []
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

        verified = []
        unverified = []

        for alias in raw_aliases:
            opaque_id = registry.get(alias)
            if opaque_id is not None:
                verified.append(opaque_id)
            else:
                unverified.append(alias)

        data["verified_source_ids"] = verified
        data["unverified_aliases"] = unverified
        data["is_verified"] = len(unverified) == 0

        # Remove the raw source_alias as it is replaced by verified/unverified lists
        if "source_alias" in data:
            del data["source_alias"]

        return data
