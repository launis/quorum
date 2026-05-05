from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase


class BaseDTO(V2CoreBase):
    """Base class for all Data Transfer Objects."""

    model_config = ConfigDict(populate_by_name=True)


class BaseResponseDTO(V2CoreBase):
    """Base class for all API responses to ensure Data Sovereignty and prevent Cross-Tenant leaks."""

    organization_id: str | None = Field(default=None, exclude=True)
