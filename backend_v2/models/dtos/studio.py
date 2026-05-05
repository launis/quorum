"""Data Transfer Objects for Studio domain.

These models define API Response boundaries enforcing Data Sovereignty.
"""

from typing import Any

from pydantic import Field

from backend_v2.models.dtos.base import BaseDTO, BaseResponseDTO
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


class MCPGatewayDeleteResponse(BaseResponseDTO):
    status: str
    deleted_id: str


class ModelRegistryDeleteResponse(BaseResponseDTO):
    status: str
    deleted_id: str


class PromptBlockSimulationResponse(BaseResponseDTO):
    trace: dict[str, Any] = Field(default_factory=dict)


class PromptBlockDeleteResponse(BaseResponseDTO):
    status: str
    deleted_id: str


class PromptBlockSimulationRequest(BaseDTO):
    block: PromptBlock
    mock_inputs: dict[str, Any] = Field(default_factory=dict)


class StepSimulationResponse(BaseResponseDTO):
    trace: dict[str, Any] = Field(default_factory=dict)


class StepDeleteResponse(BaseResponseDTO):
    status: str
    deleted_id: str


class StepSimulationRequest(BaseDTO):
    step: Step
    mock_inputs: dict[str, Any] = Field(default_factory=dict)


class WorkflowSimulationResponse(BaseResponseDTO):
    trace: dict[str, Any] = Field(default_factory=dict)


class WorkflowDeleteResponse(BaseResponseDTO):
    status: str
    deleted_id: str
