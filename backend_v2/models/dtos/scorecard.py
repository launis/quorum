from pydantic import BaseModel, Field


class MatrixScorecardRowDTO(BaseModel):
    """Represents a single evaluated matrix row in the scorecard."""
    
    block_id: str = Field(..., description="The opaque Stripe ID of the prompt block.")
    label_fi: str = Field(..., description="Finnish human-readable label.")
    label_en: str = Field(..., description="English human-readable label.")
    
    score: float = Field(..., description="Raw scaled score.")
    scale_max: float | None = Field(default=None, description="Maximum possible score.")
    normalized_score: float | None = Field(default=None, description="Normalized score (0-100) if evaluative.")
    
    true_atoms: int | None = Field(default=None, description="Global hits found.")
    total_atoms: int | None = Field(default=None, description="Total atoms available to evaluate.")
    
    justification: str = Field(default="", description="The one-sentence justification.")
    missing_context: str = Field(default="", description="Any missing context from evaluation.")
    
    level_breakdown: dict[str, dict[str, int]] | None = Field(
        default=None, 
        description="Epic 24 Breakdowns: DINA hits vs total per scale floor e.g. {'1.0': {'hits': 5, 'total': 5}}"
    )
    
    is_evaluative: bool = Field(default=True, description="Whether this block contributes to global average.")


class ScorecardResponseDTO(BaseModel):
    """Epic 24: Independent Scorecard API response structure."""
    
    execution_id: str = Field(..., description="The ID of the execution.")
    workflow_id: str = Field(..., description="The ID of the workflow.")
    
    global_average: float | None = Field(
        default=None, 
        description="The mathematical average extracted from normalized evaluative matrices."
    )
    
    evaluative_matrices: list[MatrixScorecardRowDTO] = Field(
        default_factory=list, 
        description="Matrices that impact the final grade."
    )
    
    informational_matrices: list[MatrixScorecardRowDTO] = Field(
        default_factory=list, 
        description="Matrices strictly for informational/tracking purposes."
    )
