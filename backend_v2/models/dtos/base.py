from __future__ import annotations

"""Base Data Transfer Objects for Cognitive Quorum V2.

Provides standard configurations and base models for request and response validation
across dynamic presentation and communication interfaces.
"""

from typing import Annotated, Literal

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase

__all__ = [
    "BaseDTO",
    "BaseResponseDTO",
    "DataStarvationEvent",
    "GenericStatusResponseDTO",
]


class BaseDTO(V2CoreBase):
    """Base class for all Data Transfer Objects (DTOs) in the system.

    Provides a standardized baseline with name population enablement for integration
    with varied serialization contexts.
    """

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="forbid")


class BaseResponseDTO(V2CoreBase):
    """Base class for all API response schemas.

    Ensures strict Data Sovereignty and prevents cross-tenant data leaks
    by globally excluding tenant scoping variables such as organization_id from client responses.

    Attributes:
        organization_id: Organization reference identifier excluded from client serialization.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    organization_id: Annotated[str | None, Field(exclude=True)] = None


class GenericStatusResponseDTO(BaseResponseDTO):
    """Standard operation status response payload.

    Attributes:
        status: Operation outcome status indicator.
        message: Human-readable operational outcome message.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    status: Annotated[str, Field(default="ok", description="Operation status indicator")] = "ok"
    message: Annotated[str, Field(description="Operational outcome message")]



class DataStarvationEvent(BaseDTO):
    """Strict domain event emitted when SynthesisEngine aborts due to atom starvation."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    event_type: Annotated[Literal["starvation"], Field(default="starvation", description="Event discriminator")] = (
        "starvation"
    )
    total_atoms: Annotated[int, Field(ge=0, description="Total raw atoms extracted before synthesis")]
    reason: Annotated[
        str, Field(default="Data starvation: insufficient atoms", description="Reason for short-circuit")
    ] = "Data starvation: insufficient atoms"
