"""Unit tests for finops_trace_analyzer.py."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
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


@pytest.mark.parametrize(
    ("state_path", "telemetry_path"),
    [
        ("", "valid_telemetry.jsonl"),
        ("   ", "valid_telemetry.jsonl"),
        ("valid_state.json", ""),
        ("valid_state.json", "   "),
    ],
)
def test_analyze_monitor_state_empty_paths_raises_app_exception(
    state_path: str,
    telemetry_path: str,
) -> None:
    """Verify empty or whitespace file paths raise AppException with VALIDATION_FAILED."""
    with pytest.raises(AppException) as exc_info:
        analyze_monitor_state(state_path, telemetry_path)
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.value


def test_analyze_monitor_state_corrupted_json_raises_app_exception(tmp_path: Path) -> None:
    """Verify malformed state or telemetry JSON raises AppException with VALIDATION_FAILED."""
    state_file = tmp_path / "monitor_state.json"
    telemetry_file = tmp_path / "llm_telemetry.jsonl"
    state_file.write_text("{not_valid_json", encoding="utf-8")

    with pytest.raises(AppException) as exc_info:
        analyze_monitor_state(str(state_file), str(telemetry_file))
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.value


def test_analyze_monitor_state_corrupted_telemetry_line_raises_app_exception(tmp_path: Path) -> None:
    """Verify malformed telemetry JSONL line in analyze_monitor_state raises AppException."""
    state_file = tmp_path / "monitor_state.json"
    telemetry_file = tmp_path / "llm_telemetry.jsonl"
    telemetry_file.write_text("{malformed_line\n", encoding="utf-8")

    with pytest.raises(AppException) as exc_info:
        analyze_monitor_state(str(state_file), str(telemetry_file))
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.parametrize(
    ("trace_path", "telemetry_path"),
    [
        ("", "valid_telemetry.jsonl"),
        ("   ", "valid_telemetry.jsonl"),
        ("valid_trace.json", ""),
        ("valid_trace.json", "   "),
    ],
)
def test_finalize_execution_empty_paths_raises_app_exception(
    trace_path: str,
    telemetry_path: str,
) -> None:
    """Verify empty or whitespace paths in finalize_execution raise AppException with VALIDATION_FAILED."""
    with pytest.raises(AppException) as exc_info:
        finalize_execution(trace_path, telemetry_path)
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.value


def test_finalize_execution_corrupted_trace_raises_app_exception(tmp_path: Path) -> None:
    """Verify malformed execution_trace.json raises AppException with VALIDATION_FAILED."""
    trace_file = tmp_path / "execution_trace.json"
    telemetry_file = tmp_path / "llm_telemetry.jsonl"
    trace_file.write_text("{invalid_json", encoding="utf-8")

    with pytest.raises(AppException) as exc_info:
        finalize_execution(str(trace_file), str(telemetry_file))
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.value


def test_finalize_execution_corrupted_telemetry_raises_app_exception(tmp_path: Path) -> None:
    """Verify malformed telemetry JSONL line in finalize_execution raises AppException."""
    trace_file = tmp_path / "execution_trace.json"
    telemetry_file = tmp_path / "llm_telemetry.jsonl"
    trace_file.write_text("[]", encoding="utf-8")
    telemetry_file.write_text("{bad_telemetry_line\n", encoding="utf-8")

    with pytest.raises(AppException) as exc_info:
        finalize_execution(str(trace_file), str(telemetry_file))
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.value


def test_finalize_execution_with_trace_events_and_explicit_cost_usd(tmp_path: Path) -> None:
    """Verify TraceEvent, ErrorTraceEvent, blank lines, and explicit cost_usd branches."""
    from backend_v2.models.domain.system_config import MCPAuditTrace
    from backend_v2.models.state import ErrorTraceEvent, TraceEvent

    trace_file = tmp_path / "execution_trace.json"
    telemetry_file = tmp_path / "llm_telemetry.jsonl"

    err_event = ErrorTraceEvent(
        step_name="stp_err",
        error_code="SchemaValidationError",
        error_message="Failed schema",
    )
    out_event = TraceEvent(
        step_name="stp_out",
        event_type="output",
        content="identical_output",
        mcp_audit_traces=[
            MCPAuditTrace(
                tool_id="search",
                step_name="stp_out",
                query="mcp_q1",
            )
        ],
    )
    trace_payload = [
        err_event.model_dump(mode="json", exclude_none=True),
        out_event.model_dump(mode="json", exclude_none=True),
    ]
    trace_file.write_text(json.dumps(trace_payload), encoding="utf-8")

    telemetry_file.write_text(
        "\n" + json.dumps({"total_tokens": 500, "model_strategy": "fast", "cost_usd": 0.042}) + "\n\n",
        encoding="utf-8",
    )

    res = finalize_execution(str(trace_file), str(telemetry_file))
    assert res.healing_cost_events == 1
    assert res.usd_cost == pytest.approx(0.042)

