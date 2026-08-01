"""Service for flattening complex execution DAG results into a flat file format (e.g. CSV-compatible dict).

Adheres to V2 Architecture:
- Flattens nested 'results' dictionaries.
- Uses `[step_id]_[key]` naming convention to guarantee uniquely identifiable global columns.
- Prevents deep nesting hiding crucial data for data analysts.
"""

from typing import Any

from backend_v2.models.v2_core import ExecutionRecord, ReportDataDTO
from backend_v2.models.view.sdui import (
    SduiMatrixTableBlock,
    SduiMetrics1DBlock,
    SduiRadarChartBlock,
    SduiScatterPlotBlock,
)


class FlatFileService:
    """Service to flatten nested ExecutionRecord results using ReportDataDTO."""

    @staticmethod
    def flatten_results(execution: ExecutionRecord, report_dto: ReportDataDTO | None = None) -> dict[str, Any]:
        """Flattens the DAG results dictionary into a single-level dictionary.

        Args:
            execution: The ExecutionRecord to flatten.
            report_dto: The headless state containing semantic atoms.

        Returns:
            dict[str, Any]: A flat dictionary suitable for CSV serialization.
        """
        flat_record: dict[str, Any] = {
            "execution_id": execution.id,
            "workflow_id": execution.workflow_id,
            "status": execution.status.value,
        }

        if report_dto:
            flat_record["global_score"] = report_dto.global_score
            flat_record["has_warning"] = report_dto.has_warning

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
                flat_record[f"{matrix_prefix}_score"] = matrix.score
                if matrix.semantic_reasoning:
                    flat_record[f"{matrix_prefix}_reasoning"] = matrix.semantic_reasoning
                if matrix.cited_text_quote:
                    flat_record[f"{matrix_prefix}_quote"] = matrix.cited_text_quote
                if matrix.cited_source_id:
                    flat_record[f"{matrix_prefix}_source"] = matrix.cited_source_id

        return flat_record
