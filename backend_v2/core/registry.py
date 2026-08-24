"""Task Registry for the Cognitive Quorum System.

Provides safe, static, global execution tracking of agentic
routines linked with formal Pydantic schemas.
"""

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import Enum, StrEnum
from typing import Annotated, Any, cast

from fastapi import status
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, create_model

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlock
from backend_v2.models.dtos.evaluation_steps import StepDTOSemantic, StepDTOStrict
from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote
from backend_v2.models.prompts.field_prompts import (
    DESC_CONTEXTUAL_OVERRIDE,
    DESC_EVALUATION_NOTES,
    DESC_EXACT_QUOTES,
    DESC_REASONING_TRACE,
)
from backend_v2.models.view.sdui import HeroInsightBlock, MarkdownBlock
from backend_v2.utils.alias_engine import AliasEngine

logger = logging.getLogger(__name__)


class TaskDefinition(V2CoreBase):
    """Metadata for a registered task.

    Attributes:
        name: Unique task identifier.
        handler: Handing callable logic.
        input_schema: Input Pydantic model.
        output_schema: Output Pydantic model.
        description: Task description text.
        metadata: Arbitrary associated dict metadata.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    handler: Callable[..., Any]
    input_schema: type[BaseModel]
    output_schema: type[BaseModel]
    description: str | None = None
    metadata: dict[str, Any] | None = None


class TaskRegistry:
    """Registry for functional agent tasks.

    Provides safe, static, global execution tracking of agentic
    routines linked with formal Pydantic schemas.

    Attributes:
        _tasks: Internal registry storage mapping task names to TaskDefinitions.
    """

    _tasks: dict[str, TaskDefinition] = {}

    @classmethod
    def register_task(
        cls,
        name: str,
        input_schema: type[BaseModel],
        output_schema: type[BaseModel],
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a function as a task.

        Args:
            name: Unique identifier for the task.
            input_schema: Pydantic model for input validation.
            output_schema: Pydantic model for output validation.
            description: Optional description (defaults to docstring).
            metadata: Optional metadata for the task.

        Returns:
            A decorator function that registers the decorated callable and returns it.

        Raises:
            AppException: Triggered with CONFIGURATION_ERROR if the task name is already registered.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            if name in cls._tasks:
                msg = f"Task with name '{name}' is already registered."
                logger.error("[TaskRegistry] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

            desc = description
            if desc is None and func.__doc__ is not None:
                desc = func.__doc__

            cls._tasks[name] = TaskDefinition(
                name=name,
                handler=func,
                input_schema=input_schema,
                output_schema=output_schema,
                description=desc,
                metadata=metadata,
            )
            return func

        return decorator

    @classmethod
    def get(cls, name: str) -> TaskDefinition:
        """Retrieve a task definition by name.

        Args:
            name: Task name identifier.

        Returns:
            The corresponding registered TaskDefinition structure.

        Raises:
            AppException: Triggered with RESOURCE_NOT_FOUND if the requested task does not exist.
        """
        if name not in cls._tasks:
            msg = f"Task '{name}' not found in registry."
            logger.error("[TaskRegistry] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_404_NOT_FOUND,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "task_name": name},
            )
        return cls._tasks[name]


# --- SDUI Schema Builder Registry ---


class SchemaBuilderStrategy(ABC):
    """Abstract base for SDUI schema builder strategies."""

    def __init__(self, resolve_i18n: Callable[..., str]) -> None:
        """Initialize with I18n resolution capability."""
        self._resolve_i18n = resolve_i18n

    @abstractmethod
    def build_schema(
        self,
        schema_name: str,
        criteria: list[PromptBlock],
        has_shuffled_atoms: bool = False,
        target_locale: str = "en",
        *,
        strictness_level: int,
        source_document_ids: list[str] | None = None,
        allowed_atom_ids: list[str] | None = None,
        allowed_dynamic_keys: list[str] | None = None,
        max_evaluations: int | None = None,
        dag_results: dict[str, Any] | None = None,
    ) -> type[BaseModel]:
        """Build and return the Pydantic model for this SDUI type."""
        pass


_SDUI_SCHEMA_REGISTRY: dict[str, type[SchemaBuilderStrategy]] = {}


def register_sdui_schema(sdui_type: str) -> Callable[[type[SchemaBuilderStrategy]], type[SchemaBuilderStrategy]]:
    """Decorator to register a SchemaBuilderStrategy for an SDUI type."""

    def decorator(cls_strategy: type[SchemaBuilderStrategy]) -> type[SchemaBuilderStrategy]:
        if sdui_type in _SDUI_SCHEMA_REGISTRY:
            msg = f"SDUI schema strategy '{sdui_type}' is already registered."
            logger.error("[SchemaRegistry] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
        _SDUI_SCHEMA_REGISTRY[sdui_type] = cls_strategy
        return cls_strategy

    return decorator


def get_schema_strategy(sdui_type: str) -> type[SchemaBuilderStrategy]:
    """Resolve strategy by SDUI type."""
    if sdui_type not in _SDUI_SCHEMA_REGISTRY:
        msg = f"Fail-Fast: Unknown expected_sdui_type '{sdui_type}'"
        logger.error("[SchemaRegistry] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )
    return _SDUI_SCHEMA_REGISTRY[sdui_type]


def _coerce_bool(v: Any) -> Any:
    """Coerces strings like 'true'/'false' into actual booleans for Vertex AI type safety."""
    if isinstance(v, str):
        v_lower = v.strip().lower()
        if v_lower in {"true", "1", "yes"}:
            return True
        if v_lower in {"false", "0", "no"}:
            return False
    return v


CoercedBool = Annotated[bool, BeforeValidator(_coerce_bool)]


class EvidenceType(StrEnum):
    """Categorizes the type of evidence discovered during TDA extraction."""

    EXPLICIT_QUOTE = "EXPLICIT_QUOTE"
    IMPLIED_INTENT = "IMPLIED_INTENT"
    NO_EVIDENCE = "NO_EVIDENCE"


class StrippedBaseTDAExtraction(BaseModel):
    """Stripped core Pydantic model for Micro-CoT extraction without localized anchors to save tokens."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    exact_quotes: list[LLMExtractedQuote] = Field(
        default_factory=list,
        description=DESC_EXACT_QUOTES,
    )
    contextual_override: bool = Field(
        description=DESC_CONTEXTUAL_OVERRIDE,
    )
    semantic_reasoning: str = Field(
        description="Write an extensive analytical reasoning trace explaining your decision-making process. You MUST use Markdown formatting (e.g. bolding, bullet points, headers) INSIDE this JSON string to structure your analysis.",
    )


