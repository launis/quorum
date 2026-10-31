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

import markdown
from jinja2 import Environment, FileSystemLoader, StrictUndefined, pass_context

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    SduiQuadrantMatrixBlock,
    SduiRadarChartBlock,
    SduiScatterPlotBlock,
)
from backend_v2.services.localization import LocaleTranslationsDTO, LocalizationService
from backend_v2.utils.static_charts import (
    generate_quadrant_matrix_chart,
    generate_radar_chart,
    generate_scatter_chart,
)

logger = logging.getLogger(__name__)

__all__ = ["PdfReportService"]


@pass_context
def _md_filter(context: Any, text: Any) -> str:
    """Render bold and italic markdown syntax into HTML.

    Args:
        context: Jinja2 template context containing l10n.
        text: Raw text to be parsed as markdown.

    Returns:
        HTML rendered string.
    """
    _ = context
    if not text:
        return ""
    if not isinstance(text, str):
        text = str(text)

    return str(markdown.markdown(text, extensions=["extra", "nl2br"]))


def _group_atoms_by_level(atoms: list[ScorecardAtomDTO]) -> dict[int, list[ScorecardAtomDTO]]:
    """Group flat scorecard atoms by their integer rubric level in ascending order.

    Args:
        atoms: Flat list of ScorecardAtomDTO instances.

    Returns:
        Dictionary mapping rubric level integer to list of atoms, sorted by level.
    """
    grouped: dict[int, list[ScorecardAtomDTO]] = {}
    if atoms:
        for atom in atoms:
            grouped.setdefault(atom.level, []).append(atom)
    return {k: grouped[k] for k in sorted(grouped.keys())}


def _normalize_lineage_claims(claims: list[str] | None) -> list[str]:
    """Normalize and deduplicate topological short-circuit and Toulmin falsification claims.

    Args:
        claims: Sequence of lineage claim strings attached to an SDUI block.

    Returns:
        Ordered list of non-empty stripped claim strings.
    """
    # Phase 3, Step 3.2: Deterministic lineage normalization for PDF parity
    if not claims:
        return []
    seen: list[str] = []
    for claim in claims:
        stripped = claim.strip()
        if stripped and stripped not in seen:
            seen.append(stripped)
    return seen


def _raise_unrecognized_sdui_block(block_type: str) -> None:
    """Trigger fail-fast exception for unrecognized SDUI blocks in Jinja2 templates.

    Args:
        block_type: Unrecognized SDUI block discriminator identifier.

    Raises:
        AppException: Always raised with ErrorCodes.CONFIGURATION_ERROR (HTTP 500).
    """
    msg = f"Strict Fail-Fast: Unrecognized SDUI block_type '{block_type}' encountered during PDF rendering."
    logger.error("[PdfReportService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
    raise AppException(
        message=msg,
        status_code=500,
        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "block_type": block_type},
    )


