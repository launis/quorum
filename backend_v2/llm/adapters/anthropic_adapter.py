"""Anthropic Claude cache adapter with structural block mapping and FinOps ROI calculation."""

import logging
from typing import Any

from pydantic import BaseModel

from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.v2_core import ModelProfile

logger = logging.getLogger(__name__)


class AnthropicCacheAdapter(BaseLLMAdapter):
    """Caching and pricing adapter for Anthropic Claude models."""

    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> tuple[list[LLMMessageDTO] | list[dict[str, Any]], dict[str, Any]]:
        """Prepare the Anthropic-specific prompt payload with block-level cache tags.

        Args:
            compiled_prompt: The structured CompiledPrompt instance.
            model_name: The target model name.

        Returns:
            A tuple containing:
                - The list of formatted messages (potentially with Anthropic cache blocks).
                - A dictionary of extra keyword arguments (empty for Anthropic).
        """
        estimated_tokens, _ = self.estimate_static_tokens(compiled_prompt, exclude_system=False)

        # Minimum threshold for Anthropic cache block creation (approx 1000 tokens / 4000 chars)
        if estimated_tokens < 1000:
            return compiled_prompt.to_flat_messages(), {}

        system_msgs = [m for m in compiled_prompt.static_messages if m.role == "system"]
        other_static_msgs = [m for m in compiled_prompt.static_messages if m.role != "system"]

        dynamic_system_msgs = [m for m in compiled_prompt.dynamic_messages if m.role == "system"]
        other_dynamic_msgs = [m for m in compiled_prompt.dynamic_messages if m.role != "system"]

        system_content_parts = [m.content for m in system_msgs + dynamic_system_msgs if m.content]
        combined_system_text = "\n\n".join(system_content_parts).strip()
        final_messages: list[dict[str, Any]] = []

        if combined_system_text:
            final_messages.append(
                {
                    "role": "system",
                    "content": [{"type": "text", "text": combined_system_text, "cache_control": {"type": "ephemeral"}}],
                }
            )

        flat_static: list[dict[str, Any]] = []
        for msg in other_static_msgs:
            role = msg.role
            content_str = str(msg.content)

            if flat_static and flat_static[-1]["role"] == role:
                flat_static[-1]["content"] = (flat_static[-1]["content"] + "\n\n" + content_str).strip()
            else:
                flat_static.append({"role": role, "content": content_str.strip()})

        if flat_static:
            last_static_msg = flat_static[-1]
            last_static_msg["content"] = [
                {"type": "text", "text": last_static_msg["content"], "cache_control": {"type": "ephemeral"}}
            ]

        flat_dynamic: list[dict[str, Any]] = []
        for msg in other_dynamic_msgs:
            role = msg.role
            content_str = str(msg.content)

            if flat_dynamic and flat_dynamic[-1]["role"] == role:
                flat_dynamic[-1]["content"] = (flat_dynamic[-1]["content"] + "\n\n" + content_str).strip()
            else:
                flat_dynamic.append({"role": role, "content": content_str.strip()})

        if flat_static and flat_dynamic and flat_static[-1]["role"] == flat_dynamic[0]["role"]:
            static_blocks = flat_static[-1]["content"]
            dynamic_text = flat_dynamic[0]["content"]

            merged_content = list(static_blocks) + [{"type": "text", "text": dynamic_text}]
            flat_static[-1]["content"] = merged_content
            final_messages.extend(flat_static)
            final_messages.extend(flat_dynamic[1:])
        else:
            final_messages.extend(flat_static)
            final_messages.extend(flat_dynamic)

        return final_messages, {}

    async def teardown_cache(self, workflow_run_id: str) -> None:
        """No-Op teardown for Anthropic Claude.

        Args:
            workflow_run_id: Identifier of the workflow pipeline execution.
        """
        pass

    def calculate_cost(self, usage: TokenUsage, pricing_config: PricingConfig) -> TokenUsage:
        """Calculate the precise Anthropic cost and savings.

        Formula:
            Cost = (regular_input_tokens * P_in) + (cache_creation_input_tokens * P_creation)
                   + (cached_tokens * P_cached) + (output_tokens * P_out)
            Savings = max(
                0.0,
                (cached_tokens * (P_in - P_cached)) - (cache_creation_input_tokens * (P_creation - P_in)),
            )

        Args:
            usage: The source TokenUsage object.
            pricing_config: Provider pricing parameters.

        Returns:
            An instance of TokenUsage with calculated values.
        """
        p_in = pricing_config.input_token_price
        p_out = pricing_config.output_token_price
        p_cached = (
            pricing_config.cached_input_token_price
            if pricing_config.cached_input_token_price is not None
            else p_in * 0.10
        )
        p_creation = (
            pricing_config.cache_creation_input_token_price
            if pricing_config.cache_creation_input_token_price is not None
            else p_in * 1.25
        )

        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        cached_tokens = usage.cached_tokens
        cache_creation_input_tokens = usage.cache_creation_input_tokens

        regular_input = max(0, prompt_tokens - cached_tokens - cache_creation_input_tokens)

        cost_regular = regular_input * p_in
        cost_creation = cache_creation_input_tokens * p_creation
        cost_cached = cached_tokens * p_cached
        cost_output = completion_tokens * p_out

        cost_usd = cost_regular + cost_creation + cost_cached + cost_output

        gross_savings = cached_tokens * max(0.0, p_in - p_cached)
        creation_surcharge = cache_creation_input_tokens * max(0.0, p_creation - p_in)
        estimated_savings_usd = max(0.0, gross_savings - creation_surcharge)

        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=usage.total_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=usage.reasoning_tokens,
            cost_usd=cost_usd,
            cache_creation_input_tokens=cache_creation_input_tokens,
            estimated_savings_usd=estimated_savings_usd,
        )

    def prepare_provider_kwargs(self, model_name: str) -> dict[str, Any]:
        """Prepare provider specific arguments for LiteLLM.

        Args:
            model_name: The target model name.

        Returns:
            An empty dictionary as no special static arguments are needed.
        """
        return {}

    def prepare_kwargs(
        self, call_kwargs: dict[str, Any], config: Any | None = None, settings: Any | None = None
    ) -> dict[str, Any]:
        """Prepare Anthropic specific kwargs, handling thinking budgets and parameter constraints.

        Args:
            call_kwargs: The dictionary of arguments to pass to litellm.
            config: Optional config object for the provider.
            settings: Optional app settings.

        Returns:
            The potentially modified call_kwargs dictionary.
        """
        model_name = str(
            call_kwargs.get("model") or (config.model_name if isinstance(config, ModelProfile) else "")
        ).lower()
        is_claude_37 = "claude-3-7" in model_name or "claude-3.7" in model_name

        thinking_budget: int | None = None
        if isinstance(config, ModelProfile) and config.thinking_budget_tokens is not None:
            thinking_budget = int(config.thinking_budget_tokens)

        if is_claude_37 and thinking_budget is not None and thinking_budget > 0:
            call_kwargs["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}
            # Anthropic strictly requires temperature = 1.0 when extended thinking is enabled
            call_kwargs["temperature"] = 1.0

        return call_kwargs

    def prepare_structured_output(self, response_model: type[BaseModel]) -> dict[str, Any] | type[BaseModel]:
        """Convert a Pydantic model into Anthropic specific strict structured output format.

        Anthropic utilizes tool-calling for JSON schemas. LiteLLM handles the conversion
        but we pass the standard strict JSON schema definition.

        Args:
            response_model: The Pydantic model defining the expected JSON structure.

        Returns:
            A dictionary matching LiteLLM's structured output format.
        """
        json_schema = response_model.model_json_schema()
        self._strip_unsupported_constraints(json_schema)

        return {
            "type": "json_schema",
            "json_schema": {
                "name": response_model.__name__,
                "schema": json_schema,
                "strict": True,
            },
        }
