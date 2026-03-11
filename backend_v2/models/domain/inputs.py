"""Domain model for workflow inputs (Payloads)."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WorkflowInputs(BaseModel):
    """Strict input payload for the workflow (Content).

    This model defines the DATA content that the workflow processes.
    It does NOT include configuration (model parameters, API keys), which belong in StepConfig.
    """

    # Primary Content (Raw Material for LLM)
    history_text: str | dict[str, Any] | None = Field(
        default=None, description="The raw conversation history or Base64 payload to analyze."
    )
    product_text: str | dict[str, Any] | None = Field(
        default=None, description="Context about the product or service or Base64 payload."
    )
    reflection_text: str | dict[str, Any] | None = Field(
        default=None, description="User's reflection or Base64 payload."
    )
    guided_reflection: dict[str, Any] | None = Field(default=None, description="Guided reflection raw data.")

    # Metadata / Context
    organization_id: str | None = Field(default=None, description="Tenant ID for multi-tenancy.")
    user_id: str | None = Field(default=None, description="User ID for audit trails.")
    simulation_mode: bool = Field(default=False, description="If True, indicates a test/simulation run.")
    language: str = Field(default="en", description="Target language code (e.g., 'en', 'fi').")

    # Config: Allow new fields so dynamic inputs are retained.
    # frozen=True ensures immutability once created.
    model_config = ConfigDict(extra="allow", frozen=True)

    @model_validator(mode="after")
    def validate_distinct_inputs(self) -> WorkflowInputs:
        """Fail fast if history_text, product_text or reflection_text are identical."""
        texts = {}
        if self.history_text and isinstance(self.history_text, str) and self.history_text.strip():
            texts["history_text"] = self.history_text.strip()

        if self.product_text and isinstance(self.product_text, str) and self.product_text.strip():
            product_val = self.product_text.strip()
            for key, val in texts.items():
                if product_val == val:
                    # Raise ValueError so Pydantic Validator catches it, which is then mapped
                    # by the FastAPI/Engine layer to AppException / VALIDATION_FAILED.
                    raise ValueError(f"product_text cannot be identical to {key}. Unique inputs are required.")
            texts["product_text"] = product_val

        if self.reflection_text and isinstance(self.reflection_text, str) and self.reflection_text.strip():
            reflection_val = self.reflection_text.strip()
            for key, val in texts.items():
                if reflection_val == val:
                    raise ValueError(f"reflection_text cannot be identical to {key}. Unique inputs are required.")

        return self
