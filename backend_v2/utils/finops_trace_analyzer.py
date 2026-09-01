"""FinOps Trace Analyzer module for monitoring token consumption and redundancy."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field


class MonitorState(BaseModel):
    """Schema for monitor state tracking."""

    model_config = ConfigDict(strict=True, extra="forbid")

    telemetry_cursor: Annotated[int, Field(default=0, ge=0)] = 0
    cursors: Annotated[dict[str, int], Field(default_factory=dict)] = Field(default_factory=dict)
    execution_id: Annotated[str | None, Field(default=None)] = None


class TelemetryRecord(BaseModel):
    """Schema for an individual LLM telemetry line."""

    model_config = ConfigDict(strict=True, extra="forbid")

    duration_ms: Annotated[int, Field(default=0, ge=0)] = 0
    cache_hit: Annotated[bool, Field(default=False)] = False
    total_tokens: Annotated[int, Field(default=0, ge=0)] = 0
    model_strategy: Annotated[str, Field(default="fast")] = "fast"
    execution_id: Annotated[str | None, Field(default=None)] = None
    step_id: Annotated[str | None, Field(default=None)] = None
    trigger_reason: Annotated[str | None, Field(default=None)] = None


class TraceMcp(BaseModel):
    """Schema for MCP trace entries."""

    model_config = ConfigDict(strict=True, extra="forbid")

    query: Annotated[str | None, Field(default=None)] = None


class TraceStepRecord(BaseModel):
    """Schema for trace step execution records."""

    model_config = ConfigDict(strict=True, extra="forbid")

    step_id: Annotated[str, Field(default="unknown")] = "unknown"
    error_code: Annotated[str | None, Field(default=None)] = None
    strategy: Annotated[str | None, Field(default=None)] = None
    schema_target: Annotated[str | None, Field(default=None)] = None
    output: Annotated[Any, Field(default=None)] = None
    mcp_traces: Annotated[list[TraceMcp], Field(default_factory=list)] = Field(default_factory=list)


def analyze_monitor_state(state_file_path: str, telemetry_file_path: str) -> dict[str, Any]:
    """Mode A: Monitor LLM telemetry for FinOps metrics.

    Args:
        state_file_path: Path to the monitor state JSON file.
        telemetry_file_path: Path to the LLM telemetry JSONL file.

    Returns:
        A dictionary containing the total duration, total calls, and any FinOps alerts.
    """
    state_file = Path(state_file_path)
    telemetry_file = Path(telemetry_file_path)

    if not state_file.exists():
        state_file.write_text(json.dumps({"telemetry_cursor": 0}))

    state_dict = json.loads(state_file.read_text())
    state = MonitorState.model_validate(state_dict)

    if "llm_telemetry.jsonl" in state.cursors:
        cursor = state.cursors["llm_telemetry.jsonl"]
    else:
        cursor = state.telemetry_cursor

    total_duration = 0
    total_calls = 0
    miss_found = False

    if telemetry_file.exists():
        with open(telemetry_file, encoding="utf-8") as f:
            lines = f.readlines()

            new_lines = lines[cursor:]
            for line in new_lines:
                if not line.strip():
                    continue
                record = TelemetryRecord.model_validate_json(line)
                total_duration += record.duration_ms
                total_calls += 1
                if not record.cache_hit:
                    miss_found = True

            if state.cursors:
                state.cursors["llm_telemetry.jsonl"] = len(lines)
            else:
                state.telemetry_cursor = len(lines)
            state_file.write_text(state.model_dump_json(exclude_unset=True))

    alerts: list[str] = []
    if total_calls > 20:
        alerts.append("Micro-call Spike (>20 calls)")
    if miss_found:
        alerts.append("Prompt Purity Violation (Cache Miss Detected)")

    return {"total_duration_ms": total_duration, "total_calls": total_calls, "alerts": alerts}


def finalize_execution(trace_file_path: str, telemetry_file_path: str) -> dict[str, Any]:
    """Mode B: Finalize execution and detect structural redundancy.

    Args:
        trace_file_path: Path to the execution trace JSON file.
        telemetry_file_path: Path to the LLM telemetry JSONL file.

    Returns:
        A dictionary containing structural warnings, MCP warnings, hashing warnings,
        healing cost events, and the total USD cost.
    """
    trace_file = Path(trace_file_path)
    telemetry_file = Path(telemetry_file_path)

    healing_cost_events = 0
    structural_warnings: list[str] = []
    hashing_warnings: list[str] = []
    mcp_warnings: list[str] = []
    total_usd = 0.0

    seen_strategies: set[str] = set()
    seen_hashes: dict[str, str] = {}
    seen_mcps: set[str] = set()

    if trace_file.exists():
        trace_raw = json.loads(trace_file.read_text())
        for raw_step in trace_raw:
            step = TraceStepRecord.model_validate(raw_step)
            # 1. Healing Cost
            if step.error_code == "SchemaValidationError":
                healing_cost_events += 1
                continue

            # 2. Structural Redundancy (DAG)
            if step.strategy and step.schema_target:
                combo = f"{step.strategy} -> {step.schema_target}"
                if combo in seen_strategies:
                    structural_warnings.append(f"Pipeline Duplication Alert: {combo}")
                else:
                    seen_strategies.add(combo)

            # 3. Payload Hashing
            if step.output:
                payload_str = json.dumps(step.output, sort_keys=True)
                payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
                if payload_hash in seen_hashes:
                    hashing_warnings.append(
                        f"Double Work Alert: {step.step_id} produced identical payload to an earlier step."
                    )
                else:
                    seen_hashes[payload_hash] = step.step_id

            # 4. Duplicate MCP Traces
            for trace_entry in step.mcp_traces:
                if trace_entry.query:
                    if trace_entry.query in seen_mcps:
                        mcp_warnings.append(f"Duplicate MCP Trace: '{trace_entry.query}'")
                    else:
                        seen_mcps.add(trace_entry.query)

    if telemetry_file.exists():
        with open(telemetry_file, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                record = TelemetryRecord.model_validate_json(line)
                # LiteLLM pricing calculation placeholder (using total_tokens approx)
                tokens = record.total_tokens
                if record.model_strategy == "reasoning":
                    total_usd += tokens * 0.000015
                else:
                    total_usd += tokens * 0.000001

    return {
        "healing_cost_events": healing_cost_events,
        "structural_warnings": structural_warnings,
        "hashing_warnings": hashing_warnings,
        "mcp_warnings": mcp_warnings,
        "usd_cost": total_usd,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="FinOps Trace Analyzer")
    parser.add_argument("--monitor", type=str, help="Path to monitor_state.json")
    parser.add_argument("--finalize", type=str, help="Execution ID")
    parser.add_argument("--telemetry-file", type=str, default=None, help="Path to telemetry file")
    parser.add_argument("--trace-file", type=str, default=None, help="Path to execution trace file")

    args = parser.parse_args()

    if args.monitor:
        state_file = Path(args.monitor)
        execution_id = "unknown"
        if state_file.exists():
            state_dict = json.loads(state_file.read_text())
            state = MonitorState.model_validate(state_dict)
            if state.execution_id:
                execution_id = state.execution_id

        telemetry_file = args.telemetry_file or f"data/files/executions/{execution_id}/llm_telemetry.jsonl"
        res = analyze_monitor_state(args.monitor, telemetry_file)
        print(json.dumps(res, indent=2))
    elif args.finalize:
        execution_id = args.finalize
        trace_file = args.trace_file or f"data/files/executions/{execution_id}/execution_trace.json"
        telemetry_file = args.telemetry_file or f"data/files/executions/{execution_id}/llm_telemetry.jsonl"
        res = finalize_execution(trace_file, telemetry_file)
        print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
