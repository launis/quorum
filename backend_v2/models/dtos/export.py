"""Export Data Transfer Objects (DTOs) for spreadsheet and flat-file streaming.

Provides strictly typed, immutable Pydantic V2 DTOs representing forensic atom
records (ExportForensicAtomDTO), standard matrix summary rows (ExportMatrixSummaryRowDTO),
and binary artifact export payloads (ExportPayloadDTO).
"""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase

__all__ = [
    "AtomScaleMetadataDTO",
    "ExportDenormalizedFlatRowDTO",
    "ExportForensicAtomDTO",
    "ExportMatrixSummaryRowDTO",
    "ExportPayloadDTO",
]


class AtomScaleMetadataDTO(V2CoreBase):
    """Metadata resolved from prompt block scale definitions for an atom."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    matrix_id: Annotated[str, Field(description="ID of the parent matrix block")]
    level: Annotated[int, Field(description="Scale score level")]
    level_name: Annotated[str, Field(description="Localized scale level name")]
    criterion: Annotated[str, Field(description="Localized claim label or description")]
    is_inverse: Annotated[bool, Field(default=False, description="Whether the assertion requires inverse evidence")]


class ExportForensicAtomDTO(V2CoreBase):
    """Forensic evaluated atom export record matching ReportAtomColumn members."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    matrix_label: Annotated[str, Field(description="Localized label of parent logic matrix")]
    context_target: Annotated[str, Field(description="Localized target context or empty string")]
    level: Annotated[int, Field(description="Numerical criterion level")]
    level_name: Annotated[str, Field(description="Descriptive level name")]
    criterion: Annotated[str, Field(description="Evaluation criterion or resolved claim")]
    claim_type: Annotated[str, Field(description="Localized claim type label")]
    result_status: Annotated[int, Field(description="Binary execution result status: 1 for passed, 0 for failed")]
    quotes: Annotated[str, Field(description="Exact forensic citation text or empty string")]
    ai_reasoning: Annotated[str, Field(description="AI evaluation rationale or empty string")]


class ExportMatrixSummaryRowDTO(V2CoreBase):
    """Standard matrix summary row record matching ReportMatrixColumn members."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    execution_id: Annotated[str, Field(description="Unique execution identifier")]
    label: Annotated[str, Field(description="Localized logic matrix label or name")]
    context_target: Annotated[str, Field(description="Localized target context or empty string")]
    distribution: Annotated[str, Field(description="Score distribution breakdown across levels")]
    hits: Annotated[int, Field(description="Number of passed atomic assertions", ge=0)]
    total_atoms: Annotated[int, Field(description="Total number of evaluated atomic assertions", ge=0)]
    hit_ratio: Annotated[float, Field(description="Ratio of passed atoms to total atoms", ge=0.0, le=1.0)]
    raw_score: Annotated[float, Field(description="Unscaled matrix raw score")]
    scale_max: Annotated[float, Field(description="Maximum possible scale value")]
    normalized_score: Annotated[float, Field(description="Normalized 0-100 matrix score")]
    row_explanation: Annotated[str, Field(description="Qualitative summary or row explanation")]
    criteria: Annotated[str, Field(description="Atom hit ratio representation (e.g. '3/4')")]
    source: Annotated[str, Field(description="Cited source title or identifier")]


class ExportDenormalizedFlatRowDTO(V2CoreBase):
    """Denormalized flat record uniting parent matrix metrics with atomic claim evaluations."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    execution_id: Annotated[str, Field(description="Unique execution identifier")]
    matrix_label: Annotated[str, Field(description="Localized label of parent logic matrix")]
    context_target: Annotated[str, Field(description="Localized target context or empty string")]
    distribution: Annotated[str, Field(description="Level score distribution breakdown")]
    hits: Annotated[int, Field(description="Number of passed atomic assertions", ge=0)]
    total_atoms: Annotated[int, Field(description="Total number of evaluated atomic assertions", ge=0)]
    hit_ratio: Annotated[float, Field(description="Ratio of passed atoms to total atoms", ge=0.0, le=1.0)]
    raw_score: Annotated[float, Field(description="Unscaled matrix raw score")]
    scale_max: Annotated[float, Field(description="Maximum possible scale value")]
    normalized_score: Annotated[float, Field(description="Normalized 0-100 matrix score")]
    level: Annotated[int, Field(description="Numerical criterion level")]
    level_name: Annotated[str, Field(description="Descriptive level name")]
    criterion: Annotated[str, Field(description="Evaluation criterion or resolved claim")]
    claim_type: Annotated[str, Field(description="Localized claim type label")]
    result_status: Annotated[int, Field(description="Binary execution outcome (1=passed, 0=failed)", ge=0, le=1)]
    quotes: Annotated[str, Field(description="Formatted text observations or citation quote")]
    ai_reasoning: Annotated[str, Field(description="Formatted qualitative reasoning explanation")]


class ExportPayloadDTO(V2CoreBase):
    """Encapsulates binary content and metadata for report file downloads."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    content_bytes: Annotated[bytes, Field(description="Raw binary content of export artifact")]
    filename: Annotated[str, Field(description="Canonical export artifact filename")]
    mime_type: Annotated[str, Field(description="MIME media type for export download")]
