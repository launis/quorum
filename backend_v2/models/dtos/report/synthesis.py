"""Synthesis top-level report structures."""

from datetime import datetime
from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.dtos.base import BaseDTO
from backend_v2.models.dtos.report.context import GlobalContextVarsDTO
from backend_v2.models.dtos.report.matrix import MatrixObservabilityDTO


class XAIFlatReportDTO(BaseDTO):
    """A flattened, machine-readable report summary optimized for BI tools and external integration."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    execution_id: Annotated[str, Field(description="The unique ID of the workflow execution.")]
    timestamp: Annotated[datetime, Field(description="When this report was generated.")]

    # High-Level Outcomes
    verdict: Annotated[str, Field(description="Final decision (e.g., 'Approved', 'Rejected').")]
    score_total: Annotated[float, Field(description="The total calculated score (0.0 - 5.0).")]
    confidence_score: Annotated[float, Field(description="AI confidence in the result (0.0 - 1.0).")]

    # Key Drivers
    top_strength_id: Annotated[str | None, Field(description="ID of the highest scoring dimension.")] = None
    top_weakness_id: Annotated[str | None, Field(description="ID of the lowest scoring dimension.")] = None

    # Flattened Metrics (Key-Value for easy BI pivoting)
    flattened_scores: Annotated[
        dict[str, float],
        Field(description="Key-value map of dimension IDs to their numeric scores.", default_factory=dict),
    ]


class ReportSynthesisDTO(BaseDTO):
    """Top-level container enforcing strict typing over the reporting hook payload."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    inputs: MatrixObservabilityDTO
    global_context_vars: GlobalContextVarsDTO
