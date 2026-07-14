import logging
from typing import Any

from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.v2_core import ReportDataDTO
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    DimensionDisplay,
    ReportView,
    ScoreCardDisplay,
    SduiQuoteCard,
    SduiWarningCard,
    SectionType,
    UiSection,
)

logger = logging.getLogger(__name__)


class SduiMapperService:
    """Service to map execution DTOs to Server-Driven UI models."""

    def map_evidence_to_sdui(self, evidence: QuoteEvidenceDTO) -> AnySduiBlock:
        """Map QuoteEvidenceDTO to SduiQuoteCard or SduiWarningCard.

        Performs Dual-Reporting Telemetry logging for hallucinated aliases.
        """
        # Telemetry logging for hallucinations (Dual-Reporting)
        if not evidence.is_verified or evidence.unverified_aliases:
            logger.warning("[TELEMETRY] Hallucination detected. Unverified aliases: %s", evidence.unverified_aliases)
            return SduiWarningCard(
                message=f"Hallucinated citations detected: {', '.join(evidence.unverified_aliases)}",
                quote_text=evidence.quote,
            )

        return SduiQuoteCard(quote=evidence.quote, source_aliases=evidence.verified_source_ids, citations=[])

    def map_report(self, report: ReportDataDTO, execution_id: str = "") -> ReportView:
        """Alias for map_report_to_sdui to satisfy existing test bindings if any."""
        return self.map_report_to_sdui(report, execution_id)

    def map_report_to_sdui(self, report: ReportDataDTO, execution_id: str = "") -> ReportView:
        """Map ReportDataDTO to ReportView."""
        # Phase B1: Metrics & Telemetry (Capture global_score, strictness_level, has_warning)
        metrics: dict[str, Any] = {}
        if report.global_score is not None:
            metrics["global_score"] = report.global_score
        if report.strictness_level is not None:
            metrics["strictness_level"] = report.strictness_level

        status_theme = "warning" if report.has_warning else "success"

        sections: list[UiSection] = []

        # Phase B1: Map global content_blocks to MARKDOWN_BLOCK sections
        if report.content_blocks:
            sections.append(
                UiSection(
                    id="global_content", type=SectionType.MARKDOWN_BLOCK, title="Yhteenveto", data=report.content_blocks
                )
            )

        # Phase B1: Layout-Driven Mapping
        for idx, layout in enumerate(report.layouts):
            # Phase B1: ScoreCard Translation
            if layout.preset_view in ("1d_metrics", "3d_matrix"):
                dimensions = []
                for axis in layout.axes:
                    dimensions.append(
                        DimensionDisplay(
                            dimension_id=axis.block_id,
                            dimension_label=axis.name,
                            score=axis.score if axis.score is not None else 0.0,
                            max_score=axis.scale_max if axis.scale_max is not None else 1.0,
                            weight=1.0,  # Default weight
                            reasoning=axis.row_explanation,
                        )
                    )

                score_card = ScoreCardDisplay(
                    agent_name=report.scoring_engine_name or "Audit",
                    total_score=report.global_score if report.global_score is not None else 0.0,
                    min_score=0,
                    max_score=100,
                    verdict=layout.description.resolve() if layout.description else "",
                    dimensions=dimensions,
                )

                title = layout.title.resolve() if layout.title else "Analyysi"
                sections.append(
                    UiSection(
                        id=f"layout_scorecard_{idx}",
                        type=SectionType.SCORE_CARD,
                        title=title,
                        data=score_card.model_dump(mode="json"),
                    )
                )

            # Phase B1: Layout-specific synthesis_blocks
            if layout.synthesis_blocks:
                title = layout.title.resolve() if layout.title else "Synteesi"
                sections.append(
                    UiSection(
                        id=f"layout_synthesis_{idx}",
                        type=SectionType.MARKDOWN_BLOCK,
                        title=title,
                        data=layout.synthesis_blocks,
                    )
                )

        # Phase B1: XAI Transparency
        if report.mcp_tool_audit:
            sections.append(
                UiSection(
                    id="xai_mcp_audit",
                    type=SectionType.USAGE_STATS,
                    title="Auditointityökalujen käyttö",
                    data=[trace.model_dump(mode="json") for trace in report.mcp_tool_audit],
                )
            )

        if report.grouped_extensions:
            sections.append(
                UiSection(
                    id="xai_extensions",
                    type=SectionType.USAGE_STATS,
                    title="Laajennettu Analytiikka",
                    data=report.grouped_extensions,
                )
            )

        return ReportView(
            view_id=execution_id,
            metrics=metrics,
            status_theme=status_theme,
            sections=sections,
        )
