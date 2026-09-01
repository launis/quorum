"""Data Transfer Objects for Studio domain.

These models define API Response boundaries enforcing Data Sovereignty.
Verified Phase 1 Decoupled TDA schema propagation.
"""

from typing import Annotated, Any, Literal

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.models.dtos.base import BaseDTO, BaseResponseDTO
from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO
from backend_v2.models.dtos.prompt_context import PromptContextDTO
from backend_v2.models.enums import (
    BlockDataType,
    HistoricalContextMode,
    LaxHistoricalContextMode,
    LaxScoringStrategy,
    LaxStepType,
    PromptBlockCategory,
    ScoringStrategy,
    StepType,
)
from backend_v2.models.v2_core import (
    ExpectedInput,
    I18nText,
    MatrixRow,
    MatrixScale,
    Step,
    StepRule,
    TheoryGrounding,
    Workflow,
)

__all__ = [
    "WorkflowCreateDTO",
    "StepCreateDTO",
    "PromptBlockCreateDTO",
    "WorkflowResponseDTO",
    "StepResponseDTO",
    "PromptBlockResponseDTO",
    "MCPGatewayDeleteResponse",
    "ModelRegistryDeleteResponse",
    "PromptBlockSimulationResponse",
    "PromptBlockDeleteResponse",
    "PromptBlockSimulationRequest",
    "StepSimulationResponse",
    "StepDeleteResponse",
    "StepSimulationRequest",
    "WorkflowSimulationResponse",
    "WorkflowDeleteResponse",
    "WorkflowAvailableExtensionsResponse",
    "OutputProfileListResponse",
    "GCPLocationDTO",
    "WorkflowUpdateDTO",
    "StepUpdateDTO",
]


class GCPLocationDTO(BaseDTO):
    """Data Transfer Object representing a supported GCP location for Vertex AI.

    Attributes:
        id: Canonical GCP region string (e.g., 'europe-north1').
        label: Human-readable location label.
        description: Informational description of region location.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    id: Annotated[str, Field(description="Canonical GCP region identifier")]
    label: Annotated[str, Field(description="Human-readable regional label")]
    description: Annotated[str, Field(description="Informational region description")]


def _default_allowed_exports() -> list[Literal["pdf", "docx", "raw_json", "xlsx"]]:
    return ["pdf"]


class WorkflowCreateDTO(V2CoreBase):
    """DTO for creating a new Workflow without client-specified ID.

    Attributes:
        slug: Human-readable routing identifier.
        name: Localized name of the workflow.
        description: Localized description of the workflow.
        expected_inputs: Sequence of expected input variable schemas.
        steps: Sequence of step routing rules.
        allowed_exports: Permitted export formats.
        historical_context_mode: Historical context retention mode.
        organization_id: Optional tenant organization scope.
        default_profile_id: Optional default output profile ID.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    slug: Annotated[str, Field(..., min_length=1, pattern=r"^[a-zA-Z0-9_\-]+$", description="Routing identifier.")]
    name: Annotated[I18nText | str, Field(..., description="Localized name of the workflow.")]
    description: Annotated[I18nText | str | None, Field(default=None, description="Detailed workflow description.")]
    expected_inputs: Annotated[
        list[ExpectedInput], Field(default_factory=list, description="Expected input variables.")
    ] = Field(default_factory=list)
    steps: Annotated[list[StepRule], Field(default_factory=list, description="Sequence of step routing rules.")] = (
        Field(default_factory=list)
    )
    allowed_exports: Annotated[
        list[Literal["pdf", "docx", "raw_json", "xlsx"]],
        Field(default_factory=_default_allowed_exports, description="Permitted export formats."),
    ] = Field(default_factory=_default_allowed_exports)
    historical_context_mode: Annotated[
        LaxHistoricalContextMode,
        Field(default=HistoricalContextMode.DISABLED, description="Historical context mode."),
    ] = HistoricalContextMode.DISABLED
    organization_id: Annotated[str | None, Field(default=None, description="Tenant organization scope.")] = None
    default_profile_id: Annotated[str | None, Field(default=None, description="Default output profile ID.")] = None
    status: Annotated[str, Field(default="draft", description="Workflow lifecycle status")] = "draft"
    version: Annotated[int, Field(default=1, description="Workflow schema version")] = 1
    is_public: Annotated[bool, Field(default=False, description="Public visibility flag")] = False
    mcp_gateway_id: Annotated[str | None, Field(default="sys_8172bda70c8641c5", description="MCP gateway ID")] = (
        "sys_8172bda70c8641c5"
    )
    default_strictness_level: Annotated[int, Field(default=50, ge=0, le=100, description="Strictness level")] = 50
    default_scoring_strategy: Annotated[
        LaxScoringStrategy, Field(default=ScoringStrategy.AVERAGE, description="Default scoring strategy")
    ] = ScoringStrategy.AVERAGE
    enable_contextual_overrides: Annotated[bool, Field(default=False, description="Enable contextual overrides")] = (
        False
    )
    enable_semantic_smoothing: Annotated[bool, Field(default=False, description="Enable semantic smoothing")] = False
    enable_eager_anonymization: Annotated[bool, Field(default=False, description="Enable eager anonymization")] = False
    system_audit_trail: Annotated[bool, Field(default=False, description="Enable system audit trail")] = False


