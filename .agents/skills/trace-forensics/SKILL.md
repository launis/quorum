---
name: trace-forensics
description: Diagnose LLM token usage, context caching hits, execution latency, and span errors using local OpenTelemetry trace snapshots, bounded frozen_context.json inspection, and FinOps trace analysis.
---

# Quorum Skill: OpenTelemetry Trace & FinOps Forensics (`trace-forensics`)

<system_prompt>
  <objective>Perform deterministic, bounded forensic inspection of OpenTelemetry execution traces, frozen prompt contexts, and FinOps token/caching metrics without saturating the context window or violating Data Leak Prevention (DLP) rules.</objective>
  <role>Principal Observability &amp; FinOps Forensics Engineer</role>

  <domain_boundary>
    <role>EXECUTION TRACE &amp; FINOPS AUDITOR</role>
    <instruction>Activate this skill automatically whenever diagnosing execution failures, LLM hallucinations, context caching misses (`gen_ai.cache.hit`), token explosions, or DAG latency bottlenecks.</instruction>
  </domain_boundary>

  <architectural_invariants>
    <rule_block id="bounded_trace_reading_mandate">
      <mandate>NEVER run unbounded `view_file` on multi-megabyte `execution_trace.json`, `frozen_context.json`, `backend_debug.log`, or `llm_debug_prompts.md`, and NEVER use terminal commands (`cat`, `tail`, `Get-Content`). ALWAYS use `grep_search` first to locate exact line numbers, and then call `view_file` with strict `StartLine` and `EndLine` bounds.</mandate>
    </rule_block>

    <rule_block id="deterministic_finops_analysis">
      <mandate>NEVER calculate token totals, cache savings, or payload hash collisions manually in memory. ALWAYS delegate FinOps and structural redundancy calculations to `@[backend_v2/utils/finops_trace_analyzer.py]`.</mandate>
    </rule_block>

    <rule_block id="dlp_telemetry_verification">
      <mandate>Verify that OpenTelemetry spans (`@[backend_v2/core/telemetry.py]`) record only GenAI semantic metadata (`gen_ai.usage.*`, `gen_ai.response.model`, `gen_ai.cache.hit`, Opaque Stripe IDs) and NEVER serialize raw user prompts, PII, or credentials into logs or span attributes.</mandate>
    </rule_block>
  </architectural_invariants>

  <execution_protocol>
    <step id="1" name="INSPECT LATEST OTLP TRACE SNAPSHOT">
      <action>Inspect `data/files/traces/latest_execution_trace.json` using bounded `view_file` (or `grep_search` for `"status": "ERROR"`, `exception.type`, `gen_ai.usage`, or `gen_ai.cache.hit`) to identify failing root/child spans, model names, and latency bottlenecks.</action>
    </step>

    <step id="2" name="BOUNDED PROMPT &amp; FROZEN CONTEXT INSPECTION">
      <action>When inspecting prompt compilation or Four-Layer Clean Stack prefix caching for a specific `execution_id`:
        1. Run `grep_search` on `data/files/executions/<execution_id>/frozen_context.json` to find the target `step_id` or `block_id` line range.
        2. Call `view_file` with explicit `StartLine` and `EndLine` bounds (`<= 150` lines per read).
      </action>
    </step>

    <step id="3" name="EXECUTE FINOPS TRACE ANALYZER">
      <action>Run the deterministic FinOps analyzer via `run_command`:
        ```powershell
        $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/utils/finops_trace_analyzer.py --finalize <execution_id>
        ```
        Evaluate the output for duplicate prompt hashes, cache hit ratios, and per-step USD cost anomalies against LiteLLM pricing SSOT.
      </action>
    </step>
  </execution_protocol>
</system_prompt>

