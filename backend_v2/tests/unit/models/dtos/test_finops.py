"""Unit tests for FinOps DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.finops import FinOpsFinalizeSummaryDTO, FinOpsMonitorSummaryDTO


def test_finops_monitor_summary_dto() -> None:
    """Test FinOpsMonitorSummaryDTO initialization and immutability."""
    dto = FinOpsMonitorSummaryDTO(
        total_duration_ms=1500,
        total_calls=12,
        alerts=["Latency spike"],
    )
    assert dto.total_duration_ms == 1500
    assert dto.total_calls == 12
    assert dto.alerts == ["Latency spike"]

    with pytest.raises(ValidationError):
        dto.total_duration_ms = 2000  # type: ignore[misc]


def test_finops_finalize_summary_dto() -> None:
    """Test FinOpsFinalizeSummaryDTO initialization and default lists."""
    dto = FinOpsFinalizeSummaryDTO(
        healing_cost_events=3,
        structural_warnings=["duplicate_block"],
        hashing_warnings=[],
        mcp_warnings=["duplicate_search"],
        usd_cost=0.045,
    )
    assert dto.healing_cost_events == 3
    assert dto.structural_warnings == ["duplicate_block"]
    assert dto.hashing_warnings == []
    assert dto.mcp_warnings == ["duplicate_search"]
    assert dto.usd_cost == 0.045


def test_finops_dto_missing_required_fields() -> None:
    """Test validation errors on missing required fields."""
    with pytest.raises(ValidationError):
        _ = FinOpsMonitorSummaryDTO()  # type: ignore[call-arg]

    with pytest.raises(ValidationError):
        _ = FinOpsFinalizeSummaryDTO()  # type: ignore[call-arg]


def test_finops_monitor_summary_dto_negative_extra_forbid() -> None:
    """Test FinOpsMonitorSummaryDTO rejects extra fields."""
    with pytest.raises(ValidationError):
        FinOpsMonitorSummaryDTO(total_duration_ms=100, total_calls=2, extra_arg="forbidden")  # type: ignore[call-arg]


def test_finops_finalize_summary_dto_negative_extra_forbid() -> None:
    """Test FinOpsFinalizeSummaryDTO rejects extra fields."""
    with pytest.raises(ValidationError):
        FinOpsFinalizeSummaryDTO(  # type: ignore[call-arg]
            healing_cost_events=1,
            usd_cost=0.01,
            forbidden_field="not_allowed",
        )


def test_finops_dto_negative_strict_type() -> None:
    """Test strict type validation rejects non-integer duration."""
    with pytest.raises(ValidationError):
        FinOpsMonitorSummaryDTO(total_duration_ms="invalid", total_calls=2)  # type: ignore[arg-type]
