from typing import List, Optional

from pydantic import BaseModel, Field


class ConceptItem(BaseModel):
    """A single theoretical concept or framework extracted from text."""
    term: str = Field(..., description="The name of the concept (Capitalized).")
    definition: str = Field(..., description="A precise definition or explanation found in the text, preferably with citations.")


class ConceptResponse(BaseModel):
    """Response schema for concept extraction."""
    concepts: List[ConceptItem] = Field(default_factory=list, description="List of extracted concepts.")


class IngestionSummary(BaseModel):
    """Summary of a knowledge base ingestion job."""
    
    job_id: str = Field(..., description="Unique ID of the ingestion job.")
    status: str = Field(..., description="Status of the ingestion (e.g. 'completed').")
    concepts_count: int = Field(0, description="Number of concepts extracted/stored.")
    references_count: int = Field(0, description="Number of references extracted/stored.")
    claims_count: int = Field(0, description="Number of claims extracted/stored.")
    filename: Optional[str] = Field(None, description="Name of the processed file.")
