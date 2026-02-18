
from datetime import datetime
from typing import Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

class KBConcept(BaseModel):
    id: str = Field(..., description="Unique concept ID")
    type: Literal["concept"] = Field("concept", description="Discriminator type")
    term: str = Field(..., description="The concept term")
    definition: str = Field(..., description="The concept definition")
    source_file: str = Field(..., description="Origin filename")
    job_id: str | None = Field(None, description="Ingestion job ID")
    ingested_at: str | datetime | None = Field(None, description="Ingestion timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "term", "definition", "source_file")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

class KBClaim(BaseModel):
    id: str = Field(..., description="Unique claim ID")
    type: Literal["claim"] = Field("claim", description="Discriminator type")
    term: str = Field(..., description="Associated term or short key")
    definition: str = Field(..., description="The claim statement text")
    source_file: str = Field(..., description="Origin filename")
    job_id: str | None = Field(None, description="Ingestion job ID")
    ingested_at: str | datetime | None = Field(None, description="Ingestion timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "term", "definition", "source_file")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

class KBReference(BaseModel):
    id: str = Field(..., description="Unique reference ID")
    type: Literal["reference"] = Field("reference", description="Discriminator type")
    definition: str = Field(..., description="Full bibliographic reference")
    short_citation: str | None = Field(None, description="Short citation (e.g., Author 2023)")
    source_file: str = Field(..., description="Origin filename")
    job_id: str | None = Field(None, description="Ingestion job ID")
    ingested_at: str | datetime | None = Field(None, description="Ingestion timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "definition", "source_file")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

KBItem = Union[KBConcept, KBClaim, KBReference]
