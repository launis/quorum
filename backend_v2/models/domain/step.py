"""Domain models for workflow steps, step rules, roles, and expected inputs.

SSOT for Step, StepRule, Role, QuestionnaireItem, ExpectedInput, and ALLOWED_INPUT_MODES.
"""

from __future__ import annotations

import logging
import uuid
from typing import Annotated, Literal

from pydantic import ConfigDict, Field, model_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, I18nText, V2CoreBase
from backend_v2.models.enums import CognitiveTier, LaxCognitiveTier, LaxStepType, StepType

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

    id: str = Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Unique UUID for storage optionally")
    slug: str = Field(description="Human-readable identifier (e.g., 'step_guard')")
    organization_id: str | None = Field(default=None, description="Tenant organization ID.")
    name: I18nText = Field(description="Localized step name")
    description: I18nText | None = Field(default=None, description="Detailed step context")
    type: LaxStepType = Field(default=StepType.LLM, description="Step execution type (llm or native logic)")
    hook: str | None = Field(default=None, description="Native Python hook to execute if type is 'logic'")
    role_block_id: str | None = Field(
        default=None,
        pattern=OPAQUE_STRIPE_ID_REGEX,
        description="Reference to role block (e.g. blk_role_critic)",
    )
    extraction_protocol_block_id: str | None = Field(
        default=None,
        pattern=OPAQUE_STRIPE_ID_REGEX,
        description="Reference to global evidence extraction protocol block",
    )
    execution_persona_block_id: str | None = Field(
        default=None,
        pattern=OPAQUE_STRIPE_ID_REGEX,
        description="Reference to the Execution Persona PromptBlock",
    )
    criteria_block_ids: list[str] = Field(
        default_factory=list,
        description="References to matrix or text blocks",
    )
    pre_hooks: list[str] = Field(
        default_factory=list, description="Native Python functions to execute BEFORE LLM context building."
    )
    post_hooks: list[str] = Field(
        default_factory=list, description="Native Python functions to execute AFTER LLM generation."
    )
    safety: Literal["safe", "unsafe"] = Field(
        default="safe",
        description="Marks step as safe (read-only MCP) or unsafe (email/API mutations) for strict execution security.",
    )
    allowed_mcp_tools: list[str] = Field(
        default_factory=list, description="List of allowed MCP tools for this step (e.g. ['mcp_tavily_search'])."
    )
    cognitive_tier: LaxCognitiveTier = Field(
        default=CognitiveTier.FAST,
        description="Step-level cognitive tier profile (e.g., 'fast', 'deep', 'reasoning').",
    )
    expected_inputs: list[str] = Field(
        default_factory=list,
        description="List of expected input keys required for this step. Replaces free-text generic routing.",
    )
    # Phase 1, Step 2: Workflow context governance field
    is_system_core: Annotated[
        bool,
        Field(description="Whether this step blueprint is a protected system foundational component."),
    ] = False

    @model_validator(mode="after")
    def validate_step_consistency(self) -> Step:
        """Strict fail-fast validation to ensure Step is structurally complete.

        Raises:
            AppException: If structure is malformed or internally inconsistent.

        Returns:
            The sanitized Step matching schema expectations.
        """
        if self.type == "llm":
            if not self.cognitive_tier or self.cognitive_tier not in CognitiveTier:
                msg = f"LLM Step '{self.id}' must declare an explicit cognitive_tier (Zero-Fallback Rule)."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if not self.criteria_block_ids:
                msg = f"LLM Step '{self.id}' must define at least one criteria_block_id."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if not self.extraction_protocol_block_id:
                msg = f"LLM Step '{self.id}' must define a valid extraction_protocol_block_id."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
        if self.type == "logic" and not self.hook:
            msg = f"Logic Step '{self.id}' must define a native 'hook' execution target."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return self


