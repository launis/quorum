"""Prompt Compiler for generating dynamic Pydantic schemas and LLM prompts.

Transforms abstract workflow state and domain models into executable
LLM payloads with system context, strictness calibration, and format enforcement.
"""

from __future__ import annotations

import datetime
import json
import logging
from enum import Enum
from functools import lru_cache
from typing import Any, cast

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, create_model, model_validator

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.enums import EvaluationMandate, SystemConcurrency
from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.web_fetcher import WebFetcher

logger = logging.getLogger(__name__)


class EvidenceType(str, Enum):
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
    """Core Pydantic model for Micro-CoT extraction with deterministic cross-validation and stripped descriptions."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    exact_quote: str | None = Field(
        default=None,
        description="Verbatim quote from the original text. MUST be empty if contextual_override is True.",
    )
    structural_location: str = Field(
        description=(
            "Exact structural location (e.g. 'page 3', 'paragraph 2'). Must be in the Localized "
            "Target Language. If contextual_override is False, you MUST output 'N/A'. "
            "If contextual_override is True, you MUST provide the concrete location."
        ),
    )
    localized_anchors_found: list[str] = Field(
        default_factory=list,
        max_length=15,
        description="Keywords in target language mapping English rule.",
    )
    contextual_override: bool = Field(
        description=(
            "Set to True only if no literal evidence exists but the rule is implicitly matched. "
            "exact_quote MUST be empty if True."
        )
    )
    semantic_reasoning: str = Field(description="Strict semantic justification for the extraction decision.")

    @model_validator(mode="after")
    def validate_override_logic(self) -> StrippedBaseTDAExtraction:
        if self.contextual_override:
            if self.exact_quote not in (None, "", "[CONTEXTUAL_OVERRIDE_APPLIED]"):
                raise ValueError(
                    "Cross-validation failed: exact_quote MUST be empty, null, "
                    "or '[CONTEXTUAL_OVERRIDE_APPLIED]' if contextual_override is True."
                )
        else:
            if self.exact_quote == "[CONTEXTUAL_OVERRIDE_APPLIED]":
                raise ValueError(
                    "Cross-validation failed: exact_quote cannot be "
                    "'[CONTEXTUAL_OVERRIDE_APPLIED]' if contextual_override is False."
                )
        return self


class PromptCompiler:
    """Core translation engine for workflow execution.

    Converts static DB models into runtime execution contexts.
    """

    def __init__(self) -> None:
        """Initialize PromptCompiler."""
        pass

    def resolve_i18n(self, text_obj: Any, target_locale: str) -> str:
        """Resolve an I18n JSON object to a string based on locale fallback rules.

        Args:
            text_obj: The I18n object (model or dict with default_locale and translations),
                      or a raw string (legacy fallback), or None.
            target_locale: The requested language code (e.g., 'fi' or 'en').

        Returns:
            Resolved text string, or empty string if None.
        """
        if not text_obj:
            return ""

        if hasattr(text_obj, "resolve"):
            return str(text_obj.resolve(target_locale))

        if isinstance(text_obj, str) or not isinstance(text_obj, dict):
            msg = (
                f"Legacy string fallback detected or invalid type: '{text_obj}'. "
                "All text MUST be valid I18nText dictionaries."
            )
            logger.error("[PromptCompiler] %s", msg)
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})

        translations = text_obj.get("translations", {})
        if not isinstance(translations, dict):
            translations = {}

        # 1. Try Target Locale
        if target_locale in translations and translations[target_locale]:
            return str(translations[target_locale])

        # V2 MANDATE: NO FALLBACKS. If a translation is requested, it MUST exist.
        msg = f"Translation missing for required locale '{target_locale}'. Fallbacks are strictly forbidden."
        logger.error(
            "Translation missing for required locale.",
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "target_locale": target_locale},
        )
        raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})

    def build_xml_context(
        self,
        input_mappings: dict[str, str],
        state_data: dict[str, Any],
        target_locale: str,
        expected_inputs: list[Any] | None = None,
    ) -> str:
        """Build XML semantic blocks from raw input mappings for LLM context.

        Args:
            input_mappings: Dict mapping logical names to value paths/keys.
            state_data: The current workflow execution state containing values.
            target_locale: The requested output locale string.
            expected_inputs: Optional list of ExpectedInput definitions to extract ai_description.

        Returns:
            A single string containing XML-wrapped elements.
        """
        xml_blocks = []

        # Build a lookup for expected inputs by input_key for full semantic context injection
        input_meta_map = {}
        if expected_inputs:
            for ei in expected_inputs:
                key = getattr(ei, "input_key", None)
                if not key:
                    continue

                # Fail-Fast Mandatory I18n extraction
                label_obj = getattr(ei, "label", None)
                label_dict = (
                    label_obj.model_dump(mode="json")
                    if label_obj is not None and hasattr(label_obj, "model_dump")
                    else label_obj
                )
                label_str = self.resolve_i18n(label_dict, target_locale) if label_dict else ""

                desc_obj = getattr(ei, "description", None)
                desc_dict = (
                    desc_obj.model_dump(mode="json")
                    if desc_obj is not None and hasattr(desc_obj, "model_dump")
                    else desc_obj
                )
                desc_str = self.resolve_i18n(desc_dict, target_locale) if desc_dict else ""

                ai_desc = getattr(ei, "ai_description", None) or ""

                input_meta_map[f"$inputs.{key}"] = {
                    "label": label_str,
                    "desc": desc_str,
                    "ai_desc": ai_desc,
                }

        for logical_name, source_path in input_mappings.items():
            value = self._extract_value_from_state(source_path, state_data)
            if value:
                meta = input_meta_map.get(source_path)
                desc_text = ""
                if meta:
                    desc_text += "  <document_metadata>\n"
                    desc_text += f"    <document_id>{logical_name}</document_id>\n"
                    if meta["label"]:
                        desc_text += f"    <document_name>{meta['label']}</document_name>\n"
                    if meta["desc"]:
                        desc_text += f"    <document_description>{meta['desc']}</document_description>\n"
                    if meta["ai_desc"]:
                        desc_text += f"    <ai_context_mandate>{meta['ai_desc']}</ai_context_mandate>\n"
                    desc_text += "  </document_metadata>\n"

                xml_blocks.append(f'<matrix_input source_id="{logical_name}">\n{desc_text}{value}\n</matrix_input>')

        compiled = "\n\n".join(xml_blocks)

        return compiled

    def get_critical_language_mandate(self, target_locale: str) -> str:
        """Epic 56 Phase 3: Exposes the mandate so ChunkWorker can place it at the exact end of the prompt."""
        return (
            f"<CRITICAL_LANGUAGE_MANDATE>\n"
            f"You must process the input and generate your general output text exclusively in the "
            f"'{target_locale}' language. However, for specific fields like 'semantic_reasoning' and "
            f"'exact_quote', you MUST output the text in the ORIGINAL language of the source "
            f"document to preserve exact fidelity. All JSON keys must strictly remain in English.\n"
            f"</CRITICAL_LANGUAGE_MANDATE>"
        )

    def _extract_value_from_state(self, path: str, state_data: dict[str, Any]) -> str:
        """Extract a value from workflow state using a path like '$inputs.history_text'."""
        if not isinstance(path, str):
            msg = f"Variable reference path must be a string, got {type(path)}"
            logger.error("[PromptCompiler] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        # Removing '$' prefix if present
        if path.startswith("$"):
            path = path[1:]

        # Support the standard V2 $steps namespace for explicit node targeting (e.g. $steps.sr_xyz.outputs)
        if path.startswith("steps."):
            path = path[len("steps.") :]

        if path == "steps":
            # Epic 27: Explicitly allow the global $steps namespace to dump the entire context
            current: Any = state_data
        else:
            parts = path.split(".")
            current = state_data

            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                elif hasattr(current, part):
                    current = getattr(current, part)
                else:
                    msg = f"Path resolution failed: '{path}'. Component '{part}' is missing from state context."
                    logger.error("[PromptCompiler] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                    )

        if isinstance(current, str):
            # Already a string, return directly
            return current

        if hasattr(current, "model_dump_json") and callable(getattr(current, "model_dump_json", None)):
            dump_fn: Any = current.model_dump_json
            return str(dump_fn(indent=2))

        if isinstance(current, dict):
            # Epic 12: Flatten nested JSON into LLM-friendly Markdown (Attention Dilution patch)
            formatted = []
            for k, v in current.items():
                formatted.append(f'<matrix_input source="{str(k).upper()}">')
                if isinstance(v, dict):
                    # Yritetään sukeltaa suoraan 'outputs' avaimeen jos se olemassa
                    target_dict = v.get("outputs", v) if "outputs" in v else v
                    for sub_k, sub_v in target_dict.items():
                        # Epic 32: Prevent Context Snowballing (95k char prompts).
                        # Never inject raw Matrix arrays into subsequent LLM contexts.
                        if sub_k == "evaluations" and isinstance(sub_v, list):
                            continue

                        if isinstance(sub_v, dict):
                            formatted.append(f"<{str(sub_k).upper()}>")
                            for micro_k, micro_v in sub_v.items():
                                # Siivotaan kognitiiviset etuliitteet pois luettavuuden vuoksi
                                clean_key = (
                                    str(micro_k)
                                    .replace("step_1_", "")
                                    .replace("step_2_", "")
                                    .replace("step_3_", "")
                                    .replace("step_4_", "")
                                    .replace("_", " ")
                                    .title()
                                )
                                formatted.append(
                                    f"  <{clean_key.replace(' ', '_')}>{micro_v}</{clean_key.replace(' ', '_')}>"
                                )
                            formatted.append(f"</{str(sub_k).upper()}>")
                        else:
                            clean_sub_k = str(sub_k).title().replace(" ", "_")
                            formatted.append(f"<{clean_sub_k}>{sub_v}</{clean_sub_k}>")
                else:
                    formatted.append(str(v))
                formatted.append("</matrix_input>")
            return "\n".join(formatted).strip()

        return str(current)

    def inject_theory_grounding(self, base_prompt: str, url: str | None) -> str:
        """Fetch and inject external theoretical context into the prompt.

        Args:
            base_prompt: The original system prompt or instructions.
            url: The source URL for theory grounding (if any).

        Returns:
            The augmented prompt containing <theory_context> if successful,
            or the original prompt if no URL provides.
        """
        if not url:
            return base_prompt

        try:
            logger.info("[PromptCompiler] Fetching theory grounding from %s", url)
            # WebFetcher raises AppException locally on failure, satisfying Fail-Fast rules
            theory_text = WebFetcher.fetch_text(url)

            if not theory_text:
                logger.warning("[PromptCompiler] Fetched text from %s was empty.", url)
                return base_prompt

            augmented = base_prompt + f"\n\n<theory_context>\n{theory_text}\n</theory_context>\n"
            return augmented

        except Exception as e:
            # Re-raise AppExceptions from WebFetcher to crash fast properly
            if isinstance(e, AppException):
                raise e

            msg = f"System failed to fetch required theoretical grounding from url: {url}"
            logger.error(
                "Theory grounding fetch failed.",
                extra={"error_code": ErrorCodes.FETCH_FAILED.name, "url": url, "detail": str(e)},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=502,
                details={"error_code": ErrorCodes.FETCH_FAILED, "url": url},
            ) from e

    def calibrate_strictness(self, level: int | float | None) -> str:
        """Convert a numeric strictness level (0-100) into a semantic directive.

        Args:
            level: The strictness integer, 0 (Lenient) to 100 (Unforgiving).

        Returns:
            A semantic prompt string commanding the LLM of the desired strictness behavior.
        """
        if level is None:
            return ""

        try:
            val = int(level)
        except (ValueError, TypeError) as e:
            logger.error("Failed to parse strictness level %s", level, exc_info=True)
            raise AppException(
                message=f"Invalid strictness level: {level}",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
            ) from e

        # Clamp between 0 and 100
        val = max(0, min(100, val))

        if val == 0:
            return (
                "STRICTNESS CALIBRATION (0/100): Absolute Leniency. You must be extremely generous and forgiving. "
                "Assume the best possible intent and assign the highest possible score unless there is a "
                "catastrophic flaw."
            )
        elif val < 30:
            return (
                f"STRICTNESS CALIBRATION ({val}/100): Lenient. Be generally forgiving of minor errors and "
                "focus on the positive aspects of the input. Do not penalize heavily for small formatting issues."
            )
        elif val < 70:
            return (
                f"STRICTNESS CALIBRATION ({val}/100): Balanced. Evaluate fairly and neutrally. "
                "Penalize errors proportionally and reward good qualities objectively."
            )
        elif val < 100:
            return (
                f"STRICTNESS CALIBRATION ({val}/100): Strict. You must be highly critical and demanding. "
                "Penalize flaws, inconsistencies, and lack of detail. High scores require exceptional quality."
            )
        else:
            return (
                "STRICTNESS CALIBRATION (100/100): Absolute Strictness. You are an unforgiving auditor. "
                "Any deviation from perfection, logical inconsistency, or lack of rigorous justification "
                "MUST be heavily penalized. "
                "Assign minimum scores unless the input is mathematically and theoretically flawless."
            )

    def build_dynamic_schema(
        self,
        schema_name: str,
        criteria: list[PromptBlock],
        has_search_result: bool = False,
        has_shuffled_atoms: bool = False,
        target_locale: str = "en",
    ) -> type[BaseModel]:
        # P4: Prevent Pydantic compilation explosion on 200+ step DAGs by hashing criteria
        # and delegating to an LRU cached private method.
        # Epic 43: Serialize strictly typed PromptBlocks back to json for the cache key.
        criteria_json = json.dumps([c.model_dump(mode="json") for c in criteria], sort_keys=True)
        return self._cached_build_dynamic_schema(
            schema_name, criteria_json, has_search_result, has_shuffled_atoms, target_locale
        )

    @lru_cache(maxsize=128)  # noqa: B019
    def _cached_build_dynamic_schema(
        self,
        schema_name: str,
        criteria_json: str,
        has_search_result: bool,
        has_shuffled_atoms: bool,
        target_locale: str,
    ) -> type[BaseModel]:
        """Build a dynamic Pydantic V2 model for LLM Structured Outputs.
        Radically stripped to enforce BaseTDAExtraction determinism and prevent Vertex AI state limits.
        """
        from backend_v2.models.v2_core import PromptBlock

        criteria: list[PromptBlock] = [PromptBlock.model_validate(c) for c in json.loads(criteria_json)]

        fields: dict[str, Any] = {
            "reasoning_trace": (
                str,
                Field(
                    ...,
                    alias="step_1_reasoning_trace",
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
                model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
                atom_id: str = Field(
                    ...,
                    description="The EXACT system identifier. MUST exactly match one of the items provided in <BLIND_ATOMS_TO_EVALUATE>.",
                )

            # V3 Fix: Pydantic multiple inheritance resolves right-to-left for fields.
            # By placing AtomResponseBase LAST in the inheritance chain, its fields (atom_id)
            # are collected FIRST by Pydantic's reverse-MRO iteration, ensuring the LLM emits it first.
            class AtomResponse(StrippedBaseTDAExtraction, AtomResponseBase):
                pass

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
                logger.warning("[PromptCompiler] Found criterion without a valid string 'id': %s. Skipping.", crit)
                continue

            if crit.category_id != "matrix" and getattr(crit, "type", None) == "instruction":
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
            base_class = StrippedBaseMatrixXAI if crit.category_id == "matrix" else StrippedBaseTDAExtraction

            # Dynamic short and concise description for the LLM to understand this specific evaluation field
            label_str = self.resolve_i18n(crit.label, target_locale) if crit.label else ""
            cat_val = crit.category_id.value if hasattr(crit.category_id, "value") else (crit.category_id or "criteria")
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

    def compile_xml_rubrics(
        self, criteria: list[PromptBlock], target_locale: str, execution_persona_block: PromptBlock | None = None
    ) -> str:
        """Epic 12/55: Generates Thick XML/Markdown rubrics for the System Prompt with Persona SSOT."""
        xml_blocks = []
        if execution_persona_block and execution_persona_block.ai_description:
            xml_blocks.append(f"<EXECUTION_PERSONA>\n{execution_persona_block.ai_description}\n</EXECUTION_PERSONA>")

        xml_blocks.append("<EVALUATION_RUBRICS>")
        for crit in criteria:
            if crit.category_id != "matrix":
                continue

            crit_id = crit.id
            label = self.resolve_i18n(crit.label, target_locale)
            desc = crit.ai_description or ""

            xml_blocks.append(f'  <MATRIX id="{crit_id}" title="{label}">')
            if desc:
                xml_blocks.append(f"    <DIRECTIVE>{desc}</DIRECTIVE>")

            scales = crit.scales or []
            if scales:
                mandate_str = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
                claims_texts = []
                for s in scales:
                    for c in s.claims:
                        for assertion in c.tda_assertions:
                            substance = (assertion.ai_rule_description or "").strip()
                            if substance:
                                rule_text = substance
                                if assertion.inverse_evidence:
                                    rule_text += (
                                        " This is an inverse rule (Vice). If rule_satisfied = True "
                                        "(no issues found), evidence_found MUST be False and you must "
                                        'return an empty string "" for exact_quote. If rule_satisfied = False '
                                        "(violation found), evidence_found MUST be True and you MUST quote "
                                        "the exact violation."
                                    )
                                if getattr(assertion, "allow_contextual_override", False):
                                    rule_text += (
                                        " [CONTEXTUAL OVERRIDE ALLOWED] If the assertion's criteria are satisfied "
                                        "semantically or contextually across the text but no single exact verbatim "
                                        "quote can be isolated, you MUST: 1) Set contextual_override = true. 2) "
                                        "Provide a detailed explanation in semantic_reasoning with structural "
                                        "references. 3) Set exact_quote to exactly "
                                        "'[CONTEXTUAL_OVERRIDE_APPLIED]'. Do NOT hallucinate a quote. Only use "
                                        "this override if a direct literal quote is physically absent."
                                    )
                                claims_texts.append(f"{rule_text} {mandate_str}")

                if claims_texts:
                    claims = " ".join(claims_texts)
                    xml_blocks.append(f"    <CRITICAL_DIRECTIVES>{claims}</CRITICAL_DIRECTIVES>")

            xml_blocks.append("  </MATRIX>")
        xml_blocks.append("</EVALUATION_RUBRICS>")

        # Epic 29 Phase 2: Anti-Sycophancy XAI Header
        anti_sycophancy_mandate = (
            "<ANTI_SYCOPHANCY_MANDATE>\n"
            "ANTI-SYCOPHANCY MANDATE: All extension fields MUST follow the same strict, "
            "coldly analytical tone as the main score. "
            "If the user's score is low, coaching and missing_context must NOT be encouraging. "
            "You must precisely point out the missing data, flawed metric, or shaky causal relationship. "
            "Speak like a strict professional auditor.\n"
            "</ANTI_SYCOPHANCY_MANDATE>"
        )
        xml_blocks.append(anti_sycophancy_mandate)

        # Extension Anchoring Mandate: Prevent generic consulting jargon in dynamic extensions
        extension_anchoring_mandate = (
            "<EXTENSION_ANCHORING_MANDATE>\n"
            "CRITICAL XAI RULE: Every generated extension field (e.g. coaching, falsification, "
            "remediation, missing_context) MUST be explicitly anchored to the user's raw input "
            "or the extracted evidence quote. Do NOT output generic theoretical advice, assumed "
            "knowledge, or standard consultant jargon. If you offer a coaching tip, falsification, "
            "or point out missing context, it MUST directly address a specific flaw or gap found "
            "in the user's text.\n"
            "</EXTENSION_ANCHORING_MANDATE>"
        )
        xml_blocks.append(extension_anchoring_mandate)

        # Anti-ID Mandate to prevent raw UUID/System-ID hallucination
        anti_id_mandate = (
            "<ANTI_ID_MANDATE>\n"
            "CRITICAL FORMATTING RULE for textual fields (e.g., semantic_reasoning, exact_quote):\n"
            "Do NOT include raw system IDs in your explanatory text. "
            "Refer to concepts by their human-readable names in your text.\n"
            "HOWEVER, the JSON key `atom_id` MUST ALWAYS be populated with the correct system ID. "
            "Never omit the `atom_id` from the JSON object.\n"
            "</ANTI_ID_MANDATE>"
        )
        xml_blocks.append(anti_id_mandate)

        # Anti-Score Mandate to enforce Zero-Trust Auditor architecture
        anti_score_mandate = (
            "<ANTI_SCORE_MANDATE>\n"
            "CRITICAL ARCHITECTURAL RULE: You are a blind micro-evaluator. You MUST NEVER declare a final score, "
            "a final grade, or use text like 'Arvioidaan tasolle 4' or 'Pysyn arviossa 3' in your justification text. "
            "Your ONLY job is to analytically explain the presence or absence of logical elements and evidence. "
            "The final mathematical calculation and grading will be done strictly by the backend system. "
            "Do NOT attempt to act as the final judge.\n"
            "</ANTI_SCORE_MANDATE>"
        )
        xml_blocks.append(anti_score_mandate)

        return "\n".join(xml_blocks)

    def compile_static_instructions(self, blocks: list[PromptBlock], target_locale: str) -> str:
        """Compile static instruction-type V2 PromptBlocks for the Cached System Prompt.

        Extracts blocks where type == "instruction" AND category_id != "runtime_variables".

        Args:
            blocks: List of PromptBlock definitions.
            target_locale: The requested language code.

        Returns:
            A formatted string of all static instruction directives.
        """
        compiled_lines = []
        for block in blocks:
            if block.category_id != "matrix" and block.category_id != "runtime_variables":
                label = self.resolve_i18n(block.label, target_locale)
                desc = block.ai_description
                if not desc:
                    block_id = block.id
                    msg = f"PromptBlock '{block_id}' is missing mandatory 'ai_description'."
                    logger.error(
                        "PromptBlock is missing mandatory 'ai_description'.",
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "block_id": block_id},
                    )
                    raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})

                if label or desc:
                    compiled_lines.append(f'<STATIC_INSTRUCTION label="{label}">\n{desc}\n</STATIC_INSTRUCTION>')

        return "\n\n".join(compiled_lines) if compiled_lines else ""

    def compile_dynamic_instructions(
        self,
        blocks: list[PromptBlock],
        target_locale: str,
        execution_time: datetime.datetime | str | None = None,
    ) -> str:
        """Compile dynamic instruction-type V2 PromptBlocks for the Uncached User Tail.

        Extracts blocks where type == "instruction" AND category_id == "runtime_variables",
        and performs real-time variable substitutions (e.g. {CURRENT_DATE}).

        Args:
            blocks: List of PromptBlock definitions.
            target_locale: The requested language code.
            execution_time: Optional static timestamp of the execution or inputs to ensure 100% determinism.

        Returns:
            A formatted string of all dynamic runtime instruction directives.
        """
        now_utc = None
        if execution_time is not None:
            if isinstance(execution_time, datetime.datetime):
                now_utc = execution_time
            elif isinstance(execution_time, str):
                try:
                    # Remove Z/UTC suffix if present for standard isoformat parsing
                    clean_str = execution_time.replace("Z", "+00:00")
                    now_utc = datetime.datetime.fromisoformat(clean_str)
                except ValueError as e:
                    msg = f"Failed to parse execution_time string '{execution_time}' into a valid ISO-8601 datetime."
                    logger.error("[PromptCompiler] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg,
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from e
            else:
                msg = f"Invalid execution_time type '{type(execution_time).__name__}'. Must be datetime, str, or None."
                logger.error("[PromptCompiler] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

        if not now_utc:
            now_utc = datetime.datetime.now(datetime.UTC)

        current_date_str = now_utc.strftime("%Y-%m-%d")
        dynamic_time_str = now_utc.strftime("%H:%M:%S UTC")

        compiled_lines = []
        for block in blocks:
            if block.category_id == "runtime_variables":
                label = self.resolve_i18n(block.label, target_locale)
                desc = block.ai_description
                if not desc:
                    block_id = block.id
                    msg = f"PromptBlock '{block_id}' is missing mandatory 'ai_description'."
                    logger.error(
                        "PromptBlock is missing mandatory 'ai_description'.",
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "block_id": block_id},
                    )
                    raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})

                # Perform Runtime Variable Substitutions
                desc = desc.replace("{CURRENT_DATE}", current_date_str)
                desc = desc.replace("{DYNAMIC_TIME}", dynamic_time_str)

                if label or desc:
                    compiled_lines.append(f'<DYNAMIC_INSTRUCTION label="{label}">\n{desc}\n</DYNAMIC_INSTRUCTION>')

        return "\n\n".join(compiled_lines) if compiled_lines else ""

    def generate_mcp_instruction(self, allowed_tools: list[str]) -> str:
        """Epic 13 M2: Generate dynamic instructions for active MCP tools."""
        if not allowed_tools:
            return ""
        tool_list = ", ".join(allowed_tools)
        return (
            "[SYSTEM: DYNAMIC TOOL AUTOMATION]\n"
            f"Use the dynamic tools [{tool_list}] proactively to search for up-to-date material. "
            "Stop data collection as soon as you have sufficient context. "
            "Embed your discovered sources into the corresponding extension fields."
        )

    def build_blind_evaluation_schema(self, schema_name: str) -> type[BaseModel]:
        """Add a dedicated schema builder for the blind extraction."""

        class AtomResponse(BaseModel):
            model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
            atom_id: str = Field(..., description="Unique system identifier of the target evaluation atom.")
            step_1_evidence_type: EvidenceType = Field(
                ...,
                description="Type of evidence discovered (EXPLICIT_QUOTE, IMPLIED_INTENT, or NO_EVIDENCE).",
            )
            step_2_quote: str | None = Field(
                default=None,
                description=(
                    "Literal verbatim quote containing the exact physical evidence from the "
                    "source document. REQUIRED if evidence type is EXPLICIT_QUOTE."
                ),
            )
            step_3_implicit_justification: str | None = Field(
                default=None,
                description=(
                    "Conclusive justification if intent is implied. Must be at least 20 words. "
                    "Allowed ONLY if strictness < 70."
                ),
            )
            step_4_reasoning: str = Field(
                ...,
                description="Strict analytical reasoning trace explaining the presence or absence of evidence.",
            )
            step_5_boolean: bool = Field(
                ...,
                description="Final Boolean determination: True if rule is satisfied, False if violated or unsupported.",
            )

            @model_validator(mode="after")
            def validate_evidence(self, info: ValidationInfo) -> Any:
                if self.step_1_evidence_type == EvidenceType.EXPLICIT_QUOTE:
                    if not self.step_2_quote or not self.step_2_quote.strip():
                        raise ValueError("ANTI-LAZINESS MANDATE: Quote required for EXPLICIT_QUOTE")
                elif self.step_1_evidence_type == EvidenceType.IMPLIED_INTENT:
                    just_str = self.step_3_implicit_justification
                    if not just_str or len(just_str.split()) < 20:
                        raise ValueError(
                            "ANTI-LAZINESS MANDATE: Justification too short for IMPLIED_INTENT (min 20 words)"
                        )
                    if info.context is None or "strictness_level" not in info.context:
                        raise ValueError(
                            "SYSTEM ARCHITECTURE MANDATE: Missing 'strictness_level' in validation context"
                        )
                    if info.context["strictness_level"] >= 70:
                        raise ValueError("Strictness >= 70 ei salli implisiittistä logiikkaa")
                elif self.step_1_evidence_type == EvidenceType.NO_EVIDENCE:
                    if self.step_5_boolean is True:
                        raise ValueError("ANTI-LAZINESS MANDATE: Cannot be True with NO_EVIDENCE")
                return self

        DynamicModel = create_model(
            schema_name,
            __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
            evaluations=(
                list[AtomResponse],
                Field(
                    ...,
                    max_length=SystemConcurrency.SCHEMA_MAX_EVALUATIONS,
                    description="List of blind atomic evaluations.",
                ),
            ),
        )

        return DynamicModel

    def compile_blind_system_instruction(self, target_locale: str = "en") -> str:
        """Create a Micro-CoT Prompt-block for the system role forcing full blindness."""
        instruction = (
            "<system_directive>\n"
            "<objective>You are a Blind Extraction Engine. Your task is to scan the text "
            "for the markers defined in the rule.</objective>\n"
            "<language_mandate>The physical markers in the rules are in English, but the "
            "source text is in Finnish. You MUST strictly map the English markers to their EXACT "
            "semantic physical equivalents in Finnish before scanning. Do not extract if the "
            "localized marker is missing.</language_mandate>\n"
            "<rules>\n"
            "  <rule>If the exact marker is not physically present, return null for "
            "exact_quote.</rule>\n"
            "  <rule>Keep your semantic_reasoning strictly under 2 sentences.</rule>\n"
            "  <rule>Use contextual_override=true ONLY as a last resort if the target "
            "concept is clearly present but physically impossible to extract as an "
            "exact continuous quote.</rule>\n"
            "  <rule>When evaluating negative conditions or presence of flaws (vice rules), "
            "you must look ONLY for physical semantic matches. If the text does not contain the "
            "exact physical anchors defined in the rule, you MUST return JSON null. "
            "Speculation, extrapolation, or rationalizing away missing evidence is strictly banned."
            "</rule>\n"
            "</rules>\n"
            "</system_directive>"
        )
        instruction += (
            f"\n\nCRITICAL MANDATE: You must generate all your output text and reasoning "
            f"exclusively in the '{target_locale}' language."
        )
        return instruction

    def build_chunk_response_schema(self, schema_name: str, item_schema: type[BaseModel]) -> type[BaseModel]:
        """Build dynamic Pydantic V2 schema for chunked Map-Reduce execution.

        Nests a target Payload schema inside a structurally strict chunk-array list.
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

        DynamicModel = create_model(
            schema_name,
            __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
            chunk_id=(
                str,
                Field(..., description="The unique system identifier of the current execution chunk."),
            ),
            # dynamically generated type aliases aren't parsed statically by mypy
            records=(
                list[ChunkRecordModel],  # type: ignore[valid-type]
                Field(
                    ...,
                    max_length=SystemConcurrency.SCHEMA_MAX_CHUNK_RECORDS,
                    description="List of records contained in this execution chunk.",
                ),
            ),
        )

        return DynamicModel

    def compile_chunk_payload_instruction(self, chunk_id: str, payload_text: str) -> str:
        """Generates an isolated context block fenced explicitly into `<user_payload>`."""
        return (
            f"You are processing map-reduce chunk '{chunk_id}'.\n"
            "Evaluate ONLY the following payload mapping to the strict chunk_id structure:\n"
            f"<user_payload>\n{payload_text}\n</user_payload>"
        )

    @staticmethod
    def get_schema_healing_prompt(error_msg: str, is_logical_error: bool, is_eof: bool) -> str:
        """Generate a Self-Healing prompt for LLM execution recovery.

        Args:
            error_msg: The specific validation or logical error message.
            is_logical_error: True if the failure was a semantic Domain validation, False if Pydantic syntax.
            is_eof: True if the LLM output was cut off (e.g. max_tokens reached).

        Returns:
            A formatted prompt string commanding the LLM to fix its previous output.
        """
        if is_eof:
            return (
                "[SYSTEM: EOF DETECTED]\n"
                "Your previous response was cut off abruptly before generating valid JSON. "
                "Please regenerate the response from the beginning and ensure the JSON is fully closed."
            )

        if is_logical_error:
            return (
                "[SYSTEM: STRICT LOGICAL COMPLIANCE REQUIRED]\n"
                "Your previous response was structurally valid JSON, but failed domain-specific logical validation:\n"
                f"Error: {error_msg}\n\n"
                "You MUST adhere strictly to the cognitive directives and logical constraints. "
                "CRITICAL: If the error mentions 'exact_quote', you MUST provide a physically contiguous, "
                "VERBATIM substring from the source text (without ANY markdown or alterations). "
                "If no such verbatim string exists, you MUST return null or an empty string.\n"
                "Regenerate your response ensuring all logical validations pass."
            )

        return (
            "[SYSTEM: STRICT JSON SCHEMA VALIDATION FAILED]\n"
            "Your previous response contained invalid JSON or failed Pydantic schema validation.\n"
            f"Error details: {error_msg}\n\n"
            "CRITICAL SCHEMA RULES:\n"
            "1. You MUST return ONLY valid JSON matching the exact schema requested.\n"
            "2. If the error says 'Field required' (e.g., missing 'atom_id'), you MUST provide it. Every evaluation MUST have a valid 'atom_id' from your <BLIND_ATOMS_TO_EVALUATE> list.\n"
            "3. If you evaluated a concept that was NOT explicitly listed in your instructions, REMOVE that evaluation block entirely. Do not hallucinate items.\n"
            "4. Do not include markdown blocks, conversational text, or any explanations outside the JSON."
        )
