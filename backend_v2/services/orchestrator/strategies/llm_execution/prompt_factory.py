"""Prompt Factory Service for Cognitive Quorum.

This module orchestrates prompt compilation and builds the final PromptPayload.
It supports modern Python 3.14 syntax, PEP 695 generic parameters, strict
pathlib integration, and adheres strictly to the architectural safety guidelines.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.mechanical_anchors import MechanicalAnchorsPayload
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    PromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.dtos.prompt import LLMContextDataDTO, PromptMappingDTO
from backend_v2.models.prompts.common import (
    GLOBAL_MANDATES_XML,
    STATIC_LINGUISTIC_PROTOCOL,
    build_linguistic_parameters,
)
from backend_v2.services.orchestrator.strategies.llm_execution.execution_time_resolver import (
    ExecutionTimeResolver,
)
from backend_v2.settings import get_settings

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

    @staticmethod
    def _extract_block_instruction(block: PromptBlock | None) -> str:
        """Extract stripped instruction text from a polymorphic Persona, Protocol, or SystemRule block.

        Args:
            block: Optional PromptBlock domain model.

        Returns:
            Stripped instruction string when present, or an empty string.
        """
        if block is None:
            return ""
        match block:
            case PersonaPromptBlock(role_enforcement=text) if text:
                return text.strip()
            case ProtocolPromptBlock(protocol_instructions=text) if text:
                return text.strip()
            case SystemRulePromptBlock(instruction_text=text) if text:
                return text.strip()
            case _:
                return ""

    @staticmethod
    def _build_atom_to_block_ids(criteria_blocks: list[PromptBlock]) -> dict[str, set[str]]:
        """Validate matrix claim TDA assertions and map atom IDs to owning PromptBlock IDs.

        Args:
            criteria_blocks: Criteria PromptBlock models evaluated by the current step.

        Returns:
            Mapping of TDA assertion IDs to sets of owning PromptBlock IDs.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if a matrix claim lacks tda_assertions.
        """
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
                                atom_to_block_ids[aid].add(b_id)
                        else:
                            msg = f"PromptBlock '{b_id}' claim is missing mandatory 'tda_assertions' during runtime."
                            logger.error(
                                "[%s] %s",
                                ErrorCodes.VALIDATION_FAILED.name,
                                msg,
                                exc_info=True,
                            )
                            raise AppException(
                                message=msg,
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )
        return atom_to_block_ids

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
        input_mappings: PromptMappingDTO,
        llm_context_data: LLMContextDataDTO,
        expected_inputs: list[Any] | None,
        has_shuffled_atoms: bool = False,
        execution_id: str | None = None,
        alias_engine: Any = None,
        global_context_vars: GlobalContextVarsDTO | None = None,
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
            input_mappings: DTO or dict definitions for variable substitutions.
            llm_context_data: Comprehensive structured context DTO or dict.
            expected_inputs: Elements expected to present in context evaluation.
            has_shuffled_atoms: Whether evaluation assets were randomized to mitigate LLM bias.
            execution_id: Parent execution tracking ID.
            alias_engine: Optional alias engine for source document IDs.
            global_context_vars: Optional global context variables (e.g. external_evidence from pre-hooks).

        Returns:
            An immutable PromptPayload containing structured prompt components.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if criteria validation checks fail
                or matrix claims lack tda_assertions.
        """
        static_instructions = compiler.compile_static_instructions(criteria_blocks, target_locale)
        execution_time = ExecutionTimeResolver.resolve(
            llm_context_data=llm_context_data,
            execution_id=execution_id,
        )
        dynamic_instructions = compiler.compile_dynamic_instructions(
            criteria_blocks, target_locale, execution_time=execution_time
        )
        mcp_instruction = compiler.generate_mcp_instruction(effective_mcp_tools)

        is_grounded_step = any(isinstance(b, MatrixPromptBlock) for b in criteria_blocks)
        anchors_xml = ""
        if is_grounded_step:
            anchors_payload = MechanicalAnchorsPayload.from_context(llm_context_data)
            anchors_xml = anchors_payload.to_xml()

        # Layer 1: Global Mandates static caching prefix and execution persona
        base_system_prompt = f"{GLOBAL_MANDATES_XML.strip()}\n\n{STATIC_LINGUISTIC_PROTOCOL.strip()}"
        persona = cls._extract_block_instruction(execution_persona_block)
        if not persona:
            persona = "You are a highly accurate, structured evaluation assistant."
        base_system_prompt += f"\n\n{persona}"

        # Layer 2: Role Directive & Extraction Protocols
        role_text = cls._extract_block_instruction(role_block)
        if role_text:
            base_system_prompt += f"\n\n<ROLE_DIRECTIVE>\n{role_text}\n</ROLE_DIRECTIVE>"

        proto_text = cls._extract_block_instruction(protocol_block)
        if proto_text:
            base_system_prompt += f"\n\n<EXTRACTION_PROTOCOL>\n{proto_text}\n</EXTRACTION_PROTOCOL>"

        # Layer 3: Criteria Guidelines & MCP Tools
        if static_instructions:
            base_system_prompt += f"\n\n<CRITERIA_GUIDELINES>\n{static_instructions}\n</CRITERIA_GUIDELINES>"
        if mcp_instruction:
            base_system_prompt += f"\n\n{mcp_instruction}"

        # Layer 4: Dynamic user payload and runtime inputs isolated at tail
        linguistic_params = build_linguistic_parameters(target_locale=target_locale)
        exec_params = f"<execution_context>\n<target_locale>{target_locale}</target_locale>\n"
        exec_params += f"{linguistic_params}\n"
        if execution_time:
            exec_params += f"<document_date>{execution_time}</document_date>\n"
        if anchors_xml:
            exec_params += f"{anchors_xml}\n"
        exec_params += "</execution_context>\n"

        source_data_content = compiler.build_xml_context(
            input_mappings=input_mappings,
            state_data=llm_context_data,
            target_locale=target_locale,
            expected_inputs=expected_inputs,
            alias_engine=alias_engine,
        )
        if (
            isinstance(global_context_vars, GlobalContextVarsDTO)
            and isinstance(global_context_vars.external_evidence, str)
            and global_context_vars.external_evidence
        ):
            evidence_budget = get_settings().source_evidence_max_chars
            truncated_evidence = global_context_vars.external_evidence[:evidence_budget].strip()
            source_data_content = f"{source_data_content}\n\n{truncated_evidence}".strip()

        user_payload = TemplateProcessor.render_prompt(
            t"{exec_params:raw}\n<source_data>\n{source_data_content:raw}\n</source_data>"
        )
        if dynamic_instructions:
            user_payload += TemplateProcessor.render_prompt(
                t"\n\n<RUNTIME_AWARENESS>\n{dynamic_instructions:raw}\n</RUNTIME_AWARENESS>"
            )

        return PromptPayload(
            base_system_prompt=base_system_prompt,
            user_payload=user_payload,
            atom_to_block_ids=cls._build_atom_to_block_ids(criteria_blocks),
        )
