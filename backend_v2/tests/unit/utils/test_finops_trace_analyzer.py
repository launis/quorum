from unittest.mock import AsyncMock
import json
from pathlib import Path

from backend_v2.utils.finops_trace_analyzer import analyze_monitor_state, finalize_execution


def test_analyze_monitor_state_updates_cursors_and_alerts(tmp_path: Path) -> None:
    """Test Mode A: Reads cursors, updates them, and triggers correct alerts."""
    state_file = tmp_path / "monitor_state.json"
    telemetry_file = tmp_path / "llm_telemetry.jsonl"

    # Initial state
    state_file.write_text(json.dumps({"telemetry_cursor": 0}))

    # Telemetry with 21 calls (triggers micro-call spike) and a cache miss (Prompt Purity)
    telemetry_lines = []
    for i in range(21):
        telemetry_lines.append(
            json.dumps(
                {
                    "duration_ms": 1000,
                    "cache_hit": False if i == 0 else True,  # First is a miss -> purity alert
                    "model_strategy": "fast",
                }
            )
        )
    telemetry_file.write_text("\n".join(telemetry_lines) + "\n")

    result = analyze_monitor_state(str(state_file), str(telemetry_file))

    # Verify cursor updated
    updated_state = json.loads(state_file.read_text())
    assert updated_state["telemetry_cursor"] > 0

    # Verify metrics
    assert result["total_duration_ms"] == 21000
    assert result["total_calls"] == 21
    assert any("Prompt Purity Violation" in alert for alert in result["alerts"])
    assert any("Micro-call Spike" in alert for alert in result["alerts"])


def test_finalize_execution_structural_redundancy(tmp_path: Path) -> None:
    """Test Mode B: Detects exact same output payloads and structural redundancy."""
    trace_file = tmp_path / "execution_trace.json"
    telemetry_file = tmp_path / "llm_telemetry.jsonl"

    telemetry_file.write_text("")  # Empty for this test

    # Execution trace with two identical outputs and identical strategy/schema
    trace_data = [
        {
            "step_id": "step_1",
            "strategy": "extraction",
            "schema_target": "DataGridBlock",
            "output": {"data": ["A", "B"]},
            "mcp_traces": [{"query": "test query"}],
        },
        {
            "step_id": "step_2",
            "strategy": "extraction",
            "schema_target": "DataGridBlock",
            "output": {"data": ["A", "B"]},  # 100% duplicate
            "mcp_traces": [{"query": "test query"}],  # duplicate MCP
        },
        {"step_id": "step_3", "error_code": "SchemaValidationError"},
    ]
    trace_file.write_text(json.dumps(trace_data))

    result = finalize_execution(str(trace_file), str(telemetry_file))

    assert result["healing_cost_events"] == 1
    assert any("Pipeline Duplication Alert" in w for w in result["structural_warnings"])
    assert any("Double Work Alert" in w for w in result["hashing_warnings"])
    assert any("Duplicate MCP Trace" in w for w in result["mcp_warnings"])
