"""Data Transfer Object for compiled report data.

SSOT for ReportDataDTO consumed by presentation adapters (SDUI, PDF, Excel).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Self

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
    """Immutable data envelope containing evaluated results, metrics, and SDUI blocks for rendering.

    Attributes:
        workflow_id: The workflow's opaque Stripe ID.
        execution_id: The execution's opaque Stripe ID.
        scoring_strategy: The mathematical strategy used for scoring (e.g. WATERFALL).
        user_name: Initiating user's name.
        scoring_engine_name: Human readable name of the scoring engine.
        strictness_level: Numeric strictness level (0-100).
        local_time_str: Localized time string from the client.
        custom_preface_md: Custom user preface rendered as Markdown.
        profile_id: The output profile's opaque Stripe ID.
        profile_name: Localized name of the output profile.
        profile_description: Detailed profile context mapped from OutputProfile.
        available_profiles: Mapping of profile IDs to localized names.
        global_score: The mathematical average extracted from the scoring_result hook.
        has_warning: Flag indicating if the report generation had non-fatal warnings.
        global_metrics: Aggregate atom-level metrics for DAG execution.
        inner_sdui_blocks: Final structured SDUI blocks for presentation.
        results: Topologically sorted list of atom evaluation results.
        hydrated_references: O(1) dictionary mapping tda_id to static HydratedAtomDTO text.
        visible_metadata: Fields visible on the UI and PDF cover header.
        created_at: Execution creation timestamp.
        org_name: Organization display name.
        cost_estimate: Estimated financial cost of the execution.
        total_tokens: Total token count consumed across the execution.
        prompt_tokens: Prompt token count consumed.
        completion_tokens: Completion token count consumed.
        reasoning_tokens: Reasoning token count consumed.
        mcp_tool_audit: Serialized MCPAuditTrace entries for XAI Evidence Box rendering.
        short_circuited_by_claims: Human-readable prerequisite claims that short-circuited downstream evaluations.
        falsified_warrant_claims: Formatted Toulmin rebuttal-warrant-claim falsification lineage entries.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    workflow_id: Annotated[str, Field(description="The workflow's opaque Stripe ID.")]
    execution_id: Annotated[str, Field(description="The execution's opaque Stripe ID.")]
    scoring_strategy: Annotated[
        str | None,
        Field(default=None, description="The mathematical strategy used for scoring (e.g. WATERFALL)."),
    ] = None
    user_name: Annotated[str | None, Field(default=None, description="Initiating user's name.")] = None
    scoring_engine_name: Annotated[
        str | None, Field(default=None, description="Human readable name of the scoring engine.")
    ] = None
    strictness_level: Annotated[int | None, Field(default=None, description="Numeric strictness level (0-100).")] = None
    local_time_str: Annotated[str | None, Field(default=None, description="Localized time string from the client.")] = (
        None
    )
    custom_preface_md: Annotated[
        str | None, Field(default=None, description="Custom user preface rendered as Markdown.")
    ] = None
    profile_id: Annotated[str, Field(description="The output profile's opaque Stripe ID.")]
    profile_name: Annotated[
        I18nText | None, Field(default=None, description="Localized name of the output profile.")
    ] = None
    profile_description: Annotated[
        I18nText | None,
        Field(default=None, description="Detailed profile context mapped from OutputProfile."),
    ] = None
    available_profiles: Annotated[
        dict[str, I18nText],
        Field(default_factory=dict, description="Mapping of profile IDs to localized names."),
    ]
    global_score: Annotated[
        float | None,
        Field(default=None, description="The mathematical average extracted from the scoring_result hook."),
    ] = None
    has_warning: Annotated[
        bool,
        Field(default=False, description="Flag indicating if the report generation had non-fatal warnings."),
    ] = False

    # Strict Topological DAG Execution Model fields
    global_metrics: Annotated[
        ExecutionMetricsDTO | None,
        Field(default=None, description="Aggregate atom-level metrics for DAG execution."),
    ] = None
    inner_sdui_blocks: Annotated[
        list[AnySduiBlock],
        Field(default_factory=list, description="Stores the final structured SDUI blocks."),
    ]
    results: Annotated[
        list[AtomResultDTO],
        Field(
            default_factory=list,
            description=(
                "SDUI-RULE: Backend must return this list strictly topologically sorted. "
                "Frontend does not compute the DAG."
            ),
        ),
    ]
    hydrated_references: Annotated[
        dict[str, HydratedAtomDTO],
        Field(default_factory=dict, description="O(1) Dictionary: tda_id -> Static text."),
    ]

    visible_metadata: Annotated[
        list[str],
        Field(default_factory=list, description="Fields visible on the UI and PDF cover header."),
    ]

    # Execution Diagnostic Metadata
    created_at: Annotated[datetime | None, Field(default=None, description="Execution creation timestamp.")] = None
    org_name: Annotated[str | None, Field(default=None, description="Organization display name.")] = None
    cost_estimate: Annotated[
        float | None, Field(default=None, description="Estimated financial cost of the execution.")
    ] = None
    total_tokens: Annotated[
        int | None, Field(default=None, description="Total token count consumed across the execution.")
    ] = None
    prompt_tokens: Annotated[int | None, Field(default=None, description="Prompt token count consumed.")] = None
    completion_tokens: Annotated[int | None, Field(default=None, description="Completion token count consumed.")] = None
    reasoning_tokens: Annotated[int | None, Field(default=None, description="Reasoning token count consumed.")] = None

    # MCP Tool Loop Audit Trail (XAI Evidence for Frontend)
    mcp_tool_audit: Annotated[
        list[MCPAuditTrace],
        Field(
            default_factory=list,
            description="Serialized MCPAuditTrace entries for XAI Evidence Box rendering.",
        ),
    ]

    # Phase 3, Step 3.1: Inline topological short-circuit and Toulmin falsification lineage
    short_circuited_by_claims: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Human-readable prerequisite claims that short-circuited downstream evaluations.",
        ),
    ]
    falsified_warrant_claims: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Formatted Toulmin rebuttal-warrant-claim falsification lineage entries.",
        ),
    ]

    @model_validator(mode="after")
    def enforce_referential_integrity(self) -> Self:
        """Ensure that every tda_id present exists in the hydrated_references dictionary.

        Returns:
            The validated ReportDataDTO instance.

        Raises:
            ValueError: If any referenced tda_id is missing from hydrated_references.
        """
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
