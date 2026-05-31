"""Abstract base class for provider-agnostic caching and pricing adapters."""

from abc import ABC, abstractmethod
from typing import Any

from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.prompt import CompiledPrompt


class BaseLLMAdapter(ABC):
    """Abstract base class defining the strict interface for caching and pricing adapters."""

    @abstractmethod
    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Prepare the payload for the API request by configuring caching structures.

        Returns:
            A tuple containing:
                - The list of formatted messages (potentially with provider-specific cache blocks).
                - A dictionary of extra keyword arguments (kwargs) to merge into the request body.
        """
        pass

    @abstractmethod
    async def teardown_cache(self, workflow_run_id: str) -> None:
        """Teardown any resources or session states associated with caching.

        Option B: Vertex AI context cache deletion or No-Op for Anthropic/OpenAI.
        """
        pass

    @abstractmethod
    def calculate_cost(self, usage: TokenUsage, pricing_config: dict[str, Any]) -> TokenUsage:
        """Calculate the precise financial usage cost and ROI utilizing provider-specific pricing coefficients."""
        pass
