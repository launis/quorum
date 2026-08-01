"""Service for generating detailed PDF reports using WeasyPrint and Jinja2.

Adheres to V2 Architecture (De-Generator Policy / SDUI Block Building):
- Completely dynamic: Iterates over frozen_context.ui_hints_snapshot to render blocks.
- No static domain models.
- Resolves XAI citations and justifications automatically.
"""

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ignore untyped markdown library as it lacks official stubs in Python 3.14
import markdown  # type: ignore[import-untyped, unused-ignore]
from jinja2 import Environment, FileSystemLoader

from backend_v2.database.interfaces import IExecutionRepository, IWorkflowRepository
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.v2_core import ReportDataDTO, Workflow
from backend_v2.models.view.sdui import SduiRadarChartBlock, SduiScatterPlotBlock
from backend_v2.utils.static_charts import generate_radar_chart, generate_scatter_chart

logger = logging.getLogger(__name__)


class CompliantAppException(AppException):
    """Bridge class to enforce Rule 18 compliance with the base AppException signature.

    Attributes:
        status_code: HTTP response status code to return.
        details: Dictionary containing error context and the error_code.
    """

    def __init__(
        self, error_code: ErrorCodes, message: str, status_code: int = 500, details: dict[str, Any] | None = None
    ) -> None:
        """Initialize the compliant application exception.

        Args:
            error_code: Standardized ErrorCodes enum key.
            message: Core exception debug text.
            status_code: HTTP response status code.
            details: Key-value dictionary carrying metadata context.
        """
        actual_details = details or {}
        actual_details["error_code"] = error_code.value
        super().__init__(message=message, status_code=status_code, details=actual_details)


