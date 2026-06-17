"""Schema Factory for generating dynamic Pydantic schemas for LLM Structured Outputs.

Extracts and centralizes all dynamic Pydantic model creation logic from the
monolithic PromptCompiler, following SRP (Rule 88).
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from enum import Enum
from typing import TYPE_CHECKING, Any, cast

from pydantic import BaseModel, ConfigDict, Field, create_model, model_validator

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.dtos.evaluation_steps import StepDTOSemantic, StepDTOStrict
from backend_v2.models.enums import SystemConcurrency
from backend_v2.models.v2_core import PromptBlock

logger = logging.getLogger(__name__)


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
        description="Analytical reasoning and qualitative justification for the assigned matrix score.",
    )


class StrippedBaseTDAExtraction(BaseModel):
    """Stripped core Pydantic model for Micro-CoT extraction without localized anchors to save tokens."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    exact_quotes: list[str] = Field(
        default_factory=list,
        max_length=3,
        description="Extract up to 3 physically contiguous sentences. Do not stitch them together. ABSOLUTE PRIORITY over contextual override. MUST be empty if contextual_override is True. CRITICAL: MUST ALWAYS be extracted in the exact original language of the source text, as physically contiguous VERBATIM substrings (do not add/remove words, markdown, or fix typos). NEVER translate the quotes, even if your reasoning is in another language.",
    )
    contextual_override: bool = Field(
        description="ABSOLUTE LAST RESORT. True only if rule is satisfied contextually without a verbatim quote. exact_quotes MUST be empty if True.",
    )
    semantic_reasoning: str = Field(
        description="Detailed analytical reasoning in target language explaining the match.",
    )

    @model_validator(mode="before")
    @classmethod
    def strip_dunder_hallucinations(cls, data: Any) -> Any:
        """Strips out hallucinated __dunder__ fields from LLM payloads."""
        if not isinstance(data, dict):
            return data
        # Strip all keys starting with __
        return {k: v for k, v in data.items() if not str(k).startswith("__")}


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
    ) -> type[BaseModel]:
        """Build a dynamic Pydantic V2 model for LLM Structured Outputs.

        Args:
            schema_name: Name for the generated Pydantic model class.
            criteria: List of PromptBlock definitions driving schema fields.
            has_search_result: Whether to include search result extensions.
            has_shuffled_atoms: Whether to include shuffled atom evaluation fields.
            target_locale: Target language code for label resolution.

        Returns:
            A dynamically generated Pydantic model class.
        """
        # P4: Prevent Pydantic compilation explosion on 200+ step DAGs by hashing criteria
        # and delegating to an LRU cached private method.
        # Epic 43: Serialize strictly typed PromptBlocks back to json for the cache key.
        criteria_ids = "_".join(sorted(str(c.id) for c in criteria if c.id))
        cache_key = (
            f"{schema_name}_{criteria_ids}_{has_search_result}_{has_shuffled_atoms}_{target_locale}_{strictness_level}"
        )

        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]

        return self._build_dynamic_schema_internal(
            schema_name, has_search_result, has_shuffled_atoms, target_locale, strictness_level, criteria, cache_key
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
        fields: dict[str, Any] = {
            "reasoning_trace": (
                str,
                Field(
                    ...,
                    description="Detailed step-by-step reasoning trace of the audit process.",
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
                    description="The EXACT system identifier. MUST exactly match one of the items provided in <BLIND_ATOMS_TO_EVALUATE>.",
                )

            # Phase D & E: Proactive Routing
            # For shuffled atoms, we use a single base class. If strictness >= 100, override is completely denied.
            # V3 Fix: Pydantic multiple inheritance resolves right-to-left for fields.
            # By placing AtomResponseBase LAST in the inheritance chain, its fields (atom_id)
            # are collected FIRST by Pydantic's reverse-MRO iteration, ensuring the LLM emits it first.
            AtomResponse: Any
            if strictness_level >= 100:

                class AtomResponseStrict(StepDTOStrict, AtomResponseBase):
                    pass

                AtomResponse = AtomResponseStrict
            else:

                class AtomResponseSemantic(StepDTOSemantic, AtomResponseBase):
                    pass

                AtomResponse = AtomResponseSemantic

            fields["evaluations"] = (
                list[AtomResponse],
                Field(
                    ...,
                    max_length=SystemConcurrency.SCHEMA_MAX_EVALUATIONS,
                    description="List of atomic evaluations. You MUST evaluate ONLY the exact atoms explicitly listed in <BLIND_ATOMS_TO_EVALUATE>. You MUST include the exact 'atom_id' for each evaluation. Do NOT hallucinate, invent, or evaluate any unlisted concepts.",
                ),
            )

        # Epic 56 Phase 4 / Bugfix: We must include matrix blocks for XAI extensions,
        # but we MUST filter out standard "criteria" blocks if has_shuffled_atoms is True.
        # Otherwise, the LLM is forced to output them both in `evaluations` AND at the root level,
        # which causes a "too many states for serving" Vertex AI Bad Request error.
        if has_shuffled_atoms:
            schema_criteria = [c for c in criteria if c.category_id != "criteria"]
        else:
            schema_criteria = criteria

        for crit in schema_criteria:
            crit_id = crit.id
            if not crit_id:
                logger.warning("[SchemaFactory] Found criterion without a valid string 'id': %s. Skipping.", crit)
                continue

            if crit.category_id != "matrix" and crit.type == "instruction":
                fields[crit_id] = (
                    str,
                    Field(
                        ...,
                        description="Instruction-based response and verification synthesis.",
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
                    base_class = StepDTOStrict
                else:
                    base_class = StepDTOSemantic

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
                                default=0.0,
                                description=f"Numeric score (0.0 to 1.0) for '{ext}'.",
                            ),
                        )
                    elif ext in boolean_extensions:
                        dynamic_fields[ext] = (
                            bool,
                            Field(
                                default=False,
                                description=f"Boolean flag for '{ext}'.",
                            ),
                        )
                    else:
                        dynamic_fields[ext] = (
                            str,
                            Field(
                                default="",
                                description=f"Qualitative extension for '{ext}' based on the matrix evaluation.",
                            ),
                        )

                # Only create dynamic subclass if there are still extensions left
                if dynamic_fields:
                    DynamicBlock = create_model(
                        f"BlockExtraction_{crit_id}",
                        __base__=base_class,
                        __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
                        **dynamic_fields,
                    )
                    fields[crit_id] = (DynamicBlock, Field(..., description=desc_val))
                else:
                    fields[crit_id] = (base_class, Field(..., description=desc_val))
            else:
                fields[crit_id] = (base_class, Field(..., description=desc_val))

        if not fields:
            fields["acknowledged_instruction"] = (
                str,
                Field(default="yes", description="Fallback confirmation that all instructions have been acknowledged."),
            )

        try:
            DynamicModel = create_model(
                schema_name, __config__=ConfigDict(extra="forbid", strict=True, frozen=True), **fields
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
                max_length=SystemConcurrency.SCHEMA_MAX_CHUNK_RECORDS,
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