class StepCreateDTO(V2CoreBase):
    """DTO for creating a new Step blueprint without client-specified ID.

    Attributes:
        slug: Human-readable identifier.
        name: Localized step name.
        description: Detailed step context.
        type: Step execution type.
        role_block_id: Optional role block reference.
        extraction_protocol_block_id: Optional extraction protocol block reference.
        execution_persona_block_id: Optional execution persona block reference.
        criteria_block_ids: List of criteria block references.
        pre_hooks: List of pre-execution hooks.
        post_hooks: List of post-execution hooks.
        safety: Safety execution rating.
        allowed_mcp_tools: List of allowed MCP tools.
        model_strategy: Optional cognitive strategy profile override.
        hook: Optional native hook name if type is logic.
        expected_inputs: List of expected input keys.
        is_system_core: Whether the step is protected system core.
        organization_id: Tenant organization scope.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    slug: Annotated[str, Field(..., description="Human-readable identifier (e.g., 'step_guard')")]
    name: Annotated[I18nText, Field(..., description="Localized step name")]
    description: Annotated[I18nText | None, Field(default=None, description="Detailed step context")] = None
    type: Annotated[
        LaxStepType, Field(default=StepType.LLM, description="Step execution type (llm or native logic)")
    ] = StepType.LLM
    hook: Annotated[str | None, Field(default=None, description="Native Python hook to execute if type is 'logic'")] = (
        None
    )
    role_block_id: Annotated[
        str | None,
        Field(default=None, pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="Role block reference"),
    ] = None
    extraction_protocol_block_id: Annotated[
        str | None,
        Field(
            default=None,
            pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$",
            description="Global evidence extraction protocol reference",
        ),
    ] = None
    execution_persona_block_id: Annotated[
        str | None,
        Field(
            default=None,
            pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$",
            description="Reference to Execution Persona PromptBlock",
        ),
    ] = None
    criteria_block_ids: Annotated[
        list[str], Field(default_factory=list, description="References to matrix or text blocks")
    ] = Field(default_factory=list)
    pre_hooks: Annotated[list[str], Field(default_factory=list, description="Pre-execution hooks")] = Field(
        default_factory=list
    )
    post_hooks: Annotated[list[str], Field(default_factory=list, description="Post-execution hooks")] = Field(
        default_factory=list
    )
    safety: Annotated[Literal["safe", "unsafe"], Field(default="safe", description="Safety execution rating")] = "safe"
    allowed_mcp_tools: Annotated[list[str], Field(default_factory=list, description="Allowed MCP tools")] = Field(
        default_factory=list
    )
    model_strategy: Annotated[str | None, Field(default=None, description="Cognitive strategy profile override")] = None
    expected_inputs: Annotated[list[str], Field(default_factory=list, description="List of expected input keys")] = (
        Field(default_factory=list)
    )
    is_system_core: Annotated[bool, Field(default=False, description="Protected system core flag")] = False
    organization_id: Annotated[str | None, Field(default=None, description="Tenant organization ID")] = None


class PromptBlockCreateDTO(V2CoreBase):
    """DTO for creating a new PromptBlock without client-specified ID.

    Attributes:
        slug: URL routing identifier.
        label: Localizable label.
        description: Localizable description.
        category_id: Block category enum value.
        type: Block data type enum value.
        output_extensions: List of XAI output extensions.
        ai_description: English cognitive instructions for LLM.
        theory_grounding: Theory grounding context.
        is_evaluative: Evaluative flag.
        allow_decimals: Allow decimals flag.
        allow_contextual_override: Allow contextual override flag.
        is_lightweight_protocol: Lightweight protocol flag.
        scales: BARS scale definitions if matrix.
        rows: Rows if matrix.
        columns: Columns if matrix.
        instruction_text: Instruction text if system rule.
        role_enforcement: Role enforcement text if persona.
        tone_directives: Tone directives if persona.
        protocol_instructions: Protocol instructions if protocol.
        organization_id: Tenant organization scope.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    slug: Annotated[str, Field(..., min_length=1, description="URL routing helper field")]
    label: Annotated[I18nText, Field(..., description="Localizable label for the UI")]
    description: Annotated[I18nText, Field(..., description="Localizable description or help text")]
    category_id: Annotated[PromptBlockCategory, Field(..., description="Prompt block category")]
    type: Annotated[BlockDataType, Field(default=BlockDataType.INSTRUCTION, description="Block data type")] = (
        BlockDataType.INSTRUCTION
    )
    output_extensions: Annotated[list[str], Field(default_factory=list, description="Requested XAI extensions")] = (
        Field(default_factory=list)
    )
    ai_description: Annotated[str | None, Field(default=None, description="English cognitive instructions")] = None
    theory_grounding: Annotated[
        TheoryGrounding | None, Field(default=None, description="Theory grounding metadata")
    ] = None
    is_evaluative: Annotated[bool, Field(default=False, description="Whether the block evaluates claims")] = False
    allow_decimals: Annotated[bool, Field(default=False, description="Whether decimal scores are allowed")] = False
    allow_contextual_override: Annotated[
        bool, Field(default=False, description="Whether contextual override is allowed")
    ] = False
    is_lightweight_protocol: Annotated[bool, Field(default=False, description="Lightweight protocol flag")] = False
    scales: Annotated[list[MatrixScale] | None, Field(default=None, description="BARS scale definitions")] = None
    rows: Annotated[list[MatrixRow] | None, Field(default=None, description="Matrix rows")] = None
    columns: Annotated[list[I18nText] | None, Field(default=None, description="Matrix columns")] = None
    instruction_text: Annotated[str | None, Field(default=None, description="Instruction text for system rules")] = None
    role_enforcement: Annotated[str | None, Field(default=None, description="Role enforcement for personas")] = None
    tone_directives: Annotated[list[str], Field(default_factory=list, description="Tone directives for personas")] = (
        Field(default_factory=list)
    )
    protocol_instructions: Annotated[
        str | None, Field(default=None, description="Protocol instructions for protocols")
    ] = None
    organization_id: Annotated[str | None, Field(default=None, description="Tenant organization scope")] = None


