"""Domain models for Metadata hook."""

import logging
from typing import Annotated

from pydantic import ConfigDict, Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.usage import TokenUsage

logger = logging.getLogger(__name__)


class MetadataHookPayloadDTO(V2CoreBase):
    """Payload to extract initiator safely.

    Attributes:
        sys_initiator_id: System initiator ID.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    sys_initiator_id: Annotated[str, Field(min_length=1, alias="_sys_initiator_id")] = "system"
    organization_id: Annotated[str | None, Field(default=None)] = None
    user_id: Annotated[str | None, Field(default=None)] = None
    simulation_mode: Annotated[bool, Field(default=False)] = False
    language: Annotated[str, Field(default="en")] = "en"


class StepMetadataDTO(V2CoreBase):
    """Strictly typed execution metadata.

    Attributes:
        execution_id: Execution ID.
        workflow_id: Workflow ID.
        step_id: Step ID.
        initiator_id: Initiator ID.
        timestamp_isot: Timestamp in ISO format.
        unix_time: Unix timestamp.
        v2_engine: Engine flag.
        task_blueprint: Optional task blueprint ID.
        model_strategy: Optional strategy name.
        cognitive_tier: Optional cognitive tier name.
        physical_model: Optional physical model name.
        token_usage: Optional TokenUsage model.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    execution_id: Annotated[str, Field(min_length=1)]
    workflow_id: Annotated[str, Field(min_length=1)]
    step_id: Annotated[str, Field(min_length=1)]
    initiator_id: Annotated[str, Field(min_length=1)]
    timestamp_isot: Annotated[str, Field(min_length=1)]
    unix_time: Annotated[int, Field(description="Unix timestamp")]
    v2_engine: bool = True
    task_blueprint: Annotated[str | None, Field(default=None)] = None
    model_strategy: Annotated[str | None, Field(default=None)] = None
    cognitive_tier: Annotated[str | None, Field(default=None)] = None
    physical_model: Annotated[str | None, Field(default=None)] = None
    token_usage: Annotated[TokenUsage | None, Field(default=None)] = None

    @field_validator("unix_time")
    @classmethod
    def validate_unix_time(cls, v: int) -> int:
        """Validate unix_time >= 0.

        Args:
            v: Unix time.

        Returns:
            The validated Unix time.

        Raises:
            AppException: If unix_time is less than 0.
        """
        if v < 0:
            msg = f"unix_time must be >= 0, got {v}"
            logger.error("[MetadataModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v


class MetadataHookResultDTO(V2CoreBase):
    """Result payload for metadata hook.

    Attributes:
        step_metadata: The metadata DTO.
        audit_signature: Deterministic audit signature.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid", populate_by_name=True)

    step_metadata: StepMetadataDTO
    audit_signature: Annotated[str, Field(default="", alias="_audit_signature")] = ""
