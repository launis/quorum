"""Unit tests for finops_trace_analyzer.py."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from backend_v2.utils.finops_trace_analyzer import (
    MonitorState,
    TelemetryRecord,
    TraceMcp,
    TraceStepRecord,
    analyze_monitor_state,
    finalize_execution,
    main,
)


def test_analyze_monitor_state_empty(tmp_path: Path) -> None:
    state_file = tmp_path / "monitor_state.json"
    telemetry_file = tmp_path / "llm_telemetry.jsonl"

    res = analyze_monitor_state(str(state_file), str(telemetry_file))
    assert res.total_duration_ms == 0
    assert res.total_calls == 0
    assert res.alerts == []


def test_analyze_monitor_state_with_records(tmp_path: Path) -> None:
    state_file = tmp_path / "monitor_state.json"
    state_file.write_text(json.dumps({"cursors": {"llm_telemetry.jsonl": 0}}))

    telemetry_file = tmp_path / "llm_telemetry.jsonl"
    records = [
        {"duration_ms": 150, "cache_hit": True, "total_tokens": 100, "model_strategy": "fast"},
        {"duration_ms": 250, "cache_hit": False, "total_tokens": 200, "model_strategy": "reasoning"},
    ]
    telemetry_file.write_text("\n".join(json.dumps(r) for r in records) + "\n")

    res = analyze_monitor_state(str(state_file), str(telemetry_file))
    assert res.total_duration_ms == 400
    assert res.total_calls == 2
    assert "Prompt Purity Violation (Cache Miss Detected)" in res.alerts


def test_finalize_execution_with_trace_and_telemetry(tmp_path: Path) -> None:
    trace_file = tmp_path / "execution_trace.json"
    telemetry_file = tmp_path / "llm_telemetry.jsonl"

    trace_data = [
        {"error_code": "SchemaValidationError"},
        {"strategy": "logic", "schema_target": "sdui_hero", "step_id": "s1", "output": {"a": 1}},
        {"strategy": "logic", "schema_target": "sdui_hero", "step_id": "s2", "output": {"a": 1}},
        {"step_id": "s3", "mcp_traces": [{"query": "test_search"}, {"query": "test_search"}]},
    ]
    trace_file.write_text(json.dumps(trace_data))

    records = [
        {"total_tokens": 1000, "model_strategy": "fast"},
        {"total_tokens": 1000, "model_strategy": "reasoning"},
    ]
    telemetry_file.write_text("\n".join(json.dumps(r) for r in records) + "\n")

    res = finalize_execution(str(trace_file), str(telemetry_file))
    assert res.healing_cost_events == 1
    assert any("Pipeline Duplication Alert" in w for w in res.structural_warnings)
    assert any("Double Work Alert" in w for w in res.hashing_warnings)
    assert any("Duplicate MCP Trace" in w for w in res.mcp_warnings)
    assert res.usd_cost > 0


def test_main_cli_monitor(tmp_path: Path) -> None:
    state_file = tmp_path / "monitor_state.json"
    state_file.write_text(json.dumps({"execution_id": "exe_123"}))
    telemetry_file = tmp_path / "llm_telemetry.jsonl"
    telemetry_file.write_text("")

    with patch(
        "sys.argv", ["finops_trace_analyzer.py", "--monitor", str(state_file), "--telemetry-file", str(telemetry_file)]
    ):
        main()


def test_main_cli_finalize(tmp_path: Path) -> None:
    trace_file = tmp_path / "execution_trace.json"
    trace_file.write_text("[]")
    telemetry_file = tmp_path / "llm_telemetry.jsonl"
    telemetry_file.write_text("")

    with patch(
        "sys.argv",
        [
            "finops_trace_analyzer.py",
            "--finalize",
            "exe_123",
            "--trace-file",
            str(trace_file),
            "--telemetry-file",
            str(telemetry_file),
        ],
    ):
        main()


def test_analyze_monitor_state_micro_call_spike(tmp_path: Path) -> None:
    state_file = tmp_path / "monitor_state.json"
    telemetry_file = tmp_path / "llm_telemetry.jsonl"
    records = [{"duration_ms": 10, "cache_hit": True, "total_tokens": 5, "model_strategy": "fast"} for _ in range(25)]
    telemetry_file.write_text("\n".join(json.dumps(r) for r in records) + "\n\n")

    res = analyze_monitor_state(str(state_file), str(telemetry_file))
    assert res.total_calls == 25
    assert "Micro-call Spike (>20 calls)" in res.alerts


def test_main_cli_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    exe_dir = tmp_path / "data" / "files" / "executions" / "exe_auto"
    exe_dir.mkdir(parents=True)
    (exe_dir / "llm_telemetry.jsonl").write_text("")
    (exe_dir / "execution_trace.json").write_text("[]")

    state_file = tmp_path / "monitor_state.json"
    state_file.write_text(json.dumps({"execution_id": "exe_auto"}))

    monkeypatch.chdir(tmp_path)

    with patch("sys.argv", ["finops_trace_analyzer.py", "--monitor", str(state_file)]):
        main()

    with patch("sys.argv", ["finops_trace_analyzer.py", "--finalize", "exe_auto"]):
        main()


def test_finops_models_strictness() -> None:
    with pytest.raises(ValidationError):
        MonitorState.model_validate({"extra_field": 123})

    with pytest.raises(ValidationError):
        TelemetryRecord.model_validate({"extra_field": 123})

    with pytest.raises(ValidationError):
        TraceMcp.model_validate({"extra_field": 123})

    with pytest.raises(ValidationError):
        TraceStepRecord.model_validate({"extra_field": 123})

