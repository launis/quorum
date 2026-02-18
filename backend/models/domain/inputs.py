"""Domain model for workflow inputs (Payloads)."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class WorkflowInputs(BaseModel):
    """Strict input payload for the workflow (Content).
    
    This model defines the DATA content that the workflow processes.
    It does NOT include configuration (model parameters, API keys), which belong in StepConfig.
    """
    
    # Primary Content (Raw Material for LLM)
    history_text: Optional[str] = Field(default=None, description="The raw conversation history to analyze.")
    product_text: Optional[str] = Field(default=None, description="Context about the product or service.")
    reflection_text: Optional[str] = Field(default=None, description="User's reflection or self-assessment.")
    
    # Metadata / Context
    organization_id: Optional[str] = Field(default=None, description="Tenant ID for multi-tenancy.")
    user_id: Optional[str] = Field(default=None, description="User ID for audit trails.")
    simulation_mode: bool = Field(default=False, description="If True, indicates a test/simulation run.")
    language: str = Field(default="en", description="Target language code (e.g., 'en', 'fi').")

    # Config: Allow new fields for forward compatibility, but keep core fields strict.
    # frozen=True ensures immutability once created.
    model_config = ConfigDict(extra="ignore", frozen=True)
