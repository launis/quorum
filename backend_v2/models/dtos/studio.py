"""Data Transfer Objects for Studio domain.

These models define API Response boundaries enforcing Data Sovereignty.
Verified Phase 1 Decoupled TDA schema propagation.
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
    valid: bool = Field(default=True, description="Indicates if the prompt block simulation is successful.")
    errors: list[str] = Field(default_factory=list, description="Validation errors found during simulation.")
    rendered_prompt: str = Field(default="", description="The simulated rendered prompt template.")
    trace: dict[str, Any] = Field(default_factory=dict, description="Execution trace metadata.")


class PromptBlockDeleteResponse(BaseResponseDTO):
    status: str
    deleted_id: str


class PromptBlockSimulationRequest(BaseDTO):
    block: PromptBlock
    mock_inputs: dict[str, Any] = Field(default_factory=dict)


class StepSimulationResponse(BaseResponseDTO):
    valid: bool = Field(default=True, description="Indicates if the step simulation is successful.")
    errors: list[str] = Field(default_factory=list, description="Validation errors found during simulation.")
    rendered_prompt: str = Field(default="", description="The simulated rendered step prompts.")
    trace: dict[str, Any] = Field(default_factory=dict, description="Execution trace metadata.")


class StepDeleteResponse(BaseResponseDTO):
    status: str
    deleted_id: str


class StepSimulationRequest(BaseDTO):
    step: Step
    mock_inputs: dict[str, Any] = Field(default_factory=dict)


class WorkflowSimulationResponse(BaseResponseDTO):
    valid: bool = Field(default=True, description="Indicates if the workflow DAG simulation is successful.")
    errors: list[str] = Field(default_factory=list, description="Structure and wiring errors.")
    step_status: dict[str, str] = Field(default_factory=dict, description="Compilation status per step.")
    execution_order: list[str] = Field(default_factory=list, description="Topologically sorted execution order.")
    trace: dict[str, Any] = Field(default_factory=dict, description="Execution trace metadata.")


class WorkflowDeleteResponse(BaseResponseDTO):
    status: str
    deleted_id: str
