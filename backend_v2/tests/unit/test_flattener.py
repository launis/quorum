from unittest.mock import AsyncMock
"""Unit tests for the FlatFileService."""

import uuid

from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.v2_core import ExecutionRecord, I18nText, MatrixScorecardRowDTO, ReportDataDTO

ExecutionRecord.model_rebuild()
from backend_v2.services.flattener import FlatFileService


def test_flat_file_service_flatten_results() -> None:
    """Test that execution traces are flattened correctly according to V2 specs."""
    execution_id = f"exe_{uuid.uuid4().hex}"

    # We create a dummy ExecutionRecord
    record = ExecutionRecord(
        id=execution_id,
        workflow_id="wf_test",
        status=ExecutionStatus.PASSED,
        execution_trace=[],
    )

    # We create a dummy ReportDataDTO
    report = ReportDataDTO(
        execution_id=execution_id,
        workflow_id="wf_test",
        profile_id="prof_test",
        global_score=85.0,
        has_warning=False,
        evaluative_matrices=[
            MatrixScorecardRowDTO(
                block_id="blk_1",
                name="Matrix 1",
                label_i18n=I18nText(translations={"en": "Matrix 1"}, default_locale="en"),
                row_explanation="Test matrix",
                score=4.0,
                semantic_reasoning="Passed because of X",
                cited_text_quote="This is a quote",
                cited_source_id="Source A",
                is_evaluative=True,
            )
        ],
    )

    flat_data = FlatFileService.flatten_results(record, report_dto=report)

    assert flat_data["execution_id"] == execution_id
    assert flat_data["workflow_id"] == "wf_test"
    assert flat_data["status"] == "PASSED"
    assert flat_data["global_score"] == 85.0
    assert flat_data["has_warning"] is False

    # Check flattened trace data
    assert flat_data["matrix_blk_1_score"] == 4.0
    assert flat_data["matrix_blk_1_reasoning"] == "Passed because of X"
    assert flat_data["matrix_blk_1_quote"] == "This is a quote"
    assert flat_data["matrix_blk_1_source"] == "Source A"


def test_flat_file_service_empty_results() -> None:
    """Test flat file service with no trace results."""
    execution_id = f"exe_{uuid.uuid4().hex}"
    record = ExecutionRecord(
        id=execution_id,
        workflow_id="wf_empty",
        status=ExecutionStatus.FAILED,
        execution_trace=[],
    )

    flat_data = FlatFileService.flatten_results(record)

    assert flat_data["execution_id"] == execution_id
    assert flat_data["workflow_id"] == "wf_empty"
    assert flat_data["status"] == "FAILED"
    assert "global_score" not in flat_data
