import logging
from typing import Any

from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.enums import ExecutionStatus, VisualIntent
from backend_v2.models.v2_core import I18nText, ReportDataDTO
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    DimensionDisplay,
    ReportView,
    ScoreCardDisplay,
    SduiNACard,
    SduiQuoteCard,
    SduiWarningCard,
    SectionType,
    UiSection,
)

logger = logging.getLogger(__name__)


class SduiMapperService:
    """Service to map execution DTOs to Server-Driven UI models."""

    def map_evidence_to_sdui(self, evidence: QuoteEvidenceDTO, lang: str = "fi") -> AnySduiBlock:
        """Map QuoteEvidenceDTO to SduiQuoteCard or SduiWarningCard.

        Performs Dual-Reporting Telemetry logging for hallucinated aliases.
        """
        # Telemetry logging for hallucinations (Dual-Reporting)
        if not evidence.is_verified or evidence.unverified_aliases:
            logger.warning("[TELEMETRY] Hallucination detected. Unverified aliases: %s", evidence.unverified_aliases)
            warning_msg = I18nText(
                default_locale="fi",
                translations={"fi": "Hallusinoituja lainauksia havaittu:", "en": "Hallucinated citations detected:"},
            ).resolve(lang)
            return SduiWarningCard(
                message=f"{warning_msg} {', '.join(evidence.unverified_aliases)}",
                quote_text=evidence.quote,
            )

        return SduiQuoteCard(quote=evidence.quote, source_aliases=evidence.verified_source_ids, citations=[])

    def map_report(self, report: ReportDataDTO, execution_id: str = "", lang: str = "fi") -> ReportView:
        """Alias for map_report_to_sdui to satisfy existing test bindings if any."""
        return self.map_report_to_sdui(report, execution_id, lang)

    def map_report_to_sdui(self, report: ReportDataDTO, execution_id: str = "", lang: str = "fi") -> ReportView:
        """Map ReportDataDTO to ReportView."""
        # Phase B1: Metrics & Telemetry (Capture global_score, strictness_level, has_warning)
        metrics: dict[str, Any] = {}
        if report.global_score is not None:
            metrics["global_score"] = report.global_score
        if report.strictness_level is not None:
            metrics["strictness_level"] = report.strictness_level

        status_theme = VisualIntent.WARNING if report.has_warning else VisualIntent.SUCCESS

        sections: list[UiSection] = []

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

                title = (
                    layout.title.resolve(lang)
                    if layout.title
                    else I18nText(default_locale="fi", translations={"fi": "Analyysi", "en": "Analysis"}).resolve(lang)
                )
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
                title = (
                    layout.title.resolve(lang)
                    if layout.title
                    else I18nText(default_locale="fi", translations={"fi": "Synteesi", "en": "Synthesis"}).resolve(lang)
                )
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
            title_audit = I18nText(
                default_locale="fi", translations={"fi": "Auditointityökalujen käyttö", "en": "Audit Tool Usage"}
            ).resolve(lang)
            sections.append(
                UiSection(
                    id="xai_mcp_audit",
                    type=SectionType.USAGE_STATS,
                    title=title_audit,
                    data=[trace.model_dump(mode="json") for trace in report.mcp_tool_audit],
                )
            )

        if report.grouped_extensions:
            title_ext = I18nText(
                default_locale="fi", translations={"fi": "Laajennettu Analytiikka", "en": "Extended Analytics"}
            ).resolve(lang)
            sections.append(
                UiSection(
                    id="xai_extensions",
                    type=SectionType.USAGE_STATS,
                    title=title_ext,
                    data=report.grouped_extensions,
                )
            )

        # Phase 3a: Map N_A outcomes to SDUI N_A Cards
        na_blocks = []

        na_default_msg = I18nText(
            default_locale="fi", translations={"fi": "Ei sovelleta (N/A)", "en": "Not applicable (N/A)"}
        ).resolve(lang)
        na_rule_prefix = I18nText(
            default_locale="fi", translations={"fi": "Ohitettu säännön perusteella:", "en": "Skipped based on rule:"}
        ).resolve(lang)

        for result in report.results:
            if result.status == ExecutionStatus.N_A:
                reason_msg = na_default_msg
                if result.short_circuit_reason_tda_ids:
                    tda_id = result.short_circuit_reason_tda_ids[0]
                    if tda_id in report.hydrated_references:
                        hydrated = report.hydrated_references[tda_id]
                        reason_msg = f"{na_rule_prefix} {hydrated.resolved_claim}"

                na_blocks.append(
                    SduiNACard(
                        short_circuit_reason_tda_ids=result.short_circuit_reason_tda_ids, message=reason_msg
                    ).model_dump(mode="json")
                )

        if na_blocks:
            title_na = I18nText(
                default_locale="fi", translations={"fi": "Ohitetut Osiot (N/A)", "en": "Skipped Sections (N/A)"}
            ).resolve(lang)
            sections.append(
                UiSection(
                    id="na_outcomes",
                    type=SectionType.MARKDOWN_BLOCK,
                    title=title_na,
                    data=na_blocks,
                )
            )

        return ReportView(
            view_id=execution_id,
            metrics=metrics,
            status_theme=status_theme,
            sections=sections,
            inner_sdui_blocks=[],
        )
