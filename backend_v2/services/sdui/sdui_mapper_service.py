"""SDUI Mapper Service for Quorum V2 Architecture.

Translates domain execution DTOs and quote evidence records into strictly typed
Server-Driven UI view models and blocks without dictionary type laundering.
"""

from __future__ import annotations

import logging

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus, VisualIntent
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    ReportView,
    ReportViewMetricsDTO,
    SduiCausalGraphBlock,
    SduiMatrixTableBlock,
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

        Raises:
            AppException: If lang is empty or whitespace-only (ErrorCodes.VALIDATION_FAILED).
        """
        if not lang or not lang.strip():
            msg = "Target language code 'lang' cannot be empty when mapping evidence to SDUI."
            logger.error("[SduiMapperService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        # Telemetry logging for hallucinations (Dual-Reporting)
        quote_str = ""
        if evidence.source_quotes:
            quote_str = " [...] ".join(evidence.source_quotes)
        if not evidence.is_verified or evidence.unverified_aliases:
            logger.warning("[TELEMETRY] Hallucination detected. Unverified aliases: %s", evidence.unverified_aliases)
            warning_msg = I18nText(
                translations={"fi": "Hallusinoituja lainauksia havaittu:", "en": "Hallucinated citations detected:"},
            ).resolve(lang)
            return SduiWarningCard(
                message=f"{warning_msg} {', '.join(evidence.unverified_aliases)}",
                quote_text=quote_str,
            )

        return SduiQuoteCard(quote=quote_str, source_aliases=evidence.verified_source_ids, citations=[])

    def map_report(self, report: ReportDataDTO, execution_id: str = "", lang: str = "fi") -> ReportView:
        """Delegate report mapping to map_report_to_sdui for caller compatibility.

        Args:
            report: The aggregated report data DTO to map into client view representation.
            execution_id: Optional explicit execution identifier override.
            lang: Target localized language code for report strings.

        Returns:
            The mapped ReportView instance for client rendering.

        Raises:
            AppException: If lang or the resolved execution_id is empty (ErrorCodes.VALIDATION_FAILED).
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

        Raises:
            AppException: If lang or the resolved execution_id is empty (ErrorCodes.VALIDATION_FAILED).
        """
        if not lang or not lang.strip():
            msg = "Target language code 'lang' cannot be empty when mapping report to SDUI."
            logger.error("[SduiMapperService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        if execution_id.strip():
            resolved_execution_id = execution_id.strip()
        else:
            resolved_execution_id = report.execution_id.strip()
        if not resolved_execution_id:
            msg = "Resolved execution_id cannot be empty when mapping report to SDUI."
            logger.error("[SduiMapperService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        # Capture top-level report score and strictness telemetry for view header rendering
        metrics = ReportViewMetricsDTO(
            global_score=report.global_score,
            strictness_level=report.strictness_level,
        )

        if report.has_warning:
            status_theme = VisualIntent.WARNING
        else:
            status_theme = VisualIntent.SUCCESS

        # Phase 3, Step 3.1: Anchor N_A short-circuit and Toulmin falsification lineage contextually
        # within parent SduiMatrixTableBlock and SduiCausalGraphBlock blocks instead of bottom-of-report orphans.
        na_default_msg = I18nText(translations={"fi": "Ei sovelleta (N/A)", "en": "Not applicable (N/A)"}).resolve(lang)
        na_rule_prefix = I18nText(
            translations={"fi": "Ohitettu säännön perusteella:", "en": "Skipped based on rule:"}
        ).resolve(lang)

        resolved_short_circuits: list[str] = list(report.short_circuited_by_claims)
        for result in report.results:
            if result.status == ExecutionStatus.N_A:
                reason_msg = na_default_msg
                if result.short_circuit_reason_tda_ids:
                    tda_id = result.short_circuit_reason_tda_ids[0]
                    if tda_id in report.hydrated_references:
                        hydrated = report.hydrated_references[tda_id]
                        reason_msg = f"{na_rule_prefix} {hydrated.resolved_claim}"
                if reason_msg not in resolved_short_circuits:
                    resolved_short_circuits.append(reason_msg)

        resolved_falsified_claims: list[str] = list(report.falsified_warrant_claims)

        inner_blocks: list[AnySduiBlock] = []
        for block in report.inner_sdui_blocks:
            match block:
                case SduiMatrixTableBlock() | SduiCausalGraphBlock():
                    merged_sc = list(block.short_circuited_by_claims)
                    for sc in resolved_short_circuits:
                        if sc not in merged_sc:
                            merged_sc.append(sc)
                    merged_fw = list(block.falsified_warrant_claims)
                    for fw in resolved_falsified_claims:
                        if fw not in merged_fw:
                            merged_fw.append(fw)
                    inner_blocks.append(
                        block.model_copy(
                            update={
                                "short_circuited_by_claims": merged_sc,
                                "falsified_warrant_claims": merged_fw,
                            }
                        )
                    )
                case _:
                    inner_blocks.append(block)

        return ReportView(
            view_id=resolved_execution_id,
            metrics=metrics,
            status_theme=status_theme,
            inner_sdui_blocks=inner_blocks,
        )
