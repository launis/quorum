"""SDUI Mapper Service for Quorum V2 Architecture.

Translates domain execution DTOs and quote evidence records into strictly typed
Server-Driven UI view models and blocks without dictionary type laundering.
"""

from __future__ import annotations

import logging

from backend_v2.models.core_base import I18nText
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus, VisualIntent
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    ReportView,
    ReportViewMetricsDTO,
    SduiNACard,
    SduiQuoteCard,
    SduiWarningCard,
)

__all__ = ["SduiMapperService"]

logger = logging.getLogger(__name__)


class SduiMapperService:
    """Service to map execution DTOs to Server-Driven UI models."""

    def map_evidence_to_sdui(self, evidence: QuoteEvidenceDTO, lang: str = "fi") -> AnySduiBlock:
        """Map QuoteEvidenceDTO to SduiQuoteCard or SduiWarningCard.

        Performs Dual-Reporting Telemetry logging for hallucinated aliases.

        Args:
            evidence: The quote evidence record containing extracted and validated quote tokens.
            lang: Target localized language code for warning card notifications.

        Returns:
            An AnySduiBlock discriminated union instance (SduiQuoteCard or SduiWarningCard).
        """
        # Telemetry logging for hallucinations (Dual-Reporting)
        if not evidence.is_verified or evidence.unverified_aliases:
            logger.warning("[TELEMETRY] Hallucination detected. Unverified aliases: %s", evidence.unverified_aliases)
            warning_msg = I18nText(
                translations={"fi": "Hallusinoituja lainauksia havaittu:", "en": "Hallucinated citations detected:"},
            ).resolve(lang)
            return SduiWarningCard(
                message=f"{warning_msg} {', '.join(evidence.unverified_aliases)}",
                quote_text=evidence.quote,
            )

        return SduiQuoteCard(quote=evidence.quote, source_aliases=evidence.verified_source_ids, citations=[])

    def map_report(self, report: ReportDataDTO, execution_id: str = "", lang: str = "fi") -> ReportView:
        """Alias for map_report_to_sdui to satisfy existing test bindings if any.

        Args:
            report: The aggregated report data DTO to map into client view representation.
            execution_id: Optional explicit execution identifier override.
            lang: Target localized language code for report strings.

        Returns:
            The mapped ReportView instance for client rendering.
        """
        return self.map_report_to_sdui(report, execution_id, lang)

    def map_report_to_sdui(self, report: ReportDataDTO, execution_id: str = "", lang: str = "fi") -> ReportView:
        """Map ReportDataDTO to ReportView.

        Args:
            report: The aggregated report data DTO to map into client view representation.
            execution_id: Optional explicit execution identifier override.
            lang: Target localized language code for report strings.

        Returns:
            The mapped ReportView instance for client rendering.
        """
        # Phase B1: Metrics & Telemetry (Capture global_score, strictness_level, has_warning)
        metrics = ReportViewMetricsDTO(
            global_score=report.global_score,
            strictness_level=report.strictness_level,
        )

        if report.has_warning:
            status_theme = VisualIntent.WARNING
        else:
            status_theme = VisualIntent.SUCCESS

        inner_blocks: list[AnySduiBlock] = list(report.inner_sdui_blocks)

        # Phase 3a: Map N_A outcomes to SDUI N_A Cards
        na_default_msg = I18nText(translations={"fi": "Ei sovelleta (N/A)", "en": "Not applicable (N/A)"}).resolve(lang)
        na_rule_prefix = I18nText(
            translations={"fi": "Ohitettu säännön perusteella:", "en": "Skipped based on rule:"}
        ).resolve(lang)

        for result in report.results:
            if result.status == ExecutionStatus.N_A:
                reason_msg = na_default_msg
                if result.short_circuit_reason_tda_ids:
                    tda_id = result.short_circuit_reason_tda_ids[0]
                    if tda_id in report.hydrated_references:
                        hydrated = report.hydrated_references[tda_id]
                        reason_msg = f"{na_rule_prefix} {hydrated.resolved_claim}"

                inner_blocks.append(
                    SduiNACard(
                        short_circuit_reason_tda_ids=result.short_circuit_reason_tda_ids,
                        message=reason_msg,
                    )
                )

        if execution_id:
            resolved_execution_id = execution_id
        else:
            resolved_execution_id = report.execution_id

        return ReportView(
            view_id=resolved_execution_id,
            metrics=metrics,
            status_theme=status_theme,
            inner_sdui_blocks=inner_blocks,
        )
