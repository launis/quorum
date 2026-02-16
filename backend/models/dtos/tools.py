from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class TextExtractionResponse(BaseModel):
    """Response for text extraction tool."""
    filename: Optional[str] = Field(None, description="Name of the processed file.")
    text: str = Field(description="Extracted raw text content.")

class ConceptExtractionResponse(BaseModel):
    """Response for concept extraction tool."""
    source_length: int = Field(description="Length of the source text processed.")
    concepts: Any = Field(description="Extracted concepts (list of strings or objects).")

class WebScrapeResponse(BaseModel):
    """Response for web scraping tool."""
    url: str = Field(description="The target URL.")
    content: str = Field(description="Scraped content.")

class CitationLookupResponse(BaseModel):
    """Response for citation lookup tool."""
    results: Dict[str, List[Dict[str, Any]]] = Field(description="Map of query to resolved context items.")
