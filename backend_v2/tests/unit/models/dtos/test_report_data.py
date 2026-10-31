"""Unit tests for ReportDataDTO using canonical imports."""

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import EntityPrefix, ExecutionStatus, SDUIComponentType


def test_report_data_dto_instantiation() -> None:
    """Verify valid ReportDataDTO instantiation and default field initialization."""
    wor_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    exe_id = generate_opaque_id(EntityPrefix.EXECUTION)
    pro_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
    tda_id = generate_opaque_id(EntityPrefix.TDA)

    dto = ReportDataDTO(
        workflow_id=wor_id,
        execution_id=exe_id,
        profile_id=pro_id,
        results=[
            AtomResultDTO(
                tda_id=tda_id,
                status=ExecutionStatus.PASSED,
                source_quotes=("Direct evidence",),
                evaluation_reasoning="Verified evidence.",
            )
        ],
        hydrated_references={
            tda_id: HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Claim text",
                source_quotes=("Direct evidence",),
            )
        },
    )
    assert dto.execution_id == exe_id
    assert dto.workflow_id == wor_id
    assert dto.profile_id == pro_id
    assert dto.inner_sdui_blocks == []
    assert len(dto.results) == 1
    assert tda_id in dto.hydrated_references


def test_report_data_dto_extra_forbidden() -> None:
    """Verify ReportDataDTO rejects unrecognized extra fields."""
    with pytest.raises(ValidationError):
        ReportDataDTO.model_validate(
            {
                "workflow_id": generate_opaque_id(EntityPrefix.WORKFLOW),
                "execution_id": generate_opaque_id(EntityPrefix.EXECUTION),
                "profile_id": generate_opaque_id(EntityPrefix.OUTPUT_PROFILE),
                "extra_field": "disallowed",
            }
        )


def test_report_data_dto_missing_required_fields_fails() -> None:
    """Verify ReportDataDTO fails fast when required fields are omitted or invalid types are passed."""
    with pytest.raises(ValidationError):
        ReportDataDTO.model_validate(
            {
                "workflow_id": generate_opaque_id(EntityPrefix.WORKFLOW),
            }
        )


def test_report_data_dto_referential_integrity_violation() -> None:
    """Verify enforce_referential_integrity raises ValidationError when tda_id is missing from hydrated_references."""
    tda_id = generate_opaque_id(EntityPrefix.TDA)
    dep_id = generate_opaque_id(EntityPrefix.TDA)

    with pytest.raises(ValidationError, match="Referential Integrity Error: Missing keys in hydrated_references"):
        ReportDataDTO(
            workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
            execution_id=generate_opaque_id(EntityPrefix.EXECUTION),
            profile_id=generate_opaque_id(EntityPrefix.OUTPUT_PROFILE),
            results=[
                AtomResultDTO(
                    tda_id=tda_id,
                    status=ExecutionStatus.PASSED,
                    source_quotes=("Direct evidence",),
                    evaluation_reasoning="Valid reason provided",
                    depends_on_tda_ids=[dep_id],
                )
            ],
            hydrated_references={},
        )


def test_report_data_dto_is_frozen() -> None:
    """Verify ReportDataDTO enforces immutability via frozen=True."""
    assert ReportDataDTO.model_config["frozen"] is True
    assert ReportDataDTO.model_config["strict"] is True
    assert ReportDataDTO.model_config["extra"] == "forbid"


def test_atom_result_dto_validation() -> None:
    """Verify AtomResultDTO instantiation with canonical Opaque Stripe ID."""
    tda_id = generate_opaque_id(EntityPrefix.TDA)
    atom = AtomResultDTO(
        tda_id=tda_id,
        status=ExecutionStatus.PASSED,
        source_quotes=("Direct evidence from text",),
        evaluation_reasoning="Valid reason provided",
    )
    assert atom.tda_id == tda_id
    assert atom.source_quotes == ("Direct evidence from text",)
    assert atom.evaluation_reasoning == "Valid reason provided"


def test_atom_result_dto_requires_reasoning() -> None:
    """Verify AtomResultDTO rejects PASSED status when evaluation_reasoning is None."""
    with pytest.raises(ValidationError):
        AtomResultDTO(
            tda_id=generate_opaque_id(EntityPrefix.TDA),
            status=ExecutionStatus.PASSED,
            source_quotes=("Some quote",),
            evaluation_reasoning=None,
        )


def test_hydrated_atom_dto() -> None:
    """Verify HydratedAtomDTO instantiation."""
    hydrated = HydratedAtomDTO(
        sdui_component=SDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Resolved Claim Text",
        source_quotes=("Verbatim Quote",),
    )
    assert hydrated.sdui_component == SDUIComponentType.BOOLEAN_CARD
    assert hydrated.resolved_claim == "Resolved Claim Text"
    assert hydrated.source_quotes == ("Verbatim Quote",)
