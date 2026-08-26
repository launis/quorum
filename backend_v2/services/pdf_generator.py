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

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.v2_core import ReportDataDTO
from backend_v2.models.view.sdui import SduiRadarChartBlock, SduiScatterPlotBlock
from backend_v2.utils.static_charts import generate_radar_chart, generate_scatter_chart

logger = logging.getLogger(__name__)


class PdfReportService:
    """Service to generate PDF reports dynamically from V2 execution data.

    Acts as a pure Dumb Painter: transforms ReportDataDTO directly into HTML/PDF
    without database queries or fallback branches.
    """

    def __init__(self) -> None:
        """Initialize the PDF report generator service."""
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

        def raise_unrecognized_sdui_block(block_type: str) -> None:
            """Strict fail-fast hook for unrecognized SDUI blocks in Jinja2."""
            msg = f"Strict Fail-Fast: Unrecognized SDUI block_type '{block_type}' encountered during PDF rendering."
            logger.error("[PdfReportService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "block_type": block_type},
            )

        self.env.globals["raise_unrecognized_sdui_block"] = raise_unrecognized_sdui_block

    async def generate_execution_html(
        self, execution_id: str, report_dto: ReportDataDTO, locale: str | None = None
    ) -> str:
        """Generates a dynamic HTML string using static DTO constraints.

        Args:
            execution_id: The execution UUID.
            report_dto: Pre-assembled ReportDataDTO layout reference.
            locale: Optional BCP-47 locale string for i18n resolution (defaults to "fi").

        Returns:
            The generated HTML document string content.

        Raises:
            AppException: Triggered under resource miss, locale layout failures, or corrupted metadata.
            ConfigurationError: Triggered if template asset rendering fails due to missing .arb L10n tables.
        """
        try:
            # 1. Resolve Locale and Profile Name directly from ReportDataDTO
            target_locale = locale or "fi"

            workflow_name = ""
            if report_dto.profile_name:
                workflow_name = report_dto.profile_name.resolve(target_locale) or ""

            # 2. Generate static charts if DTO contains radar or scatter blocks
            charts: dict[int, str] = {}
            if report_dto.inner_sdui_blocks:
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
                        raise AppException(
                            message=msg,
                            status_code=500,
                            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
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
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
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
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            ) from e

    async def generate_execution_pdf(
        self, execution_id: str, report_dto: ReportDataDTO, locale: str | None = None
    ) -> bytes:
        """Generates a dynamic PDF using static DTO constraints.

        Args:
            execution_id: The execution UUID.
            report_dto: Pre-assembled ReportDataDTO metadata snapshot.
            locale: Optional BCP-47 locale string for i18n resolution (defaults to "fi").

        Returns:
            The generated binary PDF payload.

        Raises:
            AppException: Triggered on resource errors or core upstream thread execution failures.
        """
        try:
            html_content = await self.generate_execution_html(execution_id, report_dto=report_dto, locale=locale)

            # 4. Generate PDF
            loop = asyncio.get_running_loop()

            def _render_pdf() -> bytes:
                """Generates the PDF bytes synchronously using WeasyPrint.

                Returns:
                    Raw binary content of the generated PDF document.
                """
                import weasyprint

                pdf_data = weasyprint.HTML(string=html_content).write_pdf()
                return bytes(pdf_data) if pdf_data else b""

            pdf_bytes = await loop.run_in_executor(None, _render_pdf)

            return pdf_bytes

        except AppException:
            raise

        except Exception as e:
            msg = f"PDF generation failed: {e}"
            logger.error("[PdfReportService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            ) from e
