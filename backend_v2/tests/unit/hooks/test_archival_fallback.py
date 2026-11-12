"""Unit tests for TraceEvent JSON hydration and strict schema boundaries."""

from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from backend_v2.models.state import TraceEvent


def test_archival_json_inflation_strictness() -> None:
    """Verify TraceEvent inflates string UUIDs and ISO timestamps via TypeAdapter.validate_json."""
    raw_json_str = """[
        {
            "event_id": "c3dbe82e-933e-4633-a8e7-27628dc395c8",
            "timestamp": "2026-05-17T07:21:16.425161Z",
            "step_name": "Agent_Logician",
            "event_type": "output",
            "content": {"some": "data"}
        }
    ]"""

    ta = TypeAdapter(list[TraceEvent])
    events = ta.validate_json(raw_json_str)

    assert len(events) == 1
    assert events[0].event_id.hex == "c3dbe82e933e4633a8e727628dc395c8"
    assert events[0].step_name == "Agent_Logician"


def test_archival_json_inflation_malformed_uuid_validation_error() -> None:
    """Verify malformed UUID string raises ValidationError during TraceEvent JSON hydration."""
    invalid_json_str = """[
        {
            "event_id": "not-a-valid-uuid",
            "timestamp": "2026-05-17T07:21:16.425161Z",
            "step_name": "Agent_Logician",
            "event_type": "output",
            "content": {"some": "data"}
        }
    ]"""
    ta = TypeAdapter(list[TraceEvent])
    with pytest.raises(ValidationError):
        ta.validate_json(invalid_json_str)


def test_archival_json_inflation_extra_field_forbidden_error() -> None:
    """Verify undeclared extra attributes in TraceEvent JSON trigger ValidationError."""
    extra_json_str = """[
        {
            "event_id": "c3dbe82e-933e-4633-a8e7-27628dc395c8",
            "timestamp": "2026-05-17T07:21:16.425161Z",
            "step_name": "Agent_Logician",
            "event_type": "output",
            "content": {"some": "data"},
            "undeclared_field": "forbidden"
        }
    ]"""
    ta = TypeAdapter(list[TraceEvent])
    with pytest.raises(ValidationError):
        ta.validate_json(extra_json_str)
