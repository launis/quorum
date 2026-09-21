"""Service for flattening complex execution DAG results into a flat file format (e.g. CSV-compatible dict).

Adheres to V2 Architecture:
- Flattens nested 'results' dictionaries.
- Uses `[step_id]_[key]` naming convention to guarantee uniquely identifiable global columns.
- Prevents deep nesting hiding crucial data for data analysts.
"""

from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.dtos.flat_record import FlatExecutionRecordDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.view.sdui import (
    SduiMatrixTableBlock,
    SduiMetrics1DBlock,
    SduiRadarChartBlock,
    SduiScatterPlotBlock,
)


class FlatFileService:
    """Service to flatten nested ExecutionRecord results using ReportDataDTO."""

    @staticmethod
    def flatten_results(execution: ExecutionRecord, report_dto: ReportDataDTO | None = None) -> FlatExecutionRecordDTO:
        """Flattens the DAG results into a strongly typed FlatExecutionRecordDTO.

        Args:
            execution: The ExecutionRecord to flatten.
            report_dto: The headless state containing semantic atoms.

        Returns:
            FlatExecutionRecordDTO: A flat execution record suitable for CSV serialization.
        """
        matrix_metrics: dict[str, str | float | int | bool | None] = {}
        global_score: float | None = None
        has_warning: bool = False

        if report_dto:
            global_score = report_dto.global_score
            has_warning = report_dto.has_warning

            matrices = []
            if report_dto.inner_sdui_blocks:
                for block in report_dto.inner_sdui_blocks:
                    match block:
                        case (
                            SduiRadarChartBlock(axes=axes)
                            | SduiScatterPlotBlock(axes=axes)
                            | SduiMatrixTableBlock(axes=axes)
                            | SduiMetrics1DBlock(axes=axes)
                        ):
                            matrices.extend(axes)
                        case _:
                            pass
            for matrix in matrices:
                matrix_prefix = f"matrix_{matrix.block_id}"
                matrix_metrics[f"{matrix_prefix}_score"] = matrix.score
                if matrix.semantic_reasoning:
                    matrix_metrics[f"{matrix_prefix}_reasoning"] = matrix.semantic_reasoning
                if matrix.cited_text_quote:
                    matrix_metrics[f"{matrix_prefix}_quote"] = matrix.cited_text_quote
                if matrix.cited_source_id:
                    matrix_metrics[f"{matrix_prefix}_source"] = matrix.cited_source_id

        return FlatExecutionRecordDTO(
            execution_id=execution.id,
            workflow_id=execution.workflow_id,
            status=execution.status.value,
            global_score=global_score,
            has_warning=has_warning,
            matrix_metrics=matrix_metrics,
        )
