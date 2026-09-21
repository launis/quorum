"""Unit tests for RenderExecutionResultDTO."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.execution import JobAcceptedDTO
from backend_v2.models.dtos.flat_record import FlatExecutionRecordDTO
from backend_v2.models.dtos.render import RenderExecutionResultDTO
from backend_v2.models.dtos.report_data import ReportDataDTO


def test_render_execution_result_dto_bytes_payload() -> None:
    """Verify RenderExecutionResultDTO with bytes content and filename."""
    dto = RenderExecutionResultDTO(
        content=b"%PDF-1.4 mock pdf content",
        media_type="application/pdf",
        filename="report_exe_123.pdf",
    )
    assert isinstance(dto.content, bytes)
    assert dto.content.startswith(b"%PDF")
    assert dto.media_type == "application/pdf"
    assert dto.filename == "report_exe_123.pdf"


def test_render_execution_result_dto_str_payload() -> None:
    """Verify RenderExecutionResultDTO with string content and default None filename."""
    dto = RenderExecutionResultDTO(
        content="<html><body>Report</body></html>",
        media_type="text/html",
    )
    assert isinstance(dto.content, str)
    assert dto.media_type == "text/html"
    assert dto.filename is None


def test_render_execution_result_dto_job_accepted_payload() -> None:
    """Verify RenderExecutionResultDTO with JobAcceptedDTO content."""
    job = JobAcceptedDTO(
        status="PENDING",
        message="Job processing accepted",
        execution_id="exe_123",
    )
    dto = RenderExecutionResultDTO(
        content=job,
        media_type="application/json",
    )
    assert isinstance(dto.content, JobAcceptedDTO)
    assert dto.content.execution_id == "exe_123"
    assert dto.media_type == "application/json"


def test_render_execution_result_dto_extra_fields_forbid() -> None:
    """Verify RenderExecutionResultDTO rejects extraneous attributes fail-fast."""
    with pytest.raises(ValidationError):
        RenderExecutionResultDTO(
            content="data",
            media_type="text/plain",
            extra_field="unauthorized",  # type: ignore[call-arg]
        )


def test_render_execution_result_dto_invalid_type_fail_fast() -> None:
    """Verify RenderExecutionResultDTO rejects invalid content type fail-fast."""
    with pytest.raises(ValidationError):
        RenderExecutionResultDTO(
            content=12345,  # type: ignore[arg-type]
            media_type="text/plain",
        )
