"""Mock cache adapter for testing and verification."""

from typing import Any

from pydantic import Field

from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.prompt import CompiledPrompt


class MockTokenUsage(TokenUsage):
    """Extended TokenUsage for testing caching cost calculations."""

    estimated_savings_usd: float = Field(default=0.05, ge=0.0)


class MockCacheAdapter(BaseLLMAdapter):
    """Mock LLM cache adapter for network-free testing and verification."""

    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
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
        """
        pass

    def calculate_cost(self, usage: TokenUsage, pricing_config: dict[str, Any]) -> TokenUsage:
        """Return TokenUsage with estimated_savings_usd set to 0.05.

        Args:
            usage: The source TokenUsage object.
            pricing_config: Provider-specific pricing parameters.

        Returns:
            An instance of TokenUsage containing the calculated costs.
        """
        return MockTokenUsage(
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            cached_tokens=usage.cached_tokens,
            reasoning_tokens=usage.reasoning_tokens,
            cost_usd=usage.cost_usd,
            estimated_savings_usd=0.05,
        )
