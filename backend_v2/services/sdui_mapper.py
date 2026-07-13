"""SDUI Mapper Service for Backend-For-Frontend (BFF) translation."""

import logging

from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.view.sdui import AnySduiBlock, SduiQuoteCard, SduiWarningCard

logger = logging.getLogger(__name__)


class SduiMapperService:
    """BFF service for translating unified semantic DTOs into SDUI components."""

    @classmethod
    def map_evidence_to_sdui(cls, q: QuoteEvidenceDTO) -> AnySduiBlock:
        """Map QuoteEvidenceDTO to either SduiQuoteCard or SduiWarningCard.

        Implements RFC 7807 Dual-Reporting for hallucinated aliases.

        Args:
            q: The quote evidence DTO to translate.

        Returns:
            The appropriate SDUI block representing the evidence.
        """
        for alias in q.unverified_aliases:
            if alias == "OpaqueID.UNVERIFIED":
                logger.error("Hallucinated alias detected during SDUI translation")
                return SduiWarningCard(
                    message="Lainauksen lähdettä ei voitu vahvistaa (hallusinoitu alias).", quote_text=q.quote
                )

        return SduiQuoteCard(quote=q.quote, source_aliases=q.verified_source_ids)
