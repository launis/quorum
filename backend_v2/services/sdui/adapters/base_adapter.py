"""Base adapter protocol and shared context DTO for SDUI presentation adapters."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict

from backend_v2.models.v2_core import ExecutionRecord, MCPAuditTrace, OutputProfile, RenderedSynthesisCache
from backend_v2.models.view.sdui import AnySduiBlock


class AdapterContext(BaseModel):
    """Immutable data envelope for all SDUI adapters.

    Constructed once by the BlueprintTransformer orchestrator before
    the dispatch loop. Passed identically to every adapter.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    execution: ExecutionRecord | None
    locale: str
    penalties_applied: list[str]
    mcp_audit_map: dict[str, MCPAuditTrace] | None
    global_score: float | None
    profile: OutputProfile
    profile_cache: RenderedSynthesisCache | None


class SduiAdapterProtocol(Protocol):
    """Protocol for all SDUI presentation adapters.

    Every concrete adapter MUST implement this interface with a single
    static build() method. The locked terminology (build, context,
    AdapterContext) is enforced by the KI sdui_adapter_decomposition.
    """

    @staticmethod
    def build(context: AdapterContext) -> list[AnySduiBlock]:
        """Build SDUI blocks from the adapter context.

        Args:
            context: Frozen, immutable adapter context.

        Returns:
            Ordered list of polymorphic SDUI blocks.
        """
        ...
