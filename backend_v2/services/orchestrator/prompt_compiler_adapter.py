"""Adapter for PromptCompiler to natively support structured static/dynamic prompt segregation."""

import re
from typing import Any

from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.v2_core import PromptBlock


class PromptCompilerAdapter:
    """Adapter wrapping PromptCompiler to provide structured, cache-efficient prompt segregation."""

    def __init__(self) -> None:
        """Initialize the adapter by lazily loading and instantiating the PromptCompiler."""
        from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

        self._compiler = PromptCompiler()

    def __getattr__(self, name: str) -> Any:
        """Delegate all other standard attributes and methods to the wrapped PromptCompiler."""
        return getattr(self._compiler, name)

    def compile_chunk_prompt(
        self,
        base_system_prompt: str,
        chunk_criteria: list[PromptBlock],
        local_payload: str,
        strictness_level: int,
        target_locale: str,
        task_instruction: str = (
            "Analyze the provided <source_data> and execute the extraction strictly according to instructions."
        ),
        previous_errors: list[str] | None = None,
    ) -> CompiledPrompt:
        """Natively compiles static and dynamic components into CompiledPrompt without regex splitting."""
        # 1. Compile System Prompt (Static Segment)
        local_xml_rubrics = self.compile_xml_rubrics(chunk_criteria, target_locale)
        system_content = base_system_prompt
        if local_xml_rubrics:
            system_content += f"\n\n{local_xml_rubrics}"

        # 2. Compile User Prompt Static Part
        static_user_content = f"<source_data>\n{local_payload}\n</source_data>\n\n<task>{task_instruction}</task>"

        # 3. Compile User Prompt Dynamic Part
        strictness_instruction = self.calibrate_strictness(strictness_level)
        language_mandate = self.get_critical_language_mandate(target_locale)

        dynamic_user_content = (
            f"<execution_parameters>\n"
            f"<STRICTNESS_CALIBRATION>\n{strictness_instruction}\n</STRICTNESS_CALIBRATION>\n"
            f"{language_mandate}\n"
            f"</execution_parameters>"
        )

        # Append previous healing errors at the end of the dynamic block
        if previous_errors:
            error_blocks = []
            for err in previous_errors:
                error_blocks.append(f"<PREVIOUS_SCHEMA_ERROR>\n{err}\n</PREVIOUS_SCHEMA_ERROR>")
            dynamic_user_content += "\n\n" + "\n\n".join(error_blocks)

        static_messages = [
            {"role": "system", "content": system_content.strip()},
            {"role": "user", "content": static_user_content.strip()},
        ]

        dynamic_messages = [
            {"role": "user", "content": dynamic_user_content.strip()},
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
            role = msg.get("role")
            content = msg.get("content", "")

            # Safeguard type coercion
            content_str = content if isinstance(content, str) else str(content)

            if role == "system":
                # System is 100% static
                static_msgs.append({"role": "system", "content": content_str.strip()})
            elif role == "user":
                if in_dynamic_tail:
                    dynamic_msgs.append({"role": "user", "content": content_str.strip()})
                else:
                    # Scan for dynamic parameters and previous errors
                    has_exec_params = "<execution_parameters>" in content_str
                    has_prev_error = "<PREVIOUS_SCHEMA_ERROR>" in content_str

                    if not has_exec_params and not has_prev_error:
                        static_msgs.append({"role": "user", "content": content_str.strip()})
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
                            static_msgs.append({"role": "user", "content": static_content})

                        # Keep dynamic parameter blocks in dynamic segment
                        if dynamic_parts:
                            dynamic_content = "\n\n".join(dynamic_parts).strip()
                            dynamic_msgs.append({"role": "user", "content": dynamic_content})
            else:
                # Other conversation context (assistant reply, etc.) is dynamic tail
                in_dynamic_tail = True
                dynamic_msgs.append({"role": role, "content": content_str.strip()})

        return CompiledPrompt(
            static_messages=static_msgs,
            dynamic_messages=dynamic_msgs,
        )