class WorkflowResponseDTO(BaseResponseDTO, Workflow):
    """API Response boundary for Workflow ensuring Data Sovereignty.

    Attributes:
        organization_id: Explicitly exposed for Admin Studio UI routing.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    organization_id: Annotated[
        str | None, Field(default=None, description="Explicitly exposed for Admin Studio UI routing.")
    ]
    output_profiles: Annotated[
        dict[str, OutputProfileResponseDTO],
        Field(
            default_factory=dict, description="Dictionary of fully hydrated OutputProfiles attached to this workflow."
        ),
    ]


class StepResponseDTO(BaseResponseDTO, Step):
    """API Response boundary for Step ensuring Data Sovereignty.

    Attributes:
        organization_id: Explicitly exposed for Admin Studio UI routing.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    organization_id: Annotated[
        str | None, Field(default=None, description="Explicitly exposed for Admin Studio UI routing.")
    ]


# PromptBlockResponseDTO alias to AnyPromptBlock discriminated union
PromptBlockResponseDTO = PromptBlock


class MCPGatewayDeleteResponse(BaseResponseDTO):
    """API Response schema for deleting an MCP gateway.

    Attributes:
        status: Action outcome status message.
        deleted_id: Opaque ID of the deleted gateway.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    status: str
    deleted_id: str


class ModelRegistryDeleteResponse(BaseResponseDTO):
    """API Response schema for deleting a Model Registry entry.

    Attributes:
        status: Action outcome status message.
        deleted_id: Opaque ID of the deleted model registry.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

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

    model_config = ConfigDict(strict=True, extra="forbid")

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

    model_config = ConfigDict(strict=True, extra="forbid")

    status: str
    deleted_id: str


