"""DeepSeek cache adapter with automatic prefix caching.

Provides standard FinOps estimation for DeepSeek API calls, factoring in prefix caching
with a 90% read/hit discount compared to normal input token pricing.
"""

from __future__ import annotations

import logging
from typing import Any, override

from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.openai_adapter import OpenAICacheAdapter
from backend_v2.models.domain.usage import PricingConfig, TokenUsage

logger = logging.getLogger(__name__)

__all__ = ["DeepSeekCacheAdapter"]


class DeepSeekCacheAdapter(OpenAICacheAdapter):
    """Caching and pricing adapter for DeepSeek models."""

    @override
    def prepare_provider_kwargs(self, model_name: str) -> dict[str, Any]:
        """Prepare provider specific arguments for LiteLLM.

        Args:
            model_name: The target model name.

        Returns:
            An empty dictionary as no special static arguments are needed.

        Raises:
            AppException: VALIDATION_FAILED if model_name is empty or whitespace.
        """
        if not model_name or not model_name.strip():
            logger.error(
                "[DeepSeekCacheAdapter] %s: Target model_name cannot be empty.",
                ErrorCodes.VALIDATION_FAILED.name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message="Target model_name cannot be empty for DeepSeek provider kwargs.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return {}

    @override
    def prepare_structured_output(self, response_model: type[BaseModel]) -> dict[str, Any] | type[BaseModel]:
        """Convert a Pydantic model into DeepSeek specific strict structured output format.

        Args:
            response_model: The Pydantic model defining the expected JSON structure.

        Returns:
            A dictionary matching LiteLLM's structured output format.

        Raises:
            AppException: VALIDATION_FAILED if response_model is not a Pydantic BaseModel subclass.
        """
        if not isinstance(response_model, type) or not issubclass(response_model, BaseModel):
            logger.error(
                "[DeepSeekCacheAdapter] %s: response_model must be a Pydantic BaseModel subclass.",
                ErrorCodes.VALIDATION_FAILED.name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message="response_model must be a Pydantic BaseModel subclass for DeepSeek structured output.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

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

    @override
    def calculate_cost(self, usage: TokenUsage, pricing_config: PricingConfig) -> TokenUsage:
        """Calculate the precise DeepSeek cost and savings.

        DeepSeek uses prefix caching similar to OpenAI, offering a 90% read/hit discount
        when an explicit cached_input_token_price is not specified in PricingConfig.

        Formula:
            Cost = (regular_input_tokens * P_in) + (cached_tokens * P_cached) + (output_tokens * P_out)
            Savings = cached_tokens * max(0.0, P_in - P_cached)

        Args:
            usage: The source TokenUsage object.
            pricing_config: Provider pricing parameters.

        Returns:
            An instance of TokenUsage with DeepSeek-calculated costs.
        """
        p_in = pricing_config.input_token_price
        p_out = pricing_config.output_token_price
        p_cached = (
            pricing_config.cached_input_token_price
            if pricing_config.cached_input_token_price is not None
            else p_in * 0.10
        )

        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        cached_tokens = usage.cached_tokens

        regular_input = max(0, prompt_tokens - cached_tokens)

        # Compute cost and savings (90% default read discount)
        cost_regular = regular_input * p_in
        cost_cached = cached_tokens * p_cached
        cost_output = completion_tokens * p_out

        total_cost = cost_regular + cost_cached + cost_output
        total_savings = cached_tokens * max(0.0, p_in - p_cached)

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
            cache_creation_input_tokens=usage.cache_creation_input_tokens,
            cost_usd=cost_usd,
            estimated_savings_usd=estimated_savings_usd,
        )
