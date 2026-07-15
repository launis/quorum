from backend_v2.settings import get_settings

"""Adapter for PromptCompiler to natively support structured static/dynamic prompt segregation."""

import re
from typing import Any

from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.prompts.global_mandates import GLOBAL_MANDATES_XML
from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


class PromptCompilerAdapter:
    """Adapter wrapping PromptCompiler to provide structured, cache-efficient prompt segregation."""

    def __init__(self) -> None:
        """Initialize the adapter by lazily loading and instantiating the PromptCompiler."""
        self._compiler = PromptCompiler()

    def __getattr__(self, name: str) -> Any:
        """Delegate all other standard attributes and methods to the wrapped PromptCompiler."""
        return getattr(self._compiler, name)

    def compile_chunk_prompt(
        self,
        base_system_prompt: str,
        chunk_criteria: list[PromptBlock],
        base_payload: str,
        strictness_level: int,
        target_locale: str,
        chunk_atoms_xml: str | None = None,
        task_instruction: str = (
            "Analyze the provided <source_data> and execute the extraction strictly according to instructions."
        ),
        previous_errors: list[str] | None = None,
        allowed_atom_ids: set[str] | None = None,
        atom_alias_map: dict[str, str] | None = None,
    ) -> CompiledPrompt:
        """Compile static and dynamic message tiers with V3 cache-safe separation.

        Static tier contains globally identical content (system prompt + base document).
        Dynamic tier contains per-chunk/per-retry content (rubrics, atoms, params, errors).

        When CONTENT_CACHE_ENABLED is active, the system prompt moves to user role
        to allow Vertex AI to cache only the PDF. This trades evaluation quality
        (~29% degradation) for token cost savings.
        """
        content_cache_enabled = bool(get_settings().content_cache_enabled)
        if content_cache_enabled:
            # Epic 80 Mode: Static tier = ONLY the source document (for max cache hit rate).
            # System prompt is demoted to user role in the dynamic tier.
            static_messages = [
                {"role": "user", "content": base_payload.strip()},
            ]
        else:
            # V3 Default: Static tier = system prompt (system role) + source document.
            # Preserves native system role authority for maximum LLM compliance.
            static_messages = [
                {"role": "system", "content": base_system_prompt.strip()},
                {"role": "user", "content": base_payload.strip()},
            ]

        # Dynamic Tier: Everything that varies per chunk, retry, or matrix
        dynamic_parts = []

        # Epic 80: Move system instructions to dynamic tier as user content
        if content_cache_enabled:
            dynamic_parts.append(f"<system_instructions>\n{base_system_prompt.strip()}\n</system_instructions>")

        # 1. Chunk-specific rubrics (vary per chunk when atom subsets differ)
        # We bypass the PromptCompiler adapter layer to pass allowed_atom_ids to LocalizationCompiler
        local_xml_rubrics = self._compiler._localization_compiler.compile_xml_rubrics(
            chunk_criteria, target_locale, allowed_atom_ids=allowed_atom_ids, atom_alias_map=atom_alias_map
        )
        if local_xml_rubrics:
            dynamic_parts.append(f"<evaluation_criteria>\n{local_xml_rubrics}\n</evaluation_criteria>")

        # 2. Chunk-specific atoms (NOT cacheable)
        if chunk_atoms_xml:
            dynamic_parts.append(chunk_atoms_xml)

        # 3. Task instruction
        dynamic_parts.append(f"<task>{task_instruction}</task>")

        strictness_instruction = self.calibrate_strictness(strictness_level)
        dynamic_parts.append(
            f"<execution_parameters>\n"
            f"{GLOBAL_MANDATES_XML}\n"
            f"<STRICTNESS_CALIBRATION>\n{strictness_instruction}\n</STRICTNESS_CALIBRATION>\n"
            f"</execution_parameters>"
        )

        # 5. Healing errors (if retrying)
        if previous_errors:
            for err in previous_errors:
                dynamic_parts.append(f"<PREVIOUS_SCHEMA_ERROR>\n{err}\n</PREVIOUS_SCHEMA_ERROR>")

        dynamic_messages = [
            {"role": "user", "content": "\n\n".join(dynamic_parts).strip()},
        ]

        return CompiledPrompt(
            static_messages=static_messages,
            dynamic_messages=dynamic_messages,
        )

    def compile_prompt(self, messages: list[dict[str, Any]]) -> CompiledPrompt:
        """Splits an existing flat list of messages into static_messages and dynamic_messages.

        Acts as a robust fallback for general inputs by extracting dynamic blocks (execution
        parameters and error blocks) from user messages and placing them in the dynamic tail.
        """
        static_msgs: list[dict[str, Any]] = []
        dynamic_msgs: list[dict[str, Any]] = []
        in_dynamic_tail = False

        for msg in messages:
            role = msg["role"] if "role" in msg else None
            content = msg["content"] if "content" in msg else None

            # Preserve extra properties (like tool_calls, tool_call_id, name)
            extra_props = {k: v for k, v in msg.items() if k not in ("role", "content")}

            # Handle None safely without casting it to "None"
            content_str = content if isinstance(content, str) else (str(content) if content is not None else None)

            new_msg: dict[str, Any]

            if role == "system":
                # System is 100% static
                new_msg = {"role": "system", "content": content_str.strip() if content_str else ""}
                new_msg.update(extra_props)
                static_msgs.append(new_msg)
            elif role == "user":
                if in_dynamic_tail:
                    new_msg = {"role": "user", "content": content_str.strip() if content_str else ""}
                    new_msg.update(extra_props)
                    dynamic_msgs.append(new_msg)
                else:
                    # Scan for dynamic parameters and previous errors
                    has_exec_params = content_str and "<execution_parameters>" in content_str
                    has_prev_error = content_str and "<PREVIOUS_SCHEMA_ERROR>" in content_str

                    if not has_exec_params and not has_prev_error:
                        new_msg = {"role": "user", "content": content_str.strip() if content_str else ""}
                        new_msg.update(extra_props)
                        static_msgs.append(new_msg)
                    else:
                        in_dynamic_tail = True
                        # Isolate dynamic parameters block
                        exec_params_match = (
                            re.search(r"(<execution_parameters>.*?</execution_parameters>)", content_str, re.DOTALL)
                            if content_str
                            else None
                        )
                        # Isolate previous errors block
                        prev_error_match = (
                            re.search(r"(<PREVIOUS_SCHEMA_ERROR>.*?</PREVIOUS_SCHEMA_ERROR>)", content_str, re.DOTALL)
                            if content_str
                            else None
                        )

                        dynamic_parts = []
                        static_content = content_str or ""

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
                            new_static = {"role": "user", "content": static_content}
                            new_static.update(extra_props)
                            static_msgs.append(new_static)

                        # Keep dynamic parameter blocks in dynamic segment
                        if dynamic_parts:
                            dynamic_content = "\n\n".join(dynamic_parts).strip()
                            new_dynamic = {"role": "user", "content": dynamic_content}
                            # Optional: Which message gets the extra props if it's split? Usually user messages don't have tool_calls.
                            # We'll attach them to the dynamic tail if it was a user message that got split.
                            new_dynamic.update(extra_props)
                            dynamic_msgs.append(new_dynamic)
            else:
                # Other conversation context (assistant reply, tool response, etc.) is dynamic tail
                in_dynamic_tail = True
                new_msg = {
                    "role": role if role else "",
                    "content": content_str.strip() if content_str else None,
                }
                new_msg.update(extra_props)
                dynamic_msgs.append(new_msg)

        # Fallback: Vertex AI caching requires at least one dynamic message.
        # If no explicit dynamic tags were found, move the last user message to dynamic_msgs.
        if not dynamic_msgs and static_msgs:
            last_msg = static_msgs.pop()
            dynamic_msgs.append(last_msg)

        return CompiledPrompt(
            static_messages=static_msgs,
            dynamic_messages=dynamic_msgs,
        )
