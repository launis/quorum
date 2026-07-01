from __future__ import annotations

"""Schema Factory for generating dynamic Pydantic schemas for LLM Structured Outputs.

Extracts and centralizes all dynamic Pydantic model creation logic from the
monolithic PromptCompiler, following SRP (Rule 88).
"""

import logging
from collections.abc import Callable
from enum import Enum
from typing import TYPE_CHECKING, Annotated, Any, Literal, cast

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, create_model

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.dtos.evaluation_steps import StepDTOSemantic, StepDTOStrict
from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote
from backend_v2.models.prompts.field_prompts import DESC_CONTEXTUAL_OVERRIDE, DESC_EXACT_QUOTES
from backend_v2.models.v2_core import PromptBlock
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)


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


class EvidenceType(str, Enum):
    """Categorizes the type of evidence discovered during TDA extraction."""

    EXPLICIT_QUOTE = "EXPLICIT_QUOTE"
    IMPLIED_INTENT = "IMPLIED_INTENT"
    NO_EVIDENCE = "NO_EVIDENCE"


class StrippedBaseMatrixXAI(BaseModel):
    """Pydantic model for matrix XAI qualitative extensions with stripped descriptions."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    semantic_reasoning: str = Field(
        default="",
        description="Write an extensive analytical reasoning trace explaining your decision-making process. You MUST use Markdown formatting (e.g. bolding, bullet points, headers) INSIDE this JSON string to structure your analysis.",
    )


class StrippedBaseTDAExtraction(BaseModel):
    """Stripped core Pydantic model for Micro-CoT extraction without localized anchors to save tokens."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    exact_quotes: list[LLMExtractedQuote] = Field(
        default_factory=list,
        max_length=3,
        description=DESC_EXACT_QUOTES,
    )
    contextual_override: bool = Field(
        description=DESC_CONTEXTUAL_OVERRIDE,
    )
    semantic_reasoning: str = Field(
        description="Write an extensive analytical reasoning trace explaining your decision-making process. You MUST use Markdown formatting (e.g. bolding, bullet points, headers) INSIDE this JSON string to structure your analysis.",
    )


