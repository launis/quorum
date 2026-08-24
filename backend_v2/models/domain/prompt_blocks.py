"""V2 PromptBlock Polymorphic Domain Models.

Fuses legacy components and matrices into a strict Pydantic V2 discriminated union.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, Self

from pydantic import (
    ConfigDict,
    Field,
    GetCoreSchemaHandler,
    StringConstraints,
    TypeAdapter,
    model_validator,
)
from pydantic_core import core_schema

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.models.v2_core import I18nText, MatrixRow, MatrixScale, TheoryGrounding

StrictStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class PromptBlockBase(V2CoreBase):
    """Base model for polymorphic prompt blocks with shared attributes."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[
        str,
        Field(
            pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$",
            description="Unique identifier for the prompt block. MUST be a valid Stripe Pattern Opaque ID.",
        ),
    ]
    slug: StrictStr = Field(description="URL routing helper field. Strictly no data relation role.")
    organization_id: str | None = Field(default=None, description="Tenant organization ID.")
    label: I18nText = Field(description="Localizable label for the UI.")
    description: I18nText = Field(description="Localizable description or help text for the UI.")
    output_extensions: list[str] = Field(
        default_factory=list,
        description="List of requested XAI output extensions (e.g. 'justification', 'risk_flag').",
    )
    ai_description: str | None = Field(
        default=None,
        description="MANDATORY: English cognitive instructions for the LLM. Completely isolates AI prompt from UI localizations.",
    )
    theory_grounding: TheoryGrounding | None = Field(
        default=None,
        description="Fetches and injects source theory as <theory_context>.",
    )


class MatrixPromptBlock(PromptBlockBase):
    """Matrix prompt block evaluating behavioral claims across BARS scales."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    category_id: Literal[PromptBlockCategory.MATRIX] = PromptBlockCategory.MATRIX
    type: Literal[BlockDataType.FLOAT, BlockDataType.INT] = BlockDataType.FLOAT
    is_evaluative: bool = True
    allow_decimals: bool = False
    allow_contextual_override: bool = False
    is_lightweight_protocol: bool = False
    scales: list[MatrixScale] = Field(..., min_length=1, description="BARS scale definitions with scores and claims.")
    rows: list[MatrixRow] | None = None
    columns: list[I18nText] | None = None
    computed_min: int | None = Field(default=None, description="Derived or calculated minimum score.")
    computed_max: int | None = Field(default=None, description="Derived or calculated maximum score.")

    @model_validator(mode="after")
    def compute_min_max(self) -> Self:
        """Dynamically computes absolute minimum and maximum scores from scales if not provided."""
        if self.scales:
            min_score = min(s.score for s in self.scales)
            max_score = max(s.score for s in self.scales)
            if self.computed_min is None:
                object.__setattr__(self, "computed_min", min_score)
            if self.computed_max is None:
                object.__setattr__(self, "computed_max", max_score)
        return self


class SystemRulePromptBlock(PromptBlockBase):
    """System rule, runtime variables, or task definition prompt block."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    category_id: Literal[
        PromptBlockCategory.SYSTEM_RULE,
        PromptBlockCategory.RUNTIME_VARIABLES,
        PromptBlockCategory.TASK_DEFINITION,
    ] = PromptBlockCategory.SYSTEM_RULE
    type: Literal[
        BlockDataType.INSTRUCTION,
        BlockDataType.STRING,
        BlockDataType.PANEL,
        BlockDataType.COMPLIANCE,
        BlockDataType.QUESTION,
        BlockDataType.CRITERIA,
    ] = BlockDataType.INSTRUCTION
    is_evaluative: bool = False
    allow_decimals: bool = False
    is_lightweight_protocol: bool = False
    instruction_text: StrictStr | None = None


