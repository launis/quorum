"""OpenAI cache adapter with automatic prefix caching payload preparation and FinOps cost calculation."""

from typing import Any

from pydantic import Field

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.prompt import CompiledPrompt


class OpenAITokenUsage(TokenUsage):
    """Subclass of TokenUsage supporting OpenAI-specific caching telemetry and savings."""

    estimated_savings_usd: float = Field(default=0.0, ge=0.0, description="FinOps ROI estimated savings in USD.")


class OpenAICacheAdapter(BaseLLMAdapter):
    """Caching and pricing adapter for OpenAI models."""

    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Prepare the OpenAI-specific prompt payload.

        OpenAI recognizes caching automatically by prefix matching. We simply flatten
        the messages and return empty extra keyword arguments.

        Args:
            compiled_prompt: The structured CompiledPrompt instance.
            model_name: The target model name.

        Returns:
            A tuple containing:
                - The flattened list of messages.
                - An empty extra kwargs dictionary.
        """
        flat_messages = compiled_prompt.to_flat_messages()
        return flat_messages, {}

    async def teardown_cache(self, workflow_run_id: str) -> None:
        """No-Op teardown for OpenAI."""
        pass

    def calculate_cost(self, usage: TokenUsage, pricing_config: dict[str, Any]) -> TokenUsage:
        """Calculate the precise OpenAI cost and savings.

        Formula:
            Cost = (regular_input_tokens * P_in) + (cached_tokens * P_in * 0.50) + (output_tokens * P_out)
            Savings = cached_tokens * P_in * 0.50

        Args:
            usage: The source TokenUsage object.
            pricing_config: Provider pricing parameters.

        Returns:
            An instance of OpenAITokenUsage with calculated values.
        """
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

        # Check for deepseek model override if model name is passed dynamically
        model_name = pricing_config.get("model_name") or pricing_config.get("model") or ""
        is_deepseek = "deepseek" in str(model_name).lower()

        # DeepSeek has 90% read discount, OpenAI has 50% read discount
        discount_factor = 0.10 if is_deepseek else 0.50
        savings_factor = 0.90 if is_deepseek else 0.50

        regular_input = max(0, prompt_tokens - cached_tokens)

        # Compute cost and savings
        cost_regular = regular_input * p_in
        cost_cached = cached_tokens * p_in * discount_factor
        cost_output = completion_tokens * p_out

        total_cost = cost_regular + cost_cached + cost_output
        total_savings = cached_tokens * p_in * savings_factor

        return OpenAITokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=usage.total_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=usage.reasoning_tokens,
            cost_usd=total_cost,
            estimated_savings_usd=total_savings,
        )
