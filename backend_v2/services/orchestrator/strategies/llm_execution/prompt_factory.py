import logging
from dataclasses import dataclass
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import EvaluationMandate
from backend_v2.models.v2_core import PromptBlock
from backend_v2.utils.hashing import generate_atom_hash

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PromptPayload:
    base_system_prompt: str
    user_payload: str
    atom_to_block_ids: dict[str, set[str]]


class PromptFactory:
    """Orchestrates prompt compilation and builds the final PromptPayload."""

    @classmethod
    def build(
        cls,
        compiler: Any,
        criteria_blocks: list[PromptBlock],
        target_locale: str,
        effective_mcp_tools: list[str] | None,
        input_mappings: dict[str, Any],
        llm_context_data: dict[str, Any],
        expected_inputs: list[Any] | None,
        has_shuffled_atoms: bool = False,
        execution_id: str | None = None,
    ) -> PromptPayload:
        static_instructions = compiler.compile_static_instructions(criteria_blocks, target_locale)

        # 1. Try to find if the client explicitly passed the original document creation date (e.g., file.lastModified)
        execution_time = None
        if isinstance(llm_context_data, dict):
            raw_inputs = llm_context_data.get("raw_inputs", {})
            if isinstance(raw_inputs, dict):
                dynamic_inputs = raw_inputs.get("dynamic_inputs", {})
                if isinstance(dynamic_inputs, dict):
                    # Check for explicit keys sent by the client (e.g., in UI uploads)
                    execution_time = (
                        dynamic_inputs.get("document_date")
                        or dynamic_inputs.get("input_file_date")
                        or dynamic_inputs.get("last_modified")
                    )
        if execution_time:
            logger.info(
                "[PromptFactory] Using client-supplied document date metadata for prompt timestamp: %s",
                execution_time,
            )

        # 2. Try to find the exact modification time of the physical input file on disk (Genuine File Timestamp)
        if not execution_time and execution_id:
            import datetime
            import os

            for filename in ["input_chat_log.md", "input_product_text.md", "input_reflection_text.md"]:
                file_path = f"data/files/executions/{execution_id}/inputs/{filename}"
                if os.path.exists(file_path):
                    try:
                        mtime = os.path.getmtime(file_path)
                        execution_time = datetime.datetime.fromtimestamp(mtime, datetime.UTC)
                        logger.info(
                            "[PromptFactory] Determined prompt date from file '%s' modification date: %s",
                            filename,
                            execution_time.isoformat(),
                        )
                        break
                    except Exception:
                        pass

        # 3. Fall back to execution context/database timestamps if files are not present on disk (e.g., in unit tests)
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
                logger.info(
                    "[PromptFactory] Using fallback context/database execution timestamp for prompt timestamp: %s",
                    execution_time,
                )

        dynamic_instructions = compiler.compile_dynamic_instructions(
            criteria_blocks, target_locale, execution_time=execution_time
        )

        blind_instruction = None
        if has_shuffled_atoms:
            blind_instruction = compiler.compile_blind_system_instruction(target_locale)

        mcp_instruction = compiler.generate_mcp_instruction(effective_mcp_tools)

        base_system_prompt = "Complete the evaluation according to the provided schema."
        if static_instructions:
            base_system_prompt += f"\n\n{static_instructions}"
        if blind_instruction:
            base_system_prompt += f"\n\n{blind_instruction}"
        if mcp_instruction:
            base_system_prompt += f"\n\n{mcp_instruction}"

        xml_ctx = compiler.build_xml_context(
            input_mappings=input_mappings,
            state_data=llm_context_data,
            target_locale=target_locale,
            expected_inputs=expected_inputs,
        )

        user_payload = xml_ctx
        if dynamic_instructions:
            user_payload += f"\n\n--- RUNTIME AWARENESS ---\n{dynamic_instructions}"

        atom_to_block_ids: dict[str, set[str]] = {}
        for block_model in criteria_blocks:
            if block_model.category_id == "matrix" and block_model.scales:
                b_id = block_model.id
                if not b_id:
                    continue
                for scale in block_model.scales:
                    for claim in scale.claims:
                        mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
                        tda_assertions = claim.tda_assertions
                        if tda_assertions and len(tda_assertions) > 0:
                            for tda in tda_assertions:
                                if tda.tda_id and str(tda.tda_id).startswith("tda_"):
                                    aid = str(tda.tda_id)
                                else:
                                    aid = generate_atom_hash(tda.ai_rule_description, mandate)
                                if aid not in atom_to_block_ids:
                                    atom_to_block_ids[aid] = set()
                                atom_to_block_ids[aid].add(b_id)
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
