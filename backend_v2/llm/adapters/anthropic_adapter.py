"""Anthropic Claude cache adapter with structural block mapping and FinOps ROI calculation."""

from typing import Any

from pydantic import Field

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.prompt import CompiledPrompt


class AnthropicTokenUsage(TokenUsage):
    """Subclass of TokenUsage supporting Anthropic-specific caching telemetry and savings."""

    cache_creation_input_tokens: int = Field(default=0, ge=0, description="Tokens spent creating the ephemeral cache.")
    estimated_savings_usd: float = Field(default=0.0, ge=0.0, description="FinOps ROI estimated savings in USD.")


class AnthropicCacheAdapter(BaseLLMAdapter):
    """Caching and pricing adapter for Anthropic Claude models."""

    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Prepare the Anthropic-specific prompt payload with block-level cache tags.

        Args:
            compiled_prompt: The structured CompiledPrompt instance.
            model_name: The target model name.

        Returns:
            A tuple containing:
                - The list of formatted messages (potentially with Anthropic cache blocks).
                - A dictionary of extra keyword arguments (empty for Anthropic).
        """
        # Calculate character count threshold for static messages to see if caching should be active.
        total_static_chars = 0
        for msg in compiled_prompt.static_messages:
            content = msg.get("content")
            if isinstance(content, str):
                total_static_chars += len(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        total_static_chars += len(block.get("text", ""))
            elif content is not None:
                total_static_chars += len(str(content))

        # Milestone 3.1, Rule 2: Caching is active only if total static length >= 4000 chars.
        if total_static_chars < 4000:
            return compiled_prompt.to_flat_messages(), {}

        # 1. Extract and merge all static system messages
        system_msgs = [m for m in compiled_prompt.static_messages if m.get("role") == "system"]
        other_static_msgs = [m for m in compiled_prompt.static_messages if m.get("role") != "system"]

        # Also extract system messages from dynamic part (though usually there are none)
        dynamic_system_msgs = [m for m in compiled_prompt.dynamic_messages if m.get("role") == "system"]
        other_dynamic_msgs = [m for m in compiled_prompt.dynamic_messages if m.get("role") != "system"]

        # Combine all system contents
        system_content_parts = []
        for m in system_msgs + dynamic_system_msgs:
            content = m.get("content")
            if isinstance(content, str):
                system_content_parts.append(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        system_content_parts.append(block.get("text", ""))
            elif content is not None:
                system_content_parts.append(str(content))

        combined_system_text = "\n\n".join(system_content_parts).strip()

        # Build resulting message list
        final_messages: list[dict[str, Any]] = []

        if combined_system_text:
            # First cache control tag placed on combined system block
            final_messages.append(
                {
                    "role": "system",
                    "content": [{"type": "text", "text": combined_system_text, "cache_control": {"type": "ephemeral"}}],
                }
            )

        # 2. Flatten and merge consecutive user/assistant static messages
        flat_static: list[dict[str, Any]] = []
        for msg in other_static_msgs:
            role = msg.get("role")
            content = msg.get("content", "")
            content_str = content if isinstance(content, str) else str(content)

            if flat_static and flat_static[-1]["role"] == role:
                flat_static[-1]["content"] = (flat_static[-1]["content"] + "\n\n" + content_str).strip()
            else:
                flat_static.append({"role": role, "content": content_str.strip()})

        # Tag the absolute last static user/assistant message's last content block
        if flat_static:
            last_static_msg = flat_static[-1]
            last_static_msg["content"] = [
                {"type": "text", "text": last_static_msg["content"], "cache_control": {"type": "ephemeral"}}
            ]

        # 3. Flatten and merge consecutive user/assistant dynamic messages
        flat_dynamic: list[dict[str, Any]] = []
        for msg in other_dynamic_msgs:
            role = msg.get("role")
            content = msg.get("content", "")
            content_str = content if isinstance(content, str) else str(content)

            if flat_dynamic and flat_dynamic[-1]["role"] == role:
                flat_dynamic[-1]["content"] = (flat_dynamic[-1]["content"] + "\n\n" + content_str).strip()
            else:
                flat_dynamic.append({"role": role, "content": content_str.strip()})

        # 4. Combine and check boundary for role alternation
        if flat_static and flat_dynamic and flat_static[-1]["role"] == flat_dynamic[0]["role"]:
            # Same role at boundary, merge them into a single message with list of content blocks
            static_blocks = flat_static[-1]["content"]  # List of blocks
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
        """No-Op teardown for Anthropic Claude."""
        pass

    def calculate_cost(self, usage: TokenUsage, pricing_config: dict[str, Any]) -> TokenUsage:
        """Calculate the precise Anthropic cost and savings.

        Formula:
            Cost = (regular_input_tokens * P_in) + (cache_creation_input_tokens * P_in * 1.25)
                   + (cached_tokens * P_in * 0.10) + (output_tokens * P_out)
            Savings = (cached_tokens * P_in * 0.90) - (cache_creation_input_tokens * P_in * 0.25)

        Args:
            usage: The source TokenUsage object.
            pricing_config: Provider pricing parameters.

        Returns:
            An instance of AnthropicTokenUsage with calculated values.
        """
        # Milestone 3.1 Cost Calculation
        if "input_token_price" not in pricing_config or "output_token_price" not in pricing_config:
            raise AppException(
                message="Invalid pricing configuration: missing input_token_price or output_token_price",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        p_in = float(pricing_config["input_token_price"])
        p_out = float(pricing_config["output_token_price"])

        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        cached_tokens = usage.cached_tokens

        # Check if cache_creation_input_tokens is passed on the usage object or in pricing/extra.
        # If it doesn't exist, we default to 0.
        cache_creation_tokens = getattr(usage, "cache_creation_input_tokens", 0)

        # Calculate regular, uncached prompt tokens
        regular_input = max(0, prompt_tokens - cached_tokens - cache_creation_tokens)

        # Compute cost
        cost_regular = regular_input * p_in
        cost_creation = cache_creation_tokens * p_in * 1.25
        cost_cached = cached_tokens * p_in * 0.10
        cost_output = completion_tokens * p_out

        total_cost = cost_regular + cost_creation + cost_cached + cost_output

        # Compute savings
        savings_cached = cached_tokens * p_in * 0.90
        surcharge_creation = cache_creation_tokens * p_in * 0.25
        total_savings = max(0.0, savings_cached - surcharge_creation)

        return AnthropicTokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=usage.total_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=usage.reasoning_tokens,
            cost_usd=total_cost,
            cache_creation_input_tokens=cache_creation_tokens,
            estimated_savings_usd=total_savings,
        )
