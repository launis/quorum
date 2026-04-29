"""Domain model for workflow inputs (Payloads)."""

import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

logger = logging.getLogger(__name__)

class Base64Attachment(BaseModel):
    """Strict DTO for handling binary base64 file uploads."""
    filename: str = Field(..., description="The name of the uploaded file")
    content_base64: str = Field(..., description="The base64 encoded binary content")
    content_type: str | None = Field(default=None, description="Optional MIME type")

    model_config = ConfigDict(frozen=True, extra="ignore")



class WorkflowInputs(BaseModel):
    """Strict input payload for the workflow (Content).

    This model defines the DATA content that the workflow processes.
    It does NOT include configuration (model parameters, API keys), which belong in StepConfig.
    """

    # Primary Content (Raw Material for LLM)
    # Optional inputs like 'product_text', 'reflection_text', and 'guided_reflection'
    # are dynamically accepted here based on Workflow.expected_inputs and extra="allow".
    chat_log: str | dict[str, Any] | None = Field(
        default=None, description="Optional legacy chat log or Base64 payload."
    )
    organization_id: str | None = Field(default=None, description="Tenant ID for multi-tenancy.")
    user_id: str | None = Field(default=None, description="User ID for audit trails.")
    simulation_mode: bool = Field(default=False, description="If True, indicates a test/simulation run.")
    language: str = Field(default="en", description="Target language code (e.g., 'en', 'fi').")

    # Config: Allow new fields so dynamic inputs are retained.
    # frozen=True ensures immutability once created.
    model_config = ConfigDict(extra="allow", frozen=True)

    @field_validator("chat_log", "organization_id", "user_id", "language", mode="before")
    @classmethod
    def validate_non_empty_strings(cls, v: Any) -> Any:
        if v is None:
            return v
        if isinstance(v, str) and not v.strip():
            from backend_v2.exceptions import AppException, ErrorCodes

            msg = "Workflow input field cannot be an empty string. Zero-Compromise Fail-Fast enforced."
            logger.error("[WorkflowInputs] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return v

    @model_validator(mode="before")
    @classmethod
    def prevent_base64_pollution(cls, data: Any) -> Any:
        """Fail-Fast filter: BANS content_base64 to protect against massive DB memory blobs."""
        if not isinstance(data, dict):
            return data

        for k, v in data.items():
            if isinstance(v, dict) and "content_base64" in v:
                from backend_v2.exceptions import AppException, ErrorCodes

                msg = (
                    f"V2 Strict Mandate: Binary 'content_base64' payload detected in input '{k}'. "
                    "All Base64 extraction MUST occur synchronously at the API Router level "
                    "before reaching the Domain models. Do not serialize PDFs into the DB!"
                )
                logger.error("[WorkflowInputs] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                )
        return data
