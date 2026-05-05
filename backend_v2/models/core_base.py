from pydantic import BaseModel, ConfigDict


class V2CoreBase(BaseModel):
    """Base model enforcing Pydantic strict mode across all V2 schemas."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
