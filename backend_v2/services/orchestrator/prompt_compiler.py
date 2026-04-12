"""Prompt Compiler for generating dynamic Pydantic schemas and LLM prompts.

Transforms abstract workflow state and domain models into executable
LLM payloads with system context, strictness calibration, and format enforcement.
"""

from __future__ import annotations

import logging
from functools import lru_cache
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

        if path == "steps":
            return self._extract_value_from_state(
                "",
                {
                    "": {
                        k: v
                        for k, v in state_data.items()
                        if not str(k).startswith("_") and k not in ("inputs", "raw_inputs", "reasoning_context")
                    }
                },
            )

        # Support the standard V2 $steps namespace for explicit node targeting (e.g. $steps.sr_xyz.outputs)
        if path.startswith("steps."):
            path = path[len("steps.") :]

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
            # Epic 12: Flatten nested JSON into LLM-friendly Markdown (Attention Dilution patch)
            formatted = []
            for k, v in current.items():
                formatted.append(f'<prior_step_context source="{str(k).upper()}">')
                if isinstance(v, dict):
                    # Yritetään sukeltaa suoraan 'outputs' avaimeen jos se olemassa
                    target_dict = v.get("outputs", v) if "outputs" in v else v
                    for sub_k, sub_v in target_dict.items():
                        if isinstance(sub_v, dict):
                            formatted.append(f"### {str(sub_k).upper()}")
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
                                formatted.append(f"- **{clean_key}:** {micro_v}")
                        else:
                            formatted.append(f"- **{str(sub_k).title()}:** {sub_v}")
                else:
                    formatted.append(str(v))
                formatted.append("</prior_step_context>")
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
            from backend_v2.exceptions import AppException, ErrorCodes

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
        criteria: list[dict[str, Any]],
        has_search_result: bool = False,
        has_shuffled_atoms: bool = False,
        target_locale: str = "en",
    ) -> type[BaseModel]:
        import json

        # P4: Prevent Pydantic compilation explosion on 200+ step DAGs by hashing criteria
        # and delegating to an LRU cached private method.
        criteria_json = json.dumps(criteria, sort_keys=True)
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
        import json

        from pydantic import BaseModel, model_validator

        def make_micro_cot_base(_t: float, _cid: str) -> type[BaseModel]:
            class MicroCotBase(BaseModel):
                @model_validator(mode="after")
                def validate_micro_cot(self: Any) -> Any:
                    if hasattr(self, "step_4_final_score") and hasattr(self, "step_1_evidence_quote"):
                        score = self.step_4_final_score
                        quote = self.step_1_evidence_quote
                        if isinstance(score, (int, float)) and score >= _t:
                            if not quote or str(quote).strip() == "":
                                msg = (
                                    f"CRITICAL LOGICAL ERROR: You assigned a high score ({score}) "
                                    f"but failed to provide a 'step_1_evidence_quote'. "
                                    "Semantic self-healing triggered."
                                )
                                logger.warning(
                                    "Semantic Self-Healing Triggered: High score logic error.",
                                    extra={"score": score, "block_id": f"{_cid}_Evaluation"},
                                )
                                raise ValueError(msg)
                    return self

            return MicroCotBase

        criteria = json.loads(criteria_json)

        # Dictionary of fields to define for create_model
        fields: dict[str, Any] = {
            "reasoning_trace": (
                str,
                Field(
                    ...,
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
            from pydantic import ConfigDict

            class AtomResponse(BaseModel):
                model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
                atom_id: str = Field(..., description="Suora yhdiste Flattening-hookin generoimaan hash-avaimeen.")
                quote: str | None = Field(
                    default=None,
                    description="Pakotettu lainaus alkuperäisestä tekstistä Micro-CoT säännöllä. Null if no evidence.",
                )
                reasoning: str = Field(..., description="Kognitiivinen kitka ja arvioinnin perustelu.")
                boolean: bool = Field(..., description="Puhdas True/False -osumapäätös.")

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
                label_obj = crit["label"]
                block_type = crit.get("type", "float")
                extensions = crit.get("output_extensions", [])
            except KeyError as e:
                from backend_v2.exceptions import ConfigurationError, ErrorCodes

                msg = f"PromptBlock '{crit_id}' is missing strict evaluation parameter: {str(e)}."
                logger.error(
                    "PromptBlock structurally invalid.",
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "block_id": crit_id},
                )
                raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED}) from e

            label = self.resolve_i18n(label_obj, target_locale)
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

                theory_grounding = crit.get("theory_grounding", {})
                citation_ref = (
                    theory_grounding.get("citation_reference") if isinstance(theory_grounding, dict) else None
                )
                if citation_ref:
                    from typing import Literal

                    sub_fields["step_1b_cited_source_id"] = (
                        Literal[citation_ref] | None,
                        Field(
                            default=None,
                            description=(
                                "If your justification relies on authorized theory, you MUST RETURN EXACTLY: "
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
                sub_fields["extension_coaching"] = (
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
                    list[str],
                    Field(
                        ...,
                        description=(
                            "Actionable array of all necessary textual remediation steps. "
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

            if block_type not in ("float", "int"):
                sub_fields["step_4_final_score"] = (
                    str,
                    Field(..., description=f"Textual evaluation strictly mapped to <MATRIX id='{crit_id}'>."),
                )
                threshold = 0.0
            else:
                try:
                    scales_data = crit["scales"]
                    allow_decimals = bool(crit["allow_decimals"])
                except KeyError as e:
                    from backend_v2.exceptions import ConfigurationError, ErrorCodes

                    msg = f"PromptBlock '{crit_id}' is missing strict evaluation parameter: {str(e)}."
                    logger.error(
                        "PromptBlock structurally invalid.",
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "block_id": crit_id},
                    )
                    raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED}) from e

                if not scales_data:
                    from backend_v2.exceptions import ConfigurationError, ErrorCodes

                    msg = f"PromptBlock '{crit_id}' has empty 'scales' array."
                    raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})

                llm_min = float(min(s["score"] for s in scales_data))
                llm_max = float(max(s["score"] for s in scales_data))

                if allow_decimals:
                    decimal_instruction = "Select a precise score with exactly one decimal place"
                else:
                    decimal_instruction = "Select a whole integer score"

                sub_fields["step_4_final_score"] = (
                    float,
                    Field(
                        ...,
                        ge=llm_min,
                        le=llm_max,
                        description=(
                            f"Numeric score strictly evaluated using the <MATRIX id='{crit_id}'>. "
                            f"{decimal_instruction} reflecting the exact nuance and weight of the evidence."
                        ),
                    ),
                )
                from backend_v2.models.enums import SelfHealingThresholdRatio

                raw_ratio = crit.get("self_healing_evidence_threshold_ratio", SelfHealingThresholdRatio.STRICT.value)
                ratio_val = float(raw_ratio)

                threshold = llm_min + (llm_max - llm_min) * ratio_val

            from pydantic import ConfigDict

            MicroCotBase = make_micro_cot_base(threshold, crit_id)

            NestedModel = create_model(  # type: ignore[call-overload]
                f"{crit_id}_Evaluation",
                __base__=MicroCotBase,
                __config__=ConfigDict(extra="forbid", strict=True),
                **sub_fields,
            )

            fields[crit_id] = (NestedModel, Field(..., description=f"Evaluation object for {label}"))

        if not fields:
            fields["acknowledged_instruction"] = (
                str,
                Field(default="yes", description="Acknowledge completion of the instruction."),
            )

        try:
            from typing import cast

            from pydantic import ConfigDict

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

    def compile_xml_rubrics(self, criteria: list[dict[str, Any]], target_locale: str) -> str:
        """Epic 12: Generates Thick XML/Markdown rubrics for the System Prompt."""
        xml_blocks = ["<EVALUATION_RUBRICS>"]
        for crit in criteria:
            if crit.get("type") == "instruction":
                continue

            crit_id = crit.get("id")
            label = self.resolve_i18n(crit.get("label"), target_locale)
            desc = crit.get("ai_description", "")

            xml_blocks.append(f'  <MATRIX id="{crit_id}" title="{label}">')
            if desc:
                xml_blocks.append(f"    <DIRECTIVE>{desc}</DIRECTIVE>")

            scales = crit.get("scales", [])
            if scales:
                xml_blocks.append("    | Score | Label | Critical Directive |")
                xml_blocks.append("    |---|---|---|")
                for s in scales:
                    s_val = s.get("score")
                    s_lbl = self.resolve_i18n(s.get("name"), target_locale) if s.get("name") else s.get("ai_label", "")
                    claims = " ".join([c.get("ai_description", "") for c in s.get("claims", [])])
                    xml_blocks.append(f"    | {s_val} | {s_lbl} | {claims} |")

            xml_blocks.append("  </MATRIX>")
        xml_blocks.append("</EVALUATION_RUBRICS>")
        return "\n".join(xml_blocks)

    def compile_static_instructions(self, blocks: list[dict[str, Any]], target_locale: str) -> str:
        """Compile static instruction-type V2 PromptBlocks for the Cached System Prompt.

        Extracts blocks where type == "instruction" AND category_id != "runtime_variables".

        Args:
            blocks: List of PromptBlock dictionaries.
            target_locale: The requested language code.

        Returns:
            A formatted string of all static instruction directives.
        """
        compiled_lines = []
        for block in blocks:
            if block.get("type") == "instruction" and block.get("category_id") != "runtime_variables":
                label = self.resolve_i18n(block.get("label"), target_locale)
                desc = block.get("ai_description")
                if not desc:
                    from backend_v2.exceptions import ConfigurationError

                    block_id = block.get("id")
                    msg = f"PromptBlock '{block_id}' is missing mandatory 'ai_description'."
                    logger.error(
                        "PromptBlock is missing mandatory 'ai_description'.",
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "block_id": block_id},
                    )
                    raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})

                if label:
                    compiled_lines.append(f"[Static Instruction {target_locale.upper()}]: ### {label}")
                if desc:
                    compiled_lines.append(f"{desc}")

        return "\n\n".join(compiled_lines) if compiled_lines else ""

    def compile_dynamic_instructions(self, blocks: list[dict[str, Any]], target_locale: str) -> str:
        """Compile dynamic instruction-type V2 PromptBlocks for the Uncached User Tail.

        Extracts blocks where type == "instruction" AND category_id == "runtime_variables",
        and performs real-time variable substitutions (e.g. {CURRENT_DATE}).

        Args:
            blocks: List of PromptBlock dictionaries.
            target_locale: The requested language code.

        Returns:
            A formatted string of all dynamic runtime instruction directives.
        """
        import datetime

        now_utc = datetime.datetime.now(datetime.UTC)
        current_date_str = now_utc.strftime("%Y-%m-%d")
        dynamic_time_str = now_utc.strftime("%H:%M:%S UTC")

        compiled_lines = []
        for block in blocks:
            if block.get("type") == "instruction" and block.get("category_id") == "runtime_variables":
                label = self.resolve_i18n(block.get("label"), target_locale)
                desc = block.get("ai_description")
                if not desc:
                    from backend_v2.exceptions import ConfigurationError

                    block_id = block.get("id")
                    msg = f"PromptBlock '{block_id}' is missing mandatory 'ai_description'."
                    logger.error(
                        "PromptBlock is missing mandatory 'ai_description'.",
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "block_id": block_id},
                    )
                    raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})

                # Perform Runtime Variable Substitutions
                desc = desc.replace("{CURRENT_DATE}", current_date_str)
                desc = desc.replace("{DYNAMIC_TIME}", dynamic_time_str)

                if label:
                    compiled_lines.append(f"[Dynamic Context {target_locale.upper()}]: ### {label}")
                if desc:
                    compiled_lines.append(f"{desc}")

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
        from pydantic import BaseModel, ConfigDict

        class AtomResponse(BaseModel):
            model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
            atom_id: str = Field(..., description="Suora yhdiste Flattening-hookin generoimaan hash-avaimeen.")
            quote: str | None = Field(
                default=None,
                description="Pakotettu lainaus alkuperäisestä tekstistä Micro-CoT säännöllä. Null if no evidence.",
            )
            reasoning: str = Field(..., description="Kognitiivinen kitka ja arvioinnin perustelu.")
            boolean: bool = Field(..., description="Puhdas True/False -osumapäätös.")

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
            "</rules>\n"
            "</system_directive>"
        )
        instruction += (
            f"\n\nCRITICAL MANDATE: You must generate all your output text and reasoning "
            f"exclusively in the '{target_locale}' language."
        )
        return instruction
