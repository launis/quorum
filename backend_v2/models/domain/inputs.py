"""Domain model for workflow inputs (Payloads)."""

from __future__ import annotations

import logging
from typing import Annotated, Any

from pydantic import ConfigDict, Field, model_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase

logger = logging.getLogger(__name__)


class Base64Attachment(V2CoreBase):
    """Strict DTO for handling binary base64 file uploads.

    Attributes:
        filename: The name of the uploaded file.
        content_base64: The base64 encoded binary content.
        content_type: Optional MIME type.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    filename: Annotated[str, Field(description="The name of the uploaded file")]
    content_base64: Annotated[str, Field(description="The base64 encoded binary content")]
    content_type: Annotated[str | None, Field(description="Optional MIME type")] = None


class WorkflowInputsIngress(V2CoreBase):
    """API Ingress payload for the workflow (Content).

    Allows Base64 attachments during initial API routing, before Eager Extraction happens.

    Attributes:
        organization_id: Tenant ID for multi-tenancy.
        user_id: User ID for audit trails.
        simulation_mode: If True, indicates a test/simulation run.
        language: Target language code.
        dynamic_inputs: Structured dictionary for dynamic workflow inputs.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    organization_id: Annotated[str | None, Field(min_length=1, description="Tenant ID for multi-tenancy.")] = None
    user_id: Annotated[str | None, Field(min_length=1, description="User ID for audit trails.")] = None
    simulation_mode: Annotated[bool, Field(description="If True, indicates a test/simulation run.")] = False
    language: Annotated[str, Field(min_length=1, description="Target language code (e.g., 'en', 'fi').")] = "en"

    dynamic_inputs: Annotated[
        dict[str, Any], Field(description="Structured dictionary for dynamic workflow inputs.")
    ] = Field(default_factory=dict)


class WorkflowInputs(WorkflowInputsIngress):
    """Strict Domain payload for the workflow (Content).

    This model defines the DATA content that the workflow processes.
    It rigorously BANS base64 payloads to protect the DB.
    """

    @model_validator(mode="before")
    @classmethod
    def prevent_base64_pollution(cls, data: Any) -> Any:
        """Fail-Fast filter: BANS content_base64 to protect against massive DB memory blobs.

        Args:
            data: The unvalidated data dictionary.

        Returns:
            The safe data dictionary if no base64 payloads are found.

        Raises:
            AppException: If base64 content is detected (VALIDATION_FAILED).
        """
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
                raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})

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
                        raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return data
