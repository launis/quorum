from pydantic import BaseModel, ConfigDict, Field, field_validator


class ConceptItem(BaseModel):
    """A single theoretical concept or framework extracted from text."""

    term: str = Field(..., description="The name of the concept (Capitalized).")
    definition: str = Field(
        ..., description="A precise definition or explanation found in the text, preferably with citations."
    )

    model_config = ConfigDict(frozen=True)

    @field_validator("term", "definition")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class ConceptResponse(BaseModel):
    """Response schema for concept extraction."""

    concepts: list[ConceptItem] = Field(default_factory=list, description="List of extracted concepts.")

    model_config = ConfigDict(frozen=True)


class IngestionSummary(BaseModel):
    """Summary of a knowledge base ingestion job."""

    job_id: str = Field(..., description="Unique ID of the ingestion job.")
    status: str = Field(..., description="Status of the ingestion (e.g. 'completed').")
    concepts_count: int = Field(0, description="Number of concepts extracted/stored.")
    references_count: int = Field(0, description="Number of references extracted/stored.")
    claims_count: int = Field(0, description="Number of claims extracted/stored.")
    file_size: int = Field(0, description="Size of the processed file in bytes.")
    filename: str | None = Field(None, description="Name of the processed file.")

    model_config = ConfigDict(frozen=True)

    @field_validator("job_id", "status")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()
