"""Core Base Models.

This module provides the foundational Pydantic models for the system.
"""

from pydantic import BaseModel, ConfigDict


class V2CoreBase(BaseModel):
    """Base model enforcing Pydantic strict mode across all V2 schemas.

    This model serves as the foundational class for all V2 DTOs and models,
    guaranteeing strict validation, forbidding extra fields, and enforcing
    immutability.

    Attributes:
        model_config (ConfigDict): Pydantic configuration dictionary.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
