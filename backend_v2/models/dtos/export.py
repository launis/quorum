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
    "ExportForensicAtomDTO",
    "ExportMatrixSummaryRowDTO",
    "ExportPayloadDTO",
]


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

    label: Annotated[str, Field(description="Localized logic matrix label or name")]
    context_target: Annotated[str, Field(description="Localized target context or empty string")]
    distribution: Annotated[str, Field(description="Score distribution breakdown across levels")]
    row_explanation: Annotated[str, Field(description="Qualitative summary or row explanation")]
    criteria: Annotated[str, Field(description="Atom hit ratio representation (e.g. '3/4')")]
    quotes: Annotated[str, Field(description="Primary forensic citation text")]
    source: Annotated[str, Field(description="Cited source title or identifier")]
    normalized_score: Annotated[float | str, Field(description="Normalized matrix score")]
    score: Annotated[float | str, Field(description="Absolute score representation")]


class ExportPayloadDTO(V2CoreBase):
    """Encapsulates binary content and metadata for report file downloads."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    content_bytes: Annotated[bytes, Field(description="Raw binary content of export artifact")]
    filename: Annotated[str, Field(description="Canonical export artifact filename")]
    mime_type: Annotated[str, Field(description="MIME media type for export download")]
