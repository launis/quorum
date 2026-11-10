"""Unit tests for package __init__.py module exports and SDUI package facade."""

from __future__ import annotations

import pytest

import backend_v2
import backend_v2.hooks
import backend_v2.llm
import backend_v2.models.domain
import backend_v2.services.orchestrator.engines
import backend_v2.services.sdui
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.view.sdui import SduiQuoteCard

__all__ = [
    "test_init_import",
    "test_sdui_package_export_invalid_empty_lang_error",
    "test_sdui_package_export_invalid_whitespace_lang_error",
]


def test_init_import() -> None:
    """Verify that package __init__.py facades export their canonical public symbols."""
    assert backend_v2 is not None
    assert backend_v2.hooks is not None
    assert backend_v2.llm is not None
    assert backend_v2.models.domain is not None
    assert backend_v2.services.orchestrator.engines.PromptEngine is not None
    assert backend_v2.services.orchestrator.engines.ExecutionEngine is not None
    assert backend_v2.services.orchestrator.engines.SynthesisEngine is not None
    assert backend_v2.services.orchestrator.engines.TDAEngine is not None
    assert backend_v2.services.sdui.adapters is not None
    assert backend_v2.services.sdui.sanitizers is not None

    mapper = backend_v2.services.sdui.SduiMapperService()
    evidence = QuoteEvidenceDTO(
        source_quotes=("Verified package quote.",),
        verified_source_ids=["opaque_source_1"],
        unverified_aliases=[],
        is_verified=True,
    )
    card = mapper.map_evidence_to_sdui(evidence, lang="en")
    assert isinstance(card, SduiQuoteCard)
    assert card.quote == "Verified package quote."


def test_sdui_package_export_invalid_empty_lang_error() -> None:
    """Verify SduiMapperService exported from backend_v2.services.sdui rejects empty lang."""
    mapper = backend_v2.services.sdui.SduiMapperService()
    evidence = QuoteEvidenceDTO(
        source_quotes=("Verified package quote.",),
        verified_source_ids=["opaque_source_1"],
        unverified_aliases=[],
        is_verified=True,
    )
    with pytest.raises(AppException) as exc_info:
        mapper.map_evidence_to_sdui(evidence, lang="")
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_sdui_package_export_invalid_whitespace_lang_error() -> None:
    """Verify SduiMapperService exported from backend_v2.services.sdui rejects whitespace lang."""
    mapper = backend_v2.services.sdui.SduiMapperService()
    evidence = QuoteEvidenceDTO(
        source_quotes=("Verified package quote.",),
        verified_source_ids=["opaque_source_1"],
        unverified_aliases=[],
        is_verified=True,
    )
    with pytest.raises(AppException) as exc_info:
        mapper.map_evidence_to_sdui(evidence, lang="   ")
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
