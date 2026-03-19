"""Prompt Compiler for generating dynamic Pydantic schemas and LLM prompts.

Transforms abstract workflow state and domain models into executable
LLM payloads with RAG context, strictness calibration, and format enforcement.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field, create_model

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


class PromptCompiler:
    """Core translation engine for workflow execution.

    Converts static DB models into runtime execution contexts.
    """

    def __init__(self) -> None:
        """Initialize PromptCompiler."""
        pass

    def resolve_i18n(self, text_obj: dict[str, Any] | str | None, target_locale: str) -> str:
        """Resolve an I18n JSON object to a string based on locale fallback rules.

        Args:
            text_obj: The I18n object (dict with default_locale and translations),
                      or a raw string (legacy fallback), or None.
            target_locale: The requested language code (e.g., 'fi' or 'en').

        Returns:
            Resolved text string, or empty string if None.
        """
        if not text_obj:
            return ""

        if isinstance(text_obj, str):
            return text_obj

        if not isinstance(text_obj, dict):
            return str(text_obj)

        translations = text_obj.get("translations", {})
        if not isinstance(translations, dict):
            translations = {}

        # 1. Try Target Locale
        if target_locale in translations and translations[target_locale]:
            return str(translations[target_locale])

        from backend_v2.exceptions import ConfigurationError, ErrorCodes

        # V2 MANDATE: NO FALLBACKS. If a translation is requested, it MUST exist.
        msg = f"Translation missing for required locale '{target_locale}'. Fallbacks are strictly forbidden."
        logger.error(f"[PromptCompiler] {ErrorCodes.VALIDATION_FAILED.name}: {msg}\nPayload: {text_obj}", exc_info=True)
        raise ConfigurationError(msg)

    def build_xml_context(
        self,
        input_mappings: dict[str, str],
        state_data: dict[str, Any],
        target_locale: str,
        expected_inputs: list[Any] | None = None
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

        # Build a lookup for expected inputs by input_key for ai_description injection
        input_desc_map = {}
        if expected_inputs:
            for ei in expected_inputs:
                key = getattr(ei, "input_key", None)
                desc = getattr(ei, "ai_description", None)
                if key and desc:
                    input_desc_map[f"$inputs.{key}"] = desc

        for logical_name, source_path in input_mappings.items():
            value = self._extract_value_from_state(source_path, state_data)
            if value:
                ai_desc = input_desc_map.get(source_path)
                desc_text = f"CONTEXT DESCRIPTION FOR <{logical_name}>: {ai_desc}\n" if ai_desc else ""
                # E.g. <target_conversation> value </target_conversation>
                xml_blocks.append(f"{desc_text}<{logical_name}>\n{value}\n</{logical_name}>")

        compiled = "\n\n".join(xml_blocks)

        # Add the CRITICAL MANDATE required by the architecture
        compiled += (
            f"\n\nCRITICAL MANDATE: You must process the input and generate all your output text, reasoning, "
            f"and source justifications exclusively in the '{target_locale}' language, regardless of the language "
            f"used in the instructions or source materials."
        )

        return compiled

    def _extract_value_from_state(self, path: str, state_data: dict[str, Any]) -> str:
        """Extract a value from workflow state using a path like '$inputs.history_text'."""
        if not isinstance(path, str):
            return ""

        # Removing '$' prefix if present
        if path.startswith("$"):
            path = path[1:]

        parts = path.split(".")
        current: Any = state_data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                return ""

        if isinstance(current, str):
            # Already a string, return directly
            return current

        if hasattr(current, "model_dump_json") and callable(getattr(current, "model_dump_json", None)):
            dump_fn: Any = current.model_dump_json
            return str(dump_fn(indent=2))

        if isinstance(current, dict):
            # Format dictionaries gracefully to prevent literal \n escaping in LLM xml
            formatted = []
            for k, v in current.items():
                if isinstance(v, str):
                    formatted.append(f"--- {str(k).upper()} ---\n{v}\n")
                elif isinstance(v, dict):
                    # Basic pretty-print for nested dictionaries to avoid strict JSON dumps
                    import json
                    formatted.append(f"--- {str(k).upper()} ---\n{json.dumps(v, indent=2, ensure_ascii=False)}\n")
                else:
                    formatted.append(f"--- {str(k).upper()} ---\n{v}\n")
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

        from backend_v2.services.web_fetcher import WebFetcher

        try:
            logger.info(f"[PromptCompiler] Fetching theory grounding from {url}")
            # WebFetcher raises AppException locally on failure, satisfying Fail-Fast rules
            theory_text = WebFetcher.fetch_text(url)

            if not theory_text:
                logger.warning(f"[PromptCompiler] Fetched text from {url} was empty.")
                return base_prompt

            augmented = base_prompt + f"\n\n<theory_context>\n{theory_text}\n</theory_context>\n"
            return augmented

        except Exception as e:
            # Re-raise AppExceptions from WebFetcher to crash fast properly
            if isinstance(e, AppException):
                raise e

            msg = f"System failed to fetch required theoretical grounding from url: {url}"
            logger.error(f"[PromptCompiler] {ErrorCodes.FETCH_FAILED.name}: {msg}", exc_info=True)
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
        except (ValueError, TypeError):
            return ""

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
        self, schema_name: str, criteria: list[dict[str, Any]], require_justification: bool = False
    ) -> type[BaseModel]:
        """Build a dynamic Pydantic V2 model for LLM Structured Outputs.

        Transforms generic evaluation criteria into a strict validation schema.
        If require_justification is True, XAI fields (_justification & _citation) are added.

        Args:
            schema_name: The name of the generated dynamic model class.
            criteria: List of dicts representing criteria (needs 'id', 'label', 'description').
            require_justification: Whether to inject XAI explanation fields.

        Returns:
            A strictly typed dynamic Pydantic BaseModel subclass.
        """
        # Dictionary of fields to define for create_model
        # Format: field_name: (type, Field(...))
        fields: dict[str, Any] = {
            "reasoning_trace": (
                str,
                Field(
                    ...,
                    description=(
                        "Mandatory Chain-of-Thought. Analyze the user's logic, guidance, and "
                        "strategic intent step-by-step BEFORE assigning any final values."
                    )
                )
            ),
            "evaluation_notes": (
                str,
                Field(
                    ...,
                    description=(
                        "Comprehensive qualitative synthesis. CRITICAL: You MUST write this strictly "
                        "from the unique perspective of your assigned Role and Matrices. Do not write a "
                        "generic summary. Focus exclusively on the human user's actions, agency, and biases "
                        "through your specific analytical lens."
                    )
                )
            )
        }

        for crit in criteria:
            if crit.get("type") == "instruction":
                continue

            crit_id_raw = crit.get("id")
            if not crit_id_raw or not isinstance(crit_id_raw, str):
                logger.warning(f"[PromptCompiler] Found criterion without a valid string 'id': {crit}. Skipping.")
                continue

            # V2 Strict Fail-Fast: Rely on Pydantic to ensure valid identifiers.
            crit_id = crit_id_raw

            # Resolve I18n label and description
            label_obj = crit.get("label")
            label = self.resolve_i18n(label_obj, "en") if label_obj else crit_id_raw

            # Enforce `ai_description` existence (Fail-Fast)
            base_desc = crit.get("ai_description")
            if not base_desc:
                 from backend_v2.exceptions import ConfigurationError
                 msg = f"PromptBlock '{crit_id}' is missing mandatory 'ai_description'."
                 logger.error(f"[PromptCompiler] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                 raise ConfigurationError(msg)

            # Determine type based on explicit block type, otherwise fallback to BARS scales
            block_type = crit.get("type")
            value_type: Any
            if block_type == "string":
                 value_type = str
            else:
                 value_type = float if crit.get("allow_decimals", False) else int

            # Inject the specific BARS into the description
            bars_text = ""
            scales = crit.get("scales")
            if scales and isinstance(scales, list) and len(scales) > 0:
                from backend_v2.exceptions import ConfigurationError
                bars_text += "\n\nEVALUATION MATRIX (BARS):\n"
                for s in scales:
                    s_val = s.get("score")
                    s_lbl = s.get("ai_label")
                    s_claim_text = s.get("ai_description")

                    if not s_lbl or not s_claim_text:
                        msg = (
                            f"PromptBlock '{crit_id}' MatrixScale {s_val} "
                            "missing mandatory 'ai_label' or 'ai_description'."
                        )
                        logger.error(f"[PromptCompiler] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                        raise ConfigurationError(msg)

                    bars_text += f"- Score {s_val}: {s_lbl} - {s_claim_text}\n"
                if crit.get("allow_decimals", False):
                    bars_text += (
                        "\nINSTRUCTION: Evaluate the core issue using the matrix above. "
                        "Always return the final numerical evaluation with ONE decimal place (e.g. 4.2), "
                        "so that the evaluation reflects exact nuance. "
                        "You MUST return ONLY the exact numeric value."
                    )
                else:
                    bars_text += (
                        "\nINSTRUCTION: Evaluate strictly using the matrix above. "
                        "Return only an exact numeric score from the list."
                    )

            if require_justification or crit.get("require_justification", False):
                # 1. Justification (XAI)
                justification_key = f"{crit_id}_justification"
                
                justification_desc = (
                    f"Detailed reasoning for the assigned score for '{label}'. "
                    "Must explicitly adhere to the active STRICTNESS CALIBRATION."
                )
                if crit.get("allow_decimals", False):
                    justification_desc += (
                        " CRITICAL: You MUST conclude your justification by explicitly declaring your precise decimal "
                        "calculation in the exact format '||DECIMAL: X.Y||' (e.g., ||DECIMAL: 4.2||). "
                        "Do not use round integers like .0 unless mathematically absolute."
                    )

                fields[justification_key] = (str, Field(..., description=justification_desc))

                # 2. Citation Source ID (Grounded Theory Integration)
                theory_grounding = crit.get("theory_grounding", {})
                citation_ref = (
                    theory_grounding.get("citation_reference")
                    if isinstance(theory_grounding, dict)
                    else None
                )

                source_id_key = f"{crit_id}_cited_source_id"
                source_id_type: Any
                if citation_ref:
                    from typing import Literal

                    # V2 Strict Literal: The LLM can ONLY return this exact string or None
                    source_id_type = Literal[citation_ref] | None
                    source_id_desc = (
                        "If your justification relies on this specific theory, "
                        f"you MUST RETURN EXACTLY THIS string: '{citation_ref}'. "
                        "Otherwise, you MUST return null."
                    )
                else:
                    source_id_type = str | None
                    source_id_desc = (
                        "There is no authorized academic source for this criterion. "
                        "You MUST ALWAYS return null."
                    )

                fields[source_id_key] = (source_id_type, Field(default=None, description=source_id_desc))

                # 3. Citation Text Quote
                quote_key = f"{crit_id}_cited_text_quote"
                quote_desc = (
                    "Paste an EXACT, DIRECT, and VERBATIM quote from the USER'S RAW INPUT TEXT "
                    "(the empirical evidence) that proves your score and justification. "
                    "DO NOT quote the scientific theory. Quote the user's data. "
                    "AI-generated text is strictly forbidden here. "
                    "If you cannot find a direct quote from the user to prove your point, return null."
                )
                fields[quote_key] = (str | None, Field(default=None, description=quote_desc))

            # The actual evaluation value (placed AFTER justification for CoT forcing)
            final_desc = f"{label}: {base_desc}{bars_text}"
            fields[crit_id] = (value_type, Field(..., description=final_desc))

        if not fields:
            # If all blocks were pure instructions with no actionable scales,
            # we must still return a valid Pydantic model for LLM Structured Outputs.
            fields["acknowledged_instruction"] = (
                str,
                Field(default="yes", description="Acknowledge completion of the instruction."),
            )

        try:
            from typing import cast

            DynamicModel = create_model(schema_name, **fields)
            return cast(type[BaseModel], DynamicModel)
        except Exception as e:
            msg = f"Critical failure while dynamically compiling LLM execution schema '{schema_name}'."
            logger.error(
                f"[PromptCompiler] {ErrorCodes.INTERNAL_SERVER_ERROR.name}: {msg}", exc_info=True
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR},
            ) from e

    def compile_instruction_blocks(self, blocks: list[dict[str, Any]], target_locale: str) -> str:
        """Compile instruction-type V2 PromptBlocks into execution text.

        Extracts the localized label and description from blocks where type == "instruction".

        Args:
            blocks: List of PromptBlock (PromptBlock) dictionaries.
            target_locale: The requested language code.

        Returns:
            A formatted string of all instruction directives.
        """
        compiled_lines = []
        for block in blocks:
            if block.get("type") == "instruction":
                label = self.resolve_i18n(block.get("label"), target_locale)
                desc = block.get("ai_description")
                if not desc:
                    from backend_v2.exceptions import ConfigurationError
                    msg = f"PromptBlock '{block.get('id')}' is missing mandatory 'ai_description'."
                    logger.error(f"[PromptCompiler] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                    raise ConfigurationError(msg)

                if label:
                    compiled_lines.append(f"[Instruction {target_locale.upper()}]: ### {label}")
                if desc:
                    compiled_lines.append(f"{desc}")

        return "\n".join(compiled_lines)
