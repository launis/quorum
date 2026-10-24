"""Unit tests for summary builder dataset functions in the export domain."""

from __future__ import annotations

from backend_v2.models.core_base import I18nText
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.services.export import ExportService
from backend_v2.services.export.summary_builder import build_summary_dtos


def _create_sample_summary_matrix() -> MatrixScorecardRowDTO:
    return MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="Fallback Matrix Name",
        label_i18n=I18nText(translations={"fi": "Testi Matriisi", "en": "Test Matrix"}),
        score=4.0,
        raw_score=4.0,
        scale_max=5.0,
        normalized_score=80.0,
        true_atoms=4,
        total_atoms=5,
        level_breakdown={"Level 1": "1", "Level 2": "3"},
        row_explanation="Solid reasoning and deduction throughout.",
        cited_source_title="Document A",
        cited_source_id="src_0123456789abcdef",
        is_evaluative=True,
    )


def test_build_summary_dtos_existing_parity() -> None:
    """Verify 13-column summary DTO generation matches original scorecard metrics and parity with ExportService."""
    matrix = _create_sample_summary_matrix()
    target_id = "exe_0123456789abcdef"

    direct_dtos = build_summary_dtos(
        effective_matrices=[matrix],
        locale="fi",
        target_id=target_id,
    )
    service = ExportService()
    service_dtos = service._build_summary_dtos(
        effective_matrices=[matrix],
        locale="fi",
        target_id=target_id,
    )

    assert len(direct_dtos) == 1
    assert len(service_dtos) == 1

    dto = direct_dtos[0]
    srv_dto = service_dtos[0]

    assert dto == srv_dto
    assert dto.execution_id == target_id
    assert dto.label == "Testi Matriisi"
    assert dto.hits == 4
    assert dto.total_atoms == 5
    assert dto.hit_ratio == 0.8
    assert dto.raw_score == 4.0
    assert dto.scale_max == 5.0
    assert dto.normalized_score == 80.0
    assert dto.criteria == "4/5"
    assert dto.source == "Document A"
    assert dto.distribution == "Level 1: 1, Level 2: 3"
    assert "reasoning" in dto.row_explanation.lower()


def test_summary_builder_direct_import() -> None:
    """Verify direct invocation of build_summary_dtos from backend_v2.services.export.summary_builder."""
    from backend_v2.services.export.summary_builder import (
        build_summary_dtos as direct_func,
    )

    assert callable(direct_func)
    dtos = direct_func(effective_matrices=[], locale="en", target_id="exe_0123456789abcdef")
    assert dtos == []


def test_build_summary_dtos_fallback_label_and_score() -> None:
    """Verify fallback to score when raw_score is None and zero-default behaviors."""
    matrix = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="Raw Name Fallback",
        label_i18n=I18nText(translations={"fi": "Matriisi FI", "en": "Fallback EN"}),
        score=3.5,
        raw_score=None,
        scale_max=None,
        normalized_score=None,
        true_atoms=None,
        total_atoms=None,
        level_breakdown={},
        row_explanation="",
        cited_source_title=None,
        cited_source_id="src_fallback_id",
        is_evaluative=True,
    )

    dtos = build_summary_dtos(
        effective_matrices=[matrix],
        locale="fi",
        target_id="exe_0123456789abcdef",
    )
    assert len(dtos) == 1
    dto = dtos[0]
    assert dto.label == "Matriisi FI"
    assert dto.raw_score == 3.5
    assert dto.scale_max == 0.0
    assert dto.normalized_score == 0.0
    assert dto.hits == 0
    assert dto.total_atoms == 0
    assert dto.hit_ratio == 0.0
    assert dto.criteria == "0/0"
    assert dto.source == "src_fallback_id"
    assert dto.distribution == ""


def test_build_summary_dtos_no_sources() -> None:
    """Verify source field is empty when neither title nor id is present."""
    matrix = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="No Source Matrix",
        label_i18n=I18nText(translations={"fi": "Ei Lähdettä", "en": "No Source"}),
        score=0.0,
        raw_score=0.0,
        scale_max=5.0,
        normalized_score=0.0,
        true_atoms=0,
        total_atoms=2,
        level_breakdown=None,
        row_explanation="None",
        cited_source_title=None,
        cited_source_id=None,
        is_evaluative=True,
    )

    dtos = build_summary_dtos(
        effective_matrices=[matrix],
        locale="en",
        target_id="exe_0123456789abcdef",
    )
    assert len(dtos) == 1
    assert dtos[0].source == ""
    assert dtos[0].label == "No Source"
    assert dtos[0].criteria == "0/2"


def test_build_summary_dtos_locale_resolution_english_fallback() -> None:
    """Verify that when requested locale is missing, I18nText falls back to English."""
    matrix = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="Authoritative Fallback Name",
        label_i18n=I18nText(translations={"en": "English Authoritative Label"}),
        score=2.0,
        raw_score=2.0,
        scale_max=5.0,
        normalized_score=40.0,
        true_atoms=2,
        total_atoms=5,
        level_breakdown=None,
        row_explanation="Testing English fallback.",
        cited_source_title=None,
        cited_source_id=None,
        is_evaluative=True,
    )

    dtos = build_summary_dtos(
        effective_matrices=[matrix],
        locale="fi",
        target_id="exe_0123456789abcdef",
    )
    assert len(dtos) == 1
    assert dtos[0].label == "English Authoritative Label"