class StrippedBaseMatrixXAI(BaseModel):
    """Pydantic model for matrix XAI qualitative extensions with stripped descriptions."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    semantic_reasoning: str = Field(
        description="Write an extensive analytical reasoning trace explaining your decision-making process. You MUST use Markdown formatting (e.g. bolding, bullet points, headers) INSIDE this JSON string to structure your analysis.",
    )


@register_sdui_schema("markdown")
class MarkdownSchemaStrategy(SchemaBuilderStrategy):
    """Returns the static MarkdownBlock."""

    def build_schema(
        self,
        schema_name: str,
        criteria: list[PromptBlock],
        has_shuffled_atoms: bool = False,
        target_locale: str = "en",
        *,
        strictness_level: int,
        source_document_ids: list[str] | None = None,
        allowed_atom_ids: list[str] | None = None,
        allowed_dynamic_keys: list[str] | None = None,
        max_evaluations: int | None = None,
        dag_results: dict[str, Any] | None = None,
    ) -> type[BaseModel]:
        return MarkdownBlock


@register_sdui_schema("hero_insight")
class HeroInsightSchemaStrategy(SchemaBuilderStrategy):
    """Returns the static HeroInsightBlock."""

    def build_schema(
        self,
        schema_name: str,
        criteria: list[PromptBlock],
        has_shuffled_atoms: bool = False,
        target_locale: str = "en",
        *,
        strictness_level: int,
        source_document_ids: list[str] | None = None,
        allowed_atom_ids: list[str] | None = None,
        allowed_dynamic_keys: list[str] | None = None,
        max_evaluations: int | None = None,
        dag_results: dict[str, Any] | None = None,
    ) -> type[BaseModel]:
        return HeroInsightBlock


@register_sdui_schema("grid")
class GridSchemaStrategy(SchemaBuilderStrategy):
    """Encapsulates dynamic column generation logic."""

    def build_schema(
        self,
        schema_name: str,
        criteria: list[PromptBlock],
        has_shuffled_atoms: bool = False,
        target_locale: str = "en",
        *,
        strictness_level: int,
        source_document_ids: list[str] | None = None,
        allowed_atom_ids: list[str] | None = None,
        allowed_dynamic_keys: list[str] | None = None,
        max_evaluations: int | None = None,
        dag_results: dict[str, Any] | None = None,
    ) -> type[BaseModel]:

        step_strict_class: type[BaseModel] = StepDTOStrict
        step_semantic_class: type[BaseModel] = StepDTOSemantic

        if source_document_ids is not None or allowed_atom_ids is not None or allowed_dynamic_keys is not None:
            DocIdsLiteralType = AliasEngine.build_doc_ids_literal(source_document_ids, allowed_dynamic_keys)
            QuoteIdsLiteralType = AliasEngine.build_quote_ids_literal(
                source_document_ids, allowed_atom_ids, allowed_dynamic_keys
            )

            FinalDocIdsType = DocIdsLiteralType
            FinalQuoteIdsType = QuoteIdsLiteralType

            DynamicLLMExtractedQuote = create_model(
                "DynamicLLMExtractedQuote",
                source_id=(
                    FinalQuoteIdsType,
                    Field(
                        ...,
                        description="Auto-resolved document ID (e.g. doc0, a1)",
                    ),
                ),
                text=(str, Field(..., description="Tarkka lainaus tekstistä")),
                __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
            )

            step_strict_class = create_model(
                "StepDTOStrictDynamic",
                __base__=StepDTOStrict,
                source_document_aliases=(
                    list[FinalDocIdsType],  # type: ignore
                    Field(
                        ...,
                        description="Dynamic literals corresponding to available documents.",
                    ),
                ),
                exact_quotes=(
                    list[DynamicLLMExtractedQuote],
                    Field(
                        default_factory=list,
                        description=DESC_EXACT_QUOTES,
                    ),
                ),
                __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
            )
            step_semantic_class = create_model(
                "StepDTOSemanticDynamic",
                __base__=StepDTOSemantic,
                source_document_aliases=(
                    list[FinalDocIdsType],  # type: ignore
                    Field(
                        ...,
                        description="Dynamic literals corresponding to available documents.",
                    ),
                ),
                exact_quotes=(
                    list[DynamicLLMExtractedQuote],
                    Field(
                        default_factory=list,
                        description=DESC_EXACT_QUOTES,
                    ),
                ),
                __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
            )

        fields: dict[str, Any] = {}

        if has_shuffled_atoms:

            class AtomResponseBase(BaseModel):
                model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
                atom_id: str = Field(
                    ...,
                    description="The EXACT system identifier. MUST exactly match one of the short aliases provided in <BLIND_ATOMS_TO_EVALUATE> (e.g. 'a0', 'a1').",
                    json_schema_extra={"pattern": AliasEngine.ALIAS_REGEX_PATTERN},
                )

            if strictness_level >= 100:
                AtomResponseClass = create_model(
                    "AtomResponseStrict", __base__=cast(Any, (step_strict_class, AtomResponseBase))
                )
            else:
                AtomResponseClass = create_model(  # type: ignore[misc]
                    "AtomResponseSemantic", __base__=cast(Any, (step_semantic_class, AtomResponseBase))
                )

            eval_type: Any = list[AtomResponseClass]
            fields["evaluations"] = (
                eval_type,
                Field(
                    ...,
                    description="List of atomic evaluations. You MUST evaluate ONLY the exact atoms explicitly listed in <BLIND_ATOMS_TO_EVALUATE>. You MUST include the exact 'atom_id' for each evaluation. Do NOT hallucinate, invent, or evaluate any unlisted concepts.",
                ),
            )

        def get_cat(c: PromptBlock) -> str:
            return str(c.category_id.value) if isinstance(c.category_id, Enum) else str(c.category_id or "criteria")

        matrix_blocks = [c for c in criteria if isinstance(c, MatrixPromptBlock)]
        if matrix_blocks:
            global_matrices_fields: dict[str, Any] = {}
            for matrix in matrix_blocks:
                matrix_id = matrix.id
                if not matrix_id:
                    continue

                if dag_results is not None and matrix.scales:
                    has_evidence = False
                    for scale in matrix.scales:
                        if has_evidence:
                            break
                        for claim in scale.claims:
                            if has_evidence:
                                break
                            for tda in claim.tda_assertions:
                                atom_id = str(tda.tda_id)
                                status = dag_results.get(atom_id, {}).get("status", "")
                                if hasattr(status, "name"):
                                    status = status.name
                                if str(status) == "PASSED":
                                    has_evidence = True
                                    break
                    if not has_evidence:
                        logger.warning("Zero evidence found for Matrix %s, omitting from LLM schema", matrix_id)
                        continue

                label_str = self._resolve_i18n(matrix.label, target_locale) if matrix.label else ""
                desc_val = f"Global matrix evaluation for '{matrix_id}' ({label_str})."
                if matrix.ai_description:
                    desc_val += f" Objective: {matrix.ai_description}"

                matrix_base_class = StrippedBaseMatrixXAI
                final_type: Any = matrix_base_class
                if matrix.output_extensions:
                    matrix_dynamic_fields: dict[str, Any] = {}
                    core_aliases = {"justification", "citation", "missing_context", "contextual_override", "source_id"}
                    numeric_extensions = {"confidence"}
                    boolean_extensions = {"risk_flag"}

                    for ext in matrix.output_extensions:
                        if ext in core_aliases:
                            continue

                        if ext in numeric_extensions:
                            matrix_dynamic_fields[ext] = (
                                float,
                                Field(
                                    ...,
                                    description=f"Numeric score (0.0 to 1.0) for '{ext}'. Must be a float, e.g., 0.85.",
                                ),
                            )
                        elif ext in boolean_extensions:
                            matrix_dynamic_fields[ext] = (
                                CoercedBool,
                                Field(
                                    ...,
                                    description=f"Boolean flag for '{ext}'. MUST be the native JSON boolean type (true/false) without quotes. Do NOT output a string.",
                                ),
                            )
                        else:
                            matrix_dynamic_fields[ext] = (
                                str,
                                Field(..., description=f"Detailed textual explanation or citation for '{ext}'."),
                            )

                    if len(matrix_dynamic_fields) > 6:
                        logger.warning(
                            "[SchemaRegistry] Matrix block '%s' has %d output_extensions. "
                            "Risk of LLM lazy generation with Flash models.",
                            matrix_id,
                            len(matrix_dynamic_fields),
                        )

                    if matrix_dynamic_fields:
                        final_type = create_model(
                            f"MatrixExtraction_{matrix_id}",
                            __base__=matrix_base_class,
                            __config__=ConfigDict(extra="forbid", strict=True, frozen=True, populate_by_name=True),
                            **matrix_dynamic_fields,
                        )

                global_matrices_fields[matrix_id] = (final_type, Field(..., description=desc_val))

            if global_matrices_fields:
                GlobalMatricesModel = create_model(
                    "GlobalMatrices",
                    __config__=ConfigDict(extra="forbid", strict=True, frozen=True, populate_by_name=True),
                    **global_matrices_fields,
                )
                fields["global_matrices"] = (
                    GlobalMatricesModel,
                    Field(
                        ...,
                        description="Global matrix evaluations that apply to the entire response or document as a whole. You MUST evaluate all global matrices here.",
                    ),
                )

        if has_shuffled_atoms:
            schema_criteria = []
        else:
            schema_criteria = [c for c in criteria if get_cat(c) != "matrix"]

        for index, crit in enumerate(schema_criteria):
            crit_id = crit.id
            if not crit_id:
                logger.warning("[SchemaRegistry] Found criterion without a valid string 'id': %s. Skipping.", crit)
                continue

            alias_name = f"eval_{index + 1}"

            if crit.category_id != "matrix" and crit.type == "instruction":
                label_str = self._resolve_i18n(crit.label, target_locale) if crit.label else ""
                cat_val = (
                    crit.category_id.value
                    if isinstance(crit.category_id, Enum)
                    else (crit.category_id or "instruction")
                )

                desc_val = f"Instruction field for {cat_val} block '{crit_id}' ({label_str})."

                fields[crit_id] = (
                    str,
                    Field(
                        ...,
                        description=desc_val,
                        alias=alias_name,
                    ),
                )
                continue

            if not crit.label:
                msg = f"PromptBlock '{crit_id}' is missing strict evaluation parameter: label."
                logger.error(
                    "PromptBlock structurally invalid.",
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "block_id": crit_id},
                )
                raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})

            base_class: type[BaseModel]
            if crit.category_id == "matrix":
                base_class = StrippedBaseMatrixXAI
            else:
                base_class = step_strict_class

            label_str = self._resolve_i18n(crit.label, target_locale) if crit.label else ""
            cat_val = crit.category_id.value if isinstance(crit.category_id, Enum) else (crit.category_id or "criteria")
            desc_val = f"Evaluation field for {cat_val} block '{crit_id}' ({label_str})."

            if crit.output_extensions:
                dynamic_fields: dict[str, Any] = {}
                core_aliases = {"justification", "citation", "missing_context", "contextual_override", "source_id"}
                numeric_extensions = {"confidence"}
                boolean_extensions = {"risk_flag"}

                for ext in crit.output_extensions:
                    if ext in core_aliases:
                        continue

                    if ext in numeric_extensions:
                        dynamic_fields[ext] = (
                            float,
                            Field(
                                ...,
                                description=f"Numeric score (0.0 to 1.0) for '{ext}'.",
                            ),
                        )
                    elif ext in boolean_extensions:
                        dynamic_fields[ext] = (
                            CoercedBool,
                            Field(
                                ...,
                                description=f"Boolean flag for '{ext}'. MUST be the native JSON boolean type (true/false) without quotes. Do NOT output a string.",
                            ),
                        )
                    else:
                        dynamic_fields[ext] = (
                            str,
                            Field(
                                ...,
                                description=f"Detailed textual explanation or citation for '{ext}'.",
                            ),
                        )

                if dynamic_fields:
                    DynamicBlock = create_model(
                        f"BlockExtraction_{crit_id}",
                        __base__=base_class,
                        __config__=ConfigDict(extra="forbid", strict=True, frozen=True, populate_by_name=True),
                        **dynamic_fields,
                    )
                    fields[crit_id] = (DynamicBlock, Field(..., description=desc_val, alias=alias_name))
                else:
                    fields[crit_id] = (base_class, Field(..., description=desc_val, alias=alias_name))
            else:
                fields[crit_id] = (base_class, Field(..., description=desc_val, alias=alias_name))

        fields["evaluation_notes"] = (
            str,
            Field(
                default="",
                description=DESC_EVALUATION_NOTES,
            ),
        )
        fields["reasoning_trace"] = (
            str,
            Field(
                default="",
                description=DESC_REASONING_TRACE.format(target_locale=target_locale.upper()),
            ),
        )

        if not fields:
            fields["acknowledged_instruction"] = (
                str,
                Field(default="yes", description="Fallback confirmation that all instructions have been acknowledged."),
            )

        try:
            DynamicModel = create_model(
                schema_name,
                __config__=ConfigDict(extra="forbid", strict=True, frozen=True, populate_by_name=True),
                **fields,
            )
            return cast(type[BaseModel], DynamicModel)
        except Exception as e:
            msg = f"Critical failure while dynamically compiling LLM execution schema '{schema_name}'."
            logger.error(
                "Dynamic schema compilation failed.",
                extra={
                    "error_code": ErrorCodes.INTERNAL_SERVER_ERROR.name,
                    "schema_name": schema_name,
                    "detail": str(e),
                },
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR},
            ) from e
