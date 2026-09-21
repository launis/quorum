"""Unit tests for the FlatFileService."""

from __future__ import annotations

import uuid

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.view.sdui import (
    ParagraphBlock,
    SduiMatrixTableBlock,
    SduiMetrics1DBlock,
    SduiRadarChartBlock,
    SduiScatterPlotBlock,
)
from backend_v2.services.flattener import FlatFileService


def test_flat_file_service_flatten_results() -> None:
    """Test that execution traces are flattened correctly according to V2 specs."""
    execution_id = f"exe_{uuid.uuid4().hex}"

    record = ExecutionRecord(
        id=execution_id,
        workflow_id="wf_test",
        output_profile_id="prof_test",
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=[],
    )

    report = ReportDataDTO(
        execution_id=execution_id,
        workflow_id="wf_test",
        profile_id="prof_test",
        global_score=85.0,
        has_warning=False,
        inner_sdui_blocks=[
            SduiMetrics1DBlock(
                axes=[
                    MatrixScorecardRowDTO(
                        block_id="blk_1",
                        name="Matrix 1",
                        label_i18n=I18nText(translations={"en": "Matrix 1"}),
                        row_explanation="Test matrix",
                        score=4.0,
                        semantic_reasoning="Passed because of X",
                        cited_text_quote="This is a quote",
                        cited_source_id="Source A",
                        is_evaluative=True,
                    )
                ],
            )
        ],
    )

    flat_data = FlatFileService.flatten_results(record, report_dto=report)

    assert flat_data.execution_id == execution_id
    assert flat_data.workflow_id == "wf_test"
    assert flat_data.status == "PASSED"
    assert flat_data.global_score == 85.0
    assert flat_data.has_warning is False

    # Check flattened trace data
    assert flat_data.matrix_metrics["matrix_blk_1_score"] == 4.0
    assert flat_data.matrix_metrics["matrix_blk_1_reasoning"] == "Passed because of X"
    assert flat_data.matrix_metrics["matrix_blk_1_quote"] == "This is a quote"
    assert flat_data.matrix_metrics["matrix_blk_1_source"] == "Source A"

    # Check to_csv_dict() serialization for export
    csv_dict = flat_data.to_csv_dict()
    assert csv_dict["execution_id"] == execution_id
    assert csv_dict["workflow_id"] == "wf_test"
    assert csv_dict["status"] == "PASSED"
    assert csv_dict["global_score"] == 85.0
    assert csv_dict["matrix_blk_1_score"] == 4.0


def test_flat_file_service_empty_results() -> None:
    """Test flat file service with no trace results."""
    execution_id = f"exe_{uuid.uuid4().hex}"
    record = ExecutionRecord(
        id=execution_id,
        workflow_id="wf_empty",
        output_profile_id="prof_empty",
        status=ExecutionStatus.FAILED,
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=[],
    )

    flat_data = FlatFileService.flatten_results(record)

    assert flat_data.execution_id == execution_id
    assert flat_data.workflow_id == "wf_empty"
    assert flat_data.status == "FAILED"
    assert flat_data.global_score is None

    csv_dict = flat_data.to_csv_dict()
    assert csv_dict["global_score"] is None
    assert csv_dict["execution_id"] == execution_id


def test_flat_file_service_all_chart_blocks_and_other_blocks() -> None:
    """Test flattening across radar, scatter plot, matrix table, and non-matrix blocks."""
    execution_id = f"exe_{uuid.uuid4().hex}"
    record = ExecutionRecord(
        id=execution_id,
        workflow_id="wf_multi",
        output_profile_id="prof_multi",
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=[],
    )

    row_radar = MatrixScorecardRowDTO(
        block_id="blk_radar",
        name="Radar",
        label_i18n=I18nText(translations={"en": "Radar"}),
        row_explanation="Radar axis",
        score=3.5,
        semantic_reasoning="Radar reasoning",
        cited_text_quote="Radar quote",
        cited_source_id="Radar source",
        is_evaluative=True,
    )
    row_scatter = MatrixScorecardRowDTO(
        block_id="blk_scatter",
        name="Scatter",
        label_i18n=I18nText(translations={"en": "Scatter"}),
        row_explanation="Scatter axis",
        score=2.0,
        semantic_reasoning="Scatter reasoning",
        cited_text_quote="Scatter quote",
        cited_source_id="Scatter source",
        is_evaluative=True,
    )
    row_table = MatrixScorecardRowDTO(
        block_id="blk_table",
        name="Table",
        label_i18n=I18nText(translations={"en": "Table"}),
        row_explanation="Table axis",
        score=5.0,
        semantic_reasoning="Table reasoning",
        cited_text_quote="Table quote",
        cited_source_id="Table source",
        is_evaluative=True,
    )
    row_none = MatrixScorecardRowDTO(
        block_id="blk_none",
        name="NoneFields",
        label_i18n=I18nText(translations={"en": "NoneFields"}),
        row_explanation="None fields axis",
        score=1.0,
        semantic_reasoning=None,
        cited_text_quote=None,
        cited_source_id=None,
        is_evaluative=True,
    )

    report = ReportDataDTO(
        execution_id=execution_id,
        workflow_id="wf_multi",
        profile_id="prof_multi",
        global_score=90.0,
        has_warning=True,
        inner_sdui_blocks=[
            ParagraphBlock(text="Some unflattened text block"),
            SduiRadarChartBlock(axes=[row_radar]),
            SduiScatterPlotBlock(axes=[row_scatter]),
            SduiMatrixTableBlock(axes=[row_table, row_none]),
        ],
    )

    flat_data = FlatFileService.flatten_results(record, report_dto=report)

    assert flat_data.execution_id == execution_id
    assert flat_data.global_score == 90.0
    assert flat_data.has_warning is True
    assert flat_data.matrix_metrics["matrix_blk_radar_score"] == 3.5
    assert flat_data.matrix_metrics["matrix_blk_radar_reasoning"] == "Radar reasoning"
    assert flat_data.matrix_metrics["matrix_blk_scatter_score"] == 2.0
    assert flat_data.matrix_metrics["matrix_blk_table_score"] == 5.0
    assert flat_data.matrix_metrics["matrix_blk_none_score"] == 1.0
    assert "matrix_blk_none_reasoning" not in flat_data.matrix_metrics
    assert "matrix_blk_none_quote" not in flat_data.matrix_metrics
    assert "matrix_blk_none_source" not in flat_data.matrix_metrics

