"""Domain model for workflow inputs (Payloads)."""

from __future__ import annotations

import logging
from typing import Annotated, Any, Self

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

    @model_validator(mode="after")
    def prevent_base64_pollution(self) -> Self:
        """Fail-Fast filter: BANS content_base64 to protect against massive DB memory blobs.

        Returns:
            The validated WorkflowInputs instance if no base64 payloads are found.

        Raises:
            AppException: If base64 content is detected (VALIDATION_FAILED).
        """
        if self.dynamic_inputs:
            for k, v in self.dynamic_inputs.items():
                has_b64 = isinstance(v, Base64Attachment)
                if not has_b64:
                    try:
                        has_b64 = "content_base64" in v
                    except TypeError:
                        has_b64 = False
                if has_b64:
                    msg = (
                        f"V2 Strict Mandate: Binary 'content_base64' payload detected in dynamic_inputs '{k}'. "
                        "All Base64 extraction MUST occur synchronously at the API Router level "
                        "before reaching the Domain models. Do not serialize PDFs into the DB!"
                    )
                    logger.error("[WorkflowInputs] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return self