class PersonaPromptBlock(PromptBlockBase):
    """Execution persona or agent role prompt block."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    category_id: Literal[
        PromptBlockCategory.EXECUTION_PERSONA,
        PromptBlockCategory.AGENT_ROLE,
    ] = PromptBlockCategory.EXECUTION_PERSONA
    type: Literal[BlockDataType.INSTRUCTION, BlockDataType.STRING] = BlockDataType.INSTRUCTION
    is_evaluative: bool = False
    allow_decimals: bool = False
    is_lightweight_protocol: bool = False
    role_enforcement: StrictStr | None = None
    tone_directives: list[StrictStr] = Field(default_factory=list)


class ProtocolPromptBlock(PromptBlockBase):
    """Protocol prompt block defining execution extraction mechanics."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    category_id: Literal[PromptBlockCategory.PROTOCOL] = PromptBlockCategory.PROTOCOL
    type: Literal[BlockDataType.INSTRUCTION, BlockDataType.STRING] = BlockDataType.INSTRUCTION
    is_evaluative: bool = False
    allow_decimals: bool = False
    is_lightweight_protocol: bool = False
    protocol_instructions: StrictStr | None = None


AnyPromptBlock = Annotated[
    MatrixPromptBlock | SystemRulePromptBlock | PersonaPromptBlock | ProtocolPromptBlock,
    Field(discriminator="category_id"),
]

_prompt_block_adapter: TypeAdapter[AnyPromptBlock] = TypeAdapter(AnyPromptBlock)


class PromptBlock(PromptBlockBase):
    """Polymorphic PromptBlock domain model and factory.

    Delegates schema generation to the AnyPromptBlock discriminated union
    while providing native Python constructors and validation methods.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        """Returns the core schema of the AnyPromptBlock discriminated union."""
        return _prompt_block_adapter.core_schema

    @classmethod
    def model_validate(  # type: ignore[override]
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: Any = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
        extra: Literal["allow", "ignore", "forbid"] | None = None,
    ) -> AnyPromptBlock:
        """Validates input object against the polymorphic AnyPromptBlock schema."""
        return _prompt_block_adapter.validate_python(
            obj,
            strict=strict,
            from_attributes=from_attributes,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
            extra=extra,
        )

    @classmethod
    def model_validate_json(  # type: ignore[override]
        cls,
        json_data: str | bytes | bytearray,
        *,
        strict: bool | None = None,
        context: Any = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
        extra: Literal["allow", "ignore", "forbid"] | None = None,
    ) -> AnyPromptBlock:
        """Validates JSON string or bytes against the polymorphic AnyPromptBlock schema."""
        return _prompt_block_adapter.validate_json(
            json_data,
            strict=strict,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
            extra=extra,
        )

    @classmethod
    def model_construct(cls, _fields_set: set[str] | None = None, **values: Any) -> AnyPromptBlock:  # type: ignore[override]
        """Constructs concrete PromptBlock subclass instance without validation."""
        category_id = values.get("category_id")
        if category_id == PromptBlockCategory.MATRIX or category_id == "matrix":
            return MatrixPromptBlock.model_construct(_fields_set, **values)
        elif category_id == PromptBlockCategory.SYSTEM_RULE or category_id == "system_rule":
            return SystemRulePromptBlock.model_construct(_fields_set, **values)
        elif category_id in (
            PromptBlockCategory.EXECUTION_PERSONA,
            PromptBlockCategory.AGENT_ROLE,
            "execution_persona",
            "agent_role",
            "persona",
        ):
            return PersonaPromptBlock.model_construct(_fields_set, **values)
        elif category_id == PromptBlockCategory.PROTOCOL or category_id == "protocol":
            return ProtocolPromptBlock.model_construct(_fields_set, **values)
        return SystemRulePromptBlock.model_construct(_fields_set, **values)

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        """Polymorphically instantiates the concrete PromptBlock subclass based on category_id."""
        if cls is not PromptBlock:
            return super().__new__(cls)
        if not kwargs and not args:
            return super().__new__(cls)
        category_id = kwargs.get("category_id")
        if category_id == PromptBlockCategory.MATRIX or category_id == "matrix":
            return MatrixPromptBlock(*args, **kwargs)
        elif category_id == PromptBlockCategory.SYSTEM_RULE or category_id == "system_rule":
            return SystemRulePromptBlock(*args, **kwargs)
        elif category_id in (
            PromptBlockCategory.EXECUTION_PERSONA,
            PromptBlockCategory.AGENT_ROLE,
            "execution_persona",
            "agent_role",
            "persona",
        ):
            return PersonaPromptBlock(*args, **kwargs)
        elif category_id == PromptBlockCategory.PROTOCOL or category_id == "protocol":
            return ProtocolPromptBlock(*args, **kwargs)
        return _prompt_block_adapter.validate_python(kwargs)
