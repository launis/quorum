from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LLMResponse(BaseModel):
    """Standard response for LLM completion."""

    model_config = ConfigDict(strict=True)
    result: Any = Field(description="The generated text or structured object.")
    usage: Any | None = Field(None, description="Usage statistics if available.")


class BatchLLMResponse(BaseModel):
    """Response wrapper for batch completions."""

    model_config = ConfigDict(strict=True)
    results: list[dict[str, Any]] = Field(description="List of results (success or error) for each request.")


class ProviderListResponse(BaseModel):
    """Response for listing active providers."""

    model_config = ConfigDict(strict=True)
    strategies: dict[str, str] = Field(description="Map of strategy keys to model names.")
    api_keys_set: dict[str, bool] = Field(description="Status of API keys (mask/bool).")
    available_models: dict[str, list[str]] = Field(
        default_factory=dict, description="Map of provider to list of available model IDs."
    )


class ModelRegistryResponse(BaseModel):
    """Response for model registry configuration."""

    model_config = ConfigDict(strict=True)
    models: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="Nested map of provider -> strategy -> config."
    )


class ModelRegistryUpdateResponse(BaseModel):
    """Response for model registry update."""

    model_config = ConfigDict(strict=True)
    status: str
    registry: dict[str, dict[str, str]]
