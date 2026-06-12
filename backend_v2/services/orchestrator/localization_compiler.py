"""Localization Compiler for resolving I18n text and compiling LLM prompt instructions.

Extracts and centralizes translation resolution, XML rubric compilation, and
instruction compilation logic from the monolithic PromptCompiler (Rule 88).
"""

from __future__ import annotations

import datetime
import logging
from typing import Any

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.enums import EvaluationMandate
from backend_v2.models.v2_core import PromptBlock

logger = logging.getLogger(__name__)


class LocalizationCompiler:
    """Handles I18n text resolution and instruction compilation for LLM prompts.

    Centralizes all localization-sensitive prompt compilation logic previously
    embedded in the monolithic PromptCompiler.
    """

    def __init__(self) -> None:
        """Initialize LocalizationCompiler."""
        pass

    def resolve_i18n(self, text_obj: Any, target_locale: str) -> str:
        """Resolve an I18n JSON object to a string based on locale fallback rules.

        Args:
            text_obj: The I18n object (model or dict with default_locale and translations),
                      or a raw string (legacy fallback), or None.
            target_locale: The requested language code (e.g., 'fi' or 'en').

        Returns:
            Resolved text string, or empty string if None.

        Raises:
            ConfigurationError: If the text object is a legacy string or invalid type,
                or if the required locale translation is missing.
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
            logger.error("[LocalizationCompiler] %s", msg)
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

    def compile_xml_rubrics(
        self, criteria: list[PromptBlock], target_locale: str, execution_persona_block: PromptBlock | None = None
    ) -> str:
        """Epic 12/55: Generates Thick XML/Markdown rubrics for the System Prompt with Persona SSOT.

        Args:
            criteria: List of PromptBlock definitions to compile into rubrics.
            target_locale: The requested language code for label resolution.
            execution_persona_block: Optional PromptBlock defining the execution persona.

        Returns:
            A formatted string of XML rubrics for the system prompt.
        """
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
                            substance = assertion.concept_description.strip()
                            if substance:
                                assertion_xml = [f"  <CONCEPT_DEFINITION>\n    {substance}\n  </CONCEPT_DEFINITION>"]

                                acs = assertion.acceptance_criteria
                                if acs:
                                    ac_lines = [f"    - {ac.instruction}" for ac in acs if ac.instruction]
                                    if ac_lines:
                                        assertion_xml.append(
                                            "  <ACCEPTANCE_CRITERIA>\n"
                                            + "\n".join(ac_lines)
                                            + "\n  </ACCEPTANCE_CRITERIA>"
                                        )

                                aps = assertion.anti_patterns
                                if aps:
                                    ap_lines = [f"    - {ap.pattern}" for ap in aps if ap.pattern]
                                    if ap_lines:
                                        assertion_xml.append(
                                            "  <ANTI_PATTERNS>\n" + "\n".join(ap_lines) + "\n  </ANTI_PATTERNS>"
                                        )

                                mandate_text = mandate_str
                                if assertion.inverse_evidence:
                                    mandate_text += (
                                        " This is an inverse rule (Vice). If rule_satisfied = True "
                                        "(no issues found), evidence_found MUST be False and you must "
                                        'return an empty string "" for exact_quote. If rule_satisfied = False '
                                        "(violation found), evidence_found MUST be True and you MUST quote "
                                        "the exact violation."
                                    )
                                if assertion.allow_contextual_override:
                                    mandate_text += (
                                        " [CONTEXTUAL OVERRIDE ALLOWED] If the assertion's criteria are satisfied "
                                        "semantically or contextually across the text but no single exact verbatim "
                                        "quote can be isolated, you MUST: 1) Set contextual_override = true. 2) "
                                        "Provide a detailed explanation in semantic_reasoning with structural "
                                        "references. 3) Set exact_quote to exactly "
                                        "'[CONTEXTUAL_OVERRIDE_APPLIED]'. Do NOT hallucinate a quote. Only use "
                                        "this override if a direct literal quote is physically absent."
                                    )
                                assertion_xml.append(
                                    f"  <FAIL_FAST_MANDATE>\n    {mandate_text}\n  </FAIL_FAST_MANDATE>"
                                )

                                claims_texts.append("\n".join(assertion_xml))

                if claims_texts:
                    claims = "\n\n".join(claims_texts)
                    xml_blocks.append(f"    <CRITICAL_DIRECTIVES>\n{claims}\n    </CRITICAL_DIRECTIVES>")

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

        Raises:
            ConfigurationError: If a PromptBlock is missing mandatory ai_description.
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

        Raises:
            AppException: If execution_time string cannot be parsed as ISO-8601.
            ConfigurationError: If a runtime_variables block is missing mandatory ai_description.
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
                    logger.error("[LocalizationCompiler] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg,
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from e
            else:
                msg = f"Invalid execution_time type '{type(execution_time).__name__}'. Must be datetime, str, or None."
                logger.error("[LocalizationCompiler] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
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
