"""Data Transfer Object for workflow UI schema.

SSOT for WorkflowSchemaResponseDTO consumed by /workflows/{workflow_id}/ui_schema.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.models.domain.step import ExpectedInput

__all__ = ["WorkflowSchemaResponseDTO"]


class WorkflowSchemaResponseDTO(BaseModel):
    """Schema response for dynamic frontend rendering of workflow input expectations.

    Attributes:
        expected_inputs: List of expected inputs required by the workflow blueprint.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    expected_inputs: Annotated[
        list[ExpectedInput],
        "List of expected inputs required by the workflow blueprint.",
    ] = Field(
        default_factory=list,
        description="List of expected inputs required by the workflow blueprint.",
    )
