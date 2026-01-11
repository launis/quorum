"""System Settings Models."""
from pydantic import BaseModel, Field


class SystemSettings(BaseModel):
    """Global System Configuration.

    Persisted as a singleton in the 'system_settings' table.
    """

    maintenance_mode: bool = Field(default=False, description="If True, only ROOT can login/act.")
    allow_signups: bool = Field(default=True, description="If True, new users can register.")
    global_banner: str | None = Field(default=None, description="Message displayed to all users.")
    default_model_strategy: str = Field(default="fast", description="Default LLM strategy for new agents.")

    # Feature Flags
    enable_beta_features: bool = Field(default=False, description="Toggle experimental features.")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "maintenance_mode": False,
                "allow_signups": True,
                "global_banner": "Scheduled maintenance at 02:00 UTC",
                "default_model_strategy": "fast",
            }
        }
