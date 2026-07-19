"""Prompt Compiler for generating dynamic Pydantic schemas and LLM prompts.

Transforms abstract workflow state and domain models into executable
LLM payloads with system context, strictness calibration, and format enforcement.

Acts as a high-level orchestrator delegating schema generation to SchemaFactory
and localization/instruction compilation to LocalizationCompiler (SRP Rule 88).
"""

from __future__ import annotations

import datetime
import logging
from typing import Any

from pydantic import BaseModel

from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import ExpectedInput, PromptBlock
from backend_v2.services.orchestrator.localization_compiler import LocalizationCompiler
from backend_v2.services.orchestrator.schema_factory import (
    EvidenceType,
    SchemaFactory,
    StrippedBaseMatrixXAI,
)

# Backward-compatible re-exports for consumers importing from prompt_compiler
__all__ = [
    "EvidenceType",
    "PromptCompiler",
    "StrippedBaseMatrixXAI",
]

logger = logging.getLogger(__name__)


class PromptCompiler:
    """Core translation engine for workflow execution.

    Converts static DB models into runtime execution contexts.
    Delegates schema generation to SchemaFactory and localization
    to LocalizationCompiler (SRP God Object decomposition, Rule 88).

    Attributes:
        _schema_factory: Handles dynamic Pydantic schema generation.
        _localization_compiler: Handles I18n resolution and instruction compilation.
    """

    def __init__(self) -> None:
        """Initialize PromptCompiler with composed sub-components."""
        self._localization_compiler = LocalizationCompiler()
        self._schema_factory = SchemaFactory(resolve_i18n_fn=self._localization_compiler.resolve_i18n)

    # ── Delegated LocalizationCompiler methods ──────────────────────────

    def resolve_i18n(self, text_obj: Any, target_locale: str) -> str:
        """Resolve an I18n JSON object to a string based on locale fallback rules.

        Args:
            text_obj: The I18n object (model or dict with default_locale and translations),
                      or a raw string (legacy fallback), or None.
            target_locale: The requested language code (e.g., 'fi' or 'en').

        Returns:
            Resolved text string, or empty string if None.
        """
        return self._localization_compiler.resolve_i18n(text_obj, target_locale)

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
        return self._localization_compiler.compile_xml_rubrics(criteria, target_locale, execution_persona_block)

    def compile_static_instructions(self, blocks: list[PromptBlock], target_locale: str) -> str:
        """Compile static instruction-type V2 PromptBlocks for the Cached System Prompt.

        Args:
            blocks: List of PromptBlock definitions.
            target_locale: The requested language code.

        Returns:
            A formatted string of all static instruction directives.
        """
        return self._localization_compiler.compile_static_instructions(blocks, target_locale)

    def compile_dynamic_instructions(
        self,
        blocks: list[PromptBlock],
        target_locale: str,
        execution_time: datetime.datetime | str | None = None,
    ) -> str:
        """Compile dynamic instruction-type V2 PromptBlocks for the Uncached User Tail.

        Args:
            blocks: List of PromptBlock definitions.
            target_locale: The requested language code.
            execution_time: Optional static timestamp for determinism.

        Returns:
            A formatted string of all dynamic runtime instruction directives.
        """
        return self._localization_compiler.compile_dynamic_instructions(blocks, target_locale, execution_time)

    # ── Delegated SchemaFactory methods ─────────────────────────────────

    def build_dynamic_schema(
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
        allowed_mcp_prefixes: list[str] | None = None,
        max_evaluations: int | None = None,
    ) -> type[BaseModel]:
        """Build a dynamic Pydantic V2 model for LLM Structured Outputs.

        Args:
            schema_name: Name for the generated Pydantic model class.
            criteria: List of PromptBlock definitions driving schema fields.
            has_shuffled_atoms: Whether to include shuffled atom evaluation fields.
            target_locale: Target language code for label resolution.
            strictness_level: Strictness level to control field leniency.
            source_document_ids: Dynamic literals corresponding to available documents.
            allowed_atom_ids: Dynamic literals corresponding to available atom items.
            allowed_dynamic_keys: Dynamic keys loaded from step input mappings.
            allowed_mcp_prefixes: List of dynamic tool prefixes (e.g. tavily_, jira_).
            max_evaluations: Dynamic upper limit for evaluations array.

        Returns:
            A dynamically generated Pydantic model class.
        """
        return self._schema_factory.build_dynamic_schema(
            schema_name,
            criteria,
            has_shuffled_atoms=has_shuffled_atoms,
            target_locale=target_locale,
            strictness_level=strictness_level,
            source_document_ids=source_document_ids,
            allowed_atom_ids=allowed_atom_ids,
            allowed_dynamic_keys=allowed_dynamic_keys,
            max_evaluations=max_evaluations,
        )

    def build_chunk_response_schema(self, schema_name: str, item_schema: type[BaseModel]) -> type[BaseModel]:
        """Build dynamic Pydantic V2 schema for chunked Map-Reduce execution.

        Args:
            schema_name: Name for the generated Pydantic model class.
            item_schema: The inner Pydantic model defining each record's payload.

        Returns:
            A dynamically generated Pydantic model class for chunk responses.
        """
        return self._schema_factory.build_chunk_response_schema(schema_name, item_schema)

    # ── Native PromptCompiler methods (remain here) ─────────────────────

    def build_xml_context(
        self,
        input_mappings: dict[str, str],
        state_data: dict[str, Any],
        target_locale: str,
        expected_inputs: list[Any] | None = None,
        alias_engine: Any = None,
    ) -> str:
        """Build XML semantic blocks from raw input mappings for LLM context.

        Args:
            input_mappings: Dict mapping logical names to value paths/keys.
            state_data: The current workflow execution state containing values.
            target_locale: The requested output locale string.
            expected_inputs: Optional list of ExpectedInput definitions to extract ai_description.
            alias_engine: Optional alias engine for source document IDs.

        Returns:
            A single string containing XML-wrapped elements.
        """
        xml_blocks = []

        # Build a lookup for expected inputs by input_key for full semantic context injection
        input_meta_map = {}
        if expected_inputs:
            for ei in expected_inputs:
                if not isinstance(ei, ExpectedInput):
                    continue

                key = ei.input_key
                if not key:
                    continue

                # Fail-Fast Mandatory I18n extraction
                label_obj = ei.label
                label_dict = label_obj.model_dump(mode="json") if isinstance(label_obj, BaseModel) else label_obj
                label_str = self.resolve_i18n(label_dict, target_locale) if label_dict else ""

                desc_obj = ei.description
                desc_dict = desc_obj.model_dump(mode="json") if isinstance(desc_obj, BaseModel) else desc_obj
                desc_str = self.resolve_i18n(desc_dict, target_locale) if desc_dict else ""

                ai_desc = ei.ai_description or ""

                input_meta_map[f"$inputs.{key}"] = {
                    "label": label_str,
                    "desc": desc_str,
                    "ai_desc": ai_desc,
                    "is_chat_history": getattr(ei, "is_chat_history", False),
                }

        for logical_name, source_path in input_mappings.items():
            value = self._extract_value_from_state(source_path, state_data)
            if value:
                source_id_to_use = logical_name
                if alias_engine:
                    alias = alias_engine.register(logical_name, prefix="doc")
                    alias_engine.source_document_aliases.append(alias)
                    source_id_to_use = alias

                base_path = ".".join(source_path.split(".")[:2]) if source_path.startswith("$") else source_path
                meta = input_meta_map.get(base_path)

                desc_text = ""
                if meta:
                    desc_text += "  <document_metadata>\n"
                    desc_text += f"    <document_id>{source_id_to_use}</document_id>\n"
                    if meta["label"]:
                        desc_text += f"    <document_name>{meta['label']}</document_name>\n"

                    if meta["ai_desc"]:
                        desc_text += f"    <ai_context_mandate>{meta['ai_desc']}</ai_context_mandate>\n"
                    desc_text += "  </document_metadata>\n"

                is_chat_history = meta.get("is_chat_history", False) if meta else False
                encapsulated_val = TemplateProcessor.encapsulate_payload(value)

                if source_path.startswith("$inputs"):
                    if not is_chat_history:
                        wrapped_val = f"<user_payload>\n{encapsulated_val}\n</user_payload>"
                    else:
                        wrapped_val = encapsulated_val
                elif source_path.startswith("$steps"):
                    wrapped_val = f"<ai_draft_context>\n{encapsulated_val}\n</ai_draft_context>"
                else:
                    wrapped_val = encapsulated_val

                xml_blocks.append(
                    f'<matrix_input source_id="{source_id_to_use}">\n{desc_text}{wrapped_val}\n</matrix_input>'
                )

        compiled = "\n\n".join(xml_blocks)

        return compiled

    def _extract_value_from_state(self, path: str, state_data: dict[str, Any]) -> str:
        """Extract a value from workflow state using a path like '$inputs.history_text'.

        Args:
            path: The dot-notation path string (e.g., '$inputs.document').
            state_data: The current workflow execution state dictionary.

        Returns:
            The extracted and stringified value.

        Raises:
            AppException: If the path is invalid or resolution fails.
        """
        if not isinstance(path, str):
            msg = f"Variable reference path must be a string, got {type(path)}"
            logger.error("[PromptCompiler] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        # Removing '$' prefix if present
        if path.startswith("$"):
            path = path[1:]

        parts = path.split(".")
        current = state_data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, BaseModel) and part in current.model_fields:
                current = current.model_dump()[part]
            else:
                msg = f"Path resolution failed: '{path}'. Component '{part}' is missing from state context."
                logger.error("[PromptCompiler] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                )

        if isinstance(current, str):
            # Already a string, return directly
            return current

        if isinstance(current, BaseModel):
            return str(current.model_dump_json(indent=2))

        if isinstance(current, dict):
            # Epic 12: Flatten nested JSON into LLM-friendly Markdown (Attention Dilution patch)
            formatted = []
            for k, v in current.items():
                clean_k = str(k).upper()
                formatted.append(f"<{clean_k}>")
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
                                    f"  <{clean_key.replace(' ', '_')}>{TemplateProcessor.encapsulate_payload(micro_v)}</{clean_key.replace(' ', '_')}>"
                                )
                            formatted.append(f"</{str(sub_k).upper()}>")
                        else:
                            clean_sub_k = str(sub_k).title().replace(" ", "_")
                            formatted.append(
                                f"<{clean_sub_k}>{TemplateProcessor.encapsulate_payload(sub_v)}</{clean_sub_k}>"
                            )
                else:
                    formatted.append(TemplateProcessor.encapsulate_payload(v))
                formatted.append(f"</{clean_k}>")
            return "\n".join(formatted).strip()

        return str(current)

    def calibrate_strictness(self, level: int | float | None) -> str:
        """Convert a numeric strictness level (0-100) into a semantic directive.

        Args:
            level: The strictness integer, 0 (Lenient) to 100 (Unforgiving).

        Returns:
            A semantic prompt string commanding the LLM of the desired strictness behavior.

        Raises:
            AppException: If the strictness level cannot be parsed.
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

        return f"SCORING_STRICTNESS: {val}/100"

    def generate_mcp_instruction(self, allowed_tools: list[str]) -> str:
        """Epic 13 M2: Generate dynamic instructions for active MCP tools.

        Args:
            allowed_tools: List of allowed MCP tool identifiers.

        Returns:
            A formatted MCP instruction string, or empty string if no tools.
        """
        if not allowed_tools:
            return ""
        tool_list = ", ".join(allowed_tools)
        return (
            "[SYSTEM: DYNAMIC TOOL AUTOMATION]\n"
            f"Use the dynamic tools [{tool_list}] proactively to search for up-to-date material. "
            "Stop data collection as soon as you have sufficient context. "
            "Embed your discovered sources into the corresponding extension fields."
        )

    def compile_chunk_payload_instruction(self, chunk_id: str, payload_text: str) -> str:
        """Generates an isolated context block fenced explicitly into `<user_payload>`.

        Args:
            chunk_id: The unique identifier of the current execution chunk.
            payload_text: The raw payload text to wrap.

        Returns:
            A formatted chunk payload instruction string.
        """
        safe_payload = TemplateProcessor.encapsulate_payload(payload_text)
        return (
            f"You are processing map-reduce chunk '{chunk_id}'.\n"
            "Evaluate ONLY the following payload mapping to the strict chunk_id structure:\n"
            f"<user_payload>\n{safe_payload}\n</user_payload>"
        )

    @staticmethod
    def get_schema_healing_prompt(
        error_msg: str, is_logical_error: bool, is_eof: bool, strictness_level: int | None = None
    ) -> str:
        """Generate a Self-Healing prompt for LLM execution recovery.

        Args:
            error_msg: The specific validation or logical error message.
            is_logical_error: True if the failure was a semantic Domain validation, False if Pydantic syntax.
            is_eof: True if the LLM output was cut off (e.g. max_tokens reached).
            strictness_level: Strictness level to control field leniency.

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
                "If no such verbatim string exists, you MUST return null or an empty string.\n"
                "IF these sources do not actually contain your claim, RETURN AN EMPTY LIST []. Do not invent sources.\n"
                "Regenerate your response ensuring all logical validations pass."
            )

        base = (
            "[SYSTEM: STRICT JSON SCHEMA VALIDATION FAILED]\n"
            "Your previous response contained invalid JSON or failed Pydantic schema validation.\n"
            f"Error details: {error_msg}\n\n"
            "ADDITIONAL RECOVERY INSTRUCTIONS:\n"
            "1. If the error says 'Field required' (e.g., missing 'atom_id'), you MUST provide it. Every evaluation MUST have a valid 'atom_id' from your <BLIND_ATOMS_TO_EVALUATE> list.\n"
            "2. If you evaluated a concept that was NOT explicitly listed in your instructions, REMOVE that evaluation block entirely. Do not hallucinate items.\n"
            "3. Do not include markdown blocks, conversational text, or any explanations outside the JSON."
        )

        if strictness_level is not None and strictness_level >= 100:
            base += (
                "\n\n[STRICTNESS OVERRIDE ACTIVE: level >= 100]\n"
                "The following fields are BANNED from your output: "
                "'contextual_override', 'override_reason'. "
                "You MUST NOT include these fields."
            )

        return base
