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
from typing import Any, Literal, cast

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, create_model, model_validator

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.enums import EvaluationMandate
from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.web_fetcher import WebFetcher

logger = logging.getLogger(__name__)


class EvidenceType(str, Enum):
    EXPLICIT_QUOTE = "EXPLICIT_QUOTE"
    IMPLIED_INTENT = "IMPLIED_INTENT"
    NO_EVIDENCE = "NO_EVIDENCE"


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

        # Add the CRITICAL MANDATE required by the architecture
        compiled += (
            f"\n\n<CRITICAL_LANGUAGE_MANDATE>\n"
            f"You must process the input and generate all your output text, reasoning, "
            f"and source justifications exclusively in the '{target_locale}' language, regardless of the language "
            f"used in the instructions or source materials.\n"
            f"</CRITICAL_LANGUAGE_MANDATE>"
        )

        return compiled

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
        """Build a dynamic Pydantic V2 model for LLM Structured Outputs."""

        def make_micro_cot_base(_cid: str, _citation_ref: str | None = None) -> type[BaseModel]:
            class MicroCotBase(BaseModel):
                @model_validator(mode="before")
                @classmethod
                def heal_citations(cls, data: Any) -> Any:
                    if isinstance(data, dict) and _citation_ref:
                        # Pydantic fails if the LLM arbitrarily truncates or splits the long citation string.
                        # Self-healing: if the returned string is a valid substring of the full citation, auto-fix it.
                        val = data.get("step_1b_cited_source_id")
                        if val and isinstance(val, str) and len(val) > 10 and val in _citation_ref:
                            data["step_1b_cited_source_id"] = _citation_ref
                    return data

            return MicroCotBase

        criteria = json.loads(criteria_json)

        # Dictionary of fields to define for create_model
        fields: dict[str, Any] = {
            "reasoning_trace": (
                str,
                Field(
                    ...,
                    alias="step_1_reasoning_trace",
                    description=(
                        "Mandatory Chain-of-Thought. Analyze the user's logic, guidance, and "
                        "strategic intent step-by-step BEFORE assigning any final values."
                    ),
                ),
            ),
            "evaluation_notes": (
                str,
                Field(
                    ...,
                    description=(
                        "Comprehensive qualitative synthesis. CRITICAL: You MUST write this strictly "
                        "from the unique perspective of your assigned Role and Matrices. Do not write a "
                        "through your specific analytical lens. "
                        "STRICT MANDATE: You MUST write this specific field exclusively "
                        f"in the '{target_locale}' language."
                    ),
                ),
            ),
        }

        # Epic 20 Phase 7 Hybrid Fix: Inject AtomResponse mapping directly into dynamic schema!
        if has_shuffled_atoms:

            class AtomResponse(BaseModel):
                model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
                atom_id: str = Field(..., description="Suora yhdiste Flattening-hookin generoimaan hash-avaimeen.")
                exact_quote: str = Field(
                    ..., description="The exact quote if evidence was found, otherwise empty string."
                )
                pre_quote_anchor: str = Field(..., description="5 words before the exact quote, or empty.")
                post_quote_anchor: str = Field(..., description="5 words after the exact quote, or empty.")
                mechanical_trace: str = Field(..., alias="step_1_mechanical_trace", description="Your reasoning trace.")

            fields["evaluations"] = (list[AtomResponse], Field(..., description="Array of blinded evaluations."))

        for crit in criteria:
            if crit.get("type") == "instruction":
                continue

            crit_id_raw = crit.get("id")
            if not crit_id_raw or not isinstance(crit_id_raw, str):
                logger.warning("[PromptCompiler] Found criterion without a valid string 'id': %s. Skipping.", crit)
                continue

            crit_id = crit_id_raw

            try:
                _label_obj = crit["label"]
                extensions = crit.get("output_extensions", [])
            except KeyError as e:
                msg = f"PromptBlock '{crit_id}' is missing strict evaluation parameter: {str(e)}."
                logger.error(
                    "PromptBlock structurally invalid.",
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "block_id": crit_id},
                )
                raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED}) from e

            theory_grounding = crit.get("theory_grounding", {})
            citation_ref = theory_grounding.get("citation_reference") if isinstance(theory_grounding, dict) else None

            sub_fields: dict[str, tuple[Any, Any]] = {}

            if "citation" in extensions:
                sub_fields["step_1_evidence_quote"] = (
                    str | None,
                    Field(
                        default=None,
                        description=(
                            "Provide an exact verbatim quote or a strong semantic justification "
                            "from the user's RAW INPUT TEXT that serves as empirical evidence. "
                            "AI-generated pure hallucinations are strictly forbidden. "
                            "If no evidence or connection exists, return null."
                        ),
                    ),
                )

                if citation_ref:
                    sub_fields["step_1b_cited_source_id"] = (
                        Literal[citation_ref] | None,
                        Field(
                            default=None,
                            description=(
                                "If your justification relies on authorized theory, "
                                "you MUST RETURN THIS EXACT ENTIRE STRING "
                                "(do not split or truncate it): "
                                f"'{citation_ref}'. Otherwise return null."
                            ),
                        ),
                    )

                if has_search_result:
                    sub_fields["step_1c_google_citation"] = (
                        str | None,
                        Field(
                            default=None,
                            description=(
                                "CRITICAL FACT CHECK: Mirror your output against the 'search_result' XML element. "
                                "Does the Google data support or refute the claim? If unrelated, return null."
                            ),
                        ),
                    )

            if "falsification" in extensions:
                sub_fields["step_2_falsification"] = (
                    str,
                    Field(
                        ...,
                        description=(
                            "Devil's advocate formulation argument. Why might your initial assumption be wrong? "
                            f"MANDATORY LANGUAGE: '{target_locale}'."
                        ),
                    ),
                )

            if "justification" in extensions:
                sub_fields["step_3_logical_friction"] = (
                    str,
                    Field(
                        ...,
                        description=(
                            f"Detailed reasoning bridging the evidence to <MATRIX id='{crit_id}'>. "
                            f"MANDATORY LANGUAGE: '{target_locale}'."
                        ),
                    ),
                )

            if "coaching" in extensions:
                sub_fields["step_3_coaching"] = (
                    str,
                    Field(
                        ...,
                        description=(
                            "Concrete coaching tip/remediation advice to the subject. "
                            f"MANDATORY LANGUAGE: '{target_locale}'."
                        ),
                    ),
                )
            if "confidence" in extensions:
                sub_fields["extension_confidence"] = (
                    float,
                    Field(
                        ..., ge=0.0, le=100.0, description="Numerical confidence from 0.0 to 100.0 based on evidence."
                    ),
                )
            if "missing_context" in extensions:
                sub_fields["extension_missing_context"] = (
                    str,
                    Field(
                        ...,
                        description=f"Missing context from the provided text. MANDATORY LANGUAGE: '{target_locale}'.",
                    ),
                )
            if "risk_flag" in extensions:
                sub_fields["extension_risk_flag"] = (
                    bool,
                    Field(..., description="True if there is a severe risk present; False otherwise."),
                )
            if "remediation_steps" in extensions:
                sub_fields["extension_remediation_steps"] = (
                    str,
                    Field(
                        ...,
                        description=(
                            "Actionable textual remediation steps, formatted clearly and separated by newlines. "
                            f"MANDATORY LANGUAGE: '{target_locale}'."
                        ),
                    ),
                )
            if "emotional_sentiment" in extensions:
                sub_fields["extension_emotional_sentiment"] = (
                    str,
                    Field(
                        ...,
                        description=(
                            f"Analysis of author's emotional state or tone. MANDATORY LANGUAGE: '{target_locale}'."
                        ),
                    ),
                )
            if "theory_link" in extensions:
                sub_fields["extension_theory_link"] = (
                    str,
                    Field(
                        ...,
                        description=(
                            "Direct logical connection to the governing theory framework. "
                            f"MANDATORY LANGUAGE: '{target_locale}'."
                        ),
                    ),
                )

            MicroCotBase = make_micro_cot_base(crit_id, citation_ref)

            NestedModel = create_model(  # type: ignore[call-overload]
                f"{crit_id}_Evaluation",
                __base__=MicroCotBase,
                __config__=ConfigDict(extra="forbid", strict=True),
                **sub_fields,
            )
            desc_val = f"Evaluation object for {crit_id}"
            fields[crit_id] = (NestedModel, Field(..., description=desc_val))

        if not fields:
            fields["acknowledged_instruction"] = (
                str,
                Field(default="yes", description="Acknowledge completion of the instruction."),
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

    def compile_xml_rubrics(self, criteria: list[PromptBlock], target_locale: str) -> str:
        """Epic 12: Generates Thick XML/Markdown rubrics for the System Prompt."""
        xml_blocks = ["<EVALUATION_RUBRICS>"]
        for crit in criteria:
            if crit.type == "instruction":
                continue

            crit_id = crit.id
            label = self.resolve_i18n(crit.label, target_locale)
            desc = crit.ai_description or ""

            xml_blocks.append(f'  <MATRIX id="{crit_id}" title="{label}">')
            if desc:
                xml_blocks.append(f"    <DIRECTIVE>{desc}</DIRECTIVE>")

            scales = crit.scales or []
            if scales:
                xml_blocks.append("    <SCALES>")
                mandate_str = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
                for s in scales:
                    s_val = s.score
                    s_lbl = self.resolve_i18n(s.name, target_locale) if s.name else s.ai_label

                    claims_texts = []
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
                                claims_texts.append(f"{rule_text} {mandate_str}")

                    claims = " ".join(claims_texts)
                    xml_blocks.append(f'      <SCALE value="{s_val}" label="{s_lbl}">')
                    xml_blocks.append(f"        <CRITICAL_DIRECTIVE>{claims}</CRITICAL_DIRECTIVE>")
                    xml_blocks.append("      </SCALE>")
                xml_blocks.append("    </SCALES>")

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
            "CRITICAL FORMATTING RULE: You MUST NEVER include raw system IDs, UUIDs, or MD5 hashes "
            "(e.g. 'sr_566e...', 'f6091a1defeae...') in your final output text, reasoning, or justification. "
            "Do NOT use `atom_id` values as citations. Always refer to concepts by their human-readable "
            "names or descriptions.\n"
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
            if block.type == "instruction" and block.category_id != "runtime_variables":
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

    def compile_dynamic_instructions(self, blocks: list[PromptBlock], target_locale: str) -> str:
        """Compile dynamic instruction-type V2 PromptBlocks for the Uncached User Tail.

        Extracts blocks where type == "instruction" AND category_id == "runtime_variables",
        and performs real-time variable substitutions (e.g. {CURRENT_DATE}).

        Args:
            blocks: List of PromptBlock definitions.
            target_locale: The requested language code.

        Returns:
            A formatted string of all dynamic runtime instruction directives.
        """
        now_utc = datetime.datetime.now(datetime.UTC)
        current_date_str = now_utc.strftime("%Y-%m-%d")
        dynamic_time_str = now_utc.strftime("%H:%M:%S UTC")

        compiled_lines = []
        for block in blocks:
            if block.type == "instruction" and block.category_id == "runtime_variables":
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
            atom_id: str = Field(..., description="Suora yhdiste Flattening-hookin generoimaan hash-avaimeen.")
            step_1_evidence_type: EvidenceType = Field(
                ..., description="CRITICAL: You MUST choose your strategy first."
            )
            step_2_quote: str | None = Field(
                default=None,
                description="Required if evidence_type is EXPLICIT_QUOTE. The exact verbatim quote.",
            )
            step_3_implicit_justification: str | None = Field(
                default=None,
                description=(
                    "Required ONLY if evidence_type is IMPLIED_INTENT. "
                    "Provide an exhaustive 20+ word justification to prove the implied intent."
                ),
            )
            step_4_reasoning: str = Field(..., description="Final cognitive friction and evaluation reasoning.")
            step_5_boolean: bool = Field(..., description="The final True/False decision.")

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
            evaluations=(list[AtomResponse], Field(..., description="Array of blinded evaluations.")),
        )

        return DynamicModel

    def compile_blind_system_instruction(self, target_locale: str = "en") -> str:
        """Create a Micro-CoT Prompt-block for the system role forcing full blindness."""
        instruction = (
            "<system_directive>\n"
            "<objective>Tekoäly toimii mekaanisena, empatiattomana data-erottelijana.</objective>\n"
            "<rules>\n"
            "  <rule>Täysi sokeus on pakotettu. Matrix-sarakkeiden ryhmittely on ehdottomasti kielletty.</rule>\n"
            "  <rule>Sovella 'Duck-Typing Token Shield' -konseptia. Käsittele atomit irrallisina.</rule>\n"
            "  <rule>CONSTRUCTIVE LENIENCY: Anna vastaajalle 'Benefit of the Doubt'. "
            "Jos ratkaisu on teknisesti mahdollinen vaikkakin epätäydellinen, hyväksy se.</rule>\n"
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
            original_id=(str, Field(..., description="The unique ID of the mapped item.")),
            payload=(item_schema, Field(..., description="The generated/evaluated payload for this specific item.")),
        )

        DynamicModel = create_model(
            schema_name,
            __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
            chunk_id=(str, Field(..., description="The Opaque Stripe ID of the current chunk.")),
            # dynamically generated type aliases aren't parsed statically by mypy
            records=(list[ChunkRecordModel], Field(..., description="Array of processed map-reduce records.")),  # type: ignore[valid-type]
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
                "Regenerate your response ensuring all logical validations pass."
            )

        return (
            "[SYSTEM: STRICT JSON SCHEMA VALIDATION FAILED]\n"
            "Your previous response contained invalid JSON or failed Pydantic schema validation.\n"
            f"Error details: {error_msg}\n\n"
            "You MUST return ONLY valid JSON matching the exact schema requested. "
            "Do not include markdown blocks, conversational text, or any explanations outside the JSON."
        )
