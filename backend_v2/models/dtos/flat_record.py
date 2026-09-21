"""Flat execution record DTO.

SSOT for flat execution record metrics consumed by export and flattener services.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase

__all__ = ["FlatExecutionRecordDTO"]


class FlatExecutionRecordDTO(V2CoreBase):
    """Flattened representation of an ExecutionRecord for tabular/CSV exports.

    Attributes:
        execution_id: Canonical execution identifier.
        workflow_id: Workflow definition identifier.
        status: Execution lifecycle status string.
        global_score: Global normalized execution score.
        has_warning: Flag indicating execution warnings.
        matrix_metrics: Flattened key-value metrics extracted from evaluation matrices.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    execution_id: Annotated[str, Field(description="Canonical execution identifier")]
    workflow_id: Annotated[str, Field(description="Workflow definition identifier")]
    status: Annotated[str, Field(description="Execution lifecycle status string")]
    global_score: Annotated[float | None, Field(default=None, description="Global normalized execution score")] = None
    has_warning: Annotated[bool, Field(default=False, description="Flag indicating execution warnings")] = False
    matrix_metrics: Annotated[
        dict[str, str | float | int | bool | None],
        Field(default_factory=dict, description="Flattened key-value metrics extracted from evaluation matrices"),
    ] = Field(default_factory=dict)

    def to_csv_dict(self) -> dict[str, str | float | int | bool | None]:
        """Convert flat record into a single row dictionary suitable for CSV serialization.

        Returns:
            Dictionary mapping CSV column headers to scalar values.
        """
        row: dict[str, str | float | int | bool | None] = {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "status": self.status,
            "global_score": self.global_score,
            "has_warning": self.has_warning,
        }
        row.update(self.matrix_metrics)
        return row
