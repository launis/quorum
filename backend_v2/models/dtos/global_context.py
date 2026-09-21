"""Global Context Variables DTO.

Strongly typed container for global context variables across hook pipelines,
eliminating loose dictionaries and permissive typing.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.hydration import HydrationInputSourceDTO
from backend_v2.models.domain.linguistics import LinguisticsResultDTO

__all__ = ["GlobalContextVarsDTO"]


class GlobalContextVarsDTO(V2CoreBase):
    """Strictly typed global context variables container.

    Attributes:
        language: Target translation or execution language.
        target_locale: Client localized language code.
        system_locale: System runtime default locale.
        profile_id: Active output profile identifier.
        organization_id: Multi-tenant organization identifier.
        initiator_id: Execution initiator user identifier.
        step_coach: Coach stage execution telemetry payload.
        knowledge_base: Grounding knowledge context attributes.
        hydration_results: Upstream hydrated input source payloads.
        step_linguistics: Evaluated linguistic statistics and metrics.
        external_evidence: Aggregated external search evidence.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    language: Annotated[str | None, Field(default=None, description="Target translation or execution language.")] = None
    target_locale: Annotated[str | None, Field(default=None, description="Client localized language code.")] = None
    system_locale: Annotated[str | None, Field(default=None, description="System runtime default locale.")] = None
    profile_id: Annotated[str | None, Field(default=None, description="Active output profile identifier.")] = None
    organization_id: Annotated[str | None, Field(default=None, description="Multi-tenant organization identifier.")] = (
        None
    )
    initiator_id: Annotated[
        str | None,
        Field(default=None, alias="_sys_initiator_id", description="Execution initiator user identifier."),
    ] = None
    step_coach: Annotated[
        dict[str, str | int | float | bool | list[str]] | None,
        Field(default=None, description="Coach stage execution telemetry payload."),
    ] = None
    knowledge_base: Annotated[
        dict[str, str | int | float | bool | list[str]] | None,
        Field(default=None, description="Grounding knowledge context attributes."),
    ] = None
    hydration_results: Annotated[
        HydrationInputSourceDTO | None,
        Field(default=None, description="Upstream hydrated input source payloads."),
    ] = None
    step_linguistics: Annotated[
        LinguisticsResultDTO | None,
        Field(default=None, description="Evaluated linguistic statistics and metrics."),
    ] = None
    external_evidence: Annotated[
        str | None,
        Field(default=None, description="Aggregated external search evidence."),
    ] = None
