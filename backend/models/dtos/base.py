from pydantic import BaseModel, ConfigDict

class BaseDTO(BaseModel):
    """Base class for all Data Transfer Objects."""
    model_config = ConfigDict(frozen=True, populate_by_name=True)
