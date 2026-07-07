from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.view.sdui import SduiQuoteCard, SduiWarningCard
from backend_v2.services.sdui_mapper import SduiMapperService


def test_map_evidence_to_sdui_valid() -> None:
    """Test that a valid QuoteEvidenceDTO maps to SduiQuoteCard."""
    dto = QuoteEvidenceDTO.model_validate({"quote": "A valid quote", "source_alias": ["src_1", "src_2"]}, context={"alias_registry": {"src_1": "uuid-1", "src_2": "uuid-2"}})

    result = SduiMapperService.map_evidence_to_sdui(dto)

    assert isinstance(result, SduiQuoteCard)
    assert result.quote == "A valid quote"
    assert result.source_aliases == ["uuid-1", "uuid-2"]


def test_map_evidence_to_sdui_hallucinated() -> None:
    """Test that an unverified source alias yields a Warning Card (RFC 7807)."""
    dto = QuoteEvidenceDTO.model_validate({"quote": "A hallucinated quote", "source_alias": ["src_1", "OpaqueID.UNVERIFIED", "src_2"]}, context={"alias_registry": {}})

    result = SduiMapperService.map_evidence_to_sdui(dto)

    assert isinstance(result, SduiWarningCard)
    assert "hallusinoitu" in result.message.lower()
