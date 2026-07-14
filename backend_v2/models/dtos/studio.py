"""Data Transfer Objects for Studio domain.

These models define API Response boundaries enforcing Data Sovereignty.
Verified Phase 1 Decoupled TDA schema propagation.
"""

from typing import Annotated, Any

from pydantic import Field

from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.base import BaseDTO, BaseResponseDTO
from backend_v2.models.dtos.prompt_context import PromptContextDTO
from backend_v2.models.v2_core import PromptBlock, Step, Workflow


class WorkflowResponseDTO(BaseResponseDTO, Workflow):
    """API Response boundary for Workflow ensuring Data Sovereignty.

    Attributes:
        organization_id: Explicitly exposed for Admin Studio UI routing.
    """

    organization_id: Annotated[
        str | None, Field(default=None, description="Explicitly exposed for Admin Studio UI routing.")
    ]


class StepResponseDTO(BaseResponseDTO, Step):
    """API Response boundary for Step ensuring Data Sovereignty.

    Attributes:
        organization_id: Explicitly exposed for Admin Studio UI routing.
    """

    organization_id: Annotated[
        str | None, Field(default=None, description="Explicitly exposed for Admin Studio UI routing.")
    ]


class PromptBlockResponseDTO(BaseResponseDTO, PromptBlock):
    """API Response boundary for PromptBlock ensuring Data Sovereignty.

    Attributes:
        organization_id: Explicitly exposed for Admin Studio UI routing.
    """

    organization_id: Annotated[
        str | None, Field(default=None, description="Explicitly exposed for Admin Studio UI routing.")
    ]


class MCPGatewayDeleteResponse(BaseResponseDTO):
    """API Response schema for deleting an MCP gateway.

    Attributes:
        status: Action outcome status message.
        deleted_id: Opaque ID of the deleted gateway.
    """

    status: str
    deleted_id: str


class ModelRegistryDeleteResponse(BaseResponseDTO):
    """API Response schema for deleting a Model Registry entry.

    Attributes:
        status: Action outcome status message.
        deleted_id: Opaque ID of the deleted model registry.
    """

    status: str
    deleted_id: str


class PromptBlockSimulationResponse(BaseResponseDTO):
    """Resulting simulation projection for a dry-run prompt rendering.

    Attributes:
        valid: Indicates if simulation passed verification without errors.
        errors: Compiled structural parsing errors list.
        rendered_prompt: Raw text output containing the rendered prompt block template.
        trace: Metadata containing state execution variables.
    """

    valid: Annotated[bool, Field(default=True, description="Indicates if the prompt block simulation is successful.")]
    errors: Annotated[list[str], Field(default_factory=list, description="Validation errors found during simulation.")]
    rendered_prompt: Annotated[str, Field(default="", description="The simulated rendered prompt template.")]
    trace: Annotated[dict[str, Any], Field(default_factory=dict, description="Execution trace metadata.")]
    prompt_context: Annotated[
        PromptContextDTO | None, Field(default=None, description="XAI compiled prompt structure.")
    ]


class PromptBlockDeleteResponse(BaseResponseDTO):
    """API Response schema for deleting a prompt block.

    Attributes:
        status: Status code or textual message.
        deleted_id: Opaque ID of the deleted prompt block.
    """

    status: str
    deleted_id: str


class PromptBlockSimulationRequest(BaseDTO):
    """Simulation configuration inputs for testing dynamic prompt construction.

    Attributes:
        block: The source PromptBlock domain object.
        mock_inputs: Arbitrary mock parameters mimicking actual workflow variables.
    """

    block: PromptBlock
    mock_inputs: Annotated[dict[str, Any], Field(default_factory=dict)]


class StepSimulationResponse(BaseResponseDTO):
    """Dry-run validation telemetry for isolated step execution.

    Attributes:
        valid: Verification boolean indicator.
        errors: Array of syntax or schema compliance issues.
        rendered_prompt: Concrete text string sent to the target LLM task.
        trace: Associated performance profiling variables.
    """

    valid: Annotated[bool, Field(default=True, description="Indicates if the step simulation is successful.")]
    errors: Annotated[list[str], Field(default_factory=list, description="Validation errors found during simulation.")]
    rendered_prompt: Annotated[str, Field(default="", description="The simulated rendered step prompts.")]
    trace: Annotated[dict[str, Any], Field(default_factory=dict, description="Execution trace metadata.")]
    prompt_context: Annotated[
        PromptContextDTO | None, Field(default=None, description="XAI compiled prompt structure.")
    ]


class StepDeleteResponse(BaseResponseDTO):
    """Response returned upon successful removal of a step configuration.

    Attributes:
        status: Lifecycle state mapping indicating deletion complete.
        deleted_id: Relational tracking code representing deleted target.
    """

    status: str
    deleted_id: str


class StepSimulationRequest(BaseDTO):
    """Isolated runtime input payload required to compile and verify a single step.

    Attributes:
        step: Domain step blueprint context containing prompt configurations.
        mock_inputs: Static evaluation anchors containing environment variables.
    """

    step: Step
    mock_inputs: Annotated[dict[str, Any], Field(default_factory=dict)]


class WorkflowSimulationResponse(BaseResponseDTO):
    """Full structural DAG validation result for complex multi-agent workflows.

    Attributes:
        valid: Static verification of circularity and node compatibility.
        errors: Aggregated failure logs throughout the graph parse pathway.
        step_status: Compilation status map keyed by Step identifiers.
        execution_order: Order of step executions dynamically computed from the DAG.
        trace: Aggregated telemetry profiling outputs.
    """

    valid: Annotated[bool, Field(default=True, description="Indicates if the workflow DAG simulation is successful.")]
    errors: Annotated[list[str], Field(default_factory=list, description="Structure and wiring errors.")]
    step_status: Annotated[dict[str, str], Field(default_factory=dict, description="Compilation status per step.")]
    execution_order: Annotated[
        list[str], Field(default_factory=list, description="Topologically sorted execution order.")
    ]
    trace: Annotated[dict[str, Any], Field(default_factory=dict, description="Execution trace metadata.")]


class WorkflowDeleteResponse(BaseResponseDTO):
    """API output indicating clean removal of a target workflow entity.

    Attributes:
        status: Action status string.
        deleted_id: Opaque ID representing the deleted workflow resource.
    """

    status: str
    deleted_id: str


class WorkflowAvailableExtensionsResponse(BaseResponseDTO):
    """API Response containing available XAI extensions for a workflow.

    Attributes:
        available_extensions: Union of all output_extensions defined across all Target Matrices.
    """

    available_extensions: Annotated[list[str], Field(default_factory=list)]


class OutputProfileListResponse(BaseResponseDTO):
    """Response model for a list of OutputProfiles.

    Attributes:
        items: List of OutputProfile domain objects.
    """

    items: list[OutputProfile]
