"""Domain model for workflow inputs (Payloads)."""

import logging
from typing import Any

from pydantic import Field, model_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import V2CoreBase

logger = logging.getLogger(__name__)


class Base64Attachment(V2CoreBase):
    """Strict DTO for handling binary base64 file uploads."""

    filename: str = Field(..., description="The name of the uploaded file")
    content_base64: str = Field(..., description="The base64 encoded binary content")
    content_type: str | None = Field(default=None, description="Optional MIME type")


class WorkflowInputsIngress(V2CoreBase):
    """API Ingress payload for the workflow (Content).
    
    Allows Base64 attachments during initial API routing, before Eager Extraction happens.
    """

    organization_id: str | None = Field(default=None, description="Tenant ID for multi-tenancy.", min_length=1)
    user_id: str | None = Field(default=None, description="User ID for audit trails.", min_length=1)
    simulation_mode: bool = Field(default=False, description="If True, indicates a test/simulation run.")
    language: str = Field(default="en", description="Target language code (e.g., 'en', 'fi').", min_length=1)

    dynamic_inputs: dict[str, Any] = Field(
        default_factory=dict, description="Structured dictionary for dynamic workflow inputs."
    )


class WorkflowInputs(WorkflowInputsIngress):
    """Strict Domain payload for the workflow (Content).

    This model defines the DATA content that the workflow processes.
    It rigorously BANS base64 payloads to protect the DB.
    """

    @model_validator(mode="before")
    @classmethod
    def prevent_base64_pollution(cls, data: Any) -> Any:
        """Fail-Fast filter: BANS content_base64 to protect against massive DB memory blobs."""
        if not isinstance(data, dict):
            return data

        for k, v in data.items():
            if isinstance(v, dict) and "content_base64" in v:
                msg = (
                    f"V2 Strict Mandate: Binary 'content_base64' payload detected in input '{k}'. "
                    "All Base64 extraction MUST occur synchronously at the API Router level "
                    "before reaching the Domain models. Do not serialize PDFs into the DB!"
                )
                logger.error("[WorkflowInputs] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise ValueError(msg)

            # Recursively check dynamic_inputs if present
            if k == "dynamic_inputs" and isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    if isinstance(sub_v, dict) and "content_base64" in sub_v:
                        msg = (
                            f"V2 Strict Mandate: Binary 'content_base64' payload detected in dynamic_inputs '{sub_k}'. "
                            "All Base64 extraction MUST occur synchronously at the API Router level "
                            "before reaching the Domain models. Do not serialize PDFs into the DB!"
                        )
                        logger.error("[WorkflowInputs] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                        raise ValueError(msg)
        return data
