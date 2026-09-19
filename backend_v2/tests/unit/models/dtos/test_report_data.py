"""Unit tests for ReportDataDTO using canonical imports."""

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.report_data import AtomResultDTO, HydratedAtomDTO, ReportDataDTO
from backend_v2.models.enums import ExecutionStatus


def test_report_data_dto_instantiation() -> None:
    dto = ReportDataDTO(
        workflow_id="wor_1234567890abcdef",
        execution_id="exe_1234567890abcdef",
        profile_id="pro_1234567890abcdef",
    )
    assert dto.execution_id == "exe_1234567890abcdef"
    assert dto.workflow_id == "wor_1234567890abcdef"
    assert dto.profile_id == "pro_1234567890abcdef"
    assert dto.inner_sdui_blocks == []
    assert dto.results == []


def test_report_data_dto_extra_forbidden() -> None:
    with pytest.raises(ValidationError):
        ReportDataDTO(
            workflow_id="wor_1234567890abcdef",
            execution_id="exe_1234567890abcdef",
            profile_id="pro_1234567890abcdef",
            extra_field="disallowed",  # type: ignore[call-arg]
        )


def test_atom_result_dto_validation() -> None:
    atom = AtomResultDTO(
        tda_id="tda_1234567890abcdef1234567890abcdef",
        status=ExecutionStatus.PASSED,
        source_quote="Direct evidence from text",
        evaluation_reasoning="Valid reason provided",
    )
    assert atom.tda_id == "tda_1234567890abcdef1234567890abcdef"
    assert atom.source_quote == "Direct evidence from text"
    assert atom.evaluation_reasoning == "Valid reason provided"


def test_atom_result_dto_requires_reasoning() -> None:
    with pytest.raises(ValidationError):
        AtomResultDTO(
            tda_id="tda_1234567890abcdef1234567890abcdef",
            status=ExecutionStatus.PASSED,
            source_quote="Some quote",
            evaluation_reasoning=None,
        )


def test_hydrated_atom_dto() -> None:
    hydrated = HydratedAtomDTO(
        sdui_component="boolean_card",
        resolved_claim="Resolved Claim Text",
        source_quote="Verbatim Quote",
    )
    assert hydrated.sdui_component == "boolean_card"
    assert hydrated.resolved_claim == "Resolved Claim Text"
    assert hydrated.source_quote == "Verbatim Quote"


