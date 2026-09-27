# Tracker: OpenTelemetry (OTel) Distributed Tracing and Pydantic Logfire Observability Architecture
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_OpenTelemetry_and_Logfire_Architecture.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
</required_context_rules>

## Step Execution Status
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_OpenTelemetry_and_Logfire_Architecture.md]
- [x] **[OK] Execution:** `/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_OpenTelemetry_and_Logfire_Architecture.md] @[docs/implementationplans/TRACKER_OpenTelemetry_and_Logfire_Architecture.md]`
  - [x] Step 1: TECHNICAL_DEBT_PURGE_AND_DEPENDENCIES
  - [x] Step 2: SETTINGS_AND_TELEMETRY_CORE_INITIALIZATION
  - [x] Step 3: W3C_TRACE_CONTEXT_PROPAGATION_PIPELINE
  - [x] Step 4: DAG_EXECUTOR_AND_NODE_LEVEL_INSTRUMENTATION
  - [x] Step 5: GENAI_SEMANTIC_CONVENTIONS_IN_LLM_ADAPTERS
  - [x] Step 6: LOG_CORRELATION_AND_FINOPS_HARMONIZATION
  - [x] Step 7: WORKFLOW_GOVERNANCE_UPGRADES
  - [x] Step 8: AUTOMATED_TESTING_AND_AST_GUARDRAILS
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_OpenTelemetry_and_Logfire_Architecture.md] @[docs/implementationplans/TRACKER_OpenTelemetry_and_Logfire_Architecture.md]`

### Post-Implementation Gates
- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [x] **[OK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified @-referenced production backend files:
  - [x] @[backend_v2/settings.py]
  - [x] @[backend_v2/logging_config.py]
  - [x] @[backend_v2/main.py]
  - [x] @[backend_v2/core/telemetry.py]
  - [x] @[backend_v2/models/dtos/telemetry.py]
  - [x] @[backend_v2/models/execution_core.py]
  - [x] @[backend_v2/services/execution/facade.py]
  - [x] @[backend_v2/services/execution/ingress_service.py]
  - [x] @[backend_v2/workers/execution_worker.py]
  - [x] @[backend_v2/services/orchestrator/dag_executor.py]
  - [x] @[backend_v2/services/orchestrator/engines/tda_engine.py]
  - [x] @[backend_v2/services/orchestrator/engines/synthesis_engine.py]
  - [x] @[backend_v2/llm/provider.py]
  - [x] @[backend_v2/llm/adapters/base_adapter.py]
  - [x] @[backend_v2/llm/caching_service.py]
  - [x] @[backend_v2/services/mcp/dispatcher.py]
  - [x] @[backend_v2/services/llm_task_executor.py]
  - [x] @[backend_v2/services/orchestrator/strategies/llm.py]
  - [x] @[backend_v2/utils/finops_trace_analyzer.py]
  - [x] @[scripts/_ast_guardrails.py]
  - [x] @[scripts/backend_audit_loop.py]
  - [x] @[scripts/run_e2e_variance_test.py]
- [x] **[OK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified @-referenced production Flutter files:
  - [x] @[client_app_v2/lib/features/execution/models/trace_context_carrier.dart]
  - [x] @[client_app_v2/lib/features/execution/models/execution_metadata.dart]
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update
- [x] **[OK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to anchor physical implementation in `docs/architecture/` (scoped to relevant documents), update relevant Knowledge Items, and synchronize `.agents/rules/04_directory_reference.md`.
  - [x] Create New Knowledge Item: `@[ki_opentelemetry_logfire_observability.md]` in `<appDataDir>\knowledge\opentelemetry_logfire_observability\artifacts\`
  - [x] Synchronize Existing Knowledge Items: `@[ki_execution_record_ssot.md]`, `@[ki_python_314_concurrency_strictness.md]`
  - [x] Synchronize Architecture Pillar: `@[docs/architecture/05_resilience_and_observability.md]` (Section 2.8, Section 2.9, Section 2.12, Section 2.13)
  - [x] Synchronize Architecture Pillar: `@[docs/architecture/03_cognitive_orchestration_engine.md]` (Section 2.3)
  - [x] Synchronize Architecture Rule: `@[.agents/rules/04_directory_reference.md]`

### Final Plan Audit
- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_OpenTelemetry_and_Logfire_Architecture.md] @[docs/implementationplans/TRACKER_OpenTelemetry_and_Logfire_Architecture.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent
- **Atomic Commit Mandate**: After each successful step or cohesive logical block verification, commit changes atomically with strict Conventional Commits syntax (`<type>(<scope>): <summary>`). Explicitly list all staged files.
- **Single Source of Truth**: All telemetry configurations, carrier schemas, and token usage metrics must derive from authoritative models in `backend_v2/core/telemetry.py` and `backend_v2/models/dtos/telemetry.py`. Shadow dictionaries or ad-hoc logger dumps are strictly banned.
- **Zero Permissive Typing**: Enforce strict Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`). No naked dictionaries (`dict[str, Any]`), lazy `.get()` calls, or silent exception swallowing.
- **Quality Gates**:
  - Python tests & static analysis: `uv run python scripts/backend_audit_loop.py <target_path> --test`
  - Python tests with Logfire tracing: `uv run python scripts/backend_audit_loop.py <target_path> --test --logfire`
  - Flutter Freezed generation & analysis: `uv run python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **Execution Mode**: Supports Step-by-Step execution (default pause per step) and Continuous Full-Auto Mode (invoked via `/tier2-execute --full-auto`).
- **Context Budget Watchdog**: In Continuous Mode, proactively trigger `/tier5-session-handover` when context budget limit is reached: >8 turns, 3 atomic commits, or >5 modified complex files.
- **Diagnostic Trace Inspection**: When any test fails, inspect `data/files/traces/latest_execution_trace.json` using `view_file` to determine the root error span, duration, and stack trace before modifying code.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-01 | Align OpenTelemetry and Logfire dependencies in `pyproject.toml` and export to `backend_v2/requirements.txt` | Step 1 | [x] |
| REQ-02 | Eradicate `llm_debug_logger` imports/calls in `llm_task_executor.py` and `strategies/llm.py`, including phantom `_dlq_handle_debug_log_error` | Step 1 | [x] |
| REQ-03 | Delete `backend_v2/utils/llm_debug_logger.py` and unit test `test_llm_debug_logger.py` with zero lingering shims | Step 1 | [x] |
| REQ-04 | Remove obsolete unit tests patching deleted debug loggers in `test_llm_task_executor.py` | Step 1 | [x] |
| REQ-05 | Add centralized `mcp_default_timeout_seconds` configuration to `Settings` in `backend_v2/settings.py` | Step 1 | [x] |
| REQ-06 | Extend `Settings` in `backend_v2/settings.py` with centralized OpenTelemetry configurations using `AliasChoices` | Step 2 | [x] |
| REQ-07 | Implement strict Pydantic V2 DTOs (`TraceContextCarrierDTO`, `SpanSnapshotDTO`, `TraceSnapshotDTO`) with `extra="forbid", frozen=True` in `models/dtos/telemetry.py` | Step 2 | [x] |
| REQ-08 | Add `telemetry: TraceContextCarrierDTO | None` field to `ExecutionMetadata` in `models/execution_core.py` | Step 2 | [x] |
| REQ-09 | Create Dart Freezed `TraceContextCarrier` model and update `ExecutionMetadata` in Flutter client with build runner parity | Step 2 | [x] |
| REQ-10 | Implement `backend_v2/core/telemetry.py` with `configure_telemetry`, idempotency guard, NoOp fallback, context extraction/injection, and `use_trace_context` context manager with deterministic detach token cleanup | Step 2 | [x] |
| REQ-11 | Implement `LocalTraceSnapshotExporter` with Context Window Protection Guard (<20 KB, max 60 spans) and deterministic `error_fingerprint` exporting to `latest_execution_trace.json` | Step 2 | [x] |
| REQ-12 | Configure Logfire MCP Server integration and refactor `configure_logfire()` in `logging_config.py` into a thin delegation wrapper | Step 2 | [x] |
| REQ-13 | Inject W3C Trace Context into `ExecutionMetadata.telemetry` at API ingress in `ingress_service.py` and `facade.py` | Step 3 | [x] |
| REQ-14 | Sequence execution record retrieval before opening root span in `execution_worker.py`, binding worker execution to caller via `use_trace_context(carrier)` and root span `execution.worker_process` | Step 3 | [x] |
| REQ-15 | Implement resilient orphan root span creation with `telemetry.orphan_execution=True` when carrier is missing or unparseable | Step 3 | [x] |
| REQ-16 | Instrument `DAGExecutor.execute_workflow` with parent span `dag.orchestration` and execution/workflow metadata attributes | Step 4 | [x] |
| REQ-17 | Instrument `NodeExecutor.execute` and `run_step_wrapper` with child span `dag.node.{step_id}`, exception recording, and error status before re-raising `AppException` | Step 4 | [x] |
| REQ-18 | Instrument `TDAEngine` with `tda.atomization` and `tda.topological_evaluation` spans, and `SynthesisEngine` with `synthesis.distill` span | Step 4 | [x] |
| REQ-19 | Enforce OpenTelemetry context preservation across concurrent `asyncio.TaskGroup` node evaluations | Step 4 | [x] |
| REQ-20 | Activate standard OpenTelemetry GenAI Semantic Conventions via `logfire.instrument_litellm()` in `configure_telemetry` and `LiteLLMProvider` | Step 5 | [x] |
| REQ-21 | Propagate active OpenTelemetry context and model-specific metadata in `BaseLLMAdapter` and provider subclasses | Step 5 | [x] |
| REQ-22 | Instrument `LLMCachingService` with `gen_ai.cache.hit` boolean attribute on active span | Step 5 | [x] |
| REQ-23 | Instrument MCP tool dispatch with `logfire.instrument_mcp()`, `mcp.tool_call` span, `mcp.tool_id` attribute, and timeout guard in `dispatcher.py` | Step 5 | [x] |
| REQ-24 | Enforce strict PII and prompt scrubbing guardrail banning raw prompt text in span attributes | Step 5 | [x] |
| REQ-25 | Correlate structured logs with active OpenTelemetry context by injecting `trace_id` and `span_id` into `ContextFilter`, `StructuredLogContextDTO`, and `JSONFormatter` in `logging_config.py` | Step 6 | [x] |
| REQ-26 | Initialize telemetry in FastAPI `lifespan` in `main.py` and remove redundant top-level `instrument_fastapi` block | Step 6 | [x] |
| REQ-27 | Refactor `finops_trace_analyzer.py` to extract metrics from structured `ExecutionRecord` telemetry, removing hardcoded pricing formulas and duplicate `Field()` assignments | Step 6 | [x] |
| REQ-28 | Modernize `<rule_block id="logfire_delegation_mandate">` in `00-antigravity-core.md` and `<rule_block id="local_prompt_debugging_mandate">` in `05_llm_architecture.md` | Step 7 | [x] |
| REQ-29 | Update `.agents/workflows/` (`tier4-bug-hunting.md`, `tier6-execution-monitor.md`, `tier5-session-handover.md`, `tier8-audit-feature.md`) to utilize trace IDs, span trees, and `latest_execution_trace.json` | Step 7 | [x] |
| REQ-30 | Update `.agents/workflows/` (`tier2-execute.md`, `tier2-hardening-backend.md`, `tier8-test-coverage-expansion.md`, `tier5-resume.md`, `tier3-feature-refactor.md`, `tier8-red-teaming-audit.md`) with structured trace snapshot diagnostic workflows | Step 7 | [x] |
| REQ-31 | Implement unit test suite `test_telemetry.py` covering NoOp fallback, W3C injection/extraction, malformed headers, Logfire config, and local trace snapshot exporter | Step 8 | [x] |
| REQ-32 | Implement unit test suite `test_dag_executor_telemetry.py` asserting DAG span hierarchy, error status recording, and TaskGroup concurrency context | Step 8 | [x] |
| REQ-33 | Implement unit test suite `test_provider_telemetry.py` asserting GenAI semantic attributes, cache hits, and timeout handling | Step 8 | [x] |
| REQ-34 | Implement `in_memory_spans` pytest fixture and terminal summary failure hook emitting diagnostic banner in `backend_v2/tests/conftest.py` | Step 8 | [x] |
| REQ-35 | Implement AST guardrail `QGR021` in `_ast_guardrails.py` banning direct imports of `llm_debug_logger`, with corresponding unit tests | Step 8 | [x] |
| REQ-36 | Synchronize unit tests in `test_logging_config.py`, `test_main.py`, `test_finops_trace_analyzer.py`, and Dart `execution_models_test.dart` | Step 8 | [x] |
| REQ-37 | Unblock pytest Logfire plugin in `pyproject.toml`, add `--logfire` flag and diagnostic failure banner to `scripts/backend_audit_loop.py`, and add `--logfire` to `scripts/run_e2e_variance_test.py` | Step 8 | [x] |

# Session Handover Context
## Achieved
- Implementation plan researched, verified, and established at `@[docs/implementationplans/IMPLEMENTATION_PLAN_OpenTelemetry_and_Logfire_Architecture.md]`.
- Granular 5-Column Architectural Directives and Tri-Axis Dialectical Audit embedded within implementation plan.
- Double-entry bookkeeping tracker generated at `@[docs/implementationplans/TRACKER_OpenTelemetry_and_Logfire_Architecture.md]` with 1:1 step tracking (Step 1 to Step 8), 24 production hardening targets (22 Backend, 2 Frontend), and 37-row Requirements Traceability Matrix.
- 100% physical implementation of all 8 steps completed and committed across commits `5abff47c` through `ad2751dd`.
- All 37 requirements (REQ-01 to REQ-37) physically verified with passing test suites and zero legacy shims.
- Post-implementation hardening gates (Backend & Frontend) verified with 100% pass and >90% line coverage.
- System 2 Red-Team Audit (`/tier8-audit-plan`) executed with 0 fatal errors.
- As-built architectural documentation synchronized across `@[docs/architecture/03_cognitive_orchestration_engine.md]`, `@[docs/architecture/05_resilience_and_observability.md]`, `@[.agents/rules/04_directory_reference.md]`, and Knowledge Item `@[ki_opentelemetry_logfire_observability.md]`.

## Learned
- **W3C Distributed Trace Context:** Passing W3C `traceparent` through `ExecutionMetadata.telemetry` establishes seamless distributed trace continuity across asynchronous FastAPI ingress and Redis Arq workers without requiring external queue envelope wrappers.
- **Full-Duplex Freezed Parity:** Adding `telemetry` to backend `ExecutionMetadata` requires synchronizing Flutter Freezed model `execution_metadata.dart` to prevent client deserialization crashes under `@JsonSerializable(disallowUnrecognizedKeys: true)`.
- **Zero-Overhead NoOp Guard:** Setting `otel_enabled=False` must instantiate `NoOpTracerProvider`, ensuring strictly 0.0ms overhead delta and zero network bindings during default local testing.
- **Context Window Protection:** Diagnostic trace exporter `LocalTraceSnapshotExporter` must enforce a 60-span cap prioritizing root and failing spans to guarantee `latest_execution_trace.json` remains strictly under 20 KB for AI assistant context consumption.
- **Logfire Pytest Plugin Inactivity:** Logfire's pytest plugin defaults to inactive (`default=False`), allowing unblocking in `pyproject.toml` without impacting isolated local unit testing speed.

## Remaining
- None. All implementation steps, hardening gates, architectural documentation synchronizations, and red-team audits are 100% complete and verified.

## Resume Command
```powershell
# Plan execution, hardening, documentation sync, and red-team audit are 100% complete.
```