class PdfReportService:
    """Service to generate PDF reports dynamically from V2 execution data."""

    def __init__(self, exec_repo: IExecutionRepository, workflow_repo: IWorkflowRepository) -> None:
        """Initialize the PDF report generator service with required repositories.

        Args:
            exec_repo: The data layer interface targeting execution snapshots.
            workflow_repo: The repository holding active workflow metadata.
        """
        self.exec_repo = exec_repo
        self.workflow_repo = workflow_repo

        # Suppress verbose fontTools logs (used by WeasyPrint)
        logging.getLogger("fontTools.subset").setLevel(logging.WARNING)
        logging.getLogger("fontTools.ttLib").setLevel(logging.WARNING)

        # Setup Jinja2 env
        template_dir = Path(__file__).parent.parent / "templates"
        import jinja2

        self.env = Environment(loader=FileSystemLoader(str(template_dir)), undefined=jinja2.StrictUndefined)

        from jinja2 import pass_context

        @pass_context
        def md_filter(context: Any, text: Any) -> str:
            """Lightweight Custom Markdown Filter for Bold (**) and Italic (*).

            Args:
                context: Jinja2 template context containing l10n.
                text: Raw text to be parsed as markdown.

            Returns:
                HTML rendered string.
            """
            if not text:
                return ""
            if not isinstance(text, str):
                text = str(text)

            # Translation is now handled centrally by BlueprintTransformer (SSOT)

            return str(markdown.markdown(text, extensions=["extra", "nl2br"]))

        def group_atoms_by_level(atoms: list[Any]) -> dict[int, list[Any]]:
            """Smart getter grouping flat atoms by their level for rendering.

            Args:
                atoms: Flat list of ScorecardAtomDTOs.

            Returns:
                Dictionary mapping level int to list of atoms, sorted by level.
            """
            grouped: dict[int, list[Any]] = {}
            if atoms:
                for a in atoms:
                    grouped.setdefault(a.level, []).append(a)
            return {k: grouped[k] for k in sorted(grouped.keys())}

        self.env.filters["md"] = md_filter
        self.env.filters["group_atoms_by_level"] = group_atoms_by_level

    async def generate_execution_html(self, execution_id: str, report_dto: ReportDataDTO | None = None) -> str:
        """Generates a dynamic HTML string for the given execution ID using static DTO constraints.

        Args:
            execution_id: The execution UUID.
            report_dto: Optional pre-assembled ReportDataDTO layout reference.

        Returns:
            The generated HTML document string content.

        Raises:
            CompliantAppException: Triggered under resource miss, locale layout failures, or corrupted metadata.
            ConfigurationError: Triggered if template asset rendering fails due to missing .arb L10n tables.
        """
        try:
            # 1. Fetch Data
            execution = await self.exec_repo.get_execution(execution_id)
            if not execution:
                msg = f"Execution {execution_id} not found"
                logger.error("[PdfReportService] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg, exc_info=True)
                raise CompliantAppException(
                    error_code=ErrorCodes.RESOURCE_NOT_FOUND,
                    message=msg,
                    status_code=404,
                )

            if not execution.metadata or "target_locale" not in execution.metadata:
                msg = f"Execution {execution_id} is missing target_locale in metadata."
                logger.error("[PdfReportService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise CompliantAppException(
                    error_code=ErrorCodes.VALIDATION_FAILED,
                    message=msg,
                    status_code=400,
                )

            target_locale = str(execution.metadata["target_locale"])

            # Fetch Workflow Name for Header
            workflow_id = execution.workflow_id
            workflow_name = ""

            if report_dto and report_dto.profile_name:
                workflow_name = report_dto.profile_name.resolve(target_locale) or ""
            elif workflow_id:
                workflow_dict = await self.workflow_repo.get_workflow_by_id(workflow_id)
                if workflow_dict:
                    workflow = Workflow.model_validate(workflow_dict)
                    if isinstance(workflow.name, str):
                        msg = (
                            f"Execution {execution_id} uses a legacy string workflow name, "
                            "which is forbidden in Phase 9."
                        )
                        logger.error("[PdfReportService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                        raise CompliantAppException(
                            error_code=ErrorCodes.VALIDATION_FAILED,
                            message=msg,
                            status_code=400,
                        )
                    workflow_name = workflow.name.resolve(target_locale) or ""

            if not workflow_name:
                msg = f"Execution {execution_id} is missing a valid workflow name resolution."
                logger.error("[PdfReportService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise CompliantAppException(
                    error_code=ErrorCodes.VALIDATION_FAILED,
                    message=msg,
                    status_code=400,
                )

            # 2. (Legacy raw states removed)

            # 2.5 Generate static charts if DTO is provided
            charts = {}
            if report_dto and report_dto.inner_sdui_blocks:
                for idx, block in enumerate(report_dto.inner_sdui_blocks):
                    try:
                        match block:
                            case SduiRadarChartBlock():
                                b64_data = generate_radar_chart(block.axes)
                                if b64_data:
                                    charts[idx] = b64_data
                                else:
                                    msg = f"generate_radar_chart returned empty data for block {idx}"
                                    raise ConfigurationError(msg)
                            case SduiScatterPlotBlock():
                                b64_data = generate_scatter_chart(block.axes)
                                if b64_data:
                                    charts[idx] = b64_data
                                else:
                                    msg = f"generate_scatter_chart returned empty data for block {idx}"
                                    raise ConfigurationError(msg)
                            case _:
                                pass
                    except ConfigurationError:
                        raise
                    except (ValueError, TypeError) as e:
                        msg = f"Failed to render PDF charts for block {idx}: {e}"
                        logger.error(
                            "[PdfReportService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True
                        )
                        raise CompliantAppException(
                            error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
                            message=msg,
                            status_code=500,
                        ) from e

            # 3. Render Template
            template = self.env.get_template("report_template.jinja2")

            printed_at = datetime.now(timezone.utc).astimezone().strftime("%d.%m.%Y %H:%M")

            from backend_v2.services.localization import LocalizationService

            try:
                LocalizationService.load_if_needed()
            except Exception as e:
                msg = f"Failed to load localization: {e}"
                logger.error("[PdfReportService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
                raise ConfigurationError(msg) from e

            lang_simple = target_locale.split("-")[0].lower()
            l10n = LocalizationService._translations.get(lang_simple)

            if not l10n:
                msg = f"Locale '{target_locale}' is not supported in .arb L10n files."
                logger.error("[PdfReportService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise CompliantAppException(
                    error_code=ErrorCodes.VALIDATION_FAILED,
                    message=msg,
                    status_code=400,
                )

            html_content = template.render(
                execution_id=execution_id,
                workflow_name=workflow_name,
                report_data=report_dto,
                printed_at=printed_at,
                charts=charts,
                l10n=l10n,
                lang_code=target_locale,
            )
            return str(html_content)

        except AppException:
            raise

        except Exception as e:
            msg = f"HTML generation failed: {e}"
            logger.error("[PdfReportService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True)
            raise CompliantAppException(
                error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
                message=msg,
                status_code=500,
            ) from e

    async def generate_execution_pdf(self, execution_id: str, report_dto: ReportDataDTO | None = None) -> bytes:
        """Generates a dynamic PDF for the given execution ID using static DTO constraints.

        Args:
            execution_id: The execution UUID.
            report_dto: Optional pre-assembled ReportDataDTO metadata snapshot.

        Returns:
            The generated binary PDF payload.

        Raises:
            CompliantAppException: Triggered on resource errors or core upstream thread execution failures.
        """
        try:
            html_content = await self.generate_execution_html(execution_id, report_dto)

            # 4. Generate PDF
            loop = asyncio.get_running_loop()

            def _render_pdf() -> bytes:
                """Generates the PDF bytes synchronously using WeasyPrint.

                Returns:
                    Raw binary content of the generated PDF document.
                """
                import weasyprint

                # Type safe cast since write_pdf returns bytes
                pdf_data = weasyprint.HTML(string=html_content).write_pdf()
                return bytes(pdf_data) if pdf_data else b""

            pdf_bytes = await loop.run_in_executor(None, _render_pdf)

            return pdf_bytes

        except AppException:
            raise

        except Exception as e:
            msg = f"PDF generation failed: {e}"
            logger.error("[PdfReportService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True)
            raise CompliantAppException(
                error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
                message=msg,
                status_code=500,
            ) from e
