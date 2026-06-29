import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator

from backend_v2.models.core_base import V2CoreBase

logger = logging.getLogger(__name__)


class SourceDocumentContext(BaseModel):
    """Typed context representing source document text and metadata during validation."""

    opaque_id: str = Field(description="Opaque Stripe ID or static input key of the source document.")
    text_content: str = Field(description="The extracted raw text content of the document.")
    display_name: str = Field(description="User-facing display name or label of the document.")
    model_config = ConfigDict(frozen=True, extra="forbid")


class LLMExtractedQuote(BaseModel):
    """Schema for quotes extracted by the LLM, tracking their resolved document ID."""

    text: str = Field(description="Tarkka lainaus tekstistä")
    source_id: str | None = Field(default=None, description="Auto-resolved document ID")
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
            # Safety bypass if context is missing (e.g. tests or internal system calls)
            return data

        alias_map = info.context.get("alias_map", {})
        if not alias_map:
            return data

        if source_id.startswith("src_"):
            if source_id in alias_map:
                data["source_id"] = alias_map[source_id]
            else:
                msg = f"Hallucinated source_id '{source_id}'. Must be one of valid src_X keys: {list(alias_map.keys())}"
                logger.warning(f"Pydantic Validation Error: {msg}")
                raise ValueError(msg)

        return data


class QuoteEvidenceDTO(V2CoreBase):
    """Evidence DTO linking a quote to its resolved database ID."""

    quote_text: str
    source_id: str | None = Field(
        default=None,
        pattern=r"^([a-z0-9_]{2,30}|[a-z]{2,5}_[a-fA-F0-9]{16,32})$",
        description="Resolved document Opaque ID or input key.",
    )
    display_name: str | None = None
