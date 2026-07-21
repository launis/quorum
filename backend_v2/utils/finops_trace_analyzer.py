import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


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

    state = json.loads(state_file.read_text())
    cursors = state.get("cursors", {})
    cursor = cursors.get("llm_telemetry.jsonl", state.get("telemetry_cursor", 0))

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
                data = json.loads(line)
                total_duration += data.get("duration_ms", 0)
                total_calls += 1
                if data.get("cache_hit") is False:
                    miss_found = True

            if "cursors" in state:
                state["cursors"]["llm_telemetry.jsonl"] = len(lines)
            else:
                state["telemetry_cursor"] = len(lines)
            state_file.write_text(json.dumps(state))

    alerts = []
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
    structural_warnings = []
    hashing_warnings = []
    mcp_warnings = []
    total_usd = 0.0

    seen_strategies = set()
    seen_hashes = {}
    seen_mcps = set()

    if trace_file.exists():
        trace_data = json.loads(trace_file.read_text())
        for step in trace_data:
            # 1. Healing Cost
            if step.get("error_code") == "SchemaValidationError":
                healing_cost_events += 1
                continue

            # 2. Structural Redundancy (DAG)
            strategy = step.get("strategy")
            schema_target = step.get("schema_target")
            if strategy and schema_target:
                combo = f"{strategy} -> {schema_target}"
                if combo in seen_strategies:
                    structural_warnings.append(f"Pipeline Duplication Alert: {combo}")
                else:
                    seen_strategies.add(combo)

            # 3. Payload Hashing
            output = step.get("output")
            step_id = step.get("step_id", "unknown")
            if output:
                payload_str = json.dumps(output, sort_keys=True)
                payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
                if payload_hash in seen_hashes:
                    hashing_warnings.append(
                        f"Double Work Alert: {step_id} produced identical payload to an earlier step."
                    )
                else:
                    seen_hashes[payload_hash] = step_id

            # 4. Duplicate MCP Traces
            mcp_traces = step.get("mcp_traces", [])
            for trace in mcp_traces:
                query = trace.get("query")
                if query:
                    if query in seen_mcps:
                        mcp_warnings.append(f"Duplicate MCP Trace: '{query}'")
                    else:
                        seen_mcps.add(query)

    if telemetry_file.exists():
        with open(telemetry_file, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                # LiteLLM pricing calculation placeholder (using total_tokens approx)
                tokens = data.get("total_tokens", 0)
                strategy = data.get("model_strategy", "fast")
                if strategy == "reasoning":
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
            state = json.loads(state_file.read_text())
            execution_id = state.get("execution_id", "unknown")

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
