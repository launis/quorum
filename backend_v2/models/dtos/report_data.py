"""Data Transfer Object for compiled report data.

SSOT for ReportDataDTO consumed by presentation adapters (SDUI, PDF, Excel).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from backend_v2.models.view.sdui import AnySduiBlock

from pydantic import ConfigDict, Field, model_validator

from backend_v2.models.core_base import I18nText, V2CoreBase
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.dtos.atom_result import (
    AtomResultDTO,
    ExecutionMetricsDTO,
    HydratedAtomDTO,
)

__all__ = ["ReportDataDTO"]


class ReportDataDTO(V2CoreBase):
    """Immutable data envelope containing evaluated results, metrics, and SDUI blocks for rendering."""

    model_config = ConfigDict(strict=True, extra="forbid")

    workflow_id: str
    execution_id: str = Field(description="The execution's opaque Stripe ID.")
    scoring_strategy: str | None = Field(
        default=None, description="The mathematical strategy used for scoring (e.g. WATERFALL)"
    )
    user_name: str | None = Field(default=None, description="Initiating user's name")
    scoring_engine_name: str | None = Field(default=None, description="Human readable name of the scoring engine")
    strictness_level: int | None = Field(default=None, description="Numeric strictness level (0-100)")
    local_time_str: str | None = Field(default=None, description="Localized time string from the client")
    custom_preface_md: str | None = Field(default=None, description="Custom user preface rendered as Markdown")
    profile_id: str
    profile_name: I18nText | None = Field(default=None)
    profile_description: I18nText | None = Field(
        default=None, description="Detailed profile context mapped from OutputProfile"
    )
    available_profiles: dict[str, I18nText] = Field(default_factory=dict)
    global_score: float | None = Field(
        default=None, description="The mathematical average extracted from the scoring_result hook."
    )
    has_warning: bool = Field(
        default=False, description="Flag indicating if the report generation had non-fatal warnings."
    )

    # Strict Topological DAG Execution Model fields
    global_metrics: ExecutionMetricsDTO | None = Field(default=None)
    inner_sdui_blocks: list[AnySduiBlock] = Field(
        default_factory=list, description="Stores the final structured SDUI blocks."
    )
    results: list[AtomResultDTO] = Field(
        default_factory=list,
        description=(
            "SDUI-RULE: Backend must return this list strictly topologically sorted. Frontend does not compute the DAG."
        ),
    )
    hydrated_references: dict[str, HydratedAtomDTO] = Field(
        default_factory=dict, description="O(1) Dictionary: tda_id -> Static text."
    )

    visible_metadata: list[str] = Field(
        default_factory=list, description="Fields visible on the UI and PDF cover header."
    )

    # Execution Diagnostic Metadata
    created_at: datetime | None = None
    org_name: str | None = None
    cost_estimate: float | None = None
    total_tokens: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    reasoning_tokens: int | None = None

    # MCP Tool Loop Audit Trail (XAI Evidence for Frontend)
    mcp_tool_audit: list[MCPAuditTrace] = Field(
        default_factory=list, description="Serialized MCPAuditTrace entries for XAI Evidence Box rendering."
    )

    @model_validator(mode="after")
    def enforce_referential_integrity(self) -> Self:
        """Ensure that every tda_id present exists in the hydrated_references dictionary."""
        ref_keys = set(self.hydrated_references.keys())

        # Declarative Set Logic
        used_ids = {res.tda_id for res in self.results}
        dep_ids = {dep for res in self.results for dep in res.depends_on_tda_ids}
        sc_ids = {sc for res in self.results for sc in res.short_circuit_reason_tda_ids}

        all_referenced_ids = used_ids | dep_ids | sc_ids
        missing_keys = all_referenced_ids - ref_keys

        if missing_keys:
            raise ValueError(f"Referential Integrity Error: Missing keys in hydrated_references: {missing_keys}")

        return self


from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.view.sdui import AnySduiBlock

ReportDataDTO.model_rebuild(
    _types_namespace={
        "AnySduiBlock": AnySduiBlock,
        "MatrixScorecardRowDTO": MatrixScorecardRowDTO,
        "MCPAuditTrace": MCPAuditTrace,
    }
)
