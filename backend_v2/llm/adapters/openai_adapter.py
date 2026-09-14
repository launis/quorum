"""OpenAI cache adapter with automatic prefix caching payload preparation and FinOps cost calculation."""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel

from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.v2_core import ModelProfile

logger = logging.getLogger(__name__)


class OpenAICacheAdapter(BaseLLMAdapter):
    """Caching and pricing adapter for OpenAI models."""

    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> tuple[list[LLMMessageDTO] | list[dict[str, Any]], dict[str, Any]]:
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
        """No-Op teardown for OpenAI.

        Args:
            workflow_run_id: The execution tracking workflow identifier.
        """
        pass

    def calculate_cost(self, usage: TokenUsage, pricing_config: PricingConfig) -> TokenUsage:
        """Calculate the precise OpenAI cost and savings.

        Formula:
            Cost = (regular_input_tokens * P_in) + (cached_tokens * P_in * discount_factor) + (output_tokens * P_out)
            Savings = cached_tokens * P_in * savings_factor

        Args:
            usage: The source TokenUsage object.
            pricing_config: Provider pricing parameters.

        Returns:
            An instance of TokenUsage with calculated values.
        """
        p_in = pricing_config.input_token_price
        p_out = pricing_config.output_token_price

        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        cached_tokens = usage.cached_tokens
        reasoning_tokens = usage.reasoning_tokens

        # OpenAI has fixed 50% read discount and 50% savings factor
        discount_factor = 0.50
        savings_factor = 0.50

        regular_input = max(0, prompt_tokens - cached_tokens)

        # Compute cost and savings
        cost_regular = regular_input * p_in
        cost_cached = cached_tokens * p_in * discount_factor
        cost_output = completion_tokens * p_out

        cost_usd = cost_regular + cost_cached + cost_output
        estimated_savings_usd = cached_tokens * p_in * savings_factor
        total_tokens = usage.total_tokens

        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=reasoning_tokens,
            cost_usd=cost_usd,
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
        """Prepare OpenAI specific kwargs, translating reasoning effort and stripping unsupported sampling params.

        Args:
            call_kwargs: The dictionary of arguments to pass to litellm.
            config: Optional config object for the provider.
            settings: Optional app settings.

        Returns:
            The potentially modified call_kwargs dictionary.
        """
        resolved_model: str = ""
        if "model" in call_kwargs and call_kwargs["model"]:
            resolved_model = str(call_kwargs["model"])
        elif isinstance(config, ModelProfile):
            resolved_model = config.model_name
        model_name = resolved_model.lower()

        # Epistemic SSOT: Query authoritative LiteLLM registry dynamically instead of hardcoded prefix guessing
        is_reasoning_model = False
        try:
            import litellm

            clean_model = model_name.removeprefix("openai/")
            info = litellm.get_model_info(clean_model)
            raw_params = info.get("supported_openai_params")
            supported_params: list[str] = []
            if isinstance(raw_params, list):
                supported_params = raw_params
            if info.get("supports_reasoning") or "reasoning_effort" in supported_params:
                is_reasoning_model = True
        except Exception:  # noqa: QGR003 [REASON: Non-fatal fallback to prefix heuristic for local or unmapped models]
            # Fallback for local, mock, unmapped, or cutting-edge unindexed models
            is_reasoning_model = any(prefix in model_name for prefix in ("o1", "o3", "o4", "o5", "gpt-5"))

        thinking_budget: int | None = None
        if isinstance(config, ModelProfile) and config.thinking_budget_tokens is not None:
            thinking_budget = int(config.thinking_budget_tokens)

        if is_reasoning_model:
            # Map thinking budget tokens to reasoning effort
            if thinking_budget is not None and thinking_budget > 0:
                if thinking_budget <= 2048:
                    call_kwargs["reasoning_effort"] = "low"
                elif thinking_budget <= 4096:
                    call_kwargs["reasoning_effort"] = "medium"
                else:
                    call_kwargs["reasoning_effort"] = "high"

            # Strip sampling parameters that OpenAI reasoning models reject (400 Bad Request)
            for param in ("temperature", "top_p", "frequency_penalty", "presence_penalty"):
                call_kwargs.pop(param, None)

        return call_kwargs

    def _enforce_openai_strict_schema(
        self,
        schema_dict: Any,
        known_discriminators: set[str] | None = None,
    ) -> None:
        """Enforce strict OpenAI JSON schema requirements across root and nested definitions.

        Args:
            schema_dict: The root or nested JSON schema dictionary to transform.
            known_discriminators: Optional set of discriminator property names.
        """
        if known_discriminators is None:
            known_discriminators = set()
            self._collect_discriminator_names(schema_dict, known_discriminators)

        self._strip_unsupported_constraints(schema_dict, known_discriminators=known_discriminators)
        self._apply_strict_schema_invariants(schema_dict)

    def _apply_strict_schema_invariants(self, node: Any) -> None:
        """Recursively enforce additionalProperties=False, saturated required lists, and strip defaults.

        Args:
            node: Node within the JSON schema graph to inspect and mutate in-place.
        """
        if isinstance(node, dict):  # noqa: QGR012 [REASON: Recursive raw JSON schema dictionary transformation for OpenAI strict API]
            node.pop("default", None)
            if node.get("type") == "object" or "properties" in node:
                node["additionalProperties"] = False
                if "properties" in node:
                    properties = node["properties"]
                    if isinstance(properties, dict):  # noqa: QGR012 [REASON: JSON schema properties dictionary inspection]
                        if "required" not in node or not isinstance(node["required"], list):
                            node["required"] = []
                        for prop_name in properties:
                            if prop_name not in node["required"]:
                                node["required"].append(prop_name)

            for v in list(node.values()):
                self._apply_strict_schema_invariants(v)
        elif isinstance(node, list):
            for item in node:
                self._apply_strict_schema_invariants(item)

    def prepare_structured_output(self, response_model: type[BaseModel]) -> dict[str, Any] | type[BaseModel]:
        """Convert a Pydantic model into OpenAI specific strict structured output format.

        OpenAI strict structured outputs (JSON Schema mode) require strict=True,
        additionalProperties=False, saturated required lists, and stripped constraints.

        Args:
            response_model: The Pydantic model defining the expected JSON structure.

        Returns:
            A dictionary matching LiteLLM's structured output format.
        """
        json_schema = response_model.model_json_schema()
        self._enforce_openai_strict_schema(json_schema)

        return {
            "type": "json_schema",
            "json_schema": {
                "name": response_model.__name__,
                "schema": json_schema,
                "strict": True,
            },
        }
