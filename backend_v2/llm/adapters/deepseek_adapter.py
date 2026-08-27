"""DeepSeek cache adapter with automatic prefix caching.

Provides standard FinOps estimation for DeepSeek API calls, factoring in prefix caching
with a 90% read/hit discount compared to normal input token pricing.
"""

import logging
from typing import Any

from pydantic import BaseModel

from backend_v2.llm.adapters.openai_adapter import OpenAICacheAdapter
from backend_v2.models.domain.usage import PricingConfig, TokenUsage

logger = logging.getLogger(__name__)


class DeepSeekCacheAdapter(OpenAICacheAdapter):
    """Caching and pricing adapter for DeepSeek models.

    Attributes:
        None.
    """

    def prepare_provider_kwargs(self, model_name: str) -> dict[str, Any]:
        """Prepare provider specific arguments for LiteLLM.

        Args:
            model_name: The target model name.

        Returns:
            An empty dictionary as no special static arguments are needed.
        """
        return {}

    def prepare_structured_output(self, response_model: type[BaseModel]) -> dict[str, Any] | type[BaseModel]:
        """Convert a Pydantic model into DeepSeek specific strict structured output format.

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

    def calculate_cost(self, usage: TokenUsage, pricing_config: PricingConfig) -> TokenUsage:
        """Calculate the precise DeepSeek cost and savings.

        DeepSeek uses prefix caching similar to OpenAI, but offers a 90% read/hit discount.

        Formula:
            Cost = (regular_input_tokens * P_in) + (cached_tokens * P_in * 0.10) + (output_tokens * P_out)
            Savings = cached_tokens * P_in * 0.90

        Args:
            usage: The source TokenUsage object.
            pricing_config: Provider pricing parameters.

        Returns:
            An instance of TokenUsage with DeepSeek-calculated costs.
        """
        p_in = pricing_config.input_token_price
        p_out = pricing_config.output_token_price

        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        cached_tokens = usage.cached_tokens

        regular_input = max(0, prompt_tokens - cached_tokens)

        # Compute cost and savings (90% read discount)
        cost_regular = regular_input * p_in
        cost_cached = cached_tokens * p_in * 0.10
        cost_output = completion_tokens * p_out

        total_cost = cost_regular + cost_cached + cost_output
        total_savings = cached_tokens * p_in * 0.90

        # Retrieve other usage fields
        total_tokens = usage.total_tokens
        reasoning_tokens = usage.reasoning_tokens
        cost_usd = total_cost
        estimated_savings_usd = total_savings

        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=reasoning_tokens,
            cost_usd=cost_usd,
            estimated_savings_usd=estimated_savings_usd,
        )
