"""Abstract base class for provider-agnostic caching and pricing adapters.

All implementations must enforce high-fidelity adapters supporting performance metrics,
strict pricing policies, and distributed rate pacing control patterns.
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.prompt import CompiledPrompt


class BaseLLMAdapter(ABC):
    """Abstract base class defining the strict interface for caching and pricing adapters."""

    @abstractmethod
    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Prepare the payload for the API request by configuring caching structures.

        Args:
            compiled_prompt: The prompt after execution compilation stages.
            model_name: The physical target deployment model.

        Returns:
            A tuple containing:
                - The list of formatted messages (potentially with provider-specific cache blocks).
                - A dictionary of extra keyword arguments (kwargs) to merge into the request body.
        """
        pass

    @abstractmethod
    async def teardown_cache(self, workflow_run_id: str) -> None:
        """Teardown any resources or session states associated with caching.

        Args:
            workflow_run_id: Identifies the active pipeline execution sequence.
        """
        pass

    @abstractmethod
    def calculate_cost(self, usage: TokenUsage, pricing_config: dict[str, Any]) -> TokenUsage:
        """Calculate the precise financial usage cost and ROI utilizing provider-specific pricing coefficients.

        Args:
            usage: Token count footprint statistics.
            pricing_config: Provider rate tables mapping models to pricing metrics.

        Returns:
            TokenUsage structure updated with monetary and evaluation values.
        """
        pass

    @abstractmethod
    def prepare_provider_kwargs(self, model_name: str) -> dict[str, Any]:
        """Prepare LLM provider specific static configuration arguments.

        Called unconditionally for every LLM request to inject required provider-specific
        flags (e.g. safety_settings, custom formats) that bypass the LiteLLM translation layer.

        Args:
            model_name: The actual deployment model identifier.

        Returns:
            A dictionary containing provider-specific keyword arguments.
        """
        pass

    def sanitize_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Sanitize message array to prevent provider-specific API crashes.

        Defaults to returning the messages unmodified. Can be overridden by
        specific adapters to handle provider quirks (like orphaned tool messages).

        Args:
            messages: A list of message dictionaries.

        Returns:
            A sanitized list of message dictionaries.
        """
        return messages

    def prepare_kwargs(
        self, call_kwargs: dict[str, Any], config: Any | None = None, settings: Any | None = None
    ) -> dict[str, Any]:
        """Optional: Modifies parameters passed to LiteLLM (e.g. provider specific mappings).

        Args:
            call_kwargs: The dictionary of arguments to pass to litellm.
            config: Optional config object for the provider.
            settings: Optional app settings.

        Returns:
            The potentially modified call_kwargs dictionary.
        """
        return call_kwargs

    def build_http_client(self, timeout: float) -> Any | None:
        """Optional: Build a provider-specific HTTP client wrapper.

        Args:
            timeout: The requested timeout in seconds.

        Returns:
            A custom HTTP client or None to use default.
        """
        return None

    @abstractmethod
    def prepare_structured_output(self, response_model: type[BaseModel]) -> dict[str, Any] | type[BaseModel]:
        """Convert a Pydantic model into a provider-specific structured output schema format.

        Args:
            response_model: The Pydantic model defining the expected JSON structure.

        Returns:
            A dictionary matching the provider's native schema format, or the Pydantic type itself.
        """
        pass

    def _strip_unsupported_constraints(self, schema_dict: Any) -> None:
        """Strip unsupported JSON schema constraints (e.g. minLength, maxLength) for strict mode.

        Args:
            schema_dict: The JSON schema dictionary to mutate in place.
        """
        if isinstance(schema_dict, dict):
            # [2026-07-03] Targeted Schema Stripping:
            # We MUST strip mechanical constraints that cause Vertex's Guided Decoding state machine to explode
            # ("too many states for serving"). These include lengths, regexes, and bounds.
            # We MUST NOT strip semantic fields ("title", "description", "enum") because the LLM relies on them to prevent hallucinations.
            keys_to_strip: list[str] = [
                "maxLength",
                "minLength",
                "pattern",
                "format",
                "maximum",
                "minimum",
                "exclusiveMaximum",
                "exclusiveMinimum",
                "multipleOf",
            ]
            for k in keys_to_strip:
                schema_dict.pop(k, None)

            if "const" in schema_dict:
                schema_dict["enum"] = [schema_dict.pop("const")]

            # Remove contextual constraints not supported by standard strict schemas
            if "properties" in schema_dict:
                schema_dict["properties"].pop("contextual_override", None)
                schema_dict["properties"].pop("override_reason", None)
            if "required" in schema_dict and isinstance(schema_dict["required"], list):
                if "contextual_override" in schema_dict["required"]:
                    schema_dict["required"].remove("contextual_override")
                if "override_reason" in schema_dict["required"]:
                    schema_dict["required"].remove("override_reason")

            for v in list(schema_dict.values()):
                self._strip_unsupported_constraints(v)
        elif isinstance(schema_dict, list):
            for item in schema_dict:
                self._strip_unsupported_constraints(item)
