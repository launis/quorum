"""Unit tests for SDUI aesthetics and presentation rules DTOs."""

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.sdui_rules import (
    GlobalScoreAestheticsDTO,
    MatrixGraphMinAxesDTO,
    MatrixGraphsAestheticsDTO,
    MatrixSummaryAestheticsDTO,
    MatrixSummaryRuleItemDTO,
    McpAuditAestheticsDTO,
    MetadataAestheticsDTO,
    PenaltiesRulesDTO,
    PenaltyRuleItemDTO,
    PrintableSourcesRulesDTO,
    SourceDisplayNameDTO,
    SynthesisTextAestheticsDTO,
    TheoryEvidenceItemDTO,
    VarianceRuleItemDTO,
    VarianceRulesDTO,
    WarningCardAestheticsDTO,
    WarningCardSeverityDTO,
    XaiAestheticsItemDTO,
    XaiAestheticsRulesDTO,
)
from backend_v2.models.enums import VisualIntent


def test_source_display_name_dto_locale_resolution() -> None:
    """Verify localized display name resolution with Finnish and English fallbacks."""
    dto = SourceDisplayNameDTO(display_name_fi="Asiakirjat", display_name_en="Documents")
    assert dto.get_display_name("fi") == "Asiakirjat"
    assert dto.get_display_name("en") == "Documents"
    assert dto.get_display_name("de") == "Documents"


def test_theory_evidence_item_dto_locale_resolution() -> None:
    """Verify theory explanation resolution by locale."""
    dto = TheoryEvidenceItemDTO(fi="Teoria Suomeksi", en="Theory in English")
    assert dto.get_text("fi") == "Teoria Suomeksi"
    assert dto.get_text("en") == "Theory in English"
    assert dto.get_text("fr") == "Theory in English"


def test_printable_sources_rules_dto() -> None:
    """Verify PrintableSourcesRulesDTO default mappings."""
    dto = PrintableSourcesRulesDTO(
        literature_source=SourceDisplayNameDTO(display_name_fi="fi", display_name_en="en"),
        theory_evidence_map={"t1": TheoryEvidenceItemDTO(fi="t_fi", en="t_en")},
        default_tool=SourceDisplayNameDTO(display_name_fi="tool_fi", display_name_en="tool_en"),
    )
    assert dto.literature_source.get_display_name("fi") == "fi"


def test_xai_aesthetics_rules_dto_lookup() -> None:
    """Verify XaiAestheticsRulesDTO item access, containment, and extra forbid."""
    item = XaiAestheticsItemDTO(severity=VisualIntent.SUCCESS, icon_name="lightbulb")
    rules = XaiAestheticsRulesDTO(rules={"coaching": item})
    assert "coaching" in rules
    assert "missing" not in rules
    assert rules["coaching"].severity == VisualIntent.SUCCESS
    assert rules["coaching"].icon_name == "lightbulb"

    with pytest.raises(KeyError):
        _ = rules["nonexistent"]

    with pytest.raises(ValidationError):
        XaiAestheticsItemDTO(severity=VisualIntent.SUCCESS, icon_name="bulb", extra_field="bad")  # type: ignore[call-arg]


def test_penalties_rules_dto_lookup() -> None:
    """Verify PenaltiesRulesDTO item lookup and containment."""
    item = PenaltyRuleItemDTO(severity=VisualIntent.WARNING, title_key="penalty_passivity", desc_key="penalty_desc")
    rules = PenaltiesRulesDTO(rules={"passivity": item})
    assert "passivity" in rules
    assert "missing" not in rules
    assert rules["passivity"].title_key == "penalty_passivity"


def test_variance_rules_dto_lookup() -> None:
    """Verify VarianceRulesDTO item lookup and containment."""
    item = VarianceRuleItemDTO(severity=VisualIntent.ERROR)
    rules = VarianceRulesDTO(rules={"high": item})
    assert "high" in rules
    assert "missing" not in rules
    assert rules["high"].severity == VisualIntent.ERROR


def test_global_score_aesthetics_dto() -> None:
    """Verify GlobalScoreAestheticsDTO defaults and immutability."""
    dto = GlobalScoreAestheticsDTO()
    assert dto.visual_intent == "primary"

    with pytest.raises(ValidationError):
        GlobalScoreAestheticsDTO(unknown_key=123)  # type: ignore[call-arg]


def test_matrix_graphs_aesthetics_dto() -> None:
    """Verify MatrixGraphsAestheticsDTO view lookup and containment."""
    views = {"radar": MatrixGraphMinAxesDTO(min_axes=3)}
    dto = MatrixGraphsAestheticsDTO(rules=views)
    assert "radar" in dto
    assert "bar" not in dto
    assert dto["radar"].min_axes == 3

    with pytest.raises(KeyError):
        _ = dto["unknown"]


def test_matrix_summary_aesthetics_dto() -> None:
    """Verify MatrixSummaryAestheticsDTO column lookup and containment."""
    cols = {"score": MatrixSummaryRuleItemDTO(min_axes=3)}
    dto = MatrixSummaryAestheticsDTO(rules=cols)
    assert "score" in dto
    assert "name" not in dto
    assert dto["score"].min_axes == 3

    with pytest.raises(KeyError):
        _ = dto["unknown"]


def test_mcp_audit_aesthetics_dto() -> None:
    """Verify McpAuditAestheticsDTO and McpAuditItemDTO default values."""
    dto = McpAuditAestheticsDTO()
    assert dto.default.visual_intent == "secondary"


def test_metadata_aesthetics_dto() -> None:
    """Verify MetadataAestheticsDTO default attributes."""
    dto = MetadataAestheticsDTO()
    assert dto.default_metadata == {}


def test_synthesis_text_aesthetics_dto() -> None:
    """Verify SynthesisTextAestheticsDTO defaults."""
    dto = SynthesisTextAestheticsDTO()
    assert dto.default_text.mode == "standard"


def test_warning_card_aesthetics_dto() -> None:
    """Verify WarningCardAestheticsDTO event type lookup and containment."""
    item = WarningCardSeverityDTO(severity=VisualIntent.WARNING)
    dto = WarningCardAestheticsDTO(rules={"starvation": item})
    assert "starvation" in dto
    assert "timeout" not in dto
    assert dto["starvation"].severity == VisualIntent.WARNING

    with pytest.raises(KeyError):
        _ = dto["unknown"]
