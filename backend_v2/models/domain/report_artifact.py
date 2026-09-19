"""Domain model for Materialized Report Artifacts.

Elevates generated presentation outputs (PDF, SDUI JSON, Excel, CSV) into first-class,
independently versioned records adhering to Tripartite Pipeline Architecture.
"""

from datetime import UTC, datetime
from typing import Annotated

from pydantic import ConfigDict, Field, StrictStr

from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, V2CoreBase
from backend_v2.models.dtos.report_artifact import (
    ReportMetadataDTO,
    ReportStatus,
    ReportStoragePathsDTO,
)

__all__ = ["ReportArtifact"]


class ReportArtifact(V2CoreBase):
    """Domain model representing an independently versioned, materialized report artifact."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: Annotated[
        str,
        Field(
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="Unique identifier prefixed with 'rep_'. MUST be a valid Stripe Pattern Opaque ID.",
        ),
    ]
    execution_id: Annotated[StrictStr, Field(description="Associated analytical execution ID.")]
    workflow_id: Annotated[StrictStr, Field(description="Associated workflow definition ID.")]
    profile_id: Annotated[StrictStr, Field(description="Associated presentation profile ID.")]
    locale: Annotated[StrictStr, Field(description="Report target locale code (e.g., 'fi', 'en').")]
    title: Annotated[StrictStr, Field(description="Human-readable title of the report artifact.")]
    status: Annotated[ReportStatus, Field(description="Current lifecycle compilation status.")]
    storage_paths: Annotated[
        ReportStoragePathsDTO,
        Field(default_factory=ReportStoragePathsDTO, description="Physical storage artifact paths on disk/cloud."),
    ]
    metadata: Annotated[
        ReportMetadataDTO,
        Field(default_factory=ReportMetadataDTO, description="FinOps and generation telemetry metadata."),
    ]
    error_message: Annotated[
        str | None,
        Field(default=None, description="Detailed error description if report compilation failed."),
    ] = None
    created_at: Annotated[
        datetime,
        Field(default_factory=lambda: datetime.now(UTC), description="Creation timestamp in UTC."),
    ]
    updated_at: Annotated[
        datetime,
        Field(default_factory=lambda: datetime.now(UTC), description="Last update timestamp in UTC."),
    ]
