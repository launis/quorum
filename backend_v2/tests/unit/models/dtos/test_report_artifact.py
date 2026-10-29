"""Unit tests for report artifact DTOs."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.report_artifact import (
    CreateReportRequestDTO,
    PublicReportDTO,
    ReportArtifactCreateDTO,
    ReportArtifactSummaryDTO,
    ReportArtifactUpdateDTO,
    ReportMetadataDTO,
    ReportRowItemDTO,
    ReportStatus,
    ReportStoragePathsDTO,
)
from backend_v2.models.enums import CognitiveTier, LLMProvider


def test_report_storage_paths_dto_defaults_and_roundtrip() -> None:
    """Verify ReportStoragePathsDTO default initialization and serialization."""
    paths = ReportStoragePathsDTO()
    assert paths.pdf_path is None
    assert paths.sdui_json_path is None
    assert paths.excel_path is None
    assert paths.csv_path is None

    populated = ReportStoragePathsDTO(
        pdf_path="reports/report.pdf",
        sdui_json_path="reports/report.sdui.json",
        excel_path="reports/report.xlsx",
        csv_path="reports/report.csv",
    )
    dumped = populated.model_dump(mode="json")
    loaded = ReportStoragePathsDTO.model_validate(dumped)
    assert loaded == populated
    assert loaded.pdf_path == "reports/report.pdf"


def test_report_storage_paths_dto_rejects_extra() -> None:
    """Verify ReportStoragePathsDTO rejects unauthorized extra fields."""
    with pytest.raises(ValidationError):
        ReportStoragePathsDTO.model_validate({"pdf_path": "path", "forbidden_field": "error"})


def test_report_metadata_dto_validation_and_roundtrip() -> None:
    """Verify ReportMetadataDTO serialization and FinOps metrics integrity."""
    meta = ReportMetadataDTO(
        cost_usd=0.045,
        duration_ms=1250,
        tokens_used=5000,
        llm_model="gpt-5.4",
        provider="openai",
        cognitive_tier=CognitiveTier.REASONING,
        model_registry_id="reg_123",
        thinking_tokens=1500,
    )
    assert meta.cost_usd == 0.045
    assert meta.cognitive_tier == CognitiveTier.REASONING
    dumped = meta.model_dump(mode="python")
    loaded = ReportMetadataDTO.model_validate(dumped)
    assert loaded == meta


def test_report_metadata_dto_rejects_extra() -> None:
    """Verify ReportMetadataDTO rejects extra properties."""
    with pytest.raises(ValidationError):
        ReportMetadataDTO.model_validate({"tokens_used": 100, "extra_metric": 999})


def test_report_row_item_dto_validation() -> None:
    """Verify ReportRowItemDTO validation and strict string requirements."""
    row = ReportRowItemDTO(
        execution_id="exe_0195f3a0000070008000000000000001",
        report_id="rep_0195f3a0000070008000000000000001",
        metric_key="blk_0195f3a0000070008000000000000001",
        metric_label="Governance Metric",
        score=4.5,
        max_scale=5.0,
        weight=1.0,
        reasoning="Exemplary leadership evidence.",
        quote="Quote A [...] Quote B",
        is_inverse_evidence=False,
    )
    assert row.score == 4.5
    assert row.quote == "Quote A [...] Quote B"
    assert row.is_inverse_evidence is False

    dumped = row.model_dump(mode="python")
    loaded = ReportRowItemDTO.model_validate(dumped)
    assert loaded == row


def test_report_row_item_dto_rejects_invalid_types_and_extra() -> None:
    """Verify ReportRowItemDTO rejects non-strict types and extra fields."""
    with pytest.raises(ValidationError):
        ReportRowItemDTO.model_validate(
            {
                "execution_id": 12345,  # StrictStr rejects int
                "report_id": "rep_1",
                "metric_key": "blk_1",
                "metric_label": "Label",
                "score": 1.0,
                "max_scale": 5.0,
                "weight": 1.0,
            }
        )

    with pytest.raises(ValidationError):
        ReportRowItemDTO.model_validate(
            {
                "execution_id": "exe_1",
                "report_id": "rep_1",
                "metric_key": "blk_1",
                "metric_label": "Label",
                "score": 1.0,
                "max_scale": 5.0,
                "weight": 1.0,
                "unauthorized_key": "error",
            }
        )


def test_public_report_dto_validation() -> None:
    """Verify PublicReportDTO initialization, dict roundtrip, and JSON roundtrip."""
    now = datetime.now(timezone.utc)
    public = PublicReportDTO(
        report_id="rep_public_1",
        created_at=now,
        title="Public Report Title",
        target_audience="Executive Board",
        overall_score=85.5,
        metrics={"governance": 4.5, "strategy": 4.0},
        executive_summary_markdown="# Summary\nHigh performance observed.",
        downloads={"pdf": "https://example.com/download.pdf"},
    )
    assert public.report_id == "rep_public_1"
    assert public.metrics["governance"] == 4.5
    assert public.downloads["pdf"] == "https://example.com/download.pdf"

    dumped_python = public.model_dump(mode="python")
    loaded_python = PublicReportDTO.model_validate(dumped_python)
    assert loaded_python.report_id == public.report_id

    dumped_json_str = public.model_dump_json()
    loaded_json = PublicReportDTO.model_validate_json(dumped_json_str)
    assert loaded_json.report_id == public.report_id


def test_public_report_dto_rejects_extra() -> None:
    """Verify PublicReportDTO forbids unexpected fields."""
    with pytest.raises(ValidationError):
        PublicReportDTO.model_validate(
            {
                "report_id": "rep_1",
                "created_at": datetime.now(timezone.utc),
                "title": "Title",
                "extra_key": "bad",
            }
        )


def test_create_report_request_dto_validation() -> None:
    """Verify CreateReportRequestDTO defaults and provider validation."""
    req = CreateReportRequestDTO(
        profile_id="prf_board_summary",
    )
    assert req.locale == "fi"
    assert req.force_resynthesis is False
    assert req.execution_id is None

    custom = CreateReportRequestDTO(
        profile_id="prf_board_summary",
        locale="en",
        execution_id="exe_custom",
        force_resynthesis=True,
        custom_preface_md="Custom Preface",
        model_registry_id="reg_claude",
        provider_override=LLMProvider.ANTHROPIC,
    )
    assert custom.provider_override == LLMProvider.ANTHROPIC
    assert custom.force_resynthesis is True


def test_create_report_request_dto_rejects_extra() -> None:
    """Verify CreateReportRequestDTO rejects extra attributes."""
    with pytest.raises(ValidationError):
        CreateReportRequestDTO.model_validate(
            {
                "profile_id": "prf_1",
                "unknown_arg": "forbidden",
            }
        )


def test_report_artifact_create_dto_validation() -> None:
    """Verify ReportArtifactCreateDTO parameter validation."""
    create = ReportArtifactCreateDTO(
        execution_id="exe_1",
        profile_id="prf_1",
        locale="fi",
        force_resynthesis=False,
    )
    assert create.execution_id == "exe_1"
    assert create.profile_id == "prf_1"


def test_report_artifact_create_dto_rejects_extra() -> None:
    """Verify ReportArtifactCreateDTO rejects extra properties."""
    with pytest.raises(ValidationError):
        ReportArtifactCreateDTO.model_validate(
            {
                "execution_id": "exe_1",
                "profile_id": "prf_1",
                "bad_extra": 123,
            }
        )


def test_report_artifact_update_dto_validation() -> None:
    """Verify ReportArtifactUpdateDTO optional field updates."""
    update = ReportArtifactUpdateDTO(
        status=ReportStatus.READY,
        storage_paths=ReportStoragePathsDTO(pdf_path="report.pdf"),
        metadata=ReportMetadataDTO(cost_usd=0.02),
        error_message=None,
    )
    assert update.status == ReportStatus.READY
    assert update.storage_paths is not None
    assert update.storage_paths.pdf_path == "report.pdf"


def test_report_artifact_update_dto_rejects_extra() -> None:
    """Verify ReportArtifactUpdateDTO rejects unexpected fields."""
    with pytest.raises(ValidationError):
        ReportArtifactUpdateDTO.model_validate({"status": "READY", "illegal_param": "error"})


def test_report_artifact_summary_dto_validation() -> None:
    """Verify ReportArtifactSummaryDTO representation."""
    now = datetime.now(timezone.utc)
    summary = ReportArtifactSummaryDTO(
        id="rep_summary_1",
        execution_id="exe_summary_1",
        profile_id="prf_summary_1",
        locale="fi",
        title="Executive Summary Report",
        status=ReportStatus.GENERATING,
        created_at=now,
        updated_at=now,
    )
    assert summary.id == "rep_summary_1"
    assert summary.status == ReportStatus.GENERATING
    assert summary.title == "Executive Summary Report"


def test_report_artifact_summary_dto_rejects_missing_and_extra() -> None:
    """Verify ReportArtifactSummaryDTO rejects missing required attributes and extra fields."""
    with pytest.raises(ValidationError):
        ReportArtifactSummaryDTO.model_validate(
            {
                "id": "rep_1",
                # missing execution_id, profile_id, locale, etc.
            }
        )

    with pytest.raises(ValidationError):
        now = datetime.now(timezone.utc)
        ReportArtifactSummaryDTO.model_validate(
            {
                "id": "rep_1",
                "execution_id": "exe_1",
                "profile_id": "prf_1",
                "locale": "fi",
                "title": "Title",
                "status": "READY",
                "created_at": now,
                "updated_at": now,
                "extra": "bad",
            }
        )
