"""Agent implementations for the Cognitive Quorum backend."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain.panel import PanelInput, PanelOutput, PanelOutputDTO
from backend.utils.json_utils import flexible_json_dump

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class PanelAgent(BaseAgent[PanelInput, PanelOutput]):
    """Paneeli-agentti (Panel Agent).

    Executes multiple critical roles in a single LLM call to save tokens and time.
    Acts as a composite agent that performs fan-out of results to individual state fields.
    """

    state_field = "dbcaf18a-4ea3-4469-baa5-1abe63c64700"
    REQUIRES_KEYS = ["step_analyst", "46f13eed-f411-4aac-ac41-d8e11f98a648"]
    PRODUCES_KEYS = [
        "dbcaf18a-4ea3-4469-baa5-1abe63c64700",
        "faaf85a4-6781-478e-8ab5-437c670baf6f",
        "2a82920d-86ff-4b30-b357-5718a37b03d6",
        "fc347c2f-3df6-4551-9279-429af3114ef3",
        "7440dcea-282b-4b08-b469-bb33f334ab54",
        "2e24724a-29c9-44ab-8eb9-0ac8862b8fe1"
    ]
    DTO_SCHEMA = PanelOutputDTO
    INPUT_SCHEMA = PanelInput
    OUTPUT_SCHEMA = PanelOutput

    def __init__(self, model: str | None = None, provider: str | None = None, **kwargs: Any):
        """Initializes PanelAgent with strict configuration (Zero-Fallback)."""
        # ZERO-FALLBACK RULE: Fail fast if configuration is missing
        if not model:
            # We allow None during init if it's injected later via Registry,
            # but we do NOT provide a hardcoded default string here.
            # The Registry/Factory logic must ensure 'model' is passed.
            pass

        super().__init__(model=model, provider=provider)

    def construct_user_prompt(self, input_data: PanelInput, execution_context: dict[str, Any] | None = None) -> str:
        """Constructs the user prompt using strict PanelInput.

        Args:
            input_data (PanelInput): Input data.
            execution_context (dict[str, Any] | None): Config/Context.

        Returns:
            str: Constructed prompt.
        """
        # Dependencies enforced by Input Schema, but let's double check content
        if not input_data.step_analyst:
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                original_error=ValueError("PanelAgent: Missing dependency 'step_analyst'."),
                agent_name="PanelAgent",
            )
        if not input_data.step_profiler:
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                original_error=ValueError("PanelAgent: Missing dependency 'step_profiler'."),
                agent_name="PanelAgent",
            )

        # Hydrate for prompt - use Objects directly, flexible_json_dump handles serialization
        prompt_input_data = {
            "inputs": {
                "history_text": input_data.history_text,
                "product_text": input_data.product_text,
                "reflection_text": input_data.reflection_text,
            },
            "step_analyst": input_data.step_analyst,
            "step_profiler": input_data.step_profiler,
        }

        # Context (Knowledge Base)
        context_section = ""
        if execution_context:
            context_raw = execution_context.get("step_context")
            if context_raw:
                # Try to hydrate or use as is
                # For template context_section, we need 'precedents' string.
                if hasattr(context_raw, "precedents"):
                    context_section = (
                        f"\nJÄRJESTELMÄN KONTEKSTI (TIETOPANKKI & ENNAKKOTAPAUKSET):\n{context_raw.precedents}\n---"
                    )
                elif isinstance(context_raw, dict):
                    precedents = context_raw.get("precedents", "")
                    if precedents:
                        context_section = (
                            f"\nJÄRJESTELMÄN KONTEKSTI (TIETOPANKKI & ENNAKKOTAPAUKSET):\n{precedents}\n---"
                        )

                # Also update prompt_input_data for JSON dump
                # strict: we prefer the object itself if available
                prompt_input_data["step_context"] = context_raw

        # External Search Results
        search_section = ""
        # Access from execution_context "aux_data" or similar?
        # Only if injected.

        # Linguistics
        linguistics_section = ""
        linguistics_result = execution_context.get("linguistics_result") if execution_context else None
        if linguistics_result:
            # Logic to format linguistics
            patterns = []
            if isinstance(linguistics_result, dict):
                patterns = linguistics_result.get("performative_patterns", [])
            elif hasattr(linguistics_result, "performative_patterns"):
                patterns = linguistics_result.performative_patterns

            if patterns:

                def get_phrase(p: Any) -> str:
                    return p.detected_phrase if hasattr(p, "detected_phrase") else p.get("detected_phrase", "")

                def get_category(p: Any) -> str:
                    return p.category if hasattr(p, "category") else p.get("category", "")

                pattern_list = "\n".join([f'- "{get_phrase(p)}" ({get_category(p)})' for p in patterns])
                linguistics_section = f"\nKIELIOPILLINEN ANALYYSI (PERFORMATIIVISUUS):\nHavaittu seuraavat performatiiviset ilmaisut:\n{pattern_list}\n---"

        # Template (Dynamic Slug Resolution via ComponentRegistry)
        template_str = execution_context.get("PANEL_PROMPT_TEMPLATE") if execution_context else None
        
        task_prompts = []
        config_prompts = execution_context.get("llm_prompts", []) if execution_context else []
        if isinstance(config_prompts, list):
            for p in config_prompts:
                content = execution_context.get(p) if execution_context else None
                # Skip the template itself if we encounter its UUID or slug
                if content and isinstance(content, str) and content != template_str:
                    task_prompts.append(content)

        if not template_str:
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_NOT_CONFIGURED,
                original_error=ValueError("PANEL_PROMPT_TEMPLATE slug not injected into execution context. Ensure the core component exists and is referenced."),
                agent_name="PanelAgent",
            )

        task_section = "\n\n".join(task_prompts)


        return template_str.format(
            input_json=flexible_json_dump(prompt_input_data),
            context_section=context_section,
            search_section=search_section,
            linguistics_section=linguistics_section,
            task_section=task_section,
        )

    async def execute(
        self,
        input_data: PanelInput,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> PanelOutput:
        """Executes the Panel Agent logic.

        Args:
            input_data (PanelInput): Inputs.
            execution_context (dict[str, Any] | None, optional): Config.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
             PanelOutput: The composite PanelOutput result.
        """
        # 1. Construct User Prompt
        try:
            # Construct the prompt using inputs and the injected template from execution_context.

            # Let's see construct_user_prompt. It calls _hydrate_inputs(input_data).
            # If we pass PanelInput, it might fail if it expects dict.
            # _hydrate_inputs expects dict.

            # Refactoring strategy:
            # PanelInput ALREADY HAS the hydrated models (step_analyst, step_profiler).
            # So _hydrate_inputs is redundant if we trust PanelInput!

            # But wait, PanelInput fields are Optional?
            # construct_user_prompt checks for them.

            # Let's strictly use PanelInput in execute using attributes.

            user_content = self.construct_user_prompt(input_data, execution_context=execution_context)

            # 2. Call LLM with strict PanelOutputDTO schema (Content Only)
            if not self.llm_provider:
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_NOT_CONFIGURED,
                    original_error=ValueError("PanelAgent requires a configured LLM Provider."),
                    agent_name="PanelAgent",
                )

            # ENFORCEMENT: Model must be configured
            if not self.model:
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_NOT_CONFIGURED,
                    original_error=ValueError(
                        "PanelAgent requires a configured Model string (Zero-Fallback Violation)."
                    ),
                    agent_name="PanelAgent",
                )

            response = await self.llm_provider.generate(
                prompt=user_content,
                system_instruction=system_instruction,
                response_schema=self.DTO_SCHEMA,  # Request DTO
                mock_identity="PanelAgent",
                **kwargs,
            )

            # 3. Process Response (Structured Output)
            panel_dto = None

            # OPTIMIZATION: Use pre-parsed content if available (Instructor Pattern)
            if response.parsed_content is not None:
                if isinstance(response.parsed_content, PanelOutputDTO):
                    panel_dto = response.parsed_content
                elif isinstance(response.parsed_content, PanelOutput):
                    panel_dto = response.parsed_content
                elif isinstance(response.parsed_content, dict):
                    panel_dto = PanelOutputDTO(**response.parsed_content)
                else:
                    logger.warning(
                        f"[PanelAgent] parsed_content was {type(response.parsed_content)}, "
                        "expected Dict or PanelOutputDTO."
                    )

            # STRICTNESS: No Fallback Parsing (Removed `if not panel_dto` block)
            # If provider failed to return structured data, we FAIL.

            if panel_dto:
                # 4. Promotion to Domain Model (Inject Metadata)
                panel_domain = self._apply_python_authority(panel_dto)

                logger.info("[PanelAgent] Successfully generated PanelOutput (Domain Model).")
                return panel_domain

            else:
                # Detailed error for debugging
                raw_content = response.content if hasattr(response, "content") else "No content"
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_RESPONSE_PARSING_FAILED,
                    original_error=ValueError(
                        f"LLM Provider returned no structured data. Raw: {str(raw_content)[:200]}..."
                    ),
                    agent_name="PanelAgent",
                )

        except AgentExecutionError:
            # Re-raise known agent errors (e.g. Configuration errors) to preserve error codes
            raise

        except Exception as e:
            # ECHO PROTOCOL: Safety Net for unexpected crashes
            error_code = ErrorCodes.AGENT_EXECUTION_CRITICAL
            logger.error(f"{error_code}: Unexpected failure - {e}", exc_info=True)
            raise AgentExecutionError(detail=error_code, original_error=e) from e
