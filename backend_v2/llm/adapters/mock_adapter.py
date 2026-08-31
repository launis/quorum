"""Mock cache adapter for testing and verification.

This module implements network-free testing utilities matching the 2026 Enterprise core standard.
"""

import logging
from typing import Any

from pydantic import BaseModel

from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt

logger = logging.getLogger(__name__)


class MockCacheAdapter(BaseLLMAdapter):
    """Mock LLM cache adapter for network-free testing and verification.

    Conforms to structural protocols without making downstream API calls.
    """

    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> tuple[list[LLMMessageDTO] | list[dict[str, Any]], dict[str, Any]]:
        """Return the flat compiled prompt messages as-is and set mock active flag.

        Args:
            compiled_prompt: The structured CompiledPrompt instance.
            model_name: The target model name.

        Returns:
            A tuple of flat messages and extra kwargs with 'mock_cache_active' enabled.
        """
        flat_messages = compiled_prompt.to_flat_messages()
        extra_kwargs = {"mock_cache_active": True}
        return flat_messages, extra_kwargs

    async def teardown_cache(self, workflow_run_id: str) -> None:
        """Perform a No-Op teardown.

        Args:
            workflow_run_id: The ID of the workflow run to tear down.

        Returns:
            None.
        """
        pass

    def calculate_cost(self, usage: TokenUsage, pricing_config: PricingConfig) -> TokenUsage:
        """Return TokenUsage with estimated_savings_usd set to 0.05.

        Args:
            usage: The source TokenUsage object.
            pricing_config: Provider-specific pricing parameters.

        Returns:
            An instance of TokenUsage containing the calculated costs.
        """
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens
        cached_tokens = usage.cached_tokens
        reasoning_tokens = usage.reasoning_tokens
        cost_usd = usage.cost_usd

        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=reasoning_tokens,
            cost_usd=cost_usd,
            estimated_savings_usd=0.05,
        )

    def prepare_provider_kwargs(self, model_name: str) -> dict[str, Any]:
        """Prepare provider specific arguments for LiteLLM.

        Args:
            model_name: The target model name.

        Returns:
            An empty dictionary as no special static arguments are needed.
        """
        return {}

    def prepare_structured_output(self, response_model: type[BaseModel]) -> dict[str, Any] | type[BaseModel]:
        """Return the pure Pydantic model for the Mock provider.

        Args:
            response_model: The Pydantic model defining the expected JSON structure.

        Returns:
            The original model or stripped schema.
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
