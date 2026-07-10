"""Characterization Tests (Golden Master) for Epic 91.5 Phase 0.

Validates that the newly formatted legacy V1 engine output JSONs
successfully parse into the strict V2 ReportDataDto base.
"""

import json
from pathlib import Path

from backend_v2.models.dtos.report import ReportDataDto

TEST_DATA_DIR = Path(__file__).parent.parent / "test_data"


def test_legacy_golden_master_parse_success() -> None:
    """Test that the massive V1 fixtures (now converted and stripped of base64)
    parse perfectly into ReportDataDto without triggering strict validation errors.
    """
    fixture_path = TEST_DATA_DIR / "exe_c0bc_inputs.json"

    with open(fixture_path, encoding="utf-8") as f:
        raw_data = json.load(f)

    # Must use strict parsing to ensure no extra fields or legacy data structures bleed in.
    # Note: Pydantic ConfigDict(strict=True, extra="forbid") is enforced globally.
    dto = ReportDataDto.model_validate(raw_data)

    assert dto.executive_summary == "Legacy V1 converted summary."
    assert dto.evidence_quotes == []
    assert dto.urgency_level == 0


def test_legacy_golden_master_noisy_parse_success() -> None:
    """Test the noisy variant of the legacy V1 fixture."""
    fixture_path = TEST_DATA_DIR / "exe_c0bc_inputs_NOISY.json"

    with open(fixture_path, encoding="utf-8") as f:
        raw_data = json.load(f)

    dto = ReportDataDto.model_validate(raw_data)

    assert dto.executive_summary == "Legacy V1 converted summary."
    assert dto.evidence_quotes == []
    assert dto.urgency_level == 0
