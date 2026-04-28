"""Service for generating detailed PDF reports using WeasyPrint and Jinja2.

Adheres to V2 Architecture (De-Generator Policy / SDUI Block Building):
- Completely dynamic: Iterates over frozen_context.ui_hints_snapshot to render blocks.
- No static domain models.
- Resolves XAI citations and justifications automatically.
"""

import logging
from pathlib import Path

import weasyprint
from jinja2 import Environment, FileSystemLoader

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import ReportDataDTO

logger = logging.getLogger(__name__)


class PdfReportService:
    """Service to generate PDF reports dynamically from V2 execution data."""

    def __init__(self, repository: AbstractWorkflowRepository):
        """Initialize the service.

        Args:
            repository: Workflow repository.
        """
        self.repository = repository

        # Suppress verbose fontTools logs (used by WeasyPrint)
        logging.getLogger("fontTools.subset").setLevel(logging.WARNING)
        logging.getLogger("fontTools.ttLib").setLevel(logging.WARNING)

        # Setup Jinja2 env
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))

        # Lightweight Custom Markdown Filter for Bold (**) and Italic (*)

        def md_filter(text: str) -> str:
            if not isinstance(text, str):
                return str(text) if text else ""
            try:
                import markdown  # type: ignore[import-untyped, unused-ignore]

                return str(markdown.markdown(text, extensions=["extra", "nl2br"]))
            except ImportError as e:
                from backend_v2.exceptions import ConfigurationError

                msg = "Fail-Fast: 'markdown' package is required for PDF Markdown rendering but is not installed."
                logger.error("[PdfReportService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise ConfigurationError(msg) from e

        self.env.filters["md"] = md_filter

    async def generate_execution_html(self, execution_id: str, report_dto: ReportDataDTO | None = None) -> str:
        """Generates a dynamic HTML string for the given execution ID using static DTO constraints.

        Args:
            execution_id: The execution UUID.
            report_dto: Optional pre-assembled ReportDataDTO.

        Returns:
            str: The generated HTML content.
        """
        try:
            # 1. Fetch Data
            execution = await self.repository.get_execution(execution_id)
            if not execution:
                msg = f"Execution {execution_id} not found"
                logger.error("[PdfReportService] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
                raise AppException(
                    message=msg,
                    status_code=404,
                    details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                )

            target_locale = execution.metadata.get("target_locale", "en") if execution.metadata else "en"

            # Fetch Workflow Name for Header
            workflow_id = execution.workflow_id
            workflow_name = "Dynamic Workflow Execution"
            if report_dto and report_dto.profile_name:
                title_obj = report_dto.profile_name
                workflow_name = title_obj.get(target_locale, title_obj.get("en", workflow_name))
            elif workflow_id:
                workflow_dict = await self.repository.get_workflow_by_id(workflow_id)
                if workflow_dict and "name" in workflow_dict:
                    name_obj = workflow_dict["name"]
                    # Assuming I18nText dict or just string
                    if isinstance(name_obj, dict):
                        workflow_name = name_obj.get("default_locale", workflow_name)
                    else:
                        workflow_name = str(name_obj)

            # 2. Extract context and results
            frozen_context = execution.frozen_context.model_dump() if execution.frozen_context else {}
            from backend_v2.models.state import StateProjector

            projector = StateProjector()
            results = projector.fold_trace(execution.execution_trace)

            # 2.5 Generate static charts if DTO is provided
            charts = {}
            if report_dto and report_dto.layouts:
                from backend_v2.utils.static_charts import generate_radar_chart, generate_scatter_chart

                for idx, layout in enumerate(report_dto.layouts):
                    try:
                        if layout.preset_view in ("radar_3d", "3d_complex"):
                            b64_data = generate_radar_chart(layout.axes)
                            if b64_data:
                                charts[idx] = b64_data
                            else:
                                from backend_v2.exceptions import ConfigurationError

                                msg = f"generate_radar_chart returned empty data for layout {idx}"
                                raise ConfigurationError(msg)
                        elif layout.preset_view in ("matrix_2d", "2d_compare", "matrix_3d", "3d_matrix"):
                            b64_data = generate_scatter_chart(layout.axes)
                            if b64_data:
                                charts[idx] = b64_data
                            else:
                                from backend_v2.exceptions import ConfigurationError

                                msg = f"generate_scatter_chart returned empty data for layout {idx}"
                                raise ConfigurationError(msg)
                    except Exception as e:
                        msg = f"Failed to render PDF charts for layout {idx}: {e}"
                        logger.error(
                            "[PdfReportService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True
                        )
                        raise AppException(
                            message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                        ) from e

            # 3. Render Template
            template = self.env.get_template("report_template.jinja2")

            from datetime import datetime

            printed_at = datetime.now().astimezone().strftime("%d.%m.%Y %H:%M")

            import json
            l10n_dir = Path(__file__).parent.parent.parent / "client_app_v2" / "lib" / "l10n"
            l10n_dict = {"en": {}, "fi": {}}
            
            try:
                with open(l10n_dir / "app_en.arb", "r", encoding="utf-8") as f:
                    l10n_dict["en"] = json.load(f)
                with open(l10n_dir / "app_fi.arb", "r", encoding="utf-8") as f:
                    l10n_dict["fi"] = json.load(f)
            except Exception as e:
                logger.warning("Failed to load .arb files, falling back to static dict: %s", e)
                l10n_dict = {
                    "en": {
                        "lblLogicMatrix": "Logic Matrix",
                        "score": "Score",
                        "atomicBreakdownTitle": "Level Breakdown",
                        "xaiJustification": "Justification",
                        "normalizedScore": "100 %",
                        "matrixEvaluativeAsteriskLegend": "* Matrix score is included in the global average.",
                    },
                    "fi": {
                        "lblLogicMatrix": "Logiikkamatriisi",
                        "score": "Pisteet",
                        "atomicBreakdownTitle": "Tasojakauma",
                        "xaiJustification": "Perustelut",
                        "normalizedScore": "100 %",
                        "matrixEvaluativeAsteriskLegend": "* Matriisi lasketaan mukaan kokonaisarvosanan keskiarvoon.",
                    },
                }
            l10n = l10n_dict.get(target_locale, l10n_dict["en"])

            html_content = template.render(
                execution_id=execution_id,
                workflow_name=workflow_name,
                frozen_context=frozen_context,
                results=results,
                report_data=report_dto,
                printed_at=printed_at,
                charts=charts,
                l10n=l10n,
            )
            return str(html_content)

        except AppException:
            # Re-raise known AppExceptions (e.g. 404) as-is
            raise

        except Exception as e:
            msg = f"HTML generation failed: {e}"
            logger.error("[PdfReportService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "original_error": str(e)},
            ) from e

    async def generate_execution_pdf(self, execution_id: str, report_dto: ReportDataDTO | None = None) -> bytes:
        """Generates a dynamic PDF for the given execution ID using static DTO constraints.

        Args:
            execution_id: The execution UUID.
            report_dto: Optional pre-assembled ReportDataDTO.

        Returns:
            bytes: The generated PDF data.
        """
        try:
            html_content = await self.generate_execution_html(execution_id, report_dto)

            # 4. Generate PDF
            import asyncio

            loop = asyncio.get_running_loop()

            def _render_pdf() -> bytes:
                # Type safe cast since write_pdf returns bytes
                pdf_data = weasyprint.HTML(string=html_content).write_pdf()
                return bytes(pdf_data) if pdf_data else b""

            pdf_bytes = await loop.run_in_executor(None, _render_pdf)

            return pdf_bytes

        except AppException:
            # Re-raise known AppExceptions (e.g. 404) as-is
            raise

        except Exception as e:
            msg = f"PDF generation failed: {e}"
            logger.error("[PdfReportService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "original_error": str(e)},
            ) from e