class SchemaFactory:
    """Centralizes dynamic Pydantic V2 schema generation for LLM Structured Outputs.

    Encapsulates all create_model() operations previously embedded in the
    monolithic PromptCompiler, enforcing Single Responsibility Principle.

    Attributes:
        _resolve_i18n: Injected callable for resolving I18n text objects to locale strings.
    """

    def __init__(self, resolve_i18n_fn: Callable[..., str]) -> None:
        """Initialize SchemaFactory with an I18n resolution callable.

        Args:
            resolve_i18n_fn: Callable that resolves I18n objects to strings given a locale.
        """
        self._resolve_i18n = resolve_i18n_fn
        self._schema_cache: dict[str, type[BaseModel]] = {}

    def build_dynamic_schema(
        self,
        schema_name: str,
        criteria: list[PromptBlock],
        has_search_result: bool = False,
        has_shuffled_atoms: bool = False,
        target_locale: str = "en",
        *,
        strictness_level: int,
        source_document_ids: list[str] | None = None,
    ) -> type[BaseModel]:
        """Build a dynamic Pydantic V2 model for LLM Structured Outputs.

        Args:
            schema_name: Name for the generated Pydantic model class.
            criteria: List of PromptBlock definitions driving schema fields.
            has_search_result: Whether to include search result extensions.
            has_shuffled_atoms: Whether to include shuffled atom evaluation fields.
            target_locale: Target language code for label resolution.
            strictness_level: Strictness level to control field leniency.
            source_document_ids: Dynamic literals corresponding to available documents.

        Returns:
            A dynamically generated Pydantic model class.
        """
        # P4: Prevent Pydantic compilation explosion on 200+ step DAGs by hashing criteria
        # and delegating to an LRU cached private method.
        # Epic 43: Serialize strictly typed PromptBlocks back to json for the cache key.
        criteria_ids = "_".join(sorted(str(c.id) for c in criteria if c.id))
        doc_ids_str = "_".join(sorted(source_document_ids)) if source_document_ids else ""
        cache_key = f"{schema_name}_{criteria_ids}_{has_search_result}_{has_shuffled_atoms}_{target_locale}_{strictness_level}_{doc_ids_str}"

        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]

        return self._build_dynamic_schema_internal(
            schema_name,
            has_search_result,
            has_shuffled_atoms,
            target_locale,
            strictness_level,
            criteria,
            cache_key,
            source_document_ids=source_document_ids,
        )

    def _build_dynamic_schema_internal(
        self,
        schema_name: str,
        has_search_result: bool,
        has_shuffled_atoms: bool,
        target_locale: str,
        strictness_level: int,
        criteria: list[PromptBlock],
        cache_key: str,
        *,
        source_document_ids: list[str] | None = None,
    ) -> type[BaseModel]:
        """Build a dynamic Pydantic V2 model for LLM Structured Outputs.

        Radically stripped to enforce BaseTDAExtraction determinism and prevent Vertex AI state limits.

        Args:
            schema_name: Name for the generated Pydantic model class.
            has_search_result: Whether to include search result extensions.
            has_shuffled_atoms: Whether to include shuffled atom evaluation fields.
            target_locale: Target language code for label resolution.
            criteria: List of PromptBlock objects to build the schema from.
            cache_key: Key to save the built schema in cache.

        Returns:
            A dynamically generated Pydantic model class.

        Raises:
            ConfigurationError (ErrorCodes.VALIDATION_FAILED): If a PromptBlock is missing required fields.
            AppException (ErrorCodes.INTERNAL_SERVER_ERROR): If dynamic schema compilation fails critically.
        """
        # Resolve target base classes, overriding source_document_ids if requested
        step_strict_class = StepDTOStrict
        step_semantic_class = StepDTOSemantic

        if source_document_ids is not None:
            choices = list(set(source_document_ids))
            if not choices:
                choices = ["N/A"]
            elif "N/A" not in choices:
                choices.append("N/A")
            choices.sort()
            DocIdsLiteral = Literal[tuple(choices)]  # type: ignore

            step_strict_class = create_model(
                "StepDTOStrictDynamic",
                __base__=StepDTOStrict,
                source_document_aliases=(
                    list[DocIdsLiteral],  # type: ignore
                    Field(..., description="Dynamic literals corresponding to available documents."),
                ),
                __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
            )
            step_semantic_class = create_model(
                "StepDTOSemanticDynamic",
                __base__=StepDTOSemantic,
                source_document_aliases=(
                    list[DocIdsLiteral],  # type: ignore
                    Field(..., description="Dynamic literals corresponding to available documents."),
                ),
                __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
            )

        fields: dict[str, Any] = {
            "reasoning_trace": (
                str,
                Field(
                    ...,
                    description="Write an extensive analytical reasoning trace explaining your decision-making process. You MUST use Markdown formatting (e.g. bolding, bullet points, headers) INSIDE this JSON string to structure your analysis.",
                ),
            ),
            "evaluation_notes": (
                str,
                Field(
                    ...,
                    description="General qualitative evaluation notes and analytical synthesis.",
                ),
            ),
        }

        if has_shuffled_atoms:

            class AtomResponseBase(BaseModel):
                """Base identity model providing the atom_id field for blind evaluations."""

                model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
                atom_id: str = Field(
                    ...,
                    description="The EXACT system identifier. MUST exactly match one of the short aliases provided in <BLIND_ATOMS_TO_EVALUATE> (e.g. 'a0', 'a1').",
                )

            # Phase D & E: Proactive Routing
            # For shuffled atoms, we use a single base class. If strictness >= 100, override is completely denied.
            # V3 Fix: Pydantic multiple inheritance resolves right-to-left for fields.
            # By placing AtomResponseBase LAST in the inheritance chain, its fields (atom_id)
            # are collected FIRST by Pydantic's reverse-MRO iteration, ensuring the LLM emits it first.
            AtomResponse: Any
            if strictness_level >= 100:

                class AtomResponseStrict(step_strict_class, AtomResponseBase):  # type: ignore
                    pass

                AtomResponse = AtomResponseStrict
            else:

                class AtomResponseSemantic(step_semantic_class, AtomResponseBase):  # type: ignore
                    pass

                AtomResponse = AtomResponseSemantic

            fields["evaluations"] = (
                list[AtomResponse],
                Field(
                    ...,
                    max_length=get_settings().schema_max_evaluations,
                    description="List of atomic evaluations. You MUST evaluate ONLY the exact atoms explicitly listed in <BLIND_ATOMS_TO_EVALUATE>. You MUST include the exact 'atom_id' for each evaluation. Do NOT hallucinate, invent, or evaluate any unlisted concepts.",
                ),
            )

        # Global Matrices Refactor: Extract all matrix blocks to a native GlobalMatrices model
        # to prevent them from mingling with eval_N aliases at the root schema layer.
        def get_cat(c: PromptBlock) -> str:
            return str(c.category_id.value) if isinstance(c.category_id, Enum) else str(c.category_id or "criteria")

        matrix_blocks = [c for c in criteria if get_cat(c) == "matrix"]
        if matrix_blocks:
            global_matrices_fields: dict[str, Any] = {}
            for matrix in matrix_blocks:
                matrix_id = matrix.id
                if not matrix_id:
                    continue

                label_str = self._resolve_i18n(matrix.label, target_locale) if matrix.label else ""
                desc_val = f"Global matrix evaluation for '{matrix_id}' ({label_str})."
                if matrix.ai_description:
                    desc_val += f" Objective: {matrix.ai_description}"

                # Matrix blocks also support output extensions
                matrix_base_class = StrippedBaseMatrixXAI
                final_type: Any = matrix_base_class
                if matrix.output_extensions:
                    matrix_dynamic_fields: dict[str, Any] = {}
                    core_aliases = {"justification", "citation", "missing_context", "contextual_override"}
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

        # Epic 56 Phase 4 / Bugfix: We MUST filter out standard "criteria" blocks if has_shuffled_atoms is True.
        # Matrix blocks are ALWAYS excluded from this loop because they now live in global_matrices.
        # Epic 92 Bugfix: If has_shuffled_atoms is True, we must completely empty schema_criteria
        # so that NO eval_X fields are generated at the root level, otherwise Pydantic hits Max schema retries.
        if has_shuffled_atoms:
            schema_criteria = []
        else:
            schema_criteria = [c for c in criteria if get_cat(c) != "matrix"]

        for index, crit in enumerate(schema_criteria):
            crit_id = crit.id
            if not crit_id:
                logger.warning("[SchemaFactory] Found criterion without a valid string 'id': %s. Skipping.", crit)
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
                if crit.ai_description:
                    desc_val += f" Objective: {crit.ai_description}"

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

            # Phase 1, Step 4: Use stripped base models to resolve Vertex AI state limit
            # Phase D & E: Dynamic Zero-Trust Routing based on rule requirements and strictness level
            base_class: type[BaseModel]
            if crit.category_id == "matrix":
                base_class = StrippedBaseMatrixXAI
            else:
                rule_allows_override = False
                if crit.scales:
                    for scale in crit.scales:
                        for claim in scale.claims:
                            for tda in claim.tda_assertions:
                                if getattr(tda, "allow_contextual_override", False):
                                    rule_allows_override = True

                if strictness_level >= 100 or not rule_allows_override:
                    base_class = step_strict_class
                else:
                    base_class = step_semantic_class

            # Dynamic short and concise description for the LLM to understand this specific evaluation field
            label_str = self._resolve_i18n(crit.label, target_locale) if crit.label else ""
            cat_val = crit.category_id.value if isinstance(crit.category_id, Enum) else (crit.category_id or "criteria")
            desc_val = f"Evaluation field for {cat_val} block '{crit_id}' ({label_str})."
            # plan: Restore full ai_description without truncation since FSM
            # serving limit is bypassed via strict=False.
            if crit.ai_description:
                desc_val += f" Objective: {crit.ai_description}"

            if crit.output_extensions:
                dynamic_fields: dict[str, Any] = {}
                core_aliases = {"justification", "citation", "missing_context", "contextual_override"}

                # RCA Fix: Extensions that must be numeric or boolean for downstream
                # blueprint.py _coerce_float / _coerce_bool to succeed.
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

                # Only create dynamic subclass if there are still extensions left
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
            model_class = cast(type[BaseModel], DynamicModel)
            self._schema_cache[cache_key] = model_class
            return model_class
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

    def build_chunk_response_schema(self, schema_name: str, item_schema: type[BaseModel]) -> type[BaseModel]:
        """Build dynamic Pydantic V2 schema for chunked Map-Reduce execution.

        Nests a target Payload schema inside a structurally strict chunk-array list.

        Args:
            schema_name: Name for the generated Pydantic model class.
            item_schema: The inner Pydantic model defining each record's payload.

        Returns:
            A dynamically generated Pydantic model class for chunk responses.
        """
        ChunkRecordModel = create_model(
            f"{schema_name}Record",
            __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
            original_id=(
                str,
                Field(..., description="The original system identifier of the source record."),
            ),
            payload=(
                item_schema,
                Field(..., description="The validated item payload matching the target data schema."),
            ),
        )

        records_tuple: Any = (
            list[Any],
            Field(
                ...,
                max_length=get_settings().schema_max_chunk_records,
                description="List of records contained in this execution chunk.",
            ),
        )
        if not TYPE_CHECKING:
            records_tuple = (list[ChunkRecordModel], records_tuple[1])

        DynamicModel = create_model(
            schema_name,
            __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
            chunk_id=(
                str,
                Field(..., description="The unique system identifier of the current execution chunk."),
            ),
            # dynamically generated type aliases aren't parsed statically by mypy
            records=records_tuple,
        )

        return DynamicModel
