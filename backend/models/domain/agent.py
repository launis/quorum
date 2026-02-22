"""Agent Domain Models.

This module defines strict Pydantic models for Agent configuration and strategy resolution.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ModelConfig(BaseModel):
    """Strict model for LLM Model Configuration."""

    model_name: str = Field(..., description="Concrete model name (e.g. 'vertex_ai/gemini-1.5-pro').")
    provider: str = Field(..., description="Provider identifier (e.g. 'vertex_ai', 'openai').")

    # Optional parameters often found in strategy definitions
    max_tokens: int | None = Field(default=None, description="Maximum output tokens.")
    temperature: float | None = Field(default=None, description="Sampling temperature.")
    top_p: float | None = Field(default=None, description="Nucleus sampling probability.")
    supports_grounding: bool = Field(
        default=False, description="Whether this model strategy supports grounding (Google Search)."
    )
    is_active: bool = Field(..., description="Whether this model configuration is active.")
    tpm_limit: int = Field(..., description="Tokens Per Minute Limit (0 = Unlimited/Default).")
    rpm_limit: int = Field(..., description="Requests Per Minute Limit (0 = Unlimited/Default).")
    api_key: str | None = Field(default=None, description="API Key (optional/resolved).")

    # Additional provider-specific settings
    extra_params: dict[str, Any] = Field(default_factory=dict, description="Provider specific parameters.")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("model_name", "provider")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("temperature", "top_p")
    @classmethod
    def validate_probability(cls, v: float | None) -> float | None:
        if v is not None and not (0.0 <= v <= 2.0):  # Temperature can be > 1
            # Just basic sanity check
            pass
        return v
