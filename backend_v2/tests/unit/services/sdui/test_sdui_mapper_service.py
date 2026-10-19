"""Unit tests for relocated SduiMapperService at canonical path."""

from __future__ import annotations

import pytest

from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.view.sdui import SduiQuoteCard, SduiWarningCard
from backend_v2.services.sdui.sdui_mapper_service import SduiMapperService


def test_sdui_mapper_service_canonical_import_and_evidence_mapping() -> None:
    """Verify SduiMapperService functions correctly from canonical path."""
    mapper = SduiMapperService()
    evidence = QuoteEvidenceDTO.model_validate(
        {"source_quotes": "Direct quote from source.", "source_alias": "DOC-1"},
        context={"alias_registry": {"DOC-1": "opaque_source_1"}},
    )
    card = mapper.map_evidence_to_sdui(evidence, lang="en")
    assert isinstance(card, SduiQuoteCard)
    assert card.quote == "Direct quote from source."
    assert card.source_aliases == ["opaque_source_1"]


def test_sdui_mapper_service_unverified_evidence_warning_card() -> None:
    """Verify unverified quote evidence maps to SduiWarningCard."""
    mapper = SduiMapperService()
    evidence = QuoteEvidenceDTO.model_validate(
        {"source_quotes": "Unverified claim.", "source_alias": "UNKNOWN-ALIAS"},
        context={"alias_registry": {"DOC-1": "opaque_source_1"}},
    )
    card = mapper.map_evidence_to_sdui(evidence, lang="en")
    assert isinstance(card, SduiWarningCard)
    assert "Hallucinated citations detected:" in card.message


def test_sdui_mapper_service_legacy_root_import_fails_fast() -> None:
    """Scenario NEG-14: Importing from deleted root path raises ModuleNotFoundError."""
    with pytest.raises(ModuleNotFoundError):
        __import__("backend_v2.services.sdui_mapper_service")
