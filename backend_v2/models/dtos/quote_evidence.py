from pydantic import BaseModel, ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase


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


class QuoteEvidenceDTO(V2CoreBase):
    """Evidence DTO linking a quote to its resolved database ID."""

    quote_text: str
    source_id: str | None = Field(
        default=None,
        pattern=r"^([a-z0-9_]{2,30}|[a-z]{2,5}_[a-fA-F0-9]{16,32})$",
        description="Resolved document Opaque ID or input key.",
    )
    display_name: str | None = None
