"""DeepSeek cache adapter with automatic prefix caching.

Provides standard FinOps estimation for DeepSeek API calls, factoring in prefix caching
with a 90% read/hit discount compared to normal input token pricing.
"""

import logging

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.openai_adapter import OpenAICacheAdapter, OpenAITokenUsage
from backend_v2.models.domain.usage import TokenUsage

logger = logging.getLogger(__name__)


class DeepSeekCacheAdapter(OpenAICacheAdapter):
    """Caching and pricing adapter for DeepSeek models.

    Attributes:
        None.
    """

    def calculate_cost(self, usage: TokenUsage, pricing_config: dict[str, float | int]) -> OpenAITokenUsage:
        """Calculate the precise DeepSeek cost and savings.

        DeepSeek uses prefix caching similar to OpenAI, but offers a 90% read/hit discount.

        Formula:
            Cost = (regular_input_tokens * P_in) + (cached_tokens * P_in * 0.10) + (output_tokens * P_out)
            Savings = cached_tokens * P_in * 0.90

        Args:
            usage: The source TokenUsage object.
            pricing_config: Provider pricing parameters.

        Returns:
            An instance of OpenAITokenUsage with DeepSeek-calculated costs.

        Raises:
            AppException: Triggered with ErrorCodes.CONFIGURATION_ERROR if pricing model keys are absent.
        """
        if "input_token_price" not in pricing_config or "output_token_price" not in pricing_config:
            logger.error(
                "Invalid pricing configuration: missing input_token_price or output_token_price in pricing_config",
                exc_info=True,
            )
            raise AppException(
                message="Invalid pricing configuration: missing input_token_price or output_token_price",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        p_in = float(pricing_config["input_token_price"])
        p_out = float(pricing_config["output_token_price"])

        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        cached_tokens = getattr(usage, "cached_tokens", 0)

        regular_input = max(0, prompt_tokens - cached_tokens)

        # Compute cost and savings (90% read discount)
        cost_regular = regular_input * p_in
        cost_cached = cached_tokens * p_in * 0.10
        cost_output = completion_tokens * p_out

        total_cost = cost_regular + cost_cached + cost_output
        total_savings = cached_tokens * p_in * 0.90

        # Retrieve other usage fields
        total_tokens = usage.total_tokens
        reasoning_tokens = getattr(usage, "reasoning_tokens", 0)
        cost_usd = total_cost
        estimated_savings_usd = total_savings

        # Deploying PEP 736 Shorthand Syntax where appropriate
        return OpenAITokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=reasoning_tokens,
            cost_usd=cost_usd,
            estimated_savings_usd=estimated_savings_usd,
        )
