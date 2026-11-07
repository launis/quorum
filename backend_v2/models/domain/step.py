"""Domain models for workflow steps, step rules, roles, and expected inputs.

SSOT for Step, StepRule, Role, QuestionnaireItem, ExpectedInput, and ALLOWED_INPUT_MODES.
"""

from __future__ import annotations

import logging
from typing import Annotated, Literal

from pydantic import ConfigDict, Field, model_validator
from starlette import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, I18nText, V2CoreBase, generate_opaque_id
from backend_v2.models.dtos.mcp import MCPToolParamOverrides
from backend_v2.models.enums import (
    CognitiveTier,
    EngineType,
    EntityPrefix,
    LaxCognitiveTier,
    LaxStepType,
    LaxStepZone,
    StepType,
    StepZone,
)

logger = logging.getLogger(__name__)

__all__ = [
    "ALLOWED_INPUT_MODES",
    "ExpectedInput",
    "QuestionnaireItem",
    "Role",
    "Step",
    "StepRule",
]

ALLOWED_INPUT_MODES: frozenset[str] = frozenset({"file", "paste", "text", "questionnaire", "assignment"})


class Step(V2CoreBase):
    """Isolated, reusable orchestrator cognitive module (e.g. Guard or step_input_processing).
    Formerly known as TaskBlueprint.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    # Phase 2, Step 2.2: Convert bare Field(...) declarations to PEP 593 Annotated (QGR020 Check 20B)
    id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Unique UUID for storage optionally")]
    slug: Annotated[str, Field(description="Human-readable identifier (e.g., 'step_guard')")]
    organization_id: Annotated[str | None, Field(default=None, description="Tenant organization ID.")] = None
    name: Annotated[I18nText, Field(description="Localized step name")]
    description: Annotated[I18nText | None, Field(default=None, description="Detailed step context")] = None
    type: Annotated[
        LaxStepType,
        Field(default=StepType.LLM, description="Step execution type (llm or native logic)"),
    ] = StepType.LLM
    hook: Annotated[str | None, Field(default=None, description="Native Python hook to execute if type is 'logic'")] = (
        None
    )
    role_block_id: Annotated[
        str | None,
        Field(
            default=None,
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="Reference to role block (e.g. blk_role_critic)",
        ),
    ] = None
    extraction_protocol_block_id: Annotated[
        str | None,
        Field(
            default=None,
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="Reference to global evidence extraction protocol block",
        ),
    ] = None
    execution_persona_block_id: Annotated[
        str | None,
        Field(
            default=None,
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="Reference to the Execution Persona PromptBlock",
        ),
    ] = None
    criteria_block_ids: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="References to matrix or text blocks",
        ),
    ]
    pre_hooks: Annotated[
        list[str],
        Field(default_factory=list, description="Native Python functions to execute BEFORE LLM context building."),
    ]
    post_hooks: Annotated[
        list[str],
        Field(default_factory=list, description="Native Python functions to execute AFTER LLM generation."),
    ]
    safety: Annotated[
        Literal["safe", "unsafe"],
        Field(
            default="safe",
            description="Marks step as safe (read-only MCP) or unsafe (email/API mutations) for strict execution security.",
        ),
    ] = "safe"
    allowed_mcp_tools: Annotated[
        list[str],
        Field(
            default_factory=list, description="List of allowed MCP tools for this step (e.g. ['mcp_tavily_search'])."
        ),
    ]
    # Step-level static parameter overrides keyed by namespaced MCP tool alias
    mcp_tool_params: Annotated[
        dict[str, MCPToolParamOverrides],
        Field(
            default_factory=dict,
            description="Per-tool static parameter overrides keyed by namespaced MCP tool alias.",
        ),
    ]
    cognitive_tier: Annotated[
        LaxCognitiveTier | None,
        Field(
            default=CognitiveTier.FAST,
            description="Step-level cognitive tier profile (e.g., 'fast', 'deep', 'reasoning').",
        ),
    ] = CognitiveTier.FAST
    expected_inputs: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="List of expected input keys required for this step. Replaces free-text generic routing.",
        ),
    ]
    # Workflow context governance field
    is_system_core: Annotated[
        bool,
        Field(description="Whether this step blueprint is a protected system foundational component."),
    ] = False
    engine_type: Annotated[
        EngineType,
        Field(
            default=EngineType.PROMPT,
            strict=False,
            description="Explicit ExecutionEngine responsible for computing this step.",
        ),
    ] = EngineType.PROMPT
    zone: Annotated[
        LaxStepZone,
        Field(
            default=StepZone.ZONE_B,
            description="Functional workflow zone classification (Zone A Ingestion, Zone B Specialists, Zone C Funnel Anchors).",
        ),
    ] = StepZone.ZONE_B

    @model_validator(mode="after")
    def validate_step_consistency(self) -> Step:
        """Strict fail-fast validation to ensure Step is structurally complete.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if structure is malformed or internally inconsistent.

        Returns:
            The sanitized Step matching schema expectations.
        """
        if self.type == StepType.LLM:
            if not self.cognitive_tier or self.cognitive_tier not in CognitiveTier:
                msg = f"LLM Step '{self.id}' must declare an explicit cognitive_tier (Zero-Fallback Rule)."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                )
            if not self.criteria_block_ids:
                msg = f"LLM Step '{self.id}' must define at least one criteria_block_id."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                )
            if not self.extraction_protocol_block_id:
                msg = f"LLM Step '{self.id}' must define a valid extraction_protocol_block_id."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                )
        if self.type == StepType.CAUSAL_DISCOVERY:
            if not self.cognitive_tier or self.cognitive_tier not in CognitiveTier:
                msg = f"Causal Discovery Step '{self.id}' must declare an explicit cognitive_tier (Zero-Fallback Rule)."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                )
            # Require BARS causal cohesion matrix on CAUSAL_DISCOVERY steps
            if not self.criteria_block_ids:
                msg = f"Causal Discovery Step '{self.id}' must define at least one criteria_block_id."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                )
            if not self.extraction_protocol_block_id:
                msg = f"Causal Discovery Step '{self.id}' must define a valid extraction_protocol_block_id."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                )
        if self.type == StepType.LOGIC and not self.hook:
            msg = f"Logic Step '{self.id}' must define a native 'hook' execution target."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
            )
        return self


class StepRule(V2CoreBase):
    """Execution step mapping (DAG Router Node)."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[
        str,
        Field(
            default_factory=lambda: generate_opaque_id(EntityPrefix.STEP_REFERENCE),
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="Unique node ID in the workflow (e.g. blk_node_1).",
        ),
    ]
    task_blueprint: Annotated[
        str,
        Field(
            min_length=1,
            description="ID reference to the isolated Step (e.g., 'step_f15853d2584e4096aeb60f11a3e6ea7c')",
        ),
    ]
    depends_on: Annotated[
        list[str],
        Field(default_factory=list, description="IDs of steps that must complete first."),
    ]
    input_mappings: Annotated[
        dict[str, str],
        Field(
            default_factory=dict,
            description='Maps upstream results to LLM inputs. e.g. {"context": "$inputs.document"}',
        ),
    ]
    expected_sdui_type: Annotated[
        Literal["markdown", "hero_insight", "grid"] | None,
        Field(description="Declares the expected SDUI output schema for schema compilation."),
    ] = None
    # Synthesis context governance field
    is_synthesis_source: Annotated[
        bool,
        Field(description="Whether this step's narrative text output is forwarded to the synthesis LLM context."),
    ] = True
    causal_source_step_id: Annotated[
        str | None,
        Field(
            default=None,
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="Reference to upstream causal discovery step for fusion atom extraction.",
        ),
    ] = None

    ui_pos_x: Annotated[float, Field(default=0.0, description="X coordinate on the 2D DAG canvas.")] = 0.0
    ui_pos_y: Annotated[float, Field(default=0.0, description="Y coordinate on the 2D DAG canvas.")] = 0.0

    @model_validator(mode="after")
    def validate_step_rule_consistency(self) -> StepRule:
        """Enforces that causal_source_step_id exists in depends_on if specified.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if causal_source_step_id is not in depends_on.

        Returns:
            The validated StepRule instance.
        """
        if self.causal_source_step_id is not None and self.causal_source_step_id not in self.depends_on:
            msg = (
                f"StepRule '{self.id}' references causal_source_step_id '{self.causal_source_step_id}' "
                f"which is not declared in depends_on: {self.depends_on}."
            )
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
            )
        return self

    def extract_variable_references(self) -> list[str]:
        """Extracts dynamic variable references (e.g. $inputs.x, $steps.y) from input_mappings.

        Returns:
            List of variables discovered in mapping.
        """
        refs = []
        for val in self.input_mappings.values():
            if isinstance(val, str) and val.startswith("$"):
                refs.append(val)
        return refs


