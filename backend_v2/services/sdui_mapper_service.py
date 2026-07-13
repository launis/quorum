import logging

from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.report.root import ReportDataDto
from backend_v2.models.view.sdui import AnySduiBlock, ReportView, SduiQuoteCard, SduiWarningCard

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

    def map_report(self, report: ReportDataDto) -> ReportView:
        """Alias for map_report_to_sdui to satisfy existing test bindings if any."""
        return self.map_report_to_sdui(report)

    def map_report_to_sdui(self, report: ReportDataDto) -> ReportView:
        """Map ReportDataDto to ReportView."""
        # Fail-Fast Principle: We access attributes directly, no .get()
        # The DTO validation already ensures everything is present
        return ReportView(
            view_id=report.execution_id,
            metrics=report.global_metrics.model_dump(),
        )
