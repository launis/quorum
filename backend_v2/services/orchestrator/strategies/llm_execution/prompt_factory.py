import hashlib
import logging
from dataclasses import dataclass
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import EvaluationMandate

logger = logging.getLogger(__name__)


@dataclass
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
        criteria_blocks: list[dict[str, Any]],
        target_locale: str,
        effective_mcp_tools: list[str] | None,
        input_mappings: dict[str, Any],
        llm_context_data: dict[str, Any],
        expected_inputs: list[Any] | None,
    ) -> PromptPayload:
        static_instructions = compiler.compile_static_instructions(criteria_blocks, target_locale)
        dynamic_instructions = compiler.compile_dynamic_instructions(criteria_blocks, target_locale)
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
        for block in criteria_blocks:
            if block.get("category_id") == "matrix" and block.get("scales"):
                b_id = block.get("id")
                if not b_id:
                    continue
                for scale in block.get("scales", []):
                    scale_atoms: list[str] = []
                    for claim in scale.get("claims", []):
                        mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
                        micro_atoms = claim.get("micro_atoms")
                        if micro_atoms and len(micro_atoms) > 0:
                            scale_atoms.extend([f"{ma.strip()}{mandate}" for ma in micro_atoms])
                        else:
                            msg = f"PromptBlock '{b_id}' claim is missing mandatory 'micro_atoms' during runtime."
                            logger.error("[%s] %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                            raise AppException(
                                message=msg,
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )

                        for text in scale_atoms:
                            aid = hashlib.md5(text.encode("utf-8")).hexdigest()
                            if aid not in atom_to_block_ids:
                                atom_to_block_ids[aid] = set()
                            atom_to_block_ids[aid].add(b_id)

        return PromptPayload(
            base_system_prompt=base_system_prompt,
            user_payload=user_payload,
            atom_to_block_ids=atom_to_block_ids,
        )
