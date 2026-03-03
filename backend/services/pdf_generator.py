"""Service for generating detailed PDF reports using WeasyPrint and Jinja2."""

import json
import logging
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

# Optional imports handled gracefully could be considered, but dependencies are mandated in task.
import weasyprint
from jinja2 import Environment, FileSystemLoader

from backend.api.transformers import ReportTransformer
from backend.database.repository import AbstractWorkflowRepository
from backend.exceptions import AppException, ErrorCodes
from backend.models.view.semantic_models import BlockType
from backend.services.chart_service import ChartService

logger = logging.getLogger(__name__)


@runtime_checkable
class ProgressServiceProtocol(Protocol):
    """Protocol used for emitting progress updates."""

    async def emit_progress(self, execution_id: str, task_key: str, message: str, progress: float) -> None:
        """Emits a progress event."""
        ...


class PdfReportService:
    """Service to generate PDF reports from execution data."""

    def __init__(self, repository: AbstractWorkflowRepository, progress: ProgressServiceProtocol | None = None):
        """Initialize the service.

        Args:
            repository: Workflow repository.
            progress: Optional progress service for real-time updates.
        """
        self.repository = repository
        # Use a dummy progress handler if none provided to avoid if-checks everywhere
        self.progress = progress or self._noop_progress()
        # Suppress verbose fontTools logs (used by WeasyPrint)
        logging.getLogger("fontTools.subset").setLevel(logging.WARNING)
        logging.getLogger("fontTools.ttLib").setLevel(logging.WARNING)
        self.transformer = ReportTransformer()

        # Setup Jinja2 env
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))

        # Load translations
        try:
            l10n_path = Path(__file__).parent.parent / "l10n" / "fi.json"
            with open(l10n_path, encoding="utf-8") as f:
                self.translations = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load translations from {l10n_path}: {e}")
            self.translations = {}

        # Register translate filter
        def translate_filter(key: Any) -> str:
            if not key:
                return ""
            return str(self.translations.get(str(key), key))

        self.env.filters["translate"] = translate_filter

    def _noop_progress(self) -> ProgressServiceProtocol:
        class NoOpProgress:
            async def emit_progress(self, *args: Any, **kwargs: Any) -> None:
                pass

        return NoOpProgress()

    async def generate_execution_pdf(self, execution_id: str) -> bytes:
        """Generates a PDF for the given execution ID.

        Args:
            execution_id: The execution UUID.

        Returns:
            bytes: The generated PDF data.
        """
        task_key = "pdf_gen"

        try:
            # 1. Start
            await self.progress.emit_progress(execution_id, task_key, "Fetching report data...", 0.05)

            # 2. Fetch Data
            execution = await self.repository.get_execution(execution_id)
            if not execution:
                raise AppException(
                    message=f"Execution {execution_id} not found",
                    status_code=404,
                    details={"error_code": ErrorCodes.EXECUTION_NOT_FOUND},
                )

            # 3. Transform
            await self.progress.emit_progress(execution_id, task_key, "Analyzing results...", 0.10)

            from pydantic import BaseModel
            # Helper for explicit typing if needed, but transformer expects ExecutionRecord
            report_view = self.transformer.transform(execution)
            ex_data: dict[str, Any] = execution.model_dump(mode="json") if isinstance(execution, BaseModel) else execution

            # 4. Generate Visualizations (Radar Charts)
            await self.progress.emit_progress(execution_id, task_key, "Generating visualization...", 0.15)

            # Metadata Lookup Strategy: Fetch Matrix Config to translate IDs -> Labels
            # The Result object has 'dimension_id' (e.g. 'agency'), but we want 'Strateginen Ohjaus'.
            # That mapping lives in the 'EvaluationMatrixConfig' component.
            matrix_map = {}
            try:
                # 4.1 Attempt to find matrix_id from the first score card or root result
                # (Skipped: We check the raw execution data instead)
                matrix_id = None

                # Better: Check raw execution data first
                step_judge = ex_data.get("results", {}).get("step_results", {}).get("step_judge", {})
                # Handle nested output or direct
                if "output" in step_judge:
                    matrix_id = step_judge["output"].get("matrix_id")
                elif "matrix_id" in step_judge:
                    matrix_id = step_judge.get("matrix_id")

                if matrix_id:
                    comp = await self.repository.get_matrix_by_id(matrix_id)
                    if comp and "content" in comp:
                        criteria = comp["content"].get("criteria", [])
                        for c in criteria:
                            c_id = c.get("id")
                            c_label = c.get("label")
                            if c_id and c_label:
                                matrix_map[c_id] = c_label
                        logger.info(f"Loaded {len(matrix_map)} labels from matrix '{matrix_id}'")
            except Exception as e:
                logger.warning(f"Failed to load matrix labels: {e}")

            new_blocks = []
            for block in report_view.blocks:
                if not block.value:
                    new_blocks.append(block)
                    continue

                # Ensure block.value is strictly a dictionary so Jinja and .get() work
                if hasattr(block.value, "model_dump"):
                    sec_data = block.value.model_dump(mode="json")
                elif hasattr(block.value, "dict"):
                    sec_data = block.value.dict()
                elif not isinstance(block.value, dict):
                    sec_data = vars(block.value)
                else:
                    sec_data = dict(block.value)

                if block.type == BlockType.CARD:
                    # Check if dimensions exist and we can plot
                    dims = sec_data.get("dimensions", [])
                    if dims:
                        scores = {}
                        for d in dims:
                            # 1. New Standard
                            display_label = d.get("dimension_label")
                            tech_id = d.get("dimension_id")

                            # 2. Lookup: If no label yet, try to map from ID using Matrix Map
                            if not display_label and tech_id and tech_id in matrix_map:
                                display_label = matrix_map[tech_id]

                            # 3. Strict Mode: No fallback to ID.
                            if not display_label:
                                raise AppException(
                                    message=f"Strict Label Resolution Failed in PDF: Dimension '{tech_id}' has no label.",
                                    status_code=500,
                                    details={"error_code": ErrorCodes.CHART_GENERATION_FAILED},
                                )

                            if display_label:
                                try:
                                    val = float(d.get("score", 0))
                                    scores[display_label] = val
                                except (ValueError, TypeError) as e:
                                    # Fail Fast: corrupted score data should not be ignored
                                    raise AppException(
                                        message=f"Invalid score value for dimension '{display_label}'",
                                        status_code=500,
                                        details={
                                            "error_code": ErrorCodes.CHART_GENERATION_FAILED,
                                            "original_error": str(e),
                                        },
                                    ) from e
                            else:
                                logger.warning(f"Skipping dimension with missing ID/Label in report {execution_id}")

                        # Generate chart
                        max_score = int(sec_data["max_score"])
                        chart_b64 = ChartService.generate_radar_chart(scores, max_val=max_score)
                        sec_data["chart_image"] = chart_b64

                elif block.id == "logic-analysis":
                    # Extract scores
                    bloom = float(sec_data.get("bloom_score", 0.0) or 0.0)
                    strat = float(sec_data.get("strategic_score", 0.0) or 0.0)
                    toulmin_score = float(sec_data.get("toulmin_score", 0.0) or 0.0)

                    if bloom > 0 and strat > 0:
                        chart_b64 = ChartService.generate_bubble_chart(
                            x_val=bloom, y_val=strat, size_val=toulmin_score, title="Logic Matrix Position"
                        )
                        sec_data["logic_chart_image"] = chart_b64

                if hasattr(sec_data, "model_dump"):
                    sec_data = sec_data.model_dump(mode="json")
                elif hasattr(sec_data, "dict"):
                    sec_data = sec_data.dict()

                new_blocks.append(block.model_copy(update={"value": sec_data}))

            report_view = report_view.model_copy(update={"blocks": new_blocks})

            # 5. Render Template
            await self.progress.emit_progress(execution_id, task_key, "Preparing report layout...", 0.20)

            template = self.env.get_template("dashboard_pdf.html")
            html_content = template.render(view=report_view.model_dump(mode="json"))

            # 6. Generate PDF
            # WeasyPrint is CPU intensive and blocking.
            await self.progress.emit_progress(execution_id, task_key, "Consulting Print Engine (WeasyPrint)...", 0.30)

            import asyncio

            loop = asyncio.get_running_loop()

            # Run blocking PDF generation in a thread pool
            def _render_pdf() -> bytes:
                # Type safe cast since write_pdf returns bytes but may return Optional[bytes] or Any in stubs
                pdf_data = weasyprint.HTML(string=html_content).write_pdf()
                return bytes(pdf_data) if pdf_data else b""

            pdf_bytes = await loop.run_in_executor(None, _render_pdf)

            # 7. Complete
            await self.progress.emit_progress(execution_id, task_key, "Done", 1.0)

            return pdf_bytes

        except AppException:
            # Re-raise known AppExceptions (e.g. 404, Validation Error) as-is
            raise

        except Exception as e:
            logger.error(f"{ErrorCodes.PDF_GENERATION_FAILED}: PDF generation failed for {execution_id}: {e}", exc_info=True)

            try:
                await self.progress.emit_progress(execution_id, task_key, f"Error: {e}", 0.0)
            except Exception as prog_e:
                logger.warning(f"Failed to emit progress error for {execution_id}: {prog_e}")

            raise AppException(
                message=f"PDF generation failed: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.PDF_GENERATION_FAILED, "original_error": str(e)},
            ) from e
