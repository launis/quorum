from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.view.sdui import SduiQuoteCard, SduiWarningCard
from backend_v2.services.sdui_mapper_service import SduiMapperService


def test_map_evidence_to_sdui_verified():
    mapper = SduiMapperService()
    evidence = QuoteEvidenceDTO.model_validate(
        {"quote": "Verified quote.", "source_alias": "DOC-1"},
        context={"alias_registry": {"DOC-1": "opaque_1"}},
    )
    result = mapper.map_evidence_to_sdui(evidence)
    assert isinstance(result, SduiQuoteCard)
    assert result.quote == "Verified quote."
    assert result.source_aliases == ["opaque_1"]


def test_map_evidence_to_sdui_unverified():
    mapper = SduiMapperService()
    evidence = QuoteEvidenceDTO.model_validate(
        {"quote": "Unverified quote.", "source_alias": "DOC-99"},
        context={"alias_registry": {"DOC-1": "opaque_1"}},
    )
    result = mapper.map_evidence_to_sdui(evidence)
    assert isinstance(result, SduiWarningCard)
    assert "Hallucinated citations detected" in result.message
