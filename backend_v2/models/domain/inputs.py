"""Domain model for workflow inputs (Payloads)."""

from typing import Any
import logging

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


class WorkflowInputs(BaseModel):
    """Strict input payload for the workflow (Content).

    This model defines the DATA content that the workflow processes.
    It does NOT include configuration (model parameters, API keys), which belong in StepConfig.
    """

    # Primary Content (Raw Material for LLM)
    # The 'chat_log' key is the definitive mandatory field for processing.
    # Optional inputs like 'product_text', 'reflection_text', and 'guided_reflection'
    # are dynamically accepted here based on Workflow.expected_inputs and extra="allow".
    chat_log: str | dict[str, Any] = Field(..., description="The definitive, mandatory chat log or Base64 payload to analyze.")
    organization_id: str | None = Field(default=None, description="Tenant ID for multi-tenancy.")
    user_id: str | None = Field(default=None, description="User ID for audit trails.")
    simulation_mode: bool = Field(default=False, description="If True, indicates a test/simulation run.")
    language: str = Field(default="en", description="Target language code (e.g., 'en', 'fi').")

    # Config: Allow new fields so dynamic inputs are retained.
    # frozen=True ensures immutability once created.
    model_config = ConfigDict(extra="allow", frozen=True)


