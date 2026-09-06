"""Prompt Factory Service for Cognitive Quorum.

This module orchestrates prompt compilation and builds the final PromptPayload.
It supports modern Python 3.14 syntax, PEP 695 generic parameters, strict
pathlib integration, and adheres strictly to the architectural safety guidelines.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.mechanical_anchors import MechanicalAnchorsPayload
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    PromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.prompts.common import (
    GLOBAL_MANDATES_XML,
    STATIC_LINGUISTIC_PROTOCOL,
    build_linguistic_parameters,
)
from backend_v2.services.orchestrator.strategies.llm_execution.execution_time_resolver import (
    ExecutionTimeResolver,
)

logger = logging.getLogger(__name__)

__all__ = ["PromptFactory", "PromptPayload"]


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
        alias_engine: Any = None,
        global_context_vars: dict[str, Any] | None = None,
    ) -> PromptPayload:
        """Compiles criteria blocks and context variables into optimized static/dynamic prompts.

        Args:
            compiler: The prompt compiler component instance.
            role_block: The block defining execution persona and guidelines.
            protocol_block: Standard parsing extraction guideline.
            execution_persona_block: Optional execution persona block for tone guidance.
            criteria_blocks: Criteria blocks with evaluation scales.
            target_locale: Target localization code (e.g. 'fi' or 'en').
            effective_mcp_tools: Optional active MCP tools names list.
            input_mappings: Key-value definitions for variable substitutions.
            llm_context_data: Comprehensive structured context map.
            expected_inputs: Elements expected to present in context evaluation.
            has_shuffled_atoms: Whether evaluation assets were randomized to mitigate LLM bias.
            execution_id: Parent execution tracking ID.
            alias_engine: Optional alias engine for source document IDs.
            global_context_vars: Optional global context variables (e.g. external_evidence from pre-hooks).

        Returns:
            An immutable PromptPayload containing structured prompt components.

        Raises:
            AppException: If criteria validation checks fail or are structurally deficient.
        """
        static_instructions = compiler.compile_static_instructions(criteria_blocks, target_locale)

        # Deterministically resolve execution/document timestamp via ExecutionTimeResolver
        execution_time = ExecutionTimeResolver.resolve(
            llm_context_data=llm_context_data,
            execution_id=execution_id,
        )

        dynamic_instructions = compiler.compile_dynamic_instructions(
            criteria_blocks, target_locale, execution_time=execution_time
        )

        mcp_instruction = compiler.generate_mcp_instruction(effective_mcp_tools)

        # Polymorphic check for grounded matrix blocks requiring mechanical anchors
        is_grounded_step = any(isinstance(b, MatrixPromptBlock) for b in criteria_blocks)

        anchors_xml = ""
        if is_grounded_step:
            anchors_payload = MechanicalAnchorsPayload.from_context(llm_context_data)
            anchors_xml = anchors_payload.to_xml()

        # Layer 1: Global Mandates static caching prefix
        base_system_prompt = f"{GLOBAL_MANDATES_XML.strip()}\n\n{STATIC_LINGUISTIC_PROTOCOL.strip()}"

        # Persona instruction or fallback base instruction (Phase 8 pattern matching)
        persona = "You are a highly accurate, structured evaluation assistant."
        if execution_persona_block:
            match execution_persona_block:
                case PersonaPromptBlock(role_enforcement=role_text) if role_text:
                    persona = role_text.strip()
                case SystemRulePromptBlock(instruction_text=text) if text:
                    persona = text.strip()
        base_system_prompt += f"\n\n{persona}"

        # Layer 2: Role Directive & Protocols (Phase 8 pattern matching)
        if role_block:
            role_text = ""
            match role_block:
                case PersonaPromptBlock(role_enforcement=text) if text:
                    role_text = text.strip()
                case SystemRulePromptBlock(instruction_text=text) if text:
                    role_text = text.strip()
            if role_text:
                base_system_prompt += f"\n\n<ROLE_DIRECTIVE>\n{role_text}\n</ROLE_DIRECTIVE>"

        if protocol_block:
            proto_text = ""
            match protocol_block:
                case ProtocolPromptBlock(protocol_instructions=text) if text:
                    proto_text = text.strip()
                case SystemRulePromptBlock(instruction_text=text) if text:
                    proto_text = text.strip()
            if proto_text:
                base_system_prompt += f"\n\n<EXTRACTION_PROTOCOL>\n{proto_text}\n</EXTRACTION_PROTOCOL>"

        # Layer 3: Criteria Guidelines & MCP Tools
        if static_instructions:
            base_system_prompt += f"\n\n<CRITERIA_GUIDELINES>\n{static_instructions}\n</CRITERIA_GUIDELINES>"

        if mcp_instruction:
            base_system_prompt += f"\n\n{mcp_instruction}"

        # Dynamic user payload (Layer 4 / dynamic inputs isolated at tail)
        linguistic_params = build_linguistic_parameters(target_locale=target_locale)

        exec_params = f"<execution_context>\n<target_locale>{target_locale}</target_locale>\n"
        exec_params += f"{linguistic_params}\n"
        if execution_time:
            exec_params += f"<document_date>{execution_time}</document_date>\n"
        if anchors_xml:
            exec_params += f"{anchors_xml}\n"
        exec_params += "</execution_context>\n"

        xml_ctx = compiler.build_xml_context(
            input_mappings=input_mappings,
            state_data=llm_context_data,
            target_locale=target_locale,
            expected_inputs=expected_inputs,
            alias_engine=alias_engine,
        )

        source_data_content = xml_ctx
        if global_context_vars and "external_evidence" in global_context_vars:
            evidence_val = global_context_vars["external_evidence"]
            if evidence_val and isinstance(evidence_val, str):
                from backend_v2.settings import get_settings

                evidence_budget = get_settings().source_evidence_max_chars
                truncated_evidence = evidence_val[:evidence_budget].strip()
                source_data_content = f"{source_data_content}\n\n{truncated_evidence}".strip()

        user_payload = f"{exec_params}\n<source_data>\n{source_data_content}\n</source_data>"
        if dynamic_instructions:
            user_payload += f"\n\n<RUNTIME_AWARENESS>\n{dynamic_instructions}\n</RUNTIME_AWARENESS>"

        atom_to_block_ids: dict[str, set[str]] = {}
        for block_model in criteria_blocks:
            if isinstance(block_model, MatrixPromptBlock) and block_model.scales:
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
