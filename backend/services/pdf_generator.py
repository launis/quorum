"""Service for generating detailed PDF reports using WeasyPrint and Jinja2."""

import logging
from pathlib import Path
from typing import Protocol, runtime_checkable

# Optional imports handled gracefully could be considered, but dependencies are mandated in task.
import weasyprint  # type: ignore
from jinja2 import Environment, FileSystemLoader

from backend.api.bff_transformer import ReportTransformer
from backend.database.repository import AbstractWorkflowRepository
from backend.models.view import SectionType
from backend.services.chart_service import ChartService
from backend.exceptions import AppException, ErrorCodes

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
            await self.progress.emit_progress(execution_id, task_key, "Fetching report data...", 0.1)

            # 2. Fetch Data
            execution = await self.repository.get_execution(execution_id)
            if not execution:
                raise ValueError(f"Execution {execution_id} not found")

            # 3. Transform
            await self.progress.emit_progress(execution_id, task_key, "Analyzing results...", 0.3)
            # Use dump() compatibility if it's a Pydantic object, or dict if it's already dict
            # BFF Transformer generally expects a dict representation of the execution
            ex_data = execution.model_dump() if hasattr(execution, 'model_dump') else execution
            # Or if execution is Execution object, we might need model_dump.
            # Assuming Repository returns Pydantic V2 model.

            report_view = self.transformer.transform(ex_data)

            # 4. Generate Visualizations (Radar Charts)
            await self.progress.emit_progress(execution_id, task_key, "Generating visualization...", 0.5)

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
                if section.type == SectionType.SCORE_CARD and section.data:
                    # Check if dimensions exist and we can plot
                    dims = section.data.get("dimensions", [])
                    if dims:
                        scores = {}
                        for d in dims:
                             # We map ID directly to score. 
                             # If visualization needs prettier labels, it must happen in ChartService or via metadata lookup.
                             # But here we stick to the raw data ID as the key.
                            
                            # Compatible Extraction: Support V3 (dimension_id) and Legacy (label/name/id)
                            # FIX 2026-01-24: Use 'label' or 'name' for the CHART KEY to ensure human-readable text.
                            # The ChartService uses keys as labels.
                            
                            # 1. Try direct label in data (Legacy/Loose)
                            display_label = d.get("label") or d.get("name")
                            
                            # 2. Try technical ID (V3 Strict)
                            tech_id = d.get("dimension_id") or d.get("id")
                            
                            # 3. Lookup: If we have an ID but no label, look it up in Matrix Map
                            if not display_label and tech_id and tech_id in matrix_map:
                                display_label = matrix_map[tech_id]
                            
                            # 4. Fallback to ID
                            if not display_label:
                                display_label = tech_id
                            
                            if display_label:
                                try:
                                    val = float(d.get("score", 0))
                                    scores[display_label] = val
                                except (ValueError, TypeError):
                                    pass
                            else:
                                logger.warning(f"Skipping dimension with missing ID/Label in report {execution_id}")
                            
                        # Generate chart
                        # Retrieve dynamic max_score from section data (populated by ReportTransformer from DB or default)
                        max_score = int(section.data.get("max_score", 4))
                        chart_b64 = ChartService.generate_radar_chart(scores, max_val=max_score)
                        # Inject back into data view for template
                        section.data["chart_image"] = chart_b64

            # 5. Render Template
            await self.progress.emit_progress(execution_id, task_key, "Preparing report layout...", 0.8)

            template = self.env.get_template("dashboard_pdf.html")
            html_content = template.render(view=report_view)

            # 6. Generate PDF
            # WeasyPrint is CPU intensive and blocking.
            await self.progress.emit_progress(execution_id, task_key, "Writing PDF file (this may take a moment)...", 0.9)
            
            # WeasyPrint requires GTK3 on Windows, assume it's set up per knowledge base.
            pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()

            # 7. Complete
            await self.progress.emit_progress(execution_id, task_key, "Done", 1.0)

            return pdf_bytes

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
