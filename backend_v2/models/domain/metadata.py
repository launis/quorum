"""Domain models for Metadata hook."""

from pydantic import BaseModel, ConfigDict, Field


class MetadataHookPayloadDTO(BaseModel):
    """Payload to extract initiator safely."""

    model_config = ConfigDict(strict=True, extra="ignore")

    sys_initiator_id: str = Field(default="system", alias="_sys_initiator_id")


class StepMetadataDTO(BaseModel):
    """Strictly typed execution metadata."""

    model_config = ConfigDict(strict=True, extra="forbid")

    execution_id: str
    workflow_id: str
    step_id: str
    initiator_id: str
    timestamp_isot: str
    unix_time: int
    v2_engine: bool = True


class MetadataHookResultDTO(BaseModel):
    """Result payload for metadata hook."""

    model_config = ConfigDict(strict=True, extra="forbid")

    step_metadata: StepMetadataDTO
