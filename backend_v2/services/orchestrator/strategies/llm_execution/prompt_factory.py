from __future__ import annotations

"""Prompt Factory Service for Cognitive Quorum.

This module orchestrates prompt compilation and builds the final PromptPayload.
It supports modern Python 3.14 syntax, PEP 695 generic parameters, strict
pathlib integration, and adheres strictly to the architectural safety guidelines.
"""

import datetime
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import PromptBlock

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PromptPayload:
    """Structured projection of compiled prompting states for LLM consumption.

    Attributes:
        base_system_prompt: Static system instructions with roles, schemas and protocols.
        user_payload: Dynamic runtime parameters and source data XML contexts.
        atom_to_block_ids: Association mapping of evidence hashes to criteria identifiers.
    """

    base_system_prompt: str
    user_payload: str
    atom_to_block_ids: dict[str, set[str]]


class PromptFactory:
    """Orchestrates prompt compilation and builds the final PromptPayload.

    Enforces physical disk timestamp alignment and formats mechanical UI anchors safely.
    """

    @classmethod
    def build(
        cls,
        compiler: Any,
        role_block: PromptBlock | None,
        protocol_block: PromptBlock | None,
        execution_persona_block: PromptBlock | None,
        criteria_blocks: list[PromptBlock],
        target_locale: str,
        effective_mcp_tools: list[str] | None,
        input_mappings: dict[str, Any],
        llm_context_data: dict[str, Any],
        expected_inputs: list[Any] | None,
        has_shuffled_atoms: bool = False,
        execution_id: str | None = None,
    ) -> PromptPayload:
        """Compiles criteria blocks and context variables into optimized static/dynamic prompts.

        Args:
            compiler: The prompt compiler component instance.
            role_block: The block defining execution persona and guidelines.
            protocol_block: Standard parsing extraction guideline.
            criteria_blocks: Criteria blocks with evaluation scales.
            target_locale: Target localization code (e.g. 'fi' or 'en').
            effective_mcp_tools: Optional active MCP tools names list.
            input_mappings: Key-value definitions for variable substitutions.
            llm_context_data: Comprehensive structured context map.
            expected_inputs: Elements expected to present in context evaluation.
            has_shuffled_atoms: Whether evaluation assets were randomized to mitigate LLM bias.
            execution_id: Parent execution tracking ID.

        Returns:
            An immutable PromptPayload containing structured prompt components.

        Raises:
            AppException: If criteria validation checks fail or are structurally deficient.
        """
        static_instructions = compiler.compile_static_instructions(criteria_blocks, target_locale)

        # 1. Try to find if the client explicitly passed the original document creation date
        execution_time: Any | None = None
        if isinstance(llm_context_data, dict):
            raw_inputs = llm_context_data.get("raw_inputs", {})
            if isinstance(raw_inputs, dict):
                dynamic_inputs = raw_inputs.get("dynamic_inputs", {})
                if isinstance(dynamic_inputs, dict):
                    execution_time = (
                        dynamic_inputs.get("document_date")
                        or dynamic_inputs.get("input_file_date")
                        or dynamic_inputs.get("last_modified")
                    )
        if execution_time:
            logger.info("[PromptFactory] Client-supplied document date found.")

        # 2. Try to find the exact modification time of the physical input file on disk
        if not execution_time and execution_id:
            for filename in ["input_chat_log.md", "input_product_text.md", "input_reflection_text.md"]:
                file_path = Path("data") / "files" / "executions" / execution_id / "inputs" / filename
                if file_path.exists():
                    try:
                        mtime = file_path.stat().st_mtime
                        execution_time = datetime.datetime.fromtimestamp(mtime, datetime.UTC)
                        logger.info("[PromptFactory] Determined prompt date from physical input metadata.")
                        break
                    except OSError as exc:
                        logger.warning(
                            "[PromptFactory] Failed to read physical file mtime: %s",
                            str(exc),
                        )

        # 3. Fall back to execution context/database timestamps if files are not present on disk
        if not execution_time and isinstance(llm_context_data, dict):
            metadata = llm_context_data.get("metadata", {})
            if isinstance(metadata, dict):
                execution_time = metadata.get("created_at") or metadata.get("timestamp")

            if not execution_time:
                raw_inputs = llm_context_data.get("raw_inputs", {})
                if isinstance(raw_inputs, dict):
                    execution_time = raw_inputs.get("timestamp") or raw_inputs.get("metadata", {}).get("timestamp")

            if not execution_time:
                execution_time = llm_context_data.get("created_at") or llm_context_data.get("timestamp")

            if execution_time:
                logger.info("[PromptFactory] Using fallback database timestamp.")

        dynamic_instructions = compiler.compile_dynamic_instructions(
            criteria_blocks, target_locale, execution_time=execution_time
        )

        blind_instruction = None
        if has_shuffled_atoms:
            blind_instruction = compiler.compile_blind_system_instruction(target_locale)

        mcp_instruction = compiler.generate_mcp_instruction(effective_mcp_tools)

        def find_value_by_key(obj: Any, key: str) -> Any:
            """Safely searches deep nested structures for a specific attribute/key.

            Args:
                obj: Dictionary, list or custom class instance to inspect.
                key: Key or property name being extracted.

            Returns:
                Value if found, otherwise None.
            """
            if isinstance(obj, dict):
                if key in obj:
                    return obj[key]
                for v in obj.values():
                    res = find_value_by_key(v, key)
                    if res is not None:
                        return res
            elif isinstance(obj, list):
                for item in obj:
                    res = find_value_by_key(item, key)
                    if res is not None:
                        return res
            elif hasattr(obj, "__dict__"):
                if hasattr(obj, key):
                    return getattr(obj, key)
                for v in obj.__dict__.values():
                    res = find_value_by_key(v, key)
                    if res is not None:
                        return res
            return None

        is_grounded_step = False
        for b in criteria_blocks:
            if getattr(b, "slug", None) in ("matrix_causal_analyst", "block_taskperformativity"):
                is_grounded_step = True
                break

        anchors_xml = ""
        if is_grounded_step:
            word_count = find_value_by_key(llm_context_data, "word_count")
            if word_count is None:
                word_count = 0
            say_do_gap = find_value_by_key(llm_context_data, "say_do_gap")
            if say_do_gap is None:
                say_do_gap = 0.0
            automation_bias = find_value_by_key(llm_context_data, "automation_bias")
            if automation_bias is None:
                automation_bias = 0.0

            patterns = find_value_by_key(llm_context_data, "performative_patterns") or find_value_by_key(
                llm_context_data, "performative_phrases"
            )
            phrase_list = []
            if isinstance(patterns, list):
                for pat in patterns:
                    if isinstance(pat, dict):
                        phrase = pat.get("detected_phrase") or pat.get("phrase")
                        if phrase:
                            phrase_list.append(str(phrase))
                    elif hasattr(pat, "detected_phrase"):
                        phrase = pat.detected_phrase
                        if phrase:
                            phrase_list.append(str(phrase))
                    elif isinstance(pat, str):
                        phrase_list.append(pat)

            phrase_count = len(phrase_list)
            items_xml = ""
            for p in phrase_list:
                items_xml += f"      <phrase>{p}</phrase>\n"

            anchors_xml = "<mechanical_anchors>\n"
            anchors_xml += "  <text_metrics>\n"
            anchors_xml += f"    <word_count>{word_count}</word_count>\n"
            anchors_xml += f"    <say_do_gap>{say_do_gap}</say_do_gap>\n"
            anchors_xml += f"    <automation_bias>{automation_bias}</automation_bias>\n"
            anchors_xml += "  </text_metrics>\n"
            anchors_xml += "  <detected_performative_phrases>\n"
            anchors_xml += f"    <phrase_count>{phrase_count}</phrase_count>\n"
            anchors_xml += f"    <items>\n{items_xml}    </items>\n"
            anchors_xml += "  </detected_performative_phrases>\n"
            anchors_xml += "</mechanical_anchors>"

        base_system_prompt = "You are a highly accurate, structured evaluation assistant."
        if execution_persona_block and execution_persona_block.ai_description:
            base_system_prompt = execution_persona_block.ai_description

        if role_block and role_block.ai_description:
            base_system_prompt += f"\n\n<ROLE_DIRECTIVE>\n{role_block.ai_description}\n</ROLE_DIRECTIVE>"
            if is_grounded_step:
                base_system_prompt += f"\n\n{anchors_xml}"
        else:
            if is_grounded_step:
                base_system_prompt += f"\n\n{anchors_xml}"

        if protocol_block and protocol_block.ai_description:
            base_system_prompt += f"\n\n<EXTRACTION_PROTOCOL>\n{protocol_block.ai_description}\n</EXTRACTION_PROTOCOL>"
        if static_instructions:
            base_system_prompt += f"\n\n<CRITERIA_GUIDELINES>\n{static_instructions}\n</CRITERIA_GUIDELINES>"
        if blind_instruction:
            base_system_prompt += f"\n\n{blind_instruction}"
        if mcp_instruction:
            base_system_prompt += f"\n\n{mcp_instruction}"

        exec_params = f"<execution_parameters>\n<target_locale>{target_locale}</target_locale>\n"
        if execution_time:
            exec_params += f"<document_date>{execution_time}</document_date>\n"
        exec_params += "</execution_parameters>\n"

        xml_ctx = compiler.build_xml_context(
            input_mappings=input_mappings,
            state_data=llm_context_data,
            target_locale=target_locale,
            expected_inputs=expected_inputs,
        )

        user_payload = f"{exec_params}\n<source_data>\n{xml_ctx}\n</source_data>"
        if dynamic_instructions:
            user_payload += f"\n\n<RUNTIME_AWARENESS>\n{dynamic_instructions}\n</RUNTIME_AWARENESS>"

        atom_to_block_ids: dict[str, set[str]] = {}
        for block_model in criteria_blocks:
            if block_model.category_id == "matrix" and block_model.scales:
                b_id = block_model.id
                if not b_id:
                    continue
                for scale in block_model.scales:
                    for claim in scale.claims:
                        tda_assertions = claim.tda_assertions
                        if tda_assertions and len(tda_assertions) > 0:
                            for tda in tda_assertions:
                                aid = str(tda.tda_id)
                                if aid not in atom_to_block_ids:
                                    atom_to_block_ids[aid] = set()
                                mock_block_set = atom_to_block_ids[aid]
                                mock_block_set.add(b_id)
                        else:
                            msg = f"PromptBlock '{b_id}' claim is missing mandatory 'tda_assertions' during runtime."
                            logger.error("[%s] %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                            raise AppException(
                                message=msg,
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )

        return PromptPayload(
            base_system_prompt=base_system_prompt,
            user_payload=user_payload,
            atom_to_block_ids=atom_to_block_ids,
        )
