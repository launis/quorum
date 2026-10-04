"""Unit tests for ReportArtifact domain model."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.dtos.report_artifact import ReportMetadataDTO, ReportStatus, ReportStoragePathsDTO


def test_report_artifact_valid_instantiation() -> None:
    """Positive test: ReportArtifact instantiates cleanly with valid parameters."""
    artifact = ReportArtifact(
        id="rep_1234567890abcdef",
        execution_id="exe_1234567890abcdef",
        workflow_id="wor_1234567890abcdef",
        profile_id="prf_1234567890abcdef",
        locale="en",
        title="Executive Summary",
        status=ReportStatus.READY,
    )
    assert artifact.id == "rep_1234567890abcdef"
    assert artifact.execution_id == "exe_1234567890abcdef"
    assert artifact.status == ReportStatus.READY
    assert isinstance(artifact.storage_paths, ReportStoragePathsDTO)
    assert isinstance(artifact.metadata, ReportMetadataDTO)
    assert isinstance(artifact.created_at, datetime)
    assert isinstance(artifact.updated_at, datetime)
    assert artifact.custom_preface_md is None
    assert artifact.error_message is None


def test_report_artifact_rejects_invalid_id_pattern() -> None:
    """Negative test: ReportArtifact rejects invalid Opaque Stripe ID."""
    with pytest.raises(ValidationError) as exc_info:
        ReportArtifact(
            id="invalid_id",
            execution_id="exe_1234567890abcdef",
            workflow_id="wor_1234567890abcdef",
            profile_id="prf_1234567890abcdef",
            locale="fi",
            title="Raportti",
            status=ReportStatus.PENDING,
        )
    assert "String should match pattern" in str(exc_info.value)


def test_report_artifact_rejects_extra_fields() -> None:
    """Negative test: ReportArtifact enforces extra='forbid'."""
    with pytest.raises(ValidationError):
        ReportArtifact(
            id="rep_1234567890abcdef",
            execution_id="exe_1234567890abcdef",
            workflow_id="wor_1234567890abcdef",
            profile_id="prf_1234567890abcdef",
            locale="fi",
            title="Raportti",
            status=ReportStatus.PENDING,
            extra_field="disallowed",  # type: ignore[call-arg]
        )


def test_report_artifact_custom_preface_and_error() -> None:
    """Positive test: ReportArtifact supports custom preface and error message."""
    now = datetime.now(UTC)
    artifact = ReportArtifact(
        id="rep_abcdef1234567890",
        execution_id="exe_abcdef1234567890",
        workflow_id="wor_abcdef1234567890",
        profile_id="prf_abcdef1234567890",
        locale="fi",
        title="Virheraportti",
        status=ReportStatus.FAILED,
        custom_preface_md="# Johdanto",
        error_message="Compilation failed due to storage timeout",
        created_at=now,
        updated_at=now,
    )
    assert artifact.status == ReportStatus.FAILED
    assert artifact.custom_preface_md == "# Johdanto"
    assert artifact.error_message == "Compilation failed due to storage timeout"
    assert artifact.created_at == now
    assert artifact.updated_at == now


def test_report_artifact_strict_type_enforcement() -> None:
    """Negative test: ReportArtifact rejects non-string types for strict fields."""
    with pytest.raises(ValidationError):
        ReportArtifact(
            id="rep_1234567890abcdef",
            execution_id=12345,  # type: ignore[arg-type]
            workflow_id="wor_1234567890abcdef",
            profile_id="prf_1234567890abcdef",
            locale="en",
            title="Report",
            status=ReportStatus.READY,
        )
