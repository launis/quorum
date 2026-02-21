"""Service for generating detailed PDF reports using WeasyPrint and Jinja2."""

import json
import logging
from pathlib import Path
from typing import Protocol, runtime_checkable

# Optional imports handled gracefully could be considered, but dependencies are mandated in task.
import weasyprint  # type: ignore
from jinja2 import Environment, FileSystemLoader

from backend.api.transformers import ReportTransformer
from backend.database.repository import AbstractWorkflowRepository
from backend.exceptions import AppException, ErrorCodes
from backend.models.view import SectionType
from backend.services.chart_service import ChartService

logger = logging.getLogger(__name__)

@runtime_checkable
class ProgressServiceProtocol(Protocol):
    """Protocol used for emitting progress updates."""

    async def emit_progress(
        self,
        execution_id: str,
        task_key: str,
        message: str,
        progress: float
    ) -> None:
        """Emits a progress event."""
        ...


class PdfReportService:
    """Service to generate PDF reports from execution data."""

    def __init__(
        self,
        repository: AbstractWorkflowRepository,
        progress: ProgressServiceProtocol | None = None
    ):
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
        def translate_filter(key):
            if not key:
                return ""
            # Try exact match first, then string match
            return self.translations.get(str(key), key)

        self.env.filters["translate"] = translate_filter



    def _noop_progress(self) -> ProgressServiceProtocol:
        class NoOpProgress:
            async def emit_progress(self, *args, **kwargs): pass
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
                    details={"error_code": ErrorCodes.EXECUTION_NOT_FOUND}
                )

            # 3. Transform
            await self.progress.emit_progress(execution_id, task_key, "Analyzing results...", 0.10)
            
            # Helper for explicit typing if needed, but transformer expects ExecutionRecord
            report_view = self.transformer.transform(execution)
            ex_data = execution.model_dump(mode='json') if hasattr(execution, 'model_dump') else execution

            # 4. Generate Visualizations (Radar Charts)
            await self.progress.emit_progress(execution_id, task_key, "Generating visualization...", 0.15)

            # Metadata Lookup Strategy: Fetch Matrix Config to translate IDs -> Labels
            # The Result object has 'dimension_id' (e.g. 'agency'), but we want 'Strateginen Ohjaus'.
            # That mapping lives in the 'EvaluationMatrixConfig' component.
            matrix_map = {}
            try:
                # 4.1 Attempt to find matrix_id from the first score card or root result
                matrix_id = None
                for section in report_view.sections:
                    if section.type == SectionType.SCORE_CARD and section.data:
                        # Assuming the data dict (from _extract_score_data) might carry matrix_id if we added it,
                        # OR we check the raw execution data.
                        pass

                # Better: Check raw execution data first
                step_judge = ex_data.get("results", {}).get("step_results", {}).get("step_judge", {})
                # Handle nested output or direct
                if "output" in step_judge:
                    matrix_id = step_judge["output"].get("matrix_id")
                elif "matrix_id" in step_judge:
                    matrix_id = step_judge.get("matrix_id")

                if matrix_id:
                    comp = await self.repository.get_component_by_id(matrix_id)
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

            for section in report_view.sections:
                if not section.data:
                    continue

                # Ensure section.data is strictly a dictionary so Jinja and .get() work
                if hasattr(section.data, "model_dump"):
                    section.data = section.data.model_dump(mode="json")
                elif hasattr(section.data, "dict"):
                    section.data = section.data.dict()
                elif not isinstance(section.data, dict):
                    section.data = vars(section.data)

                if section.type == SectionType.SCORE_CARD:
                    # Check if dimensions exist and we can plot
                    dims = section.data.get("dimensions", [])
                    if dims:
                        scores = {}
                        for d in dims:
                             # We map ID directly to score.
                             # If visualization needs prettier labels, it must happen in ChartService or via metadata lookup.
                             # But here we stick to the raw data ID as the key.

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
                                    details={"error_code": ErrorCodes.CHART_GENERATION_FAILED}
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
                                        details={"error_code": ErrorCodes.CHART_GENERATION_FAILED, "original_error": str(e)}
                                    ) from e
                            else:
                                logger.warning(f"Skipping dimension with missing ID/Label in report {execution_id}")

                        # Generate chart
                        # Retrieve dynamic max_score from section data (populated by ReportTransformer from DB)
                        # Strict Mode: Fail if max_score is missing (no default=4)
                        max_score = int(section.data["max_score"])
                        chart_b64 = ChartService.generate_radar_chart(scores, max_val=max_score)
                        # Inject back into data view for template
                        # Inject back into data view for the template
                        section.data["chart_image"] = chart_b64

                elif section.type == SectionType.LOGIC_ANALYSIS:
                    # Logic Matrix Bubble Chart
                    # Extract scores (Standardized keys from domain model)
                    bloom = float(getattr(section.data, "bloom_score", 0.0) or 0.0)
                    strat = float(getattr(section.data, "strategic_score", 0.0) or 0.0)

                    # Toulmin score might be flat in data or calculated
                    toulmin_score = float(getattr(section.data, "toulmin_score", 0.0) or 0.0)

                    if bloom > 0 and strat > 0:
                        chart_b64 = ChartService.generate_bubble_chart(
                            x_val=bloom,
                            y_val=strat,
                            size_val=toulmin_score,
                            title="Logic Matrix Position"
                        )
                        section.data["logic_chart_image"] = chart_b64

                elif section.type == SectionType.FACT_CHECK:
                    # Preprocess for Template (English Standardization)

                    # 1. Facts
                    raw_facts = section.data.get("fact_checks", [])
                    processed_facts = []
                    for item in raw_facts:
                        processed_facts.append({
                            "claim": item.get("claim"),
                            "verification_result": item.get("verification_result"),
                            "source_or_reasoning": item.get("source_or_reasoning"),
                            "is_verified": item.get("is_verified")
                        })
                    section.data["processed_facts"] = processed_facts

                    # 2. Ethics
                    raw_ethics = section.data.get("ethical_issues", [])
                    processed_ethics = []
                    for item in raw_ethics:
                        processed_ethics.append({
                            "issue_type": item.get("issue_type"),
                            "severity": item.get("severity"),
                            "description": item.get("description"),
                            "is_critical": item.get("is_critical")
                        })
                    section.data["processed_ethics"] = processed_ethics

            # 5. Render Template
            await self.progress.emit_progress(execution_id, task_key, "Preparing report layout...", 0.20)

            template = self.env.get_template("dashboard_pdf.html")
            html_content = template.render(view=report_view)

            # 6. Generate PDF
            # WeasyPrint is CPU intensive and blocking.
            await self.progress.emit_progress(execution_id, task_key, "Consulting Print Engine (WeasyPrint)...", 0.30)

            import asyncio
            loop = asyncio.get_running_loop()

            # Run blocking PDF generation in a thread pool
            def _render_pdf():
                return weasyprint.HTML(string=html_content).write_pdf()

            pdf_bytes = await loop.run_in_executor(None, _render_pdf)

            # 7. Complete
            await self.progress.emit_progress(execution_id, task_key, "Done", 1.0)

            return pdf_bytes

        except AppException:
            # Re-raise known AppExceptions (e.g. 404, Validation Error) as-is
            raise

        except Exception as e:
            error_code = ErrorCodes.PDF_GENERATION_FAILED
            error_message = "PDF generation failed"

            logger.error(f"{error_code}: {error_message} for {execution_id}: {e}", exc_info=True)

            # Attempt to emit failure progress
            try:
                await self.progress.emit_progress(execution_id, task_key, f"Error: {str(e)}", 0.0)
            except Exception:
                pass # Swallow progress error to ensure the main error is raised

            raise AppException(
                message=f"{error_message}: {str(e)}",
                status_code=500,
                details={"error_code": error_code, "original_error": str(e)}
            ) from e
