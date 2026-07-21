from unittest.mock import AsyncMock
"""Unit tests for ReportDataDTO and AtomResultDTO referential integrity & fail-fast mechanisms."""

import pytest
from pydantic import ValidationError

from backend_v2.models.enums import ExecutionStatus, SDUIComponentType
from backend_v2.models.v2_core import AtomResultDTO, HydratedAtomDTO, ReportDataDTO


def test_atom_result_cognitive_vs_system_state_missing_reasoning() -> None:
    """Test that PASSED/FAILED statuses require evaluation_reasoning."""
    with pytest.raises(ValidationError) as exc_info:
        AtomResultDTO(
            tda_id="tda_1234567890abcdef1234567890abcdef",
            status=ExecutionStatus.PASSED,
            source_quote="Some quote",
            contextual_override=False,
            evaluation_reasoning=None,
            error_details=None,
            extracted_data=None,
            depends_on_tda_ids=[],
            short_circuit_reason_tda_ids=[],
        )
    assert "Reasoning is mandatory for cognitive status" in str(exc_info.value)


def test_atom_result_cognitive_vs_system_state_missing_quote_and_override() -> None:
    """Test that PASSED/FAILED require either a source_quote or contextual_override."""
    with pytest.raises(ValidationError) as exc_info:
        AtomResultDTO(
            tda_id="tda_1234567890abcdef1234567890abcdef",
            status=ExecutionStatus.PASSED,
            evaluation_reasoning="Because I said so",
            contextual_override=False,
            source_quote=None,
            error_details=None,
            extracted_data=None,
            depends_on_tda_ids=[],
            short_circuit_reason_tda_ids=[],
        )
    assert "source_quote is mandatory unless contextual_override is True" in str(exc_info.value)


def test_atom_result_cognitive_vs_system_state_override_nullifies_quote() -> None:
    """Test that contextual_override=True forces source_quote to None."""
    atom = AtomResultDTO(
        tda_id="tda_1234567890abcdef1234567890abcdef",
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Manual override by admin",
        contextual_override=True,
        source_quote="This quote should be ignored",
        error_details=None,
        extracted_data=None,
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    assert atom.source_quote is None


def test_atom_result_system_error_requires_details() -> None:
    """Test that SYSTEM_ERROR status requires error_details."""
    with pytest.raises(ValidationError) as exc_info:
        AtomResultDTO(
            tda_id="tda_1234567890abcdef1234567890abcdef",
            status=ExecutionStatus.SYSTEM_ERROR,
            evaluation_reasoning=None,
            contextual_override=False,
            source_quote=None,
            error_details=None,
            extracted_data=None,
            depends_on_tda_ids=[],
            short_circuit_reason_tda_ids=[],
        )
    assert "Error details are mandatory when status is SYSTEM_ERROR" in str(exc_info.value)


def test_report_data_dto_referential_integrity_success() -> None:
    """Test that referential integrity passes when all IDs are in hydrated_references."""
    tda_id_1 = "tda_11111111111111111111111111111111"
    tda_id_2 = "tda_22222222222222222222222222222222"

    atom_1 = AtomResultDTO(
        tda_id=tda_id_1,
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Found proof.",
        source_quote="Proof text",
        contextual_override=False,
        error_details=None,
        extracted_data=None,
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    atom_2 = AtomResultDTO(
        tda_id=tda_id_2,
        status=ExecutionStatus.N_A,
        depends_on_tda_ids=[tda_id_1],
        evaluation_reasoning=None,
        contextual_override=False,
        source_quote=None,
        error_details=None,
        extracted_data=None,
        short_circuit_reason_tda_ids=[],
    )

    hydrated_refs = {
        tda_id_1: HydratedAtomDTO(
            sdui_component=SDUIComponentType.BOOLEAN_CARD,
            resolved_claim="Claim 1",
            source_quote=None,
        ),
        tda_id_2: HydratedAtomDTO(
            sdui_component=SDUIComponentType.BOOLEAN_CARD,
            resolved_claim="Claim 2",
            source_quote=None,
        ),
    }

    report = ReportDataDTO(
        workflow_id="wor_123",
        execution_id="exe_123",
        profile_id="pro_123",
        results=[atom_1, atom_2],
        hydrated_references=hydrated_refs,
    )

    assert len(report.results) == 2


def test_report_data_dto_referential_integrity_failure_missing_tda() -> None:
    """Test that referential integrity fails when an atom result tda_id is missing."""
    tda_id_1 = "tda_11111111111111111111111111111111"

    atom_1 = AtomResultDTO(
        tda_id=tda_id_1,
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Found proof.",
        source_quote="Proof text",
        contextual_override=False,
        error_details=None,
        extracted_data=None,
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    with pytest.raises(ValidationError) as exc_info:
        ReportDataDTO(
            workflow_id="wor_123",
            execution_id="exe_123",
            profile_id="pro_123",
            results=[atom_1],
            hydrated_references={},
        )
    assert "Referential Integrity Error: Missing keys in hydrated_references" in str(exc_info.value)


def test_report_data_dto_referential_integrity_failure_missing_dependency() -> None:
    """Test that referential integrity fails when a dependency tda_id is missing."""
    tda_id_1 = "tda_11111111111111111111111111111111"
    tda_id_2 = "tda_22222222222222222222222222222222"

    atom_1 = AtomResultDTO(
        tda_id=tda_id_1,
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Found proof.",
        source_quote="Proof text",
        depends_on_tda_ids=[tda_id_2],
        contextual_override=False,
        error_details=None,
        extracted_data=None,
        short_circuit_reason_tda_ids=[],
    )

    hydrated_refs = {
        tda_id_1: HydratedAtomDTO(
            sdui_component=SDUIComponentType.BOOLEAN_CARD,
            resolved_claim="Claim 1",
            source_quote=None,
        ),
    }

    with pytest.raises(ValidationError) as exc_info:
        ReportDataDTO(
            workflow_id="wor_123",
            execution_id="exe_123",
            profile_id="pro_123",
            results=[atom_1],
            hydrated_references=hydrated_refs,
        )
    assert "Referential Integrity Error: Missing keys in hydrated_references" in str(exc_info.value)
