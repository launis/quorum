"""System Settings Models."""

from pydantic import BaseModel, ConfigDict, Field


class SystemSettings(BaseModel):
    """Global System Configuration.

    Persisted as a singleton in the 'system_settings' table.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "maintenance_mode": False,
                "allow_signups": True,
                "global_banner": "Scheduled maintenance at 02:00 UTC",
                "default_model_strategy": "fast",
            }
        }
    )

    maintenance_mode: bool = Field(default=False, description="If True, only ROOT can login/act.")
    allow_signups: bool = Field(default=True, description="If True, new users can register.")
    global_banner: str | None = Field(default=None, description="Message displayed to all users.")
    default_model_strategy: str = Field(default="fast", description="Default LLM strategy for new agents.")

    # Feature Flags
    enable_beta_features: bool = Field(default=False, description="Toggle experimental features.")


class ModelSettings(BaseModel):
    """Configuration settings for a specific model strategy."""

    model_name: str = Field(description="The concrete model identifier (e.g. 'gemini-1.5-pro').")
    temperature: float | None = Field(default=None, description="Sampling temperature.")
    max_tokens: int | None = Field(default=None, description="Maximum output token limit.")
    top_p: float | None = Field(default=None, description="Nucleus sampling parameter.")


class GlobalModelConfig(BaseModel):
    """Global configuration for model strategies."""

    registry: dict[str, dict[str, ModelSettings]] = Field(
        description="Nested map: Provider -> Strategy -> Settings."
    )
