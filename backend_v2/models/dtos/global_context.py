"""Global Context Variables DTO.

Strongly typed container for global context variables across hook pipelines,
eliminating loose dictionaries and permissive typing.
"""

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.hydration import HydrationInputSourceDTO
from backend_v2.models.domain.linguistics import LinguisticsResultDTO

__all__ = ["GlobalContextVarsDTO"]


class GlobalContextVarsDTO(V2CoreBase):
    """Strictly typed global context variables container."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    language: str | None = None
    target_locale: str | None = None
    system_locale: str | None = None
    profile_id: str | None = None
    organization_id: str | None = None
    initiator_id: Annotated[str | None, Field(default=None, alias="_sys_initiator_id")] = None
    step_coach: Annotated[dict[str, str | int | float | bool | list[str]] | None, Field(default=None)] = None
    knowledge_base: Annotated[dict[str, str | int | float | bool | list[str]] | None, Field(default=None)] = None
    hydration_results: Annotated[HydrationInputSourceDTO | None, Field(default=None)] = None
    step_linguistics: Annotated[LinguisticsResultDTO | None, Field(default=None)] = None
    external_evidence: Annotated[str | None, Field(default=None)] = None
