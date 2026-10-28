"""Unit tests for relocated SduiMapperService at canonical path."""

from __future__ import annotations

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus, SDUIComponentType, VisualIntent
from backend_v2.models.view.sdui import ReportView, SduiNACard, SduiQuoteCard, SduiWarningCard
from backend_v2.services.sdui.sdui_mapper_service import SduiMapperService

__all__ = [
    "test_sdui_mapper_service_canonical_import_and_evidence_mapping",
    "test_sdui_mapper_service_legacy_root_import_fails_fast",
    "test_sdui_mapper_service_map_evidence_empty_lang_raises",
    "test_sdui_mapper_service_map_report_empty_execution_id_raises",
    "test_sdui_mapper_service_map_report_empty_lang_raises",
    "test_sdui_mapper_service_map_report_success_and_warning",
    "test_sdui_mapper_service_map_report_with_na_cards_and_override",
    "test_sdui_mapper_service_unverified_evidence_warning_card",
]


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


def test_sdui_mapper_service_map_report_success_and_warning() -> None:
    """Verify map_report_to_sdui maps ReportDataDTO to ReportView with success/warning themes."""
    mapper = SduiMapperService()

    report_success = ReportDataDTO(
        workflow_id="wf_test",
        execution_id="exe_test_1",
        profile_id="prf_test",
        global_score=92.5,
        strictness_level=50,
        has_warning=False,
    )
    view_success = mapper.map_report(report_success)
    assert isinstance(view_success, ReportView)
    assert view_success.view_id == "exe_test_1"
    assert view_success.status_theme == VisualIntent.SUCCESS
    assert view_success.metrics is not None
    assert view_success.metrics.global_score == 92.5
    assert view_success.metrics.strictness_level == 50

    report_warning = ReportDataDTO(
        workflow_id="wf_test",
        execution_id="exe_test_2",
        profile_id="prf_test",
        has_warning=True,
    )
    view_warning = mapper.map_report_to_sdui(report_warning)
    assert view_warning.status_theme == VisualIntent.WARNING


def test_sdui_mapper_service_map_report_with_na_cards_and_override() -> None:
    """Verify map_report_to_sdui maps N_A execution results to SduiNACard blocks."""
    mapper = SduiMapperService()

    hydrated_eval = HydratedAtomDTO(
        sdui_component=SDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Evaluated metric",
    )
    hydrated_atom = HydratedAtomDTO(
        sdui_component=SDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Prerequisite metric satisfied",
    )
    result_na = AtomResultDTO(
        tda_id="tda_eval_1",
        status=ExecutionStatus.N_A,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=["tda_prereq_1"],
    )
    result_na_default = AtomResultDTO(
        tda_id="tda_eval_1",
        status=ExecutionStatus.N_A,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    report = ReportDataDTO(
        workflow_id="wf_test",
        execution_id="exe_original",
        profile_id="prf_test",
        results=[result_na, result_na_default],
        hydrated_references={"tda_eval_1": hydrated_eval, "tda_prereq_1": hydrated_atom},
    )

    view = mapper.map_report_to_sdui(report, execution_id="exe_override", lang="en")
    assert view.view_id == "exe_override"
    assert len(view.inner_sdui_blocks) == 2
    na_card = view.inner_sdui_blocks[0]
    assert isinstance(na_card, SduiNACard)
    assert na_card.short_circuit_reason_tda_ids == ["tda_prereq_1"]
    assert "Skipped based on rule: Prerequisite metric satisfied" in na_card.message
    na_card_default = view.inner_sdui_blocks[1]
    assert isinstance(na_card_default, SduiNACard)
    assert na_card_default.message == "Not applicable (N/A)"


def test_sdui_mapper_service_map_evidence_empty_lang_raises() -> None:
    """Verify map_evidence_to_sdui raises AppException when lang is empty or whitespace."""
    mapper = SduiMapperService()
    evidence = QuoteEvidenceDTO.model_validate(
        {"source_quotes": "Direct quote from source.", "source_alias": "DOC-1"},
        context={"alias_registry": {"DOC-1": "opaque_source_1"}},
    )
    with pytest.raises(AppException) as exc_info:
        mapper.map_evidence_to_sdui(evidence, lang="   ")
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_sdui_mapper_service_map_report_empty_lang_raises() -> None:
    """Verify map_report_to_sdui raises AppException when lang is empty or whitespace."""
    mapper = SduiMapperService()
    report = ReportDataDTO(
        workflow_id="wf_test",
        execution_id="exe_test_1",
        profile_id="prf_test",
    )
    with pytest.raises(AppException) as exc_info:
        mapper.map_report_to_sdui(report, lang="")
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_sdui_mapper_service_map_report_empty_execution_id_raises() -> None:
    """Verify map_report_to_sdui raises AppException when resolved execution_id is empty."""
    mapper = SduiMapperService()
    report = ReportDataDTO(
        workflow_id="wf_test",
        execution_id="   ",
        profile_id="prf_test",
    )
    with pytest.raises(AppException) as exc_info:
        mapper.map_report_to_sdui(report, execution_id="  ", lang="en")
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
