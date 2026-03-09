from datetime import datetime
from uuid import UUID

from pydantic import Field

from backend_v2.models.dtos.base import BaseDTO


class XAIFlatReportDTO(BaseDTO):
    """A flattened, machine-readable report summary optimized for BI tools and external integration.
    Contains no Markdown, no nested structures (except the scores dict), and strictly typed fields.
    """

    execution_id: UUID = Field(..., description="The unique ID of the workflow execution.")
    timestamp: datetime = Field(..., description="When this report was generated.")

    # High-Level Outcomes
    verdict: str = Field(..., description="Final decision (e.g., 'Approved', 'Rejected').")
    score_total: float = Field(..., description="The total calculated score (0.0 - 5.0).")
    confidence_score: float = Field(..., description="AI confidence in the result (0.0 - 1.0).")

    # Key Drivers
    top_strength_id: str | None = Field(None, description="ID of the highest scoring dimension.")
    top_weakness_id: str | None = Field(None, description="ID of the lowest scoring dimension.")

    # Flattened Metrics (Key-Value for easy BI pivoting)
    # Example: {"clarity": 4.5, "logic": 3.0, "evidence": 5.0}
    flattened_scores: dict[str, float] = Field(
        default_factory=dict, description="Key-value map of dimension IDs to their numeric scores."
    )