class PdfReportService:
    """Service to generate PDF reports dynamically from V2 execution data.

    Acts as a pure Dumb Painter: transforms ReportDataDTO directly into HTML/PDF
    without database queries or fallback branches.
    """

    def __init__(self) -> None:
        """Initialize the PDF report generator service and Jinja2 environment."""
        # Suppress verbose fontTools logs (used by WeasyPrint)
        logging.getLogger("fontTools.subset").setLevel(logging.WARNING)
        logging.getLogger("fontTools.ttLib").setLevel(logging.WARNING)

        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)), undefined=StrictUndefined)
        self.env.filters["md"] = _md_filter
        self.env.filters["group_atoms_by_level"] = _group_atoms_by_level
        self.env.filters["normalize_lineage_claims"] = _normalize_lineage_claims
        self.env.globals["raise_unrecognized_sdui_block"] = _raise_unrecognized_sdui_block

    def _render_block_charts(self, blocks: list[AnySduiBlock], target_locale: str) -> dict[int, str]:
        """Render base64 chart images for radar, scatter, and quadrant SDUI blocks.

        Args:
            blocks: Ordered list of SDUI blocks from the report DTO.
            target_locale: Resolved BCP-47 locale string for chart labels.

        Returns:
            Dictionary mapping block index to base64-encoded PNG string.

        Raises:
            ConfigurationError: If chart generation returns empty payload (ErrorCodes.CONFIGURATION_ERROR).
            AppException: If chart rendering raises ValueError or TypeError (ErrorCodes.INTERNAL_SERVER_ERROR).
        """
        charts: dict[int, str] = {}
        for idx, block in enumerate(blocks):
            try:
                match block:
                    case SduiRadarChartBlock():
                        b64_data = generate_radar_chart(block.axes)
                        if b64_data:
                            charts[idx] = b64_data
                        else:
                            msg = f"generate_radar_chart returned empty data for block {idx}"
                            logger.error(
                                "[PdfReportService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True
                            )
                            raise ConfigurationError(msg)
                    case SduiScatterPlotBlock():
                        b64_data = generate_scatter_chart(block.axes)
                        if b64_data:
                            charts[idx] = b64_data
                        else:
                            msg = f"generate_scatter_chart returned empty data for block {idx}"
                            logger.error(
                                "[PdfReportService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True
                            )
                            raise ConfigurationError(msg)
                    case SduiQuadrantMatrixBlock():
                        b64_data = generate_quadrant_matrix_chart(block.axes, locale=target_locale)
                        if b64_data:
                            charts[idx] = b64_data
                        else:
                            msg = f"generate_quadrant_matrix_chart returned empty data for block {idx}"
                            logger.error(
                                "[PdfReportService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True
                            )
                            raise ConfigurationError(msg)
                    case _:
                        pass
            except ConfigurationError:
                raise
            except (ValueError, TypeError) as e:
                msg = f"Failed to render PDF charts for block {idx}: {e}"
                logger.error("[PdfReportService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                ) from e
        return charts

    def _resolve_localization(self, target_locale: str) -> LocaleTranslationsDTO:
        """Load and validate localization DTO for the target locale.

        Args:
            target_locale: Requested locale code (e.g., 'fi' or 'en-US').

        Returns:
            Strictly typed LocaleTranslationsDTO instance.

        Raises:
            ConfigurationError: If localization files fail to load (ErrorCodes.CONFIGURATION_ERROR).
            AppException: If the requested locale is unsupported (ErrorCodes.VALIDATION_FAILED).
        """
        try:
            LocalizationService.load_if_needed()
        except Exception as e:
            msg = f"Failed to load localization: {e}"
            logger.error("[PdfReportService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise ConfigurationError(msg) from e

        lang_simple = target_locale.split("-")[0].lower()
        l10n = LocalizationService.get_translations(lang_simple)

        if not l10n:
            msg = f"Locale '{target_locale}' is not supported in .arb L10n files."
            logger.error("[PdfReportService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return l10n

    async def generate_execution_html(
        self, execution_id: str, report_dto: ReportDataDTO, locale: str | None = None
    ) -> str:
        """Generate a dynamic HTML string using static DTO constraints.

        Args:
            execution_id: The execution Opaque Stripe ID.
            report_dto: Pre-assembled ReportDataDTO layout reference.
            locale: Optional BCP-47 locale string for i18n resolution (defaults to "fi").

        Returns:
            The generated HTML document string content.

        Raises:
            ConfigurationError: Triggered if chart generation returns empty data or L10n files fail to load
                (ErrorCodes.CONFIGURATION_ERROR).
            AppException: Triggered on unsupported locale (ErrorCodes.VALIDATION_FAILED) or template/chart
                rendering failures (ErrorCodes.INTERNAL_SERVER_ERROR).
        """
        try:
            target_locale = "fi"
            if locale:
                target_locale = locale

            workflow_name = ""
            if report_dto.profile_name:
                resolved_wf_name = report_dto.profile_name.resolve(target_locale)
                if resolved_wf_name:
                    workflow_name = resolved_wf_name

            charts: dict[int, str] = {}
            if report_dto.inner_sdui_blocks:
                charts = self._render_block_charts(report_dto.inner_sdui_blocks, target_locale)

            template = self.env.get_template("report_template.jinja2")
            printed_at = datetime.now(timezone.utc).astimezone().strftime("%d.%m.%Y %H:%M")
            l10n = self._resolve_localization(target_locale)

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
        """Generate a dynamic PDF binary payload using static DTO constraints.

        Args:
            execution_id: The execution Opaque Stripe ID.
            report_dto: Pre-assembled ReportDataDTO metadata snapshot.
            locale: Optional BCP-47 locale string for i18n resolution (defaults to "fi").

        Returns:
            The generated binary PDF payload.

        Raises:
            ConfigurationError: Propagated from HTML/chart/localization initialization
                (ErrorCodes.CONFIGURATION_ERROR).
            AppException: Triggered on validation errors (ErrorCodes.VALIDATION_FAILED) or WeasyPrint
                rendering failures (ErrorCodes.INTERNAL_SERVER_ERROR).
        """
        try:
            html_content = await self.generate_execution_html(execution_id, report_dto=report_dto, locale=locale)

            loop = asyncio.get_running_loop()

            def _render_pdf() -> bytes:
                """Generate the PDF bytes synchronously using WeasyPrint.

                Returns:
                    Raw binary content of the generated PDF document.
                """
                import weasyprint

                pdf_data = weasyprint.HTML(string=html_content).write_pdf()
                if pdf_data:
                    return bytes(pdf_data)
                return b""

            return await loop.run_in_executor(None, _render_pdf)

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
