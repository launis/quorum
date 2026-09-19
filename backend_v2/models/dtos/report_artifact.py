"""Data Transfer Objects for Report Artifacts.

Governs materialized report outputs, metadata, storage references, and CRUD payloads
in strict compliance with Tripartite Pipeline Architecture and Four-Tier Pydantic V2 Invariants.
"""

from datetime import datetime
from typing import Annotated

from pydantic import ConfigDict, Field, StrictStr

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import CognitiveTier, LLMProvider, ReportStatus

__all__ = [
    "PublicReportDTO",
    "ReportArtifactCreateDTO",
    "ReportArtifactSummaryDTO",
    "ReportArtifactUpdateDTO",
    "ReportMetadataDTO",
    "ReportRowItemDTO",
    "ReportStatus",
    "ReportStoragePathsDTO",
]


class ReportStoragePathsDTO(V2CoreBase):
    """Storage artifact paths for materialized reports across different formats."""

    model_config = ConfigDict(strict=True, extra="forbid")

    pdf_path: Annotated[str | None, Field(default=None, description="Storage path for compiled PDF document.")] = None
    sdui_json_path: Annotated[
        str | None, Field(default=None, description="Storage path for pre-compiled SDUI JSON tree.")
    ] = None
    excel_path: Annotated[
        str | None, Field(default=None, description="Storage path for generated forensic Excel workbook.")
    ] = None
    csv_path: Annotated[str | None, Field(default=None, description="Storage path for flat CSV export.")] = None


class ReportMetadataDTO(V2CoreBase):
    """Execution and FinOps telemetry metadata captured during report generation."""

    model_config = ConfigDict(strict=True, extra="forbid")

    cost_usd: Annotated[float | None, Field(default=None, description="Total financial cost in USD.")] = None
    duration_ms: Annotated[
        int | None, Field(default=None, description="Report compilation latency in milliseconds.")
    ] = None
    tokens_used: Annotated[int | None, Field(default=None, description="Total tokens consumed by synthesis.")] = None
    llm_model: Annotated[str | None, Field(default=None, description="Model identifier used for synthesis.")] = None
    provider: Annotated[str | None, Field(default=None, description="LLM provider name.")] = None
    cognitive_tier: Annotated[
        CognitiveTier | None, Field(default=None, description="Abstract cognitive tier assigned to synthesis.")
    ] = None
    model_registry_id: Annotated[
        str | None, Field(default=None, description="Resolved SystemConfig model registry ID.")
    ] = None
    thinking_tokens: Annotated[int | None, Field(default=None, description="Reasoning / thinking tokens consumed.")] = (
        None
    )


class ReportRowItemDTO(V2CoreBase):
    """B2B tabular row delivery DTO representing an evaluated scorecard row item."""

    model_config = ConfigDict(strict=True, extra="forbid")

    execution_id: Annotated[StrictStr, Field(description="Parent execution ID.")]
    report_id: Annotated[StrictStr, Field(description="Parent report artifact ID.")]
    metric_key: Annotated[StrictStr, Field(description="Canonical metric or prompt block ID.")]
    metric_label: Annotated[StrictStr, Field(description="Human-readable metric label.")]
    score: Annotated[float, Field(description="Evaluated numerical score.")]
    max_scale: Annotated[float, Field(description="Maximum score on the evaluation scale.")]
    weight: Annotated[float, Field(description="Relative weight of this metric.")]
    reasoning: Annotated[str | None, Field(default=None, description="Analytical reasoning justification.")] = None
    quote: Annotated[str | None, Field(default=None, description="Forensic source quote supporting evaluation.")] = None


class PublicReportDTO(V2CoreBase):
    """Public read-only DTO for external report consumption."""

    model_config = ConfigDict(strict=True, extra="forbid")

    report_id: Annotated[StrictStr, Field(description="Unique report artifact identifier.")]
    created_at: Annotated[datetime, Field(description="Timestamp when report was created.")]
    title: Annotated[StrictStr, Field(description="Human-readable title of the report.")]
    target_audience: Annotated[StrictStr | None, Field(default=None, description="Target audience classification.")] = (
        None
    )
    overall_score: Annotated[float | None, Field(default=None, description="Overall evaluated score.")] = None
    metrics: Annotated[
        dict[str, float], Field(default_factory=dict, description="Flat key-value dictionary of evaluated metrics.")
    ]
    executive_summary_markdown: Annotated[
        str | None, Field(default=None, description="Synthesized executive summary in Markdown format.")
    ] = None
    downloads: Annotated[
        dict[str, str], Field(default_factory=dict, description="Map of format keys to download URLs.")
    ]


class ReportArtifactCreateDTO(V2CoreBase):
    """Payload for creating a new materialized report artifact."""

    model_config = ConfigDict(strict=True, extra="forbid")

    execution_id: Annotated[StrictStr, Field(description="Target analytical execution ID.")]
    profile_id: Annotated[StrictStr, Field(description="Presentation OutputProfile ID.")]
    locale: Annotated[StrictStr, Field(default="fi", description="Target output locale code ('fi' or 'en').")] = "fi"
    custom_preface_md: Annotated[
        str | None, Field(default=None, description="Optional custom preface Markdown text.")
    ] = None
    model_registry_id: Annotated[
        str | None, Field(default=None, description="Optional override model registry ID.")
    ] = None
    provider_override: Annotated[
        LLMProvider | None, Field(default=None, description="Optional LLM provider override.")
    ] = None


class ReportArtifactUpdateDTO(V2CoreBase):
    """Payload for updating an existing report artifact."""

    model_config = ConfigDict(strict=True, extra="forbid")

    status: Annotated[ReportStatus | None, Field(default=None, description="Updated lifecycle status.")] = None
    storage_paths: Annotated[
        ReportStoragePathsDTO | None, Field(default=None, description="Updated storage paths for compiled files.")
    ] = None
    metadata: Annotated[ReportMetadataDTO | None, Field(default=None, description="Updated FinOps metadata.")] = None
    error_message: Annotated[
        str | None, Field(default=None, description="Error message details if generation failed.")
    ] = None


class ReportArtifactSummaryDTO(V2CoreBase):
    """Lightweight summary DTO for list endpoints and selector views."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: Annotated[StrictStr, Field(description="Report artifact Opaque Stripe ID.")]
    execution_id: Annotated[StrictStr, Field(description="Associated execution ID.")]
    profile_id: Annotated[StrictStr, Field(description="Associated presentation profile ID.")]
    locale: Annotated[StrictStr, Field(description="Report locale code.")]
    title: Annotated[str, Field(description="Report display title.")]
    status: Annotated[ReportStatus, Field(description="Current lifecycle status.")]
    created_at: Annotated[datetime, Field(description="Creation timestamp.")]
    updated_at: Annotated[datetime, Field(description="Last update timestamp.")]
