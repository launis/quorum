import pytest
from pydantic_core import ValidationError

from backend_v2.models.state import TraceEvent
from backend_v2.utils.pydantic_utils import inflate
from backend_v2.exceptions import AppException

def test_archival_json_inflation_strictness():
    """Reproduces the issue where TraceEvent cannot inflate string UUIDs/datetimes
    because V2CoreBase enforces strict=True. Fixes it via TypeAdapter."""
    
    # This mimics the output of execution_trace.json
    raw_json_str = '''[
        {
            "event_id": "c3dbe82e-933e-4633-a8e7-27628dc395c8",
            "timestamp": "2026-05-17T07:21:16.425161Z",
            "step_name": "Agent_Logician",
            "event_type": "output",
            "content": {"some": "data"}
        }
    ]'''
    
    # EPIC 56 Best Practice: Pydantic native Rust parsing
    from pydantic import TypeAdapter
    ta = TypeAdapter(list[TraceEvent])
    events = ta.validate_json(raw_json_str)
    
    # If we get here, it succeeded!
    assert len(events) == 1
    assert events[0].event_id.hex == "c3dbe82e933e4633a8e727628dc395c8"
    assert events[0].step_name == "Agent_Logician"
