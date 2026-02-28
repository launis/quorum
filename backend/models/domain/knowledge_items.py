import uuid
from datetime import datetime
from typing import Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class KBConcept(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique concept ID")
    slug: str | None = Field(default=None, description="Legacy human-readable identifier")
    type: Literal["concept"] = Field("concept", description="Discriminator type")
    term: str = Field(..., description="The concept term")
    definition: str = Field(..., description="The concept definition")
    source_file: str = Field(..., description="Origin filename")
    ingested_at: str | datetime | None = Field(None, description="Ingestion timestamp")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "term", "definition", "source_file")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class KBClaim(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique claim ID")
    slug: str | None = Field(default=None, description="Legacy human-readable identifier")
    type: Literal["claim"] = Field("claim", description="Discriminator type")
    term: str = Field(..., description="Associated term or short key")
    definition: str = Field(..., description="The claim statement text")
    source_file: str = Field(..., description="Origin filename")
    ingested_at: str | datetime | None = Field(None, description="Ingestion timestamp")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "term", "definition", "source_file")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class KBReference(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique reference ID")
    slug: str | None = Field(default=None, description="Legacy human-readable identifier")
    type: Literal["reference"] = Field("reference", description="Discriminator type")
    definition: str = Field(..., description="Full bibliographic reference")
    short_citation: str | None = Field(None, description="Short citation (e.g., Author 2023)")
    source_file: str = Field(..., description="Origin filename")
    ingested_at: str | datetime | None = Field(None, description="Ingestion timestamp")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "definition", "source_file")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


KBItem = Union[KBConcept, KBClaim, KBReference]