class PromptBlockSimulationRequest(BaseDTO):
    """Simulation configuration inputs for testing dynamic prompt construction.

    Attributes:
        block: The source PromptBlock domain object.
        mock_inputs: Arbitrary mock parameters mimicking actual workflow variables.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

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

    model_config = ConfigDict(strict=True, extra="forbid")

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

    model_config = ConfigDict(strict=True, extra="forbid")

    status: str
    deleted_id: str


class StepSimulationRequest(BaseDTO):
    """Isolated runtime input payload required to compile and verify a single step.

    Attributes:
        step: Domain step blueprint context containing prompt configurations.
        mock_inputs: Static evaluation anchors containing environment variables.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

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

    model_config = ConfigDict(strict=True, extra="forbid")

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

    model_config = ConfigDict(strict=True, extra="forbid")

    status: str
    deleted_id: str


class WorkflowAvailableExtensionsResponse(BaseResponseDTO):
    """API Response containing available XAI extensions for a workflow.

    Attributes:
        available_extensions: Union of all output_extensions defined across all Target Matrices.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    available_extensions: Annotated[list[str], Field(default_factory=list)]


class OutputProfileListResponse(BaseResponseDTO):
    """Response model for a list of OutputProfiles.

    Attributes:
        items: List of OutputProfile domain objects.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    items: list[OutputProfileResponseDTO]


class WorkflowUpdateDTO(BaseDTO):
    """DTO for updating an existing Workflow definition."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    name: Annotated[I18nText | str | None, Field(default=None, description="Updated localized workflow name")] = None
    description: Annotated[I18nText | str | None, Field(default=None, description="Updated description")] = None
    slug: Annotated[
        str | None, Field(default=None, pattern=r"^[a-zA-Z0-9_\-]+$", description="Updated routing slug")
    ] = None
    expected_inputs: Annotated[
        list[ExpectedInput] | None, Field(default=None, description="Updated expected inputs")
    ] = None
    steps: Annotated[list[StepRule] | None, Field(default=None, description="Updated step rules")] = None
    allowed_exports: Annotated[list[Literal["pdf", "docx", "raw_json", "xlsx"]] | None, Field(default=None)] = None
    historical_context_mode: Annotated[LaxHistoricalContextMode | None, Field(default=None)] = None
    default_profile_id: Annotated[str | None, Field(default=None)] = None
    status: Annotated[str | None, Field(default=None)] = None


class StepUpdateDTO(BaseDTO):
    """DTO for updating an existing Step blueprint."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    name: Annotated[I18nText | None, Field(default=None)] = None
    description: Annotated[I18nText | None, Field(default=None)] = None
    slug: Annotated[str | None, Field(default=None)] = None
    type: Annotated[LaxStepType | None, Field(default=None)] = None
    hook: Annotated[str | None, Field(default=None)] = None
    role_block_id: Annotated[str | None, Field(default=None)] = None
    extraction_protocol_block_id: Annotated[str | None, Field(default=None)] = None
    execution_persona_block_id: Annotated[str | None, Field(default=None)] = None
    criteria_block_ids: Annotated[list[str] | None, Field(default=None)] = None
    pre_hooks: Annotated[list[str] | None, Field(default=None)] = None
    post_hooks: Annotated[list[str] | None, Field(default=None)] = None
    safety: Annotated[Literal["safe", "unsafe"] | None, Field(default=None)] = None
    allowed_mcp_tools: Annotated[list[str] | None, Field(default=None)] = None
    model_strategy: Annotated[str | None, Field(default=None)] = None
    expected_inputs: Annotated[list[str] | None, Field(default=None)] = None
