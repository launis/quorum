from pydantic import BaseModel, Field

class KnowledgeStatusResponse(BaseModel):
    """Response model for Knowledge Base status check."""
    has_documents: bool = Field(..., description="True if the knowledge base contains any documents.")
    document_count: int = Field(..., description="Total number of documents in the knowledge base.")
    precedent_count: int = Field(..., description="Total number of historical precedents (completed executions).")
