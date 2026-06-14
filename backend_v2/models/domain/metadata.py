"""Domain models for Metadata hook."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes


class MetadataHookPayloadDTO(BaseModel):
    """Payload to extract initiator safely."""

    model_config = ConfigDict(strict=True, frozen=True, extra="ignore")

    sys_initiator_id: str = Field(default="system", min_length=1, alias="_sys_initiator_id")


class StepMetadataDTO(BaseModel):
    """Strictly typed execution metadata."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    execution_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    step_id: str = Field(min_length=1)
    initiator_id: str = Field(min_length=1)
    timestamp_isot: str = Field(min_length=1)
    unix_time: int = Field(description="Unix timestamp")
    v2_engine: bool = Field(default=True)

    @field_validator("unix_time")
    @classmethod
    def validate_unix_time(cls, v: int) -> int:
        """Validate unix_time >= 0."""
        if v < 0:
            raise AppException(
                message=f"unix_time must be >= 0, got {v}", details={"error_code": ErrorCodes.VALIDATION_FAILED}
            )
        return v


class MetadataHookResultDTO(BaseModel):
    """Result payload for metadata hook."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    step_metadata: StepMetadataDTO