class Role(V2CoreBase):
    """Role definition that locks physical models and pre_hooks."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Unique Role ID")]
    name: I18nText
    model_role: Annotated[str, Field(description='Maps to SystemConfig.model_mappings (e.g., "analyst_model").')]
    type: Annotated[str | None, Field(default="role", description="Component type indicator.")] = "role"
    pre_hooks: Annotated[
        list[str],
        Field(default_factory=list, description="List of registered hook logic to run BEFORE llm."),
    ]
    post_hooks: Annotated[
        list[str],
        Field(default_factory=list, description="List of registered hook logic to run AFTER llm."),
    ]


class QuestionnaireItem(V2CoreBase):
    """A single question definition within a dynamic questionnaire."""

    model_config = ConfigDict(strict=True, extra="forbid")

    question_id: Annotated[str, Field(description="Unique identifier for the question (e.g., 'q1').")]
    question: Annotated[I18nText, Field(description="Localized question text.")]
    type: Annotated[str, Field(description="Input type, e.g., 'text'.")]


class ExpectedInput(V2CoreBase):
    """Definition of an input required by a workflow."""

    model_config = ConfigDict(strict=True, extra="forbid")

    input_key: Annotated[str, Field(pattern=r"^[A-Za-z0-9_]{1,32}$", description="System identifier for the input.")]
    label: Annotated[I18nText, Field(description="Localized label for the UI.")]
    required: Annotated[bool, Field(description="Whether this input is universally required.")]
    is_chat_history: Annotated[
        bool,
        Field(default=False, description="If True, routes to ChatParserService for special parsing."),
    ] = False
    scan_for_performative_patterns: Annotated[
        bool,
        Field(default=False, description="Whether to scan this input for performative AI jargon."),
    ] = False
    is_endorsed_deliverable: Annotated[
        bool,
        Field(
            default=False,
            description=(
                "Whether this input represents an endorsed candidate deliverable (specifically final product "
                "texts and deliverables) where adopting AI co-drafted formulations is valid and not penalized "
                "as Echo Parroting."
            ),
        ),
    ] = False
    input_modes: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Allowed modes: 'file', 'paste', 'text', 'questionnaire', 'assignment'.",
        ),
    ]
    description: Annotated[I18nText, Field(description="Localized description/help text.")]
    ai_description: Annotated[
        str | None,
        Field(
            default=None,
            description="MANDATORY: English cognitive instructions for the LLM. Isolates AI prompt from UI localizations.",
        ),
    ] = None
    questionnaire_definition: Annotated[
        list[QuestionnaireItem],
        Field(default_factory=list, description="Definitions if 'questionnaire' is in input_modes."),
    ]

    @property
    def is_assignment(self) -> bool:
        """Whether this input is configured with the assignment modality.

        Returns:
            True if 'assignment' is in input_modes.
        """
        return "assignment" in self.input_modes

    @model_validator(mode="after")
    def validate_modes(self) -> ExpectedInput:
        """Strict validation for input modes.

        Raises:
            ValueError: If structure is malformed or internally inconsistent.

        Returns:
            The sanitized ExpectedInput matching schema expectations.
        """
        # Enforce strict input modes validation with closed set ALLOWED_INPUT_MODES
        if not self.input_modes:
            msg = f"ExpectedInput '{self.input_key}' must have at least one input_mode."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)

        if not set(self.input_modes).issubset(ALLOWED_INPUT_MODES):
            msg = f"ExpectedInput '{self.input_key}' contains invalid input_modes."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)

        if "assignment" in self.input_modes:
            if "questionnaire" in self.input_modes:
                msg = f"ExpectedInput '{self.input_key}' cannot mix 'questionnaire' with other input modes."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if self.is_chat_history:
                msg = f"ExpectedInput '{self.input_key}' cannot use 'assignment' mode when flagged as chat history."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)

        if "questionnaire" in self.input_modes:
            if self.is_chat_history:
                msg = f"ExpectedInput '{self.input_key}' cannot use 'questionnaire' mode when flagged as chat history."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if len(self.input_modes) > 1:
                msg = f"ExpectedInput '{self.input_key}' cannot mix 'questionnaire' with other input modes."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if not self.questionnaire_definition:
                msg = f"ExpectedInput '{self.input_key}' uses 'questionnaire' mode but lacks definitions."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
        else:
            if self.questionnaire_definition:
                msg = (
                    f"ExpectedInput '{self.input_key}' cannot have questionnaire_definition "
                    "when 'questionnaire' mode is not active."
                )
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)

        if self.is_endorsed_deliverable:
            if self.is_chat_history:
                msg = (
                    f"ExpectedInput '{self.input_key}' cannot be simultaneously marked as both "
                    "is_chat_history and is_endorsed_deliverable."
                )
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if self.is_assignment:
                msg = (
                    f"ExpectedInput '{self.input_key}' cannot be simultaneously marked as both "
                    "an assignment and is_endorsed_deliverable."
                )
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if "questionnaire" in self.input_modes:
                msg = (
                    f"ExpectedInput '{self.input_key}' cannot be simultaneously marked as both "
                    "a questionnaire and is_endorsed_deliverable."
                )
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)

        return self