class StepRule(V2CoreBase):
    """Execution step mapping (DAG Router Node)."""

    id: str = Field(
        default_factory=lambda: f"sr_{uuid.uuid4().hex[:16]}",
        pattern=OPAQUE_STRIPE_ID_REGEX,
        description="Unique node ID in the workflow (e.g. blk_node_1).",
    )
    task_blueprint: str = Field(
        min_length=1, description="ID reference to the isolated Step (e.g., 'step_f15853d2584e4096aeb60f11a3e6ea7c')"
    )
    depends_on: list[str] = Field(default_factory=list, description="IDs of steps that must complete first.")
    input_mappings: dict[str, str] = Field(
        default_factory=dict,
        description='Maps upstream results to LLM inputs. e.g. {"context": "$inputs.document"}',
    )
    expected_sdui_type: Annotated[
        Literal["markdown", "hero_insight", "grid"] | None,
        Field(description="Declares the expected SDUI output schema for schema compilation."),
    ] = None
    # Phase 1, Step 2: Synthesis context governance field
    is_synthesis_source: Annotated[
        bool,
        Field(description="Whether this step's narrative text output is forwarded to the synthesis LLM context."),
    ] = True

    ui_pos_x: float = Field(default=0.0, description="X coordinate on the 2D DAG canvas.")
    ui_pos_y: float = Field(default=0.0, description="Y coordinate on the 2D DAG canvas.")

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

    id: str = Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Unique Role ID")
    name: I18nText
    model_role: str = Field(description='Maps to SystemConfig.model_mappings (e.g., "analyst_model").')
    type: str | None = Field(default="role", description="Component type indicator.")
    pre_hooks: list[str] = Field(default_factory=list, description="List of registered hook logic to run BEFORE llm.")
    post_hooks: list[str] = Field(default_factory=list, description="List of registered hook logic to run AFTER llm.")


class QuestionnaireItem(V2CoreBase):
    """A single question definition within a dynamic questionnaire."""

    model_config = ConfigDict(strict=True, extra="forbid")

    question_id: str = Field(description="Unique identifier for the question (e.g., 'q1').")
    question: I18nText = Field(description="Localized question text.")
    type: str = Field(description="Input type, e.g., 'text'.")


class ExpectedInput(V2CoreBase):
    """Definition of an input required by a workflow."""

    model_config = ConfigDict(strict=True, extra="forbid")

    input_key: str = Field(pattern=r"^[A-Za-z0-9_]{1,32}$", description="System identifier for the input.")
    label: I18nText = Field(description="Localized label for the UI.")
    required: bool = Field(description="Whether this input is universally required.")
    is_chat_history: bool = Field(
        default=False, description="If True, routes to ChatParserService for special parsing."
    )
    scan_for_performative_patterns: bool = Field(
        default=False, description="Whether to scan this input for performative AI jargon."
    )
    is_endorsed_deliverable: bool = Field(
        default=False,
        description=(
            "Whether this input represents an endorsed candidate deliverable (specifically final product "
            "texts and deliverables) where adopting AI co-drafted formulations is valid and not penalized "
            "as Echo Parroting."
        ),
    )
    input_modes: list[str] = Field(
        default_factory=list, description="Allowed modes: 'file', 'paste', 'text', 'questionnaire', 'assignment'."
    )
    description: I18nText = Field(description="Localized description/help text.")
    ai_description: str | None = Field(
        default=None,
        description="MANDATORY: English cognitive instructions for the LLM. Isolates AI prompt from UI localizations.",
    )
    questionnaire_definition: list[QuestionnaireItem] = Field(
        default_factory=list, description="Definitions if 'questionnaire' is in input_modes."
    )

    @property
    def is_assignment(self) -> bool:
        """Whether this input is configured with the assignment modality.

        Returns:
            bool: True if 'assignment' is in input_modes.
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
        # Phase 1, Step 1.2: Strict input modes validation with closed set ALLOWED_INPUT_MODES
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
