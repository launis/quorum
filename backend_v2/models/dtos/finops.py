"""Data Transfer Objects for FinOps trace analysis and telemetry monitoring."""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase

__all__ = [
    "FinOpsFinalizeSummaryDTO",
    "FinOpsMonitorSummaryDTO",
]


class FinOpsMonitorSummaryDTO(V2CoreBase):
    """Encapsulates FinOps real-time monitoring telemetry metrics and alerts."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    total_duration_ms: Annotated[int, Field(description="Total execution duration in milliseconds")]
    total_calls: Annotated[int, Field(description="Total LLM API calls executed")]
    alerts: Annotated[list[str], Field(default_factory=list, description="FinOps alert messages")] = Field(
        default_factory=list
    )


class FinOpsFinalizeSummaryDTO(V2CoreBase):
    """Encapsulates execution finalization FinOps redundancy metrics and total cost."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    healing_cost_events: Annotated[int, Field(description="Count of healing cost events")]
    structural_warnings: Annotated[
        list[str], Field(default_factory=list, description="Structural pipeline duplication warnings")
    ] = Field(default_factory=list)
    hashing_warnings: Annotated[
        list[str], Field(default_factory=list, description="Payload hashing duplication warnings")
    ] = Field(default_factory=list)
    mcp_warnings: Annotated[list[str], Field(default_factory=list, description="Duplicate MCP tool call warnings")] = (
        Field(default_factory=list)
    )
    usd_cost: Annotated[float, Field(description="Total calculated USD cost incurred")]
