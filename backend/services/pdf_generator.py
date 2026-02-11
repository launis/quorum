"""Service for generating detailed PDF reports using WeasyPrint and Jinja2."""

import logging
from pathlib import Path
from typing import Protocol, runtime_checkable

# Optional imports handled gracefully could be considered, but dependencies are mandated in task.
import weasyprint  # type: ignore
from jinja2 import Environment, FileSystemLoader

from backend.api.bff_transformer import ReportTransformer
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
                raise ValueError(f"Execution {execution_id} not found")

            # 3. Transform
            await self.progress.emit_progress(execution_id, task_key, "Analyzing results...", 0.10)
            # Use dump() compatibility if it's a Pydantic object, or dict if it's already dict
            # BFF Transformer generally expects a dict representation of the execution
            ex_data = execution.model_dump() if hasattr(execution, 'model_dump') else execution
            # Or if execution is Execution object, we might need model_dump.
            # Assuming Repository returns Pydantic V2 model.

            report_view = self.transformer.transform(ex_data)

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

                            # 1. Try dimension_label (New Standard) or direct label in data (Legacy/Loose)
                            display_label = d.get("dimension_label") or d.get("label") or d.get("name")

                            # 2. Lookup: If no label yet, try to map from ID using Matrix Map
                            tech_id = d.get("dimension_id") or d.get("id")
                            if not display_label and tech_id and tech_id in matrix_map:
                                display_label = matrix_map[tech_id]

                            # 3. Strict Mode: No fallback to ID.
                            if not display_label:
                                raise ValueError(f"Strict Label Resolution Failed in PDF: Dimension '{tech_id}' has no label.")

                            if display_label:
                                try:
                                    val = float(d.get("score", 0))
                                    scores[display_label] = val
                                except (ValueError, TypeError):
                                    pass
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

                elif section.type == SectionType.LOGIC_ANALYSIS and section.data:
                    # Logic Matrix Bubble Chart
                    # Extract scores (Standardized keys from domain model)
                    cog = section.data.get("cognitive_level") or section.data.get("kognitiivinen_taso", {})
                    # Handle both Pydantic models (dict) and raw dicts
                    if hasattr(cog, "dict"): cog = cog.dict()
                    
                    bloom = float(cog.get("bloom_score", 0))
                    strat = float(cog.get("strategic_score", 0))
                    
                    # Toulmin score might be flat in data or calculated
                    toulmin_score = float(section.data.get("toulmin_score", 0))
                    
                    if bloom > 0 and strat > 0:
                        chart_b64 = ChartService.generate_bubble_chart(
                            x_val=bloom,
                            y_val=strat,
                            size_val=toulmin_score,
                            title="Logic Matrix Position"
                        )
                        section.data["logic_chart_image"] = chart_b64

                elif section.type == SectionType.FACT_CHECK and section.data:
                    # Preprocess for Template (English Standardization)
                    
                    # 1. Facts
                    raw_facts = section.data.get("fact_checks") or section.data.get("faktantarkistus_rfi", [])
                    processed_facts = []
                    for f in raw_facts:
                        # Normalize to dict
                        item = f.dict() if hasattr(f, "dict") else f
                        
                        # Map Legacy to English if needed
                        claim = item.get("claim") or item.get("vaite")
                        result = item.get("verification_result") or item.get("verifiointi_tulos")
                        source = item.get("source_or_reasoning") or item.get("lahde_tai_paattely")
                        is_ver = item.get("is_verified") 
                        
                        # Fallback calculation if boolean missing
                        if is_ver is None and result:
                            # Check common strings for verified status
                            is_ver = str(result).lower() in ["verified", "vahvistettu"]

                        processed_facts.append({
                            "claim": claim,
                            "verification_result": result,
                            "source_or_reasoning": source,
                            "is_verified": is_ver
                        })
                    section.data["processed_facts"] = processed_facts

                    # 2. Ethics (Overseer also populates this section type in BFF)
                    raw_ethics = section.data.get("ethical_issues") or section.data.get("eettiset_havainnot", [])
                    processed_ethics = []
                    for e in raw_ethics:
                        item = e.dict() if hasattr(e, "dict") else e
                        processed_ethics.append({
                            "issue_type": item.get("issue_type") or item.get("ongelma_tyyppi"),
                            "severity": item.get("severity") or item.get("vakavuus"),
                            "description": item.get("description") or item.get("kuvaus"),
                            "is_critical": item.get("is_critical") or (str(item.get("severity")).lower() == "critical")
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
