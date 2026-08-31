"""Adapter for PromptCompiler to natively support structured static/dynamic prompt segregation."""

import datetime
import re
from typing import Any

from pydantic import BaseModel

from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.v2_core import ChatMessageDTO
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


class PromptCompilerAdapter:
    """Adapter wrapping PromptCompiler to provide structured, cache-efficient prompt segregation."""

    def __init__(self) -> None:
        """Initialize the adapter by instantiating the PromptCompiler."""
        self._compiler = PromptCompiler()

    def resolve_i18n(self, text_obj: Any, target_locale: str) -> str:
        """Resolve an I18n JSON object to a string based on locale fallback rules."""
        return self._compiler.resolve_i18n(text_obj, target_locale)

    def compile_static_instructions(self, blocks: list[PromptBlock], target_locale: str) -> str:
        """Compile static instruction-type V2 PromptBlocks for the Cached System Prompt."""
        return self._compiler.compile_static_instructions(blocks, target_locale)

    def compile_dynamic_instructions(
        self,
        blocks: list[PromptBlock],
        target_locale: str,
        execution_time: datetime.datetime | str | None = None,
    ) -> str:
        """Compile dynamic instruction-type V2 PromptBlocks for the Uncached User Tail."""
        return self._compiler.compile_dynamic_instructions(blocks, target_locale, execution_time)

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
        """Build a dynamic Pydantic V2 model for LLM Structured Outputs."""
        return self._compiler.build_dynamic_schema(
            schema_name,
            criteria,
            has_shuffled_atoms,
            target_locale,
            strictness_level=strictness_level,
            source_document_ids=source_document_ids,
            allowed_atom_ids=allowed_atom_ids,
            allowed_dynamic_keys=allowed_dynamic_keys,
            allowed_mcp_prefixes=allowed_mcp_prefixes,
            max_evaluations=max_evaluations,
            expected_sdui_type=expected_sdui_type,
            dag_results=dag_results,
        )

    def build_chunk_response_schema(self, schema_name: str, item_schema: type[BaseModel]) -> type[BaseModel]:
        """Build dynamic Pydantic V2 schema for chunked Map-Reduce execution."""
        return self._compiler.build_chunk_response_schema(schema_name, item_schema)

    def build_xml_context(
        self,
        input_mappings: dict[str, str],
        state_data: dict[str, Any],
        target_locale: str,
        expected_inputs: list[Any] | None = None,
        alias_engine: Any = None,
    ) -> str:
        """Build XML semantic blocks from raw input mappings for LLM context."""
        return self._compiler.build_xml_context(
            input_mappings,
            state_data,
            target_locale,
            expected_inputs=expected_inputs,
            alias_engine=alias_engine,
        )

    def calibrate_strictness(self, level: int | float | None) -> str:
        """Convert a numeric strictness level (0-100) into a semantic directive."""
        return self._compiler.calibrate_strictness(level)

    def generate_mcp_instruction(self, allowed_tools: list[str]) -> str:
        """Generate dynamic instructions for active MCP tools."""
        return self._compiler.generate_mcp_instruction(allowed_tools)

    def compile_chunk_payload_instruction(self, chunk_id: str, payload_text: str) -> str:
        """Generates an isolated context block fenced explicitly into `<user_payload>`."""
        return self._compiler.compile_chunk_payload_instruction(chunk_id, payload_text)

    @staticmethod
    def get_schema_healing_prompt(
        error_msg: str, is_logical_error: bool, is_eof: bool, strictness_level: int | None = None
    ) -> str:
        """Generate a Self-Healing prompt for LLM execution recovery."""
        return PromptCompiler.get_schema_healing_prompt(
            error_msg, is_logical_error, is_eof, strictness_level=strictness_level
        )

    def compile_prompt(self, messages: list[ChatMessageDTO] | list[dict[str, Any]]) -> CompiledPrompt:
        """Splits an existing list of messages into static_messages and dynamic_messages.

        Acts as a robust fallback for general inputs by extracting dynamic blocks (execution
        parameters and error blocks) from user messages and placing them in the dynamic tail.

        Args:
            messages: The list of conversation messages (ChatMessageDTOs or raw dicts).

        Returns:
            A CompiledPrompt object with separated static and dynamic messages.
        """
        static_msgs: list[ChatMessageDTO] = []
        dynamic_msgs: list[ChatMessageDTO] = []
        in_dynamic_tail = False

        typed_messages: list[ChatMessageDTO] = [
            m if isinstance(m, ChatMessageDTO) else ChatMessageDTO.model_validate(m) for m in messages
        ]

        for msg in typed_messages:
            role = msg.role
            content_str = msg.content

            if role == "system":
                # System is 100% static
                static_msgs.append(ChatMessageDTO(role="system", content=content_str.strip()))
            elif role == "user":
                if in_dynamic_tail:
                    dynamic_msgs.append(ChatMessageDTO(role="user", content=content_str.strip()))
                else:
                    # Scan for dynamic parameters and previous errors
                    has_exec_params = "<execution_parameters>" in content_str
                    has_prev_error = "<PREVIOUS_SCHEMA_ERROR>" in content_str

                    if not has_exec_params and not has_prev_error:
                        static_msgs.append(ChatMessageDTO(role="user", content=content_str.strip()))
                    else:
                        in_dynamic_tail = True
                        # Isolate dynamic parameters block
                        exec_params_match = re.search(
                            r"(<execution_parameters>.*?</execution_parameters>)", content_str, re.DOTALL
                        )
                        # Isolate previous errors block
                        prev_error_match = re.search(
                            r"(<PREVIOUS_SCHEMA_ERROR>.*?</PREVIOUS_SCHEMA_ERROR>)", content_str, re.DOTALL
                        )

                        dynamic_parts = []
                        static_content = content_str

                        if exec_params_match:
                            exec_block = exec_params_match.group(1)
                            dynamic_parts.append(exec_block)
                            static_content = static_content.replace(exec_block, "")

                        if prev_error_match:
                            error_block = prev_error_match.group(1)
                            dynamic_parts.append(error_block)
                            static_content = static_content.replace(error_block, "")

                        # Clean leftover duplicate newlines
                        static_content = re.sub(r"\n{3,}", "\n\n", static_content).strip()

                        # Keep static user elements in static segment
                        if static_content:
                            static_msgs.append(ChatMessageDTO(role="user", content=static_content))

                        # Keep dynamic parameter blocks in dynamic segment
                        if dynamic_parts:
                            dynamic_content = "\n\n".join(dynamic_parts).strip()
                            dynamic_msgs.append(ChatMessageDTO(role="user", content=dynamic_content))
            else:
                # Other conversation context (assistant reply, tool response, etc.) is dynamic tail
                in_dynamic_tail = True
                dynamic_msgs.append(ChatMessageDTO(role=role, content=content_str.strip()))

        # Fallback: Vertex AI caching requires at least one dynamic message.
        # If no explicit dynamic tags were found, move the last user message to dynamic_msgs.
        if not dynamic_msgs and static_msgs:
            last_msg = static_msgs.pop()
            dynamic_msgs.append(last_msg)

        return CompiledPrompt(
            static_messages=[m.model_dump(mode="json") for m in static_msgs],
            dynamic_messages=[m.model_dump(mode="json") for m in dynamic_msgs],
        )
