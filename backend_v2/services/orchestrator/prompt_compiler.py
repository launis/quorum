"""Prompt Compiler for generating dynamic Pydantic schemas and LLM prompts.

Transforms abstract workflow state and domain models into executable
LLM payloads with system context, strictness calibration, and format enforcement.

Acts as a high-level orchestrator delegating schema generation to SchemaFactory
and localization/instruction compilation to LocalizationCompiler (SRP Rule 88).
"""

from __future__ import annotations

import datetime
import json
import logging
from collections.abc import Mapping
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.core.registry import EvidenceType, StrippedBaseMatrixXAI
from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.exceptions import AppException, ErrorCodes, MissingInputMappingError
from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.models.domain.step import ExpectedInput
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.prompt import LLMContextDataDTO, PromptMappingDTO
from backend_v2.services.orchestrator.localization_compiler import LocalizationCompiler
from backend_v2.services.orchestrator.schema_factory import SchemaFactory
from backend_v2.utils.math_utils import resolve_dot_notation

# Backward-compatible re-exports for consumers importing from prompt_compiler
__all__ = [
    "EvidenceType",
    "PromptCompiler",
    "StrippedBaseMatrixXAI",
]

logger = logging.getLogger(__name__)


class _InputMetaDTO(BaseModel):
    """Strongly typed immutable DTO for expected input metadata in prompt compilation.

    Attributes:
        label: Localized label string.
        desc: Localized description string.
        ai_desc: Cognitive instruction for LLM.
        is_chat_history: Whether the input represents multi-turn dialogue.
        input_modes: Allowed input modes for this input.
        is_endorsed_deliverable: Whether the input represents an endorsed candidate deliverable.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    label: Annotated[str, Field(description="Localized label string")]
    desc: Annotated[str, Field(description="Localized description string")]
    ai_desc: Annotated[str | None, Field(default=None, description="Cognitive instruction for LLM")] = None
    is_chat_history: Annotated[bool, Field(description="Whether the input represents multi-turn dialogue")]
    input_modes: Annotated[list[str], Field(default_factory=list, description="Allowed input modes for this input")] = (
        Field(default_factory=list)
    )
    is_endorsed_deliverable: Annotated[
        bool, Field(default=False, description="Whether the input represents an endorsed candidate deliverable")
    ] = False

    @property
    def is_assignment(self) -> bool:
        """Whether this input metadata includes the assignment modality.

        Returns:
            bool: True if 'assignment' is in input_modes.
        """
        return "assignment" in self.input_modes


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
        expected_sdui_type: str = "grid",
        dag_results: dict[str, Any] | None = None,
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
            expected_sdui_type: Expected Server-Driven UI component type layout.
            dag_results: Dictionary of previous topological execution results.

        Returns:
            A dynamically generated Pydantic model class.
        """
        return self._schema_factory.build_dynamic_schema(
            schema_name,
            criteria,
            has_shuffled_atoms,
            target_locale,
            strictness_level=strictness_level,
            source_document_ids=source_document_ids,
            allowed_atom_ids=allowed_atom_ids,
            allowed_dynamic_keys=allowed_dynamic_keys,
            max_evaluations=max_evaluations,
            expected_sdui_type=expected_sdui_type,
            dag_results=dag_results,
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
        input_mappings: PromptMappingDTO | dict[str, str],
        state_data: ExecutionInputsDTO | LLMContextDataDTO | dict[str, Any],
        target_locale: str,
        expected_inputs: list[Any] | None = None,
        alias_engine: Any = None,
    ) -> str:
        """Build XML semantic blocks from raw input mappings for LLM context.

        Args:
            input_mappings: DTO or dict mapping logical names to value paths/keys.
            state_data: The current workflow execution state containing values.
            target_locale: The requested output locale string.
            expected_inputs: Optional list of ExpectedInput definitions to extract ai_description.
            alias_engine: Optional alias engine for source document IDs.

        Returns:
            A single string containing XML-wrapped elements.

        Raises:
            AppException: If unmapped input reference is encountered (ErrorCodes.CONFIGURATION_ERROR).
        """
        xml_blocks = []

        # Phase 1, Step 1.1: Refactor raw dictionary lookups into strongly typed _InputMetaDTO
        input_meta_map: dict[str, _InputMetaDTO] = {}
        if expected_inputs:
            for ei in expected_inputs:
                if not isinstance(ei, ExpectedInput):
                    continue

                key = ei.input_key
                if not key:
                    continue

                # Fail-Fast Mandatory I18n extraction
                label_str = self.resolve_i18n(ei.label, target_locale)
                desc_str = self.resolve_i18n(ei.description, target_locale)

                input_meta_map[f"$inputs.{key}"] = _InputMetaDTO(
                    label=label_str,
                    desc=desc_str,
                    ai_desc=ei.ai_description,
                    is_chat_history=ei.is_chat_history,
                    input_modes=ei.input_modes,
                    is_endorsed_deliverable=ei.is_endorsed_deliverable,
                )

        mappings = input_mappings.mappings if isinstance(input_mappings, PromptMappingDTO) else input_mappings

        for logical_name, source_path in mappings.items():
            value = self._extract_value_from_state(source_path, state_data)
            if value:
                source_id_to_use = logical_name
                if alias_engine:
                    alias = alias_engine.register(logical_name, prefix="doc")
                    alias_engine.source_document_aliases.append(alias)
                    source_id_to_use = alias

                base_path = ".".join(source_path.split(".")[:2]) if source_path.startswith("$") else source_path

                desc_text = ""
                encapsulated_val = TemplateProcessor.encapsulate_payload(value)

                if source_path.startswith("$inputs"):
                    if base_path not in input_meta_map:
                        msg = (
                            f"Unmapped input reference '{source_path}' in step input mappings "
                            "(missing expected_input definition)."
                        )
                        logger.error("[PromptCompiler] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                        raise AppException(
                            message=msg,
                            status_code=400,
                            details={
                                "error_code": ErrorCodes.CONFIGURATION_ERROR.value,
                                "source_path": source_path,
                                "base_path": base_path,
                            },
                        )
                    meta = input_meta_map[base_path]

                    desc_text += "  <document_metadata>\n"
                    desc_text += f"    <document_id>{source_id_to_use}</document_id>\n"
                    if meta.label:
                        desc_text += f"    <document_name>{meta.label}</document_name>\n"
                    if meta.ai_desc:
                        desc_text += f"    <ai_context_mandate>{meta.ai_desc}</ai_context_mandate>\n"
                    if meta.is_endorsed_deliverable:
                        desc_text += "    <document_provenance>ENDORSED_FINAL_DELIVERABLE</document_provenance>\n"
                    desc_text += "  </document_metadata>\n"

                    if meta.is_assignment:
                        wrapped_val = f"<assignment_context>\n{encapsulated_val}\n</assignment_context>"
                    elif meta.is_chat_history:
                        wrapped_val = encapsulated_val
                    else:
                        wrapped_val = f"<user_payload>\n{encapsulated_val}\n</user_payload>"
                elif source_path.startswith("$steps"):
                    wrapped_val = f"<ai_draft_context>\n{encapsulated_val}\n</ai_draft_context>"
                else:
                    wrapped_val = encapsulated_val

                xml_blocks.append(
                    f'<matrix_input source_id="{source_id_to_use}">\n{desc_text}{wrapped_val}\n</matrix_input>'
                )

        compiled = "\n\n".join(xml_blocks)

        return compiled

    def _extract_value_from_state(
        self, path: str, state_data: ExecutionInputsDTO | LLMContextDataDTO | dict[str, Any] | Any
    ) -> str:
        """Extract a value from workflow state using a path like '$inputs.history_text'.

        Args:
            path: The dot-notation path string (e.g., '$inputs.document').
            state_data: The current workflow execution state dictionary or DTO.

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
        clean_path = path[1:] if path.startswith("$") else path

        try:
            if isinstance(state_data, LLMContextDataDTO):
                if clean_path.startswith("inputs."):
                    sub_key = clean_path.split(".", 1)[1]
                    if state_data.inputs and sub_key in state_data.inputs:
                        current = state_data.inputs[sub_key]
                    elif state_data.raw_inputs and sub_key in state_data.raw_inputs:
                        current = state_data.raw_inputs[sub_key]
                    else:
                        raise MissingInputMappingError(
                            path=clean_path,
                            state_type=type(state_data).__name__,
                            reason=f"Key '{sub_key}' missing from LLMContextDataDTO",
                        )
                elif state_data.inputs and clean_path in state_data.inputs:
                    current = state_data.inputs[clean_path]
                elif state_data.raw_inputs and clean_path in state_data.raw_inputs:
                    current = state_data.raw_inputs[clean_path]
                else:
                    current = resolve_dot_notation(state_data, clean_path)
            elif isinstance(state_data, ExecutionInputsDTO) and clean_path.startswith("inputs."):
                sub_key = clean_path.split(".", 1)[1]
                if sub_key in state_data.raw_inputs:
                    current = state_data.raw_inputs[sub_key]
                elif sub_key in state_data.dynamic_inputs:
                    current = state_data.dynamic_inputs[sub_key]
                else:
                    raise MissingInputMappingError(
                        path=clean_path,
                        state_type=type(state_data).__name__,
                        reason=f"Key '{sub_key}' missing from ExecutionInputsDTO",
                    )
            else:
                current = resolve_dot_notation(state_data, clean_path)
        except (MissingInputMappingError, KeyError, IndexError, AttributeError) as e:
            msg = f"Path resolution failed: '{path}'. Component missing from state context: {e}"
            logger.error("[PromptCompiler] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
            ) from e

        if isinstance(current, str):
            # Already a string, return directly
            return current

        if isinstance(current, BaseModel):
            return str(current.model_dump_json(indent=2))

        if isinstance(current, (int, float, bool)):
            return str(current)

        if not isinstance(current, list) and current is not None and isinstance(current, Mapping):
            # Flatten nested JSON into LLM-friendly Markdown (Attention Dilution patch)
            formatted = []
            for k, v in current.items():
                clean_k = str(k).upper()
                formatted.append(f"<{clean_k}>")
                if isinstance(v, Mapping):
                    # Attempt to access 'outputs' key directly if available
                    target_dict = v["outputs"] if ("outputs" in v and isinstance(v["outputs"], Mapping)) else v
                    for sub_k, sub_v in target_dict.items():
                        # Prevent Context Snowballing: never inject raw Matrix arrays into subsequent LLM contexts.
                        if sub_k == "results" and isinstance(sub_v, list):
                            continue

                        if isinstance(sub_v, Mapping):
                            formatted.append(f"<{str(sub_k).upper()}>")
                            for micro_k, micro_v in sub_v.items():
                                # Clean cognitive prefixes for readability
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
                                f"  <{clean_sub_k}>{TemplateProcessor.encapsulate_payload(sub_v)}</{clean_sub_k}>"
                            )
                else:
                    formatted.append(f"  {TemplateProcessor.encapsulate_payload(v)}")
                formatted.append(f"</{clean_k}>")
            return "\n".join(formatted)

        return json.dumps(current, indent=2, ensure_ascii=False)

    def calibrate_strictness(self, level: int | float | None) -> str:
        """Convert a numeric strictness level (0-100) into a semantic directive.

        Args:
            level: The strictness integer, 0 (Lenient) to 100 (Unforgiving).

        Returns:
            A semantic prompt string commanding the LLM of the desired strictness behavior.

        Raises:
            AppException: If the strictness level cannot be parsed (ErrorCodes.VALIDATION_FAILED).
        """
        if level is None:
            return ""

        try:
            val = int(level)
        except (ValueError, TypeError) as e:
            logger.error(
                "[PromptCompiler] %s: Failed to parse strictness level %s",
                ErrorCodes.VALIDATION_FAILED.name,
                level,
                exc_info=True,
            )
            raise AppException(
                message=f"Invalid strictness level: {level}",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

        # Clamp between 0 and 100
        val = max(0, min(100, val))

        return f"SCORING_STRICTNESS: {val}/100"

    def generate_mcp_instruction(self, allowed_tools: list[str]) -> str:
        """Generate dynamic instructions for active MCP tools.

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
