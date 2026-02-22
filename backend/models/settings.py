from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    @field_validator("default_model_strategy")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("global_banner")
    @classmethod
    def validate_non_empty_optional(cls, v: str | None) -> str | None:
        if v is not None and (not v or not v.strip()):
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip() if v else v


class ModelSettings(BaseModel):
    """Configuration settings for a specific model strategy."""

    model_name: str = Field(description="The concrete model identifier (e.g. 'gemini-1.5-pro').")
    temperature: float | None = Field(default=None, description="Sampling temperature.")
    max_tokens: int | None = Field(default=None, description="Maximum output token limit.")
    top_p: float | None = Field(default=None, description="Nucleus sampling parameter.")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("model_name")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("temperature", "top_p")
    @classmethod
    def validate_non_negative_optional(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("Value cannot be negative.")
        return v

    @field_validator("max_tokens")
    @classmethod
    def validate_positive_int_optional(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("Max tokens must be positive.")
        return v


class GlobalModelConfig(BaseModel):
    """Global configuration for model strategies."""

    registry: dict[str, dict[str, ModelSettings]] = Field(description="Nested map: Provider -> Strategy -> Settings.")
    model_config = ConfigDict(frozen=True, strict=True)
