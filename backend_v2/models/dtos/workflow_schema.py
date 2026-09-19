"""Data Transfer Object for workflow UI schema.

SSOT for WorkflowSchemaResponseDTO consumed by /workflows/{workflow_id}/ui_schema.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.models.domain.step import ExpectedInput


class WorkflowSchemaResponseDTO(BaseModel):
    """Schema response for dynamic frontend rendering of workflow input expectations."""

    model_config = ConfigDict(strict=True, extra="forbid")

    expected_inputs: list[ExpectedInput] = Field(
        default_factory=list,
        description="List of expected inputs required by the workflow blueprint.",
    )
