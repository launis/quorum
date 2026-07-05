import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.utils.alias_engine import AliasEngine

logger = logging.getLogger(__name__)


class SourceDocumentContext(BaseModel):
    """Typed context representing source document text and metadata during validation."""

    opaque_id: str = Field(description="Opaque Stripe ID or static input key of the source document.")
    text_content: str = Field(description="The extracted raw text content of the document.")
    display_name: str = Field(description="User-facing display name or label of the document.")
    model_config = ConfigDict(frozen=True, extra="forbid")


class BaseSourceId(BaseModel):
    """Base class to force source_id to appear first in the JSON schema."""

    source_id: str | None = Field(default=None, description="Auto-resolved document ID (e.g. doc0, a1)")


class LLMExtractedQuote(BaseSourceId):
    """Schema for quotes extracted by the LLM, tracking their resolved document ID."""

    text: str = Field(description="Tarkka lainaus tekstistä")
    model_config = ConfigDict(extra="ignore")

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
        source_alias: A list of resolved Opaque IDs representing the source documents.
    """

    quote: str = Field(..., description="The exact text of the quote.")
    source_alias: list[str] = Field(
        default_factory=list, description="A list of resolved Opaque IDs representing the source documents."
    )

    @field_validator("source_alias", mode="before")
    @classmethod
    def parse_source_alias(cls, v: Any) -> list[str]:
        """Normalize raw strings like 'DOC-1, DOC-2' into a list of strings."""
        import re

        if isinstance(v, str):
            return re.findall(r"DOC-\d+", v)
        if isinstance(v, list):
            extracted = []
            for item in v:
                if isinstance(item, str):
                    matches = re.findall(r"DOC-\d+", item)
                    if matches:
                        extracted.extend(matches)
                    else:
                        extracted.append(item)
                else:
                    extracted.append(str(item))
            return extracted
        raise ValueError("source_alias must be a string or a list of strings")

    @field_validator("source_alias", mode="after")
    @classmethod
    def resolve_source_alias(cls, v: list[str], info: ValidationInfo) -> list[str]:
        """Resolve aliases to Opaque IDs using the alias_registry from context."""
        if info.context is None:
            raise RuntimeError("ValidationInfo.context is missing. Cannot resolve aliases without context.")

        registry = info.context.get("alias_registry", {})

        resolved = []
        for alias in v:
            opaque_id = registry.get(alias)
            if opaque_id is not None:
                resolved.append(opaque_id)
            else:
                resolved.append("OpaqueID.UNVERIFIED")

        return resolved
