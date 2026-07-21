from unittest.mock import AsyncMock
"""Golden Master & SDUI Parity E2E Tests (Epic 95)."""

import json

import pytest

from backend_v2.models.enums import ExecutionStatus, SDUIComponentType
from backend_v2.models.v2_core import AtomResultDTO, HydratedAtomDTO, ReportDataDTO


@pytest.fixture
def sample_report() -> ReportDataDTO:
    """Creates a full valid ReportDataDTO representing a Golden Master snapshot."""
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

    hydrated_refs = {
        tda_id_1: HydratedAtomDTO(
            sdui_component=SDUIComponentType.BOOLEAN_CARD,
            resolved_claim="Claim **with markdown**",
            source_quote=None,
        )
    }

    return ReportDataDTO(
        workflow_id="wor_123",
        execution_id="exe_123",
        profile_id="pro_123",
        results=[atom_1],
        hydrated_references=hydrated_refs,
        custom_preface_md="## High-level synthesis\nAll good.",
    )


def test_golden_master_sdui_serialization(sample_report: ReportDataDTO) -> None:
    """Test that ReportDataDTO serializes cleanly for the Flutter SDUI engine."""
    # Convert to JSON using strict model dump
    json_data = sample_report.model_dump(mode="json")

    # Verify strict SDUI constraints
    assert json_data["execution_id"] == "exe_123"
    assert "tda_11111111111111111111111111111111" in json_data["hydrated_references"]

    hydrated_atom = json_data["hydrated_references"]["tda_11111111111111111111111111111111"]

    # SDUI Component must be strongly typed enum string representation
    assert hydrated_atom["sdui_component"] == SDUIComponentType.BOOLEAN_CARD.value

    # Verify markdown parity rule: No raw HTML tags allowed (Epic 93)
    raw_json_str = json.dumps(json_data)

    # Simple heuristic check for raw HTML tags which are banned in Strict ICU Markdown Parity
    forbidden_tags = ["<span", "<font", "<div", "<p>"]
    for tag in forbidden_tags:
        assert tag not in raw_json_str, f"SDUI Violation: Raw HTML tag '{tag}' found in payload."
