"""Data Transfer Objects for Studio domain.

These models define API Response boundaries enforcing Data Sovereignty.
"""

from pydantic import Field

from backend_v2.models.dtos.base import BaseResponseDTO
from backend_v2.models.v2_core import PromptBlock, Step, Workflow


class WorkflowResponseDTO(BaseResponseDTO, Workflow):
    """API Response boundary for Workflow ensuring Data Sovereignty."""

    organization_id: str | None = Field(default=None, description="Explicitly exposed for Admin Studio UI routing.")


class StepResponseDTO(BaseResponseDTO, Step):
    """API Response boundary for Step ensuring Data Sovereignty."""

    organization_id: str | None = Field(default=None, description="Explicitly exposed for Admin Studio UI routing.")


class PromptBlockResponseDTO(BaseResponseDTO, PromptBlock):
    """API Response boundary for PromptBlock ensuring Data Sovereignty."""

    organization_id: str | None = Field(default=None, description="Explicitly exposed for Admin Studio UI routing.")
