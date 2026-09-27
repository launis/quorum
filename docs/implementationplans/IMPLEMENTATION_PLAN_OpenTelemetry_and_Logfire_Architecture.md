> **STATUS: COMPLETED / TOTEUTETTU (100% Implemented & Verified)**

# IMPLEMENTATION PLAN: OpenTelemetry (OTel) Distributed Tracing and Pydantic Logfire Observability Architecture

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

## 1. Executive Summary & Objective

### Objective
This implementation plan establishes an enterprise-grade OpenTelemetry (OTel) and Pydantic Logfire distributed tracing and observability infrastructure for Quorum. It eradicates all ad-hoc debug logging mechanisms (specifically `llm_debug_logger.py` and manual text log grep filters), replacing them with standardized, machine-readable distributed tracing conforming to W3C Trace Context propagation and OpenTelemetry GenAI Semantic Conventions.

The unified telemetry project spans all Quorum backend layers:
1. **FastAPI Web Service**: Lifespan-level OpenTelemetry TracerProvider initialization and automatic HTTP request tracing.
2. **Asynchronous Background Workers**: Decoupled Arq workers restoring W3C distributed trace context (`traceparent`) from execution metadata to connect worker spans as direct children of the originating API invocations.
3. **Directed Acyclic Graph (DAG) Engine**: Hierarchical spans for workflow orchestration, node-level execution within `asyncio.TaskGroup` concurrency, and transactional checkpointing.
4. **Foundation Model (LLM) Adapters**: Standardized OpenTelemetry GenAI Semantic Conventions measuring input and output token counts, provider latency, temperature, finish reasons, and context cache hits.
5. **Model Context Protocol (MCP) Tool Loop**: Tool invocation spans measuring tool execution duration and outcome status.
6. **Agentic Workflow Governance**: Modernization of `.agents/workflows/` (`tier4-bug-hunting.md`, `tier6-execution-monitor.md`, `tier5-session-handover.md`, `tier8-audit-feature.md`, `tier2-execute.md`) to utilize structured trace IDs and parent-child span trees, completely eradicating context-destroying log dumps.

---

## 2. Tri-Axis Dialectical Audit & Root Cause Analysis

### Root Cause Analysis
- **Root Cause 1 (Ad-hoc Debug Fragmentation)**: Quorum previously relied on `backend_v2/utils/llm_debug_logger.py`, writing unstructured Markdown and JSON dump files (`llm_debug_prompts.md`, `frozen_context.json`) directly to disk. This caused disk I/O bottlenecks during concurrent runs, risked event loop stalls, and fragmented observability.
- **Root Cause 2 (Disjointed Distributed Context)**: FastAPI REST endpoints accept execution requests and enqueue jobs to Redis Arq workers. Because W3C `traceparent` headers were not injected into `ExecutionMetadata` and extracted in `backend_v2/workers/execution_worker.py`, API requests and background executions formed isolated, unlinked traces.
- **Root Cause 3 (Token Metric Inconsistency)**: FinOps token reporting parsed unstructured text logs (`finops_trace_analyzer.py`), creating two sources of truth for token usage and latency.

### Tri-Axis Dialectical Audit
1. **PROSECUTION (Over-Engineering & YAGNI Advocate)**:
   - *Attack*: Is full OpenTelemetry SDK overhead justified when Quorum already imports Pydantic Logfire?
   - *Defense*: Pydantic Logfire is natively built on the OpenTelemetry Python SDK. By configuring standard OpenTelemetry `TracerProvider`, W3C propagators, and OpenTelemetry GenAI conventions, Quorum achieves local zero-dependency testing (via `NoOpTracer`), vendor neutrality (any OTLP collector endpoint), and native Logfire cloud visualization without parallel implementations.
2. **DEFENSE (Architectural Sovereignty & Fail-Fast Advocate)**:
   - *Defense*: Distributed tracing must be fail-fast in validation (strict `TraceContextCarrierDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)`), yet resilient in trace extraction. If an execution record lacks telemetry metadata, the worker must instantiate an orphan root span with attribute `telemetry.orphan_execution=True` rather than crashing the business workflow.
3. **REALIST (Duct-Tape & Blast Radius Interrogator)**:
   - *Blast Radius*: Telemetry spans opened in concurrent `asyncio.TaskGroup` branches must retain correct context tokens. `opentelemetry.context.attach` must be managed cleanly using context managers or explicit detach tokens to avoid context pollution across greenlet tasks.
4. **BINDING VERDICT**:
   - Approved Architecture: Implement centralized `backend_v2/core/telemetry.py` initializing OpenTelemetry and Logfire. Propagate W3C trace context via `TraceContextCarrierDTO` stored in `ExecutionMetadata.telemetry`. Instrument DAG nodes, LLM adapters, and MCP dispatchers. Eradicate `llm_debug_logger.py`.

---

## 2.5. 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Core Telemetry & Settings**<br>`@[backend_v2/settings.py#L54-L853]`<br>`@[backend_v2/logging_config.py#L58-L84,L105-L152,L287-L380]`<br>`@[backend_v2/main.py#L165-L229,L242-L250]`<br>[NEW] `@[backend_v2/core/telemetry.py]`<br>[NEW] `@[backend_v2/models/dtos/telemetry.py]` | Hardcoded endpoint URLs, reading `os.getenv("DISABLE_LOGFIRE")`, silent tracer initialization bypasses, untyped dictionary carriers (`dict[str, Any]`), duplicate `logfire.configure()` calls across modules, and lazy `.get()` fallback chains. | Centralized Pydantic V2 `Settings` with `AliasChoices`, strict `TraceContextCarrierDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)`, W3C standard traceparent regex (`^00-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$`), and idempotent `configure_telemetry` consolidating existing scattered `configure_logfire()` calls with zero-overhead `NoOpTracerProvider` fallback when disabled. | Pruned speculative custom trace processor wrappers; utilize native OpenTelemetry `BatchSpanProcessor`, `OTLPSpanExporter`, and `logfire.configure()` directly without intermediate proxy classes; eliminate redundant module-level `instrument_fastapi` calls. | Unit test `backend_v2/tests/unit/core/test_telemetry.py::test_noop_fallback` proving strictly zero socket bindings, zero thread allocations, and 0.0ms overhead delta when `otel_enabled=False`. |
| **Distributed W3C Trace Propagation**<br>`@[backend_v2/services/execution/ingress_service.py#L47-L90]`<br>`@[backend_v2/services/execution/ingress_service.py#L190-L324]`<br>`@[backend_v2/services/execution/facade.py#L50-L395]`<br>`@[backend_v2/workers/execution_worker.py#L73-L518]` | Disjointed trace traces across HTTP and background workers; double-wrapping spans in `execution_worker.py` (existing `with logfire.span("execute_workflow_job")` vs new root span); opening worker root spans before fetching execution records; crashing background jobs on missing or corrupt traceparents (`except Exception: pass`); silent duct-tape fallbacks. | W3C Trace Context injection at API ingress into `ExecutionMetadata.telemetry`; in-place refactor of `execution_worker.py` ensuring `repository.get_execution(exec_id)` resolves `exec_record` and `carrier` before opening worker root span, then binding parent-linked `execution.worker_process` root span to `parent_ctx` via `use_trace_context(carrier)`. If carrier is missing or unparseable, log RFC 7807 warning and instantiate an orphan span with attribute `telemetry.orphan_execution=True`. | Pruned redundant custom Redis carrier queue channels; transit carrier directly inside authoritative `ExecutionMetadata` domain model without auxiliary transport envelopes. | Unit test `backend_v2/tests/unit/core/test_telemetry.py::test_w3c_injection_and_extraction` and malformed header test asserting graceful orphan span creation with `telemetry.orphan_execution=True`. |
| **Cross-Platform Freezed Parity**<br>`@[backend_v2/models/execution_core.py#L29-L53]`<br>`@[client_app_v2/lib/features/execution/models/execution_metadata.dart#L9-L26]`<br>[NEW] `@[client_app_v2/lib/features/execution/models/trace_context_carrier.dart]` | Adding `telemetry` field to Python backend without synchronously updating Flutter Freezed model (`@JsonSerializable(disallowUnrecognizedKeys: true)` causes catastrophic app crash on deserialization). | Full-Duplex DTO Cross-Examination: Create Dart Freezed `TraceContextCarrier`, update `ExecutionMetadata` in Dart with `@JsonKey(name: 'telemetry') TraceContextCarrier? telemetry`, and regenerate Freezed models via `build_runner`. | Pruned client-side trace collectors or local OpenTelemetry exporters in Flutter; Flutter acts strictly as a dumb consumer via Server-Driven UI. | `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/execution_metadata.dart --build` and `client_app_v2/test/features/execution/models/execution_models_test.dart`. |
| **DAG Orchestration & Concurrency**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L186-L347]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L435-L1291]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L724-L1024]`<br>`@[backend_v2/services/orchestrator/engines/tda_engine.py#L36-L258]`<br>`@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L33-L266]` | Unnamed spans, losing parent context across `asyncio.TaskGroup` coroutines, swallowing step exceptions in spans, and referencing non-existent `execute_dag` method. | `DAGExecutor.execute_workflow` wraps run in `dag.orchestration` span; `NodeExecutor.execute` and `run_step_wrapper` open child span `dag.node.{step_id}`; explicitly record exception via `span.record_exception(e)` and set `span.set_status(trace.StatusCode.ERROR)` before re-raising `AppException`. | Pruned speculative internal step semaphores; utilize existing `get_settings().max_concurrent_llm_steps` with zero shadow locks. | Unit test `backend_v2/tests/unit/services/orchestrator/test_dag_executor_telemetry.py` asserting parent-child hierarchy and TaskGroup context inheritance. |
| **Foundation LLM Adapters & MCP Telemetry**<br>`@[backend_v2/llm/provider.py#L455-L1217]`<br>`@[backend_v2/llm/adapters/base_adapter.py#L141-L370]`<br>`@[backend_v2/llm/caching_service.py#L15-L119]`<br>`@[backend_v2/services/mcp/dispatcher.py#L9-L56]` | Logging confidential user prompts or PII in span attributes; relying on fuzzy token scrapers; raw integer timeouts in MCP tools; executing un-timeout-guarded MCP tools; writing brittle manual span wrappers around LLM network calls. | Standard OpenTelemetry GenAI Semantic Conventions via Logfire 4.37.0 built-in integrations (`logfire.instrument_litellm()`, `logfire.instrument_mcp()`); centralized MCP timeout Settings field (`mcp_default_timeout_seconds`) guarding `ToolDispatcher.execute_tool` via `asyncio.timeout()`; domain context cache hit tracking (`gen_ai.cache.hit`). | Pruned manual span wrappers around LiteLLM and MCP; utilize Logfire 4.37.0 native integrations directly; pruned speculative rate-limiting token-bucket overhauls. | Unit test `backend_v2/tests/unit/llm/test_provider_telemetry.py` and AST rule `QGR021`. |
| **Legacy Debug Logging & FinOps Eradication**<br>`@[backend_v2/utils/llm_debug_logger.py]`<br>`@[backend_v2/services/llm_task_executor.py#L29,L269]`<br>`@[backend_v2/services/orchestrator/strategies/llm.py#L69,L578]`<br>`@[backend_v2/tests/unit/services/test_llm_task_executor.py#L273-L294]`<br>`@[backend_v2/tests/unit/services/test_llm_task_executor.py#L297-L327]`<br>`@[backend_v2/tests/unit/services/test_llm_task_executor.py#L631-L661]`<br>`@[backend_v2/utils/finops_trace_analyzer.py#L30-L110,L158-L235]`<br>`@[scripts/_ast_guardrails.py#L1218-L1275,L1524-L1560]` | Writing prompt dumps and telemetry logs to local disk files (`llm_debug_prompts.md`, `frozen_context.json`, `llm_telemetry.jsonl`); hardcoded shadow token pricing formulas in FinOps analyzer; duplicate `Field()` assignments on `cursors` and `mcp_traces`. | Complete deletion of `llm_debug_logger.py`; refactor `test_llm_task_executor.py` to remove stale patches; update `finops_trace_analyzer.py` to consume structured `ExecutionRecord` telemetry and fix duplicate `Field()` declarations; enforce AST rule `QGR021` banning `llm_debug_logger` resurrection. | Pruned redundant compatibility shims or dummy wrapper stubs for deleted logger functions. | `uv run python scripts/_ast_guardrails.py` and `uv run pytest backend_v2/tests/unit/services/test_llm_task_executor.py`. |
| **Automated Testing & Script Telemetry**<br>`@[scripts/backend_audit_loop.py#L73-L265,L268-L429]`<br>`@[scripts/run_e2e_variance_test.py#L1945-L2072]`<br>`@[pyproject.toml#L142-L146]` | Blocking pytest Logfire plugin unconditionally with `-p no:logfire`; inability to stream test suite latencies and failures to Logfire; lack of trace trees in CI and quality gate audit runs. | Unblock Logfire plugin in `pyproject.toml` (defaulting to inactive `default=False`), add `--logfire` flag to `scripts/backend_audit_loop.py` forwarding `--logfire` and `--logfire-service-name=quorum-audit-loop` to `pytest.main()`, and instrument `run_e2e_variance_test.py` with root span `e2e.variance_test`. | Pruned separate custom test metrics parsers or external reporter scripts; utilize native Logfire pytest plugin and test span hierarchy directly. | `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_logging_config.py --test --logfire` verifying test spans appear in Logfire trace hierarchy without breaking local runs. |
| **AI Assistant Observability & Workflow Integration**<br>[NEW] `@[backend_v2/core/telemetry.py]`<br>`@[backend_v2/tests/conftest.py]`<br>`@[.agents/rules/00-antigravity-core.md]`<br>`@[.agents/workflows/tier4-bug-hunting.md]`<br>`@[.agents/workflows/tier2-execute.md]`<br>`@[.agents/workflows/tier2-hardening-backend.md]`<br>`@[.agents/workflows/tier8-test-coverage-expansion.md]`<br>`@[.agents/workflows/tier5-resume.md]`<br>`@[.agents/workflows/tier3-feature-refactor.md]`<br>`@[.agents/workflows/tier8-red-teaming-audit.md]` | Forcing the AI coding assistant to guess root causes from truncated terminal logs, parse massive text logfiles, or scrape deleted prompt dumps (`llm_debug_prompts.md`). | Automatic atomic local trace snapshot exporter in `backend_v2/core/telemetry.py` exporting `data/files/traces/latest_execution_trace.json` during development and test runs with Context Window Protection Guard (<20 KB budget limit, max 60 prioritized spans) and deterministic `error_fingerprint` (`failing_step_id::error_code::exception_class`); `in_memory_spans` pytest fixture in `backend_v2/tests/conftest.py` using official `InMemorySpanExporter`; pytest failure summary hook in `backend_v2/tests/conftest.py` printing trace file location to stdout; Logfire MCP server integration (`https://logfire-eu.pydantic.dev/mcp`) providing native `query_spans` and `get_trace` MCP tools; modernization of `logfire_delegation_mandate` in `.agents/rules/00-antigravity-core.md` and systematic integration across execution, hardening, test expansion, refactor, and handover workflows. | Pruned complex browser-based scrapers or bulky custom telemetry viewers; utilize compact JSON snapshots on local disk and native OpenTelemetry and Logfire MCP interfaces directly. | Unit test in `backend_v2/tests/unit/core/test_telemetry.py` verifying `latest_execution_trace.json` size is <20 KB and includes `error_fingerprint`; unit tests utilizing `in_memory_spans` fixture; test failure output in `scripts/backend_audit_loop.py` displays diagnostic trace path. |

---

## 3. Touched Scope & Bounded Files

### TARGET Files

#### Configuration & Core Telemetry
- `[MODIFY]` @[backend_v2/settings.py#L54-L853] – Centralized OpenTelemetry and Logfire settings (`otel_enabled`, `logfire_token`, `otel_service_name`, `otel_exporter_otlp_endpoint`, `otel_tracing_sample_rate`, `mcp_default_timeout_seconds`).
- `[MODIFY]` @[backend_v2/logging_config.py#L58-L84,L105-L152,L287-L380] – Injection of active `trace_id` and `span_id` into `ContextFilter`, `StructuredLogContextDTO`, and `JSONFormatter`, delegation of `configure_logfire()`, and integration with `logfire.instrument_logging()`.
- `[MODIFY]` @[backend_v2/main.py#L165-L229,L242-L250] – FastAPI lifespan telemetry initialization, removal of redundant module-level `instrument_fastapi` block, and router instrumentation.
- `[NEW]` @[backend_v2/core/telemetry.py] – Centralized OpenTelemetry TracerProvider, Logfire configuration, OTLP span exporter, W3C carrier injection/extraction, NoOp tracer fallback, `use_trace_context` context manager with deterministic detach token cleanup, and `LocalTraceSnapshotExporter` dumping `data/files/traces/latest_execution_trace.json` for AI-assisted diagnostic introspection.
- `[NEW]` @[backend_v2/models/dtos/telemetry.py] – Strict Pydantic V2 DTOs: `TraceContextCarrierDTO`, `TraceSnapshotDTO`, and `SpanSnapshotDTO`.

#### Execution & Worker Layers
- `[MODIFY]` @[backend_v2/models/execution_core.py#L29-L53] – Add `telemetry: TraceContextCarrierDTO | None` field to `ExecutionMetadata`.
- `[MODIFY]` @[backend_v2/services/execution/facade.py#L50-L395] – W3C trace context injection during execution record initialization.
- `[MODIFY]` @[backend_v2/services/execution/ingress_service.py#L47-L90] – Injection of W3C carrier into `ExecutionMetadata` during `create_execution_record`.
- `[MODIFY]` @[backend_v2/services/execution/ingress_service.py#L190-L324] – Instantiation and enqueueing with telemetry carrier.
- `[MODIFY]` @[backend_v2/workers/execution_worker.py#L73-L518] – Sequence execution retrieval before root span opening, extracting W3C `traceparent` from metadata to bind `execution.worker_process` root span to API caller via `use_trace_context(carrier)`.

#### Cross-Platform SDUI Parity (Flutter Client)
- `[NEW]` @[client_app_v2/lib/features/execution/models/trace_context_carrier.dart] – Freezed DTO for W3C trace context carrier.
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/execution_metadata.dart#L9-L26] – Add `@JsonKey(name: 'telemetry') TraceContextCarrier? telemetry` to preserve `@JsonSerializable(disallowUnrecognizedKeys: true)` parity.
- `[MODIFY]` @[client_app_v2/test/features/execution/models/execution_models_test.dart#L13-L75] – Parity unit tests for `ExecutionMetadata` and `TraceContextCarrier`.

#### Orchestration & Engine Layers
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L186-L347] – NodeExecutor evaluation span (`dag.node.{step_id}`) with exception recording.
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L435-L1291] – DAG orchestration span (`dag.orchestration`) in `execute_workflow`.
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L724-L1024] – Step-level span instrumentation in `run_step_wrapper`.
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/tda_engine.py#L36-L258] – TDA engine atomization (`tda.atomization`) and topological evaluation (`tda.topological_evaluation`) span instrumentation.
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L33-L266] – Synthesis engine distillation span (`synthesis.distill`) instrumentation.

#### LLM & MCP Layers
- `[MODIFY]` @[backend_v2/llm/provider.py#L455-L1217] – OpenTelemetry GenAI Semantic Conventions instrumentation (`gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`).
- `[MODIFY]` @[backend_v2/llm/adapters/base_adapter.py#L141-L370] – Shared provider-level GenAI telemetry attribute compilation.
- `[MODIFY]` @[backend_v2/llm/caching_service.py#L15-L119] – Context cache hit attribute (`gen_ai.cache.hit`) instrumentation.
- `[MODIFY]` @[backend_v2/services/mcp/dispatcher.py#L9-L56] – Tool dispatch latency and status span instrumentation (`mcp.tool_call`) with `asyncio.timeout(get_settings().mcp_default_timeout_seconds)` guard.

#### Legacy Cleanup & FinOps
- `[MODIFY]` @[backend_v2/services/llm_task_executor.py#L29,L269] – Remove legacy `llm_debug_logger` imports and invocations.
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py#L69,L578] – Remove legacy `llm_debug_logger` imports and invocations.
- `[MODIFY]` @[backend_v2/tests/unit/services/test_llm_task_executor.py#L273-L294] – Remove obsolete test fixture patching deleted `write_llm_telemetry_log`.
- `[MODIFY]` @[backend_v2/tests/unit/services/test_llm_task_executor.py#L297-L327] – Remove obsolete test fixture patching deleted debug prompt logger.
- `[MODIFY]` @[backend_v2/tests/unit/services/test_llm_task_executor.py#L631-L661] – Remove obsolete test fixture patching deleted `log_structured_task_prompt`.
- `[MODIFY]` @[backend_v2/utils/finops_trace_analyzer.py#L30-L110,L158-L235] – Refactor to read structured telemetry tokens rather than disk prompt logs, removing hardcoded token pricing formulas and fixing duplicate Field assignments.
- `[MODIFY]` @[backend_v2/tests/unit/utils/test_finops_trace_analyzer.py#L48-L71] – Synchronize test assertions with updated structured trace analyzer.
- `[MODIFY]` @[scripts/_ast_guardrails.py#L1218-L1275,L1524-L1560] – AST guardrail `QGR021` enforcing NoOp safety and banning `llm_debug_logger` resurrection.
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1281-L1294] – Unit tests for AST rule `QGR021`.
- `[MODIFY]` @[pyproject.toml#L28-L35,L142-L146] – Upgrade dependencies and unblock native pytest Logfire plugin by removing `-p no:logfire`.
- `[MODIFY]` @[backend_v2/requirements.txt] – Synchronize exported dependencies.

#### Scripts & Test Automation
- `[MODIFY]` @[scripts/backend_audit_loop.py#L73-L265,L268-L429] – Add `--logfire` CLI flag to stream Pytest unit test execution traces and latencies to Logfire via `pytest.main([...])`, and output diagnostic trace path guidance on test failures.
- `[MODIFY]` @[scripts/run_e2e_variance_test.py#L1945-L2072] – Add `--logfire` CLI flag and wrap execution in root span `e2e.variance_test` grouping multi-run DAG telemetry.
- `[MODIFY]` @[backend_v2/tests/conftest.py] – Pytest terminal summary hook `pytest_terminal_summary` emitting local trace snapshot location (`data/files/traces/latest_execution_trace.json`) and Logfire MCP guidance directly to terminal output upon test failures.

#### Agentic Workflows & Rules Governance
- `[MODIFY]` @[.agents/rules/00-antigravity-core.md#L76-L78] – Modernize `<rule_block id="logfire_delegation_mandate">` to instruct the AI agent to inspect `data/files/traces/latest_execution_trace.json` using `view_file` and utilize Logfire MCP tools (`query_spans`, `get_trace`), eradicating obsolete references to deleted `llm_debug_prompts.md`.
- `[MODIFY]` @[.agents/rules/05_llm_architecture.md#L124-L126] – Modernize `<rule_block id="local_prompt_debugging_mandate">` to instruct the AI agent to inspect `data/files/traces/latest_execution_trace.json` using `view_file` or query OpenTelemetry spans via Logfire MCP tools, completely eradicating references to deleted `llm_debug_prompts.md`.
- `[MODIFY]` @[.agents/workflows/tier4-bug-hunting.md#L32,L117] – Trace ID-based RCA, 5 Whys span tree navigation, and mandate inspecting `data/files/traces/latest_execution_trace.json` in Step 1.
- `[MODIFY]` @[.agents/workflows/tier6-execution-monitor.md#L57,L63] – Active span duration monitoring for real-time stall detection and trace snapshot introspection.
- `[MODIFY]` @[.agents/workflows/tier5-session-handover.md] – Session handover referencing trace IDs instead of textual log dumps.
- `[MODIFY]` @[.agents/workflows/tier8-audit-feature.md] – Blast radius analysis utilizing live call graph telemetry.
- `[MODIFY]` @[.agents/workflows/tier2-execute.md] – Direct structured span inspection via `data/files/traces/latest_execution_trace.json` during test failure diagnosis.
- `[MODIFY]` @[.agents/workflows/tier2-hardening-backend.md] – Hardening failure recovery and regression latency benchmarking via `latest_execution_trace.json` and `--logfire` audit runs.
- `[MODIFY]` @[.agents/workflows/tier8-test-coverage-expansion.md] – Negative and edge-case testing verification of OpenTelemetry exception capture on spans (`span.record_exception`, status `ERROR`).
- `[MODIFY]` @[.agents/workflows/tier5-resume.md] – Auto-resume state inspection utilizing `latest_execution_trace.json` for verified prior execution state.
- `[MODIFY]` @[.agents/workflows/tier3-feature-refactor.md] – Direct structured span inspection via `latest_execution_trace.json` on quality gate failures during feature refactoring.
- `[MODIFY]` @[.agents/workflows/tier8-red-teaming-audit.md] – Red-teaming and security audit validating zero-data-leakage of prompts into telemetry span attributes.

#### Tests & Verification
- `[NEW]` @[backend_v2/tests/unit/core/test_telemetry.py] – Unit tests for core telemetry module, carrier injection/extraction, and NoOp behavior.
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_telemetry.py] – Unit tests for DAG span hierarchy and exception capture.
- `[NEW]` @[backend_v2/tests/unit/llm/test_provider_telemetry.py] – Unit tests for GenAI Semantic Conventions attributes and cache hit recording.
- `[MODIFY]` @[backend_v2/tests/unit/test_logging_config.py#L247-L269] – Synchronize `test_configure_logfire_behavior` with `configure_telemetry` delegation and test global `_TELEMETRY_CONFIGURED` guard.
- `[MODIFY]` @[backend_v2/tests/unit/test_main.py#L97-L110] – Monkeypatch `configure_telemetry` alongside `configure_logfire` in `test_lifespan_production_redis_failure`.

### DELETED Files
- `[DELETE]` @[backend_v2/utils/llm_debug_logger.py] – Obsolete ad-hoc debug logging utility.
- `[DELETE]` @[backend_v2/tests/unit/utils/test_llm_debug_logger.py] – Unit test file for deleted logger utility.

---

## 4. Pre-Implementation Technical Debt Cleanups (Phase 1)

Before introducing new business logic, the following technical debt cleanups must be completed:

1. **Ad-hoc Debug Logger Eradication & Caller Refactoring**:
   - Inspect all callers of `backend_v2/utils/llm_debug_logger.py` (`backend_v2/services/llm_task_executor.py` #L29, #L269, and `backend_v2/services/orchestrator/strategies/llm.py` #L69, #L578).
   - Remove imports and invocations of `write_debug_prompt_log`, `log_structured_task_prompt`, and `write_llm_telemetry_log`, eradicating the phantom unimplemented call `self._dlq_handle_debug_log_error(e)` on `backend_v2/services/orchestrator/strategies/llm.py#L589`.
   - In `backend_v2/tests/unit/services/test_llm_task_executor.py` (#L274-L328, #L634-L662), remove the 3 obsolete unit tests that patch deleted `write_llm_telemetry_log` and `log_structured_task_prompt`.
   - Delete `backend_v2/utils/llm_debug_logger.py` and its test `backend_v2/tests/unit/utils/test_llm_debug_logger.py`.
2. **Centralized Timeout Sovereignty**:
   - Inspect `backend_v2/services/mcp/dispatcher.py` and MCP tools for raw timeout integers.
   - Centralize default MCP tool timeout into `Settings.mcp_default_timeout_seconds` in `backend_v2/settings.py`.
3. **FinOps Shadow Pricing Multiplier & Duplicate Field Eradication**:
   - Inspect `backend_v2/utils/finops_trace_analyzer.py` (#L224-L228) and remove hardcoded shadow token pricing formulas (`0.000015`, `0.000001`).
   - Fix duplicate `Field()` assignments on `cursors` (#L38) and `mcp_traces` (#L97) in `finops_trace_analyzer.py` flagged by `scripts/audit_dict_eradication.py`.
   - Refactor `finops_trace_analyzer.py` to extract FinOps metrics from authoritative `ExecutionRecord` telemetry and `TraceEvent` payloads.
   - Update `backend_v2/tests/unit/utils/test_finops_trace_analyzer.py` to reflect the updated analyzer interface.
4. **Existing Logfire Integration Audit & Deduplication Consolidation**:
   - Audit and consolidate existing scattered Logfire configurations across the codebase:
     * `backend_v2/logging_config.py#L105-L153`: `configure_logfire()` currently initializes `logfire.configure()`, `instrument_pydantic()`, `instrument_httpx()`, `instrument_requests()`, `instrument_system_metrics()`, and `instrument_litellm()` using ad-hoc `os.getenv("DISABLE_LOGFIRE")` and hardcoded base URL `"https://api-eu.pydantic.dev/"`.
     * `backend_v2/main.py#L242-L250`: redundant top-level module code calling `_logfire.instrument_fastapi(app)` outside `lifespan`.
     * `backend_v2/worker.py#L55` and `backend_v2/run_worker.py#L23`: individual calls to `configure_logfire()`.
     * `backend_v2/workers/execution_worker.py#L116`: existing standalone `with logfire.span("execute_workflow_job", tags={"execution_id": span_execution_id}):` that is disconnected from the API caller's trace context.
     * `backend_v2/llm/provider.py#L422-L452`: preserve existing `LogfireShieldedClient` which protects `httpx.AsyncClient` from mutation crashes during deep logging serialization.
   - Refactor `configure_logfire()` in `logging_config.py` into a thin delegation wrapper calling `backend_v2/core/telemetry.py::configure_telemetry(get_settings())` with strict idempotency guards (`_TELEMETRY_CONFIGURED`), guaranteeing zero duplicate tracer initializations.
   - Preserve intentional omission of `logfire.instrument_redis()` to avoid console log flooding from Arq worker 0.5s polling (`ZRANGEBYSCORE/ZCARD`).
5. **Cross-Platform Freezed Contract Synchronization**:
   - Create `client_app_v2/lib/features/execution/models/trace_context_carrier.dart` and update `client_app_v2/lib/features/execution/models/execution_metadata.dart` to prevent `@JsonSerializable(disallowUnrecognizedKeys: true)` crashes when backend serializes `telemetry`.
6. **Strict Pydantic V2 DTO Invariant Enforcement**:
   - Define all new telemetry models with `ConfigDict(strict=True, extra="forbid", frozen=True)`.
   - Prevent naked dictionaries (`dict[str, Any]`) in trace carrier boundaries.
7. **Pytest Logfire Plugin Unblocking & Script Integration**:
   - In `pyproject.toml#L142-L146`, replace `addopts = "-p no:logfire"` with standard configuration (`addopts = ""`, `logfire_service_name = "quorum-pytest"`).
   - Because Logfire's pytest plugin has `default=False` for `--logfire`, it remains 100% inert during normal local testing and does not send network traces unless explicitly triggered via `--logfire` or in CI environments where `CI=true` and `LOGFIRE_TOKEN` is present.
   - Wire `--logfire` into `scripts/backend_audit_loop.py` so agents and CI can run audit gates with distributed trace observability.
8. **Agentic Rule Modernization & Observability Awareness**:
   - Modernize `<rule_block id="logfire_delegation_mandate">` in `@[.agents/rules/00-antigravity-core.md]` to instruct the AI agent to inspect `data/files/traces/latest_execution_trace.json` and utilize Logfire MCP tools (`query_spans`, `get_trace`), eradicating obsolete references to deleted `llm_debug_prompts.md` and `frozen_context.json`.
9. **Execution Worker Span Context Sequencing**:
   - In `backend_v2/workers/execution_worker.py#L73-L519`, reorder the initial steps of `execute_workflow_job` so `execution_data = await repository.get_execution(exec_id)` and model validation occur before starting the worker root span. Extract `carrier = exec_record.metadata.telemetry` and wrap worker execution in `use_trace_context(carrier)` to link `execution.worker_process` to the originating API caller's distributed span without disconnected or duplicate spans.
10. **Centralized MCP Tool Execution Timeout Guard**:
   - In `backend_v2/services/mcp/dispatcher.py#L9-L56`, wrap `tool.execute(**kwargs)` with `asyncio.timeout(get_settings().mcp_default_timeout_seconds)` and record `mcp.tool_call` span with attributes (`mcp.tool_id`), recording timeouts and exceptions on the active span via `span.record_exception(e)` and status `ERROR`.
11. **Structured Logging Context Trace Correlation**:
   - In `backend_v2/logging_config.py#L58-L84,L287-L380`, update `ContextFilter.filter`, `StructuredLogContextDTO`, and `JSONFormatter.format` to extract `trace_id` and `span_id` from `opentelemetry.trace.get_current_span()` and emit them in structured JSON logs.
12. **Safe OpenTelemetry Context Detachment Manager**:
   - In `backend_v2/core/telemetry.py`, implement `@contextmanager def use_trace_context(carrier: TraceContextCarrierDTO | None)` ensuring `otel_context.attach` tokens are deterministically detached via `otel_context.detach(token)` in a `finally` block, preventing context contamination across concurrent asyncio tasks.
13. **AI Developer Observability & Deterministic Test Infrastructure (Context Guard, Error Fingerprint, and In-Memory Fixtures)**:
   - Enforce a strict context window budget guard on `LocalTraceSnapshotExporter`: cap span collection (`max_spans: int = 60`) prioritizing root spans, failed spans (`status == 'ERROR'`), and top-latency spans, ensuring `latest_execution_trace.json` never exceeds 20 KB.
   - Add `error_fingerprint` to `TraceSnapshotDTO` (`failing_step_id::error_code::exception_class`) for instant regression identification and deduplication in agent workflows.
   - Provide an official `in_memory_spans` pytest fixture in `backend_v2/tests/conftest.py` using `InMemorySpanExporter`, eliminating brittle telemetry mocks in unit tests.

---

## 5. Detailed Execution Plan

```xml
<execution_protocol>
  <metadata>
    <task_id>opentelemetry_and_logfire_observability_architecture</task_id>
    <title>OpenTelemetry (OTel) Distributed Tracing and Pydantic Logfire Observability Architecture</title>
  </metadata>

  <step id="1" name="TECHNICAL_DEBT_PURGE_AND_DEPENDENCIES">
    <action>Update and align OpenTelemetry and Logfire dependencies in `@[pyproject.toml#L28-L35]`:
      - `logfire[fastapi,httpx,litellm,requests,system-metrics]>=4.37.0`
      - `opentelemetry-api>=1.42.0`
      - `opentelemetry-sdk>=1.42.0`
      - `opentelemetry-exporter-otlp>=1.42.0`
      - `opentelemetry-instrumentation-fastapi>=0.63b1`
    </action>
    <action>Export locked dependencies to `@[backend_v2/requirements.txt]` via `uv export`.</action>
    <action>Remove imports and calls to `llm_debug_logger` in `@[backend_v2/services/llm_task_executor.py#L29,L269]` and `@[backend_v2/services/orchestrator/strategies/llm.py#L69,L578]`, eradicating the phantom `self._dlq_handle_debug_log_error(e)` call on #L589.</action>
    <action>Delete `@[backend_v2/utils/llm_debug_logger.py]` and `@[backend_v2/tests/unit/utils/test_llm_debug_logger.py]`.</action>
    <action>Remove 3 obsolete unit tests patching deleted debug loggers in `@[backend_v2/tests/unit/services/test_llm_task_executor.py#L273-L294]`, `@[backend_v2/tests/unit/services/test_llm_task_executor.py#L297-L327]`, and `@[backend_v2/tests/unit/services/test_llm_task_executor.py#L631-L661]`.</action>
    <action>Add `mcp_default_timeout_seconds: Annotated[int, Field(default=30, ge=1, description="Default timeout in seconds for MCP tool executions")] = 30` to `@[backend_v2/settings.py#L54-L853]`.</action>
    <constraint invariant="zero_duct_tape">Do not leave dummy wrapper functions, commented-out lines, or empty shims in place of deleted debug logging utilities.</constraint>
  </step>

  <step id="2" name="SETTINGS_AND_TELEMETRY_CORE_INITIALIZATION">
    <action>Extend `Settings` in `@[backend_v2/settings.py#L54-L853]` with centralized OpenTelemetry configurations:
      - `otel_enabled: Annotated[bool, BeforeValidator(strip_whitespace), Field(default=False, validation_alias=AliasChoices("otel_enabled", "OTEL_ENABLED"), description="Flag to enable OpenTelemetry and Logfire distributed tracing")] = False`
      - `logfire_token: Annotated[str | None, BeforeValidator(strip_whitespace), Field(default=None, validation_alias=AliasChoices("logfire_token", "LOGFIRE_TOKEN"), description="Authentication token for Pydantic Logfire cloud service")] = None`
      - `otel_service_name: Annotated[str, BeforeValidator(strip_whitespace), Field(default="quorum-backend", validation_alias=AliasChoices("otel_service_name", "OTEL_SERVICE_NAME"), description="Logical service name emitted in OpenTelemetry resource attributes")] = "quorum-backend"`
      - `otel_exporter_otlp_endpoint: Annotated[str | None, BeforeValidator(strip_whitespace), Field(default=None, validation_alias=AliasChoices("otel_exporter_otlp_endpoint", "OTEL_EXPORTER_OTLP_ENDPOINT"), description="OTLP collector endpoint for exporting trace spans")] = None`
      - `otel_tracing_sample_rate: Annotated[float, Field(default=1.0, ge=0.0, le=1.0, validation_alias=AliasChoices("otel_tracing_sample_rate", "OTEL_TRACING_SAMPLE_RATE"), description="Sampling ratio for OpenTelemetry traces (0.0 to 1.0)")] = 1.0`
    </action>
    <action>Create [NEW] `@[backend_v2/models/dtos/telemetry.py]` defining strict Pydantic V2 DTOs:
      - `TraceContextCarrierDTO`:
        * `traceparent: Annotated[str, Field(pattern=r"^00-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$", description="W3C traceparent header string conforming to 00-traceid-spanid-flags")]`
        * `tracestate: Annotated[str | None, Field(default=None, description="Optional W3C tracestate header string")] = None`
        * Set `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)`.
      - `SpanSnapshotDTO`:
        * `span_id: Annotated[str, Field(description="Hex span identifier")]`
        * `parent_id: Annotated[str | None, Field(default=None, description="Hex parent span identifier if child span")]`
        * `name: Annotated[str, Field(description="Span operation name")]`
        * `duration_ms: Annotated[float, Field(ge=0.0, description="Span duration in milliseconds")]`
        * `status: Annotated[str, Field(description="Span completion status: OK or ERROR")]`
        * `attributes: Annotated[dict[str, str | int | float | bool], Field(default_factory=dict, description="Captured span attributes")]`
        * `error_message: Annotated[str | None, Field(default=None, description="Exception error message if failed")]`
        * Set `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)`.
      - `TraceSnapshotDTO`:
        * `trace_id: Annotated[str, Field(description="Hex trace identifier")]`
        * `service_name: Annotated[str, Field(description="Emitting service name")]`
        * `root_span: Annotated[str, Field(description="Name of root span")]`
        * `status: Annotated[str, Field(description="Overall trace status: OK or ERROR")]`
        * `duration_ms: Annotated[float, Field(ge=0.0, description="Total trace duration in milliseconds")]`
        * `timestamp: Annotated[str, Field(description="ISO-8601 UTC timestamp of trace completion")]`
        * `failing_step_id: Annotated[str | None, Field(default=None, description="Identifier of first failing DAG step if failed")] = None`
        * `error_summary: Annotated[str | None, Field(default=None, description="Summary message of root failure if failed")] = None`
        * `error_fingerprint: Annotated[str | None, Field(default=None, description="Deterministic error signature hash: failing_node::error_code::exception_class")] = None`
        * `span_tree: Annotated[list[SpanSnapshotDTO], Field(default_factory=list, description="Ordered hierarchy of completed spans")]`
        * `total_input_tokens: Annotated[int, Field(ge=0, default=0, description="Aggregated LLM input tokens")]`
        * `total_output_tokens: Annotated[int, Field(ge=0, default=0, description="Aggregated LLM output tokens")]`
        * `cache_hit: Annotated[bool, Field(default=False, description="Whether prompt caching hit occurred")]`
        * Set `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)`.
    </action>
    <action>Update `ExecutionMetadata` in `@[backend_v2/models/execution_core.py#L29-L53]`:
      - Add field `telemetry: TraceContextCarrierDTO | None = Field(default=None, description="W3C distributed trace context carrier for OpenTelemetry")`.
    </action>
    <action>Create [NEW] `@[client_app_v2/lib/features/execution/models/trace_context_carrier.dart]` Freezed model for W3C carrier.</action>
    <action>Update `ExecutionMetadata` in `@[client_app_v2/lib/features/execution/models/execution_metadata.dart#L9-L26]`:
      - Add field `@JsonKey(name: 'telemetry') TraceContextCarrier? telemetry`.
    </action>
    <action>Run Freezed build runner via `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/execution_metadata.dart --build` to guarantee Full-Duplex DTO parity.</action>
    <action>Create [NEW] `@[backend_v2/core/telemetry.py]` implementing:
      - `configure_telemetry(settings: Settings, service_name_override: str | None = None) -> None`:
        * Enforce idempotency via global `_TELEMETRY_CONFIGURED` guard to prevent double-initialization.
        * If Settings configuration property `otel_enabled` is False, initializes a `NoOpTracerProvider` with zero socket bindings or network calls.
        * If Settings configuration property `logfire_token` is present, executes `logfire.configure(token=settings_instance.logfire_token, service_name=service_name_override or settings_instance.otel_service_name, send_to_logfire=True)`.
        * Centralize and consolidate all built-in instrumentations in one place: `logfire.instrument_pydantic()`, `logfire.instrument_httpx()`, `logfire.instrument_requests()`, `logfire.instrument_system_metrics()`, `logfire.instrument_litellm()`, and `logfire.instrument_mcp()`.
        * Intentionally preserve omission of `logfire.instrument_redis()` to prevent console spamming from Arq worker polling.
        * If Settings configuration property `otel_exporter_otlp_endpoint` is specified, registers an `OTLPSpanExporter` bound to a `BatchSpanProcessor`.
        * In development mode (`settings.environment == "development"` or `DEBUG=True`), attach `LocalTraceSnapshotExporter` to `TracerProvider`.
      - `LocalTraceSnapshotExporter(SpanExporter)`:
        * Intercepts completed span batches and aggregates active trace spans into a structured `TraceSnapshotDTO`.
        * Context Window Protection Guard: caps serialized span tree (`max_spans: int = 60`) prioritizing root spans, failed spans (`status == 'ERROR'`), and top-latency spans, ensuring payload size strictly stays under 20 KB.
        * Computes deterministic `error_fingerprint` (`failing_step_id::error_code::exception_class`) upon failure to enable instant regression tracking in agent workflows.
        * Atomically writes serialized JSON snapshot to `data/files/traces/latest_execution_trace.json`.
        * Exposes full diagnostic context (failing node, duration, exception message, token counts, error fingerprint) to local tools and AI agents without requiring external cloud browser access.
      - `get_tracer(name: str) -> opentelemetry.trace.Tracer`: returns a named tracer instance.
      - `inject_trace_context() -> TraceContextCarrierDTO`: extracts the active OpenTelemetry context using `TraceContextTextMapPropagator().inject()` and returns a validated `TraceContextCarrierDTO`.
      - `extract_trace_context(carrier: TraceContextCarrierDTO | None) -> opentelemetry.context.Context`: safely extracts W3C traceparent into an OpenTelemetry Context. If carrier is None or validation fails, returns an empty context to permit graceful orphan span creation.
      - `use_trace_context(carrier: TraceContextCarrierDTO | None) -> Iterator[opentelemetry.context.Context]`: context manager that attaches extracted context and guarantees deterministic token detachment in a finally block.
    </action>
    <action>Configure Logfire MCP Server integration in workspace configuration to enable native AI assistant trace querying:
      - Point MCP server to `https://logfire-eu.pydantic.dev/mcp` using `LOGFIRE_MCP_TOKEN`.
      - Exposes native MCP tools (`query_spans`, `get_trace`, `get_service_metrics`) directly to Antigravity pair programmer.
    </action>
    <action>Refactor `configure_logfire()` in `@[backend_v2/logging_config.py#L105-L152]` to delegate directly to `configure_telemetry(get_settings())`, ensuring seamless zero-duplication startup across existing caller call-sites (`main.py`, `worker.py`, `run_worker.py`) without dual tracer initialization.</action>
    <constraint invariant="zero_permissive">`TraceContextCarrierDTO` and `TraceSnapshotDTO` must enforce strict validation against extra fields and invalid hex formats.</constraint>
  </step>

  <step id="3" name="W3C_TRACE_CONTEXT_PROPAGATION_PIPELINE">
    <action>Modify `@[backend_v2/services/execution/ingress_service.py#L47-L90]`, `@[backend_v2/services/execution/ingress_service.py#L190-L324]`, and `@[backend_v2/services/execution/facade.py#L50-L395]`:
      - In `create_execution_record`, call `inject_trace_context()`.
      - Assign the resulting `TraceContextCarrierDTO` to `metadata.telemetry`.
      - Persist the populated execution record into the database repository.
    </action>
    <action>Modify `@[backend_v2/workers/execution_worker.py#L73-L518]`:
      - In worker startup sequence, invoke `configure_telemetry(settings, service_name_override="quorum-worker")`.
      - In `execute_workflow_job`, reorder execution sequence: fetch `execution_data = await repository.get_execution(exec_id)` and validate `exec_record = ExecutionRecord.model_validate(execution_data, strict=False)` before opening the root span.
      - Extract `carrier = exec_record.metadata.telemetry`.
      - Wrap worker execution in `use_trace_context(carrier)` and open parent-linked root span `execution.worker_process` (refactoring line 116):
        * Set attributes: `execution.id`, `workflow.id`, `organization.id`, `user.id`.
        * If carrier was None or unparseable, set span attribute `telemetry.orphan_execution = True`.
        * Eradicate disconnected duplicate spans; ensure all downstream child steps attach to this single parent span.
    </action>
    <constraint invariant="fail_fast">Malformed or missing traceparent headers must yield an orphan root span rather than halting worker job execution.</constraint>
  </step>

  <step id="4" name="DAG_EXECUTOR_AND_NODE_LEVEL_INSTRUMENTATION">
    <action>Modify `@[backend_v2/services/orchestrator/dag_executor.py#L186-L347]`, `@[backend_v2/services/orchestrator/dag_executor.py#L435-L1291]`, and `@[backend_v2/services/orchestrator/dag_executor.py#L724-L1024]`:
      - In `DAGExecutor.execute_workflow` (#L435-L1291), open parent span `dag.orchestration` with attributes:
        * `execution.id`: execution identifier
        * `workflow.id`: workflow identifier
        * `workflow.node_count`: integer count of steps in graph
      - In `run_step_wrapper` (#L724-L1024) and `NodeExecutor.execute` (#L186-L347), wrap node evaluation in child span `dag.node.{step_id}` with attributes:
        * `node.id`: canonical step identifier
        * `node.blueprint`: task blueprint identifier
        * `node.depends_on`: list of dependent step IDs
      - If node evaluation raises an exception:
        * Record exception on active span via `span.record_exception(e)`.
        * Set span status to error: `span.set_status(trace.StatusCode.ERROR, str(e))`.
        * Re-raise `AppException` to preserve RFC 7807 failure semantics.
    </action>
    <action>Instrument `@[backend_v2/services/orchestrator/engines/tda_engine.py#L36-L258]` and `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L33-L266]`:
      - In `TDAEngine`, wrap atomization and graph evaluation in spans `tda.atomization` and `tda.topological_evaluation`.
      - In `SynthesisEngine`, wrap synthesis reduction and rendering in span `synthesis.distill`.
    </action>
    <constraint invariant="taskgroup_concurrency">When spawning asynchronous child tasks inside `asyncio.TaskGroup`, ensure the parent OpenTelemetry context is explicitly attached or inherited to prevent broken trace chains.</constraint>
  </step>

  <step id="5" name="GENAI_SEMANTIC_CONVENTIONS_IN_LLM_ADAPTERS">
    <action>Activate built-in GenAI and MCP instrumentations via [NEW] `@[backend_v2/core/telemetry.py]` and `@[backend_v2/llm/provider.py#L455-L1217]`:
      - Initialize `logfire.instrument_litellm()` in `configure_telemetry` to automatically capture standard OpenTelemetry GenAI Semantic Conventions across all LiteLLM provider completions (specifically and exhaustively: `gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, latency, and costs) without manual span wrappers.
      - Retain clean exception capture in `LiteLLMProvider._execute_paced_completion` to ensure `AppException` is recorded and propagated with RFC 7807 error codes.
    </action>
    <action>Update `@[backend_v2/llm/adapters/base_adapter.py#L141-L370]`:
      - Ensure `BaseLLMAdapter.execute_completion` and adapter subclasses propagate active OpenTelemetry context through async completion calls and record model-specific metadata on active spans.
    </action>
    <action>Modify `@[backend_v2/llm/caching_service.py#L15-L119]`:
      - Record context cache hit status on the active span attribute `gen_ai.cache.hit = True | False`.
    </action>
    <action>Activate built-in MCP instrumentation via [NEW] `@[backend_v2/core/telemetry.py]` and `@[backend_v2/services/mcp/dispatcher.py#L9-L56]`:
      - Initialize `logfire.instrument_mcp()` in `configure_telemetry` to automatically trace all MCP tool calls, parameters, and execution latencies.
      - In `ToolDispatcher.execute_tool`, wrap tool execution in `asyncio.timeout(get_settings().mcp_default_timeout_seconds)` and open child span `mcp.tool_call` with attribute `mcp.tool_id = tool_id`, ensuring tool errors and timeouts are recorded cleanly on the active span via `span.record_exception(e)` and `span.set_status(trace.StatusCode.ERROR)`.
    </action>
    <constraint invariant="pii_scrubbing">Under no circumstances may raw user prompts, confidential system instructions, or personal identifiable information be saved to OpenTelemetry span attributes.</constraint>
  </step>

  <step id="6" name="LOG_CORRELATION_AND_FINOPS_HARMONIZATION">
    <action>Modify `@[backend_v2/logging_config.py#L58-L84,L287-L380]`:
      - In `ContextFilter.filter`, extract current span from `opentelemetry.trace.get_current_span()`.
      - If span is valid, inject `record.trace_id = format(span.get_span_context().trace_id, "032x")` and `record.span_id = format(span.get_span_context().span_id, "016x")`.
      - Extend `StructuredLogContextDTO` with `trace_id: str | None = None` and `span_id: str | None = None`, and include `trace_id` and `span_id` in `JSONFormatter.format` output.
      - Attach `logfire.instrument_logging()` when Logfire is active.
      - Remove raw `os.getenv("DISABLE_LOGFIRE")` and hardcoded base URL, binding cleanly to `Settings`.
    </action>
    <action>Modify `@[backend_v2/main.py#L165-L229]`:
      - In `lifespan`, initialize telemetry via `configure_telemetry(get_settings())`.
      - Remove redundant top-level module block (#L242-L250) calling `_logfire.instrument_fastapi(app)` to prevent double-wrapping and ensure clean lifecycle sequencing.
    </action>
    <action>Modify `@[backend_v2/utils/finops_trace_analyzer.py#L158-L235]`:
      - Transition token auditing from scraping disk prompt logs to directly extracting token metrics and cache performance from structured execution telemetry.
      - Remove hardcoded shadow pricing formulas (`0.000015`, `0.000001`), resolving costs from `ExecutionRecord.dag_cost_usd`.
    </action>
    <action>Update `@[backend_v2/tests/unit/utils/test_finops_trace_analyzer.py#L48-L71]` to synchronize unit assertions with updated structured trace analyzer.</action>
    <constraint invariant="single_source_of_truth">Token metrics and financial tracking must resolve exclusively from authoritative OpenTelemetry GenAI usage attributes and ExecutionRecord telemetry entries.</constraint>
  </step>

  <step id="7" name="WORKFLOW_GOVERNANCE_UPGRADES">
    <action>Modify `@[.agents/rules/00-antigravity-core.md]`:
      - Modernize `<rule_block id="logfire_delegation_mandate">` to instruct the AI agent to inspect `data/files/traces/latest_execution_trace.json` using `view_file` and utilize Logfire MCP tools (`query_spans`, `get_trace`) to diagnose failures, trace latencies, and debug exceptions, completely replacing legacy log scraping.
    </action>
    <action>Update `@[.agents/workflows/tier4-bug-hunting.md]`:
      - In Step 1 (Identify &amp; Observability First), mandate querying the failing execution's `trace_id` in Logfire or OTel traces, and inspecting `data/files/traces/latest_execution_trace.json` with `view_file` to examine the root error span and exception details before editing code.
      - In Step 4 (5 Whys), mandate tracing root causes down the parent-child span hierarchy (`synthesis.distill` -> `tda.topological_evaluation` -> `gen_ai.client`).
      - In Step 2 (Regression Test), instruct extracting exact inputs directly from span telemetry attributes to construct deterministic pytest fixtures.
    </action>
    <action>Update `@[.agents/workflows/tier6-execution-monitor.md]`:
      - Enhance monitor to inspect active OpenTelemetry span durations (`duration_ms`) and inspect `data/files/traces/latest_execution_trace.json` to detect stalled workers in real-time.
    </action>
    <action>Update `@[.agents/workflows/tier5-session-handover.md]`:
      - Eradicate requirements to copy lengthy log text into session handovers; mandate referencing exact `trace_id` and `span_id` anchors in `task.md`.
    </action>
    <action>Update `@[.agents/workflows/tier8-audit-feature.md]`:
      - Mandate using telemetry span trees for Blast Radius analysis and failure inspection without ad-hoc print debugging.
    </action>
    <action>Update `@[.agents/workflows/tier2-execute.md]`:
      - In test failure diagnosis, mandate inspecting `data/files/traces/latest_execution_trace.json` using `view_file` to immediately locate failing node attributes and exception stack traces before modifying code.
    </action>
    <action>Update `@[.agents/workflows/tier2-hardening-backend.md]`:
      - In Phase 2 (Circuit Breaker &amp; Quality Gate), mandate that when quality gate fails, the auditor inspects `data/files/traces/latest_execution_trace.json` to immediately pinpoint the failing step ID and stack trace before attempting fixes.
      - Mandate that performance-critical hardening loops run with `--logfire` to capture latency traces before and after refactoring.
    </action>
    <action>Update `@[.agents/workflows/tier8-test-coverage-expansion.md]`:
      - In Step 3 (Error Path Analysis) and Step 5 (Quality Gate), mandate verifying that negative boundary tests assert exception recording on OpenTelemetry spans (`span.record_exception`, status `ERROR`) as captured in `data/files/traces/latest_execution_trace.json`.
    </action>
    <action>Update `@[.agents/workflows/tier5-resume.md]`:
      - In Step 2 (Baseline State Verification), mandate reading `data/files/traces/latest_execution_trace.json` using `view_file` to verify the execution and error status of the prior session before bootstrapping new tiers.
    </action>
    <action>Update `@[.agents/workflows/tier3-feature-refactor.md]`:
      - In Phase 2 (Quality Gate), mandate reading `data/files/traces/latest_execution_trace.json` to diagnose any failing test fixtures before making code alterations.
    </action>
    <action>Update `@[.agents/workflows/tier8-red-teaming-audit.md]`:
      - In Security &amp; DLP Audit, mandate querying Logfire MCP (`query_spans`) and inspecting span attributes to mathematically verify that raw user prompts, PII, and system secrets are never leaked into OpenTelemetry span attributes.
    </action>
    <constraint invariant="anti_hallucination">All workflow instructions must treat OpenTelemetry span data as deterministic physical evidence rather than heuristic guesses.</constraint>
  </step>

  <step id="8" name="AUTOMATED_TESTING_AND_AST_GUARDRAILS">
    <action>Create [NEW] `@[backend_v2/tests/unit/core/test_telemetry.py]`:
      - Test 1 (NoOp Fallback): Verify `configure_telemetry` with `otel_enabled=False` provisions a `NoOpTracer` without opening network connections.
      - Test 2 (W3C Injection &amp; Extraction): Verify round-trip conversion between OpenTelemetry SpanContext and `TraceContextCarrierDTO`.
      - Test 3 (Malformed Traceparent): Verify corrupt `traceparent` strings gracefully fall back to orphan root spans without raising uncaught exceptions.
      - Test 4 (Logfire Configuration): Verify EU base URL and Logfire instrumentation bindings when `logfire_token` is supplied.
      - Test 5 (Local Trace Snapshot Exporter): Verify `LocalTraceSnapshotExporter` serializes completed spans into valid `TraceSnapshotDTO` and writes atomically to `data/files/traces/latest_execution_trace.json`.
    </action>
    <action>Modify `@[backend_v2/tests/conftest.py]`:
      - Add `pytest_terminal_summary(terminalreporter, exitstatus, config)` hook:
        * If `exitstatus != 0` (tests failed), print a bold diagnostic banner directing the developer and AI coding agent to inspect `data/files/traces/latest_execution_trace.json` via `view_file` or query via Logfire MCP.
    </action>
    <action>Create [NEW] `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_telemetry.py]`:
      - Test 1 (Hierarchy Verification): Verify DAG parent span encapsulates individual child node spans.
      - Test 2 (Error Recording): Verify failing DAG node marks child span status as error and records exception stack trace.
      - Test 3 (TaskGroup Concurrency): Verify concurrent step execution inside `asyncio.TaskGroup` maintains correct parent span linkage.
    </action>
    <action>Create [NEW] `@[backend_v2/tests/unit/llm/test_provider_telemetry.py]`:
      - Test 1 (GenAI Attributes): Verify input tokens, output tokens, model name, and temperature are recorded on `gen_ai.client` span.
      - Test 2 (Cache Hit Attribute): Verify `gen_ai.cache.hit` is emitted accurately based on context caching responses.
      - Test 3 (Timeout Handling): Verify API timeouts set span status to error without dropping partial token counts.
    </action>
    <action>Update `@[client_app_v2/test/features/execution/models/execution_models_test.dart#L13-L75]` asserting Full-Duplex Freezed parity for `ExecutionMetadata` and `TraceContextCarrier`.</action>
    <action>Update `@[scripts/_ast_guardrails.py#L1218-L1275,L1524-L1560]`:
      - Add AST rule `QGR021` banning direct imports of `llm_debug_logger` across the entire codebase.
      - Add AST rule banning raw `print()` statements in orchestration, engine, and LLM modules.
    </action>
    <action>Update `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1281-L1294]` verifying `QGR021` triggers fatal violation on `llm_debug_logger` import.</action>
    <action>Update `@[backend_v2/tests/unit/test_logging_config.py#L247-L269]` synchronizing `test_configure_logfire_behavior` with `configure_telemetry` delegation and asserting global `_TELEMETRY_CONFIGURED` guard behavior.</action>
    <action>Update `@[backend_v2/tests/unit/test_main.py#L97-L110]` ensuring `test_lifespan_production_redis_failure` mocks `configure_telemetry` alongside `configure_logfire` during lifespan pre-flight failure assertions.</action>
    <action>In `@[backend_v2/tests/conftest.py]`:
      - Implement `@pytest.fixture def in_memory_spans() -> Iterator[InMemorySpanExporter]` using `opentelemetry.sdk.trace.export.in_memory_span_exporter.InMemorySpanExporter` and attaching it to a test `TracerProvider`, enabling deterministic span assertions across unit tests with zero deceptive mock objects.
      - Implement pytest terminal summary hook `pytest_terminal_summary` emitting local trace snapshot location (`data/files/traces/latest_execution_trace.json`) and Logfire MCP guidance directly to terminal output upon test failures.
    </action>
    <action>Unblock pytest Logfire plugin in `@[pyproject.toml#L142-L146]` by replacing `addopts = "-p no:logfire"` with `addopts = ""`.</action>
    <action>Update `@[scripts/backend_audit_loop.py#L73-L265,L268-L429]`:
      - Add `--logfire` argument in `argparse` (`@[scripts/backend_audit_loop.py#L268-L429]`).
      - Forward `["--logfire", "--logfire-service-name=quorum-audit-loop"]` into `pytest.main()` calls in `run_tests_with_strict_coverage` for both single-target (#L203) and directory (#L251) test executions when `--logfire` is supplied.
      - When tests fail, output diagnostic banner with path to `data/files/traces/latest_execution_trace.json` and Logfire MCP instructions.
    </action>
    <action>Update `@[scripts/run_e2e_variance_test.py#L1945-L2072]`:
      - Add `--logfire` argument in `argparse` to initialize `configure_telemetry()` and wrap the entire multi-run test in a root span `e2e.variance_test`.
    </action>
    <constraint invariant="istqb_coverage">Every unit test module must implement at least two negative boundary test cases (specifically and exhaustively: malformed headers, socket timeouts, or invalid configuration parameters).</constraint>
  </step>
</execution_protocol>
```

---

## 6. Verification Plan & Quality Gates

### Localized Unit Testing
Execute targeted pytest suites verifying core telemetry, DAG instrumentation, and LLM provider metrics:

```bash
uv run pytest backend_v2/tests/unit/core/test_telemetry.py
uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor_telemetry.py
uv run pytest backend_v2/tests/unit/llm/test_provider_telemetry.py
uv run pytest backend_v2/tests/unit/services/test_llm_task_executor.py
uv run pytest backend_v2/tests/unit/utils/test_finops_trace_analyzer.py

# Verify Logfire distributed tracing stream in pytest and audit loop
uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_logging_config.py --test --logfire
uv run pytest backend_v2/tests/unit/core/test_telemetry.py --logfire
```

### Full-Duplex Flutter Model Generation & Test Suite
Run Flutter code generator and verify Dart model parity:

```bash
uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/execution_metadata.dart --build
```

### ISTQB Negative & Boundary Testing Scenarios

1. **Zero-Overhead Disabled Gate (Negative Boundary)**:
   - *Input*: `Settings.otel_enabled = False`.
   - *Expected Result*: System initializes `NoOpTracer`; zero network I/O or background threads created; execution overhead delta is strictly 0.0ms.
2. **Corrupted W3C Traceparent Header (Malformed Boundary)**:
   - *Input*: `ExecutionMetadata.telemetry` contains `traceparent = "invalid-corrupted-hex-string"`.
   - *Expected Result*: Pydantic validation rejects the malformed value fail-fast at API ingress; if an unvalidated historical record is encountered, the worker catches the error, initializes an independent root span with `telemetry.orphan_execution = True`, and executes the workflow without a crash.
3. **LLM Provider Timeout Resilience (Timeout Boundary)**:
   - *Input*: Simulated model provider timeout (`APITimeoutError`).
   - *Expected Result*: Active `gen_ai.client` span status is set to error with exception attributes; collected token counts are preserved on span; error propagates cleanly to `AppException`.
4. **AI Assistant Local Diagnostic Snapshot & Failure Banner (Self-Healing Gate)**:
   - *Input*: Execution or test failure under `ENVIRONMENT=development`.
   - *Expected Result*: `data/files/traces/latest_execution_trace.json` is atomically created and contains failing step ID, root exception message, and span hierarchy; test runner emits terminal diagnostic banner directing the AI assistant to read `latest_execution_trace.json` using `view_file`.
5. **Context Window Protection & Snapshot Budget Gate (AI Observability Boundary)**:
   - *Input*: Deep workflow run with >100 steps and MCP tool calls.
   - *Expected Result*: `LocalTraceSnapshotExporter` caps the output to 60 spans, prioritizing root, failing, and top-latency spans; the resulting `latest_execution_trace.json` file size is strictly under 20 KB.
6. **Deterministic Error Fingerprinting & In-Memory Test Fixture (Developer Parity Gate)**:
   - *Input*: Test run utilizing `in_memory_spans` fixture triggering a simulated failure.
   - *Expected Result*: Generated `TraceSnapshotDTO.error_fingerprint` matches `failing_step_id::error_code::exception_class`; `in_memory_spans.get_finished_spans()` collects all spans without requiring mock patching.

### Static Quality Gates & AST Guardrail Validation
Run full repository linting, typechecking, and structural guardrail sweeps:

```bash
uv run python scripts/_ast_guardrails.py
uv run ruff check backend_v2
uv run mypy backend_v2 --strict
```

### Final E2E REST API Verification Gate
To verify end-to-end trace generation and execution integrity, execute the live integration test suite:

- **Windows 11 (PowerShell)**:
```powershell
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

- **Linux / Bash**:
```bash
RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

---

## 7. Knowledge Items (KI) Governance & Post-Implementation Architecture Updates

### 7.1. Knowledge Item (KI) Creation & Existing KI Synchronization

Following successful execution and verification of the implementation plan, the system knowledge base must be synchronized to establish the authoritative Single Source of Truth (SSOT) for distributed observability.

#### 1. Creation of New Knowledge Item: `ki_opentelemetry_logfire_observability`
A dedicated Knowledge Item must be generated in the local knowledge repository:
- **Directory**: `<appDataDir>\knowledge\opentelemetry_logfire_observability\`
- **Metadata File**: `<appDataDir>\knowledge\opentelemetry_logfire_observability\metadata.json`
  ```json
  {
    "title": "OpenTelemetry & Pydantic Logfire Distributed Tracing Architecture",
    "summary": "Establishes Quorum's Single Source of Truth (SSOT) for OpenTelemetry distributed tracing, W3C Trace Context propagation, OpenTelemetry GenAI Semantic Conventions, Logfire cloud correlation, and zero-dependency NoOp tracer fallbacks.",
    "updated_at": "2026-09-26T13:00:00+03:00",
    "references": [
      "backend_v2/core/telemetry.py",
      "backend_v2/models/dtos/telemetry.py",
      "backend_v2/settings.py",
      "backend_v2/logging_config.py",
      "backend_v2/workers/execution_worker.py",
      "backend_v2/services/orchestrator/dag_executor.py",
      "backend_v2/llm/provider.py",
      "backend_v2/services/mcp/dispatcher.py"
    ]
  }
  ```
- **Documentation Artifact**: `<appDataDir>\knowledge\opentelemetry_logfire_observability\artifacts\ki_opentelemetry_logfire_observability.md`
  The documentation must provide comprehensive, timeless specifications covering:
  1. **TracerProvider Lifecycle & Zero-Overhead Gate**: Configuration of OpenTelemetry TracerProvider, lazy initialization, OTLP span processor batching, and strict NoOp tracer fallback when tracing is disabled.
  2. **W3C Trace Context Propagation**: Two-phase context carrier transit using `TraceContextCarrierDTO` across FastAPI HTTP ingress and Redis Arq background workers, including orphan trace fallback mechanics.
  3. **GenAI Semantic Conventions**: Standardized telemetry attributes (`gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.response.finish_reasons`, `gen_ai.cache.hit`) and strict privacy guardrails banning prompt text in span attributes.
  4. **Log Correlation**: Injection of active `trace_id` and `span_id` into Python logging filters and seamless Logfire cloud exporter linkage.
  5. **Hierarchical Span Topologies**: DAG workflow orchestration spans, concurrent task group child step spans, and MCP tool execution spans.
  6. **AI Assistant Observability & Diagnostics**: Architecture of the local diagnostic snapshot exporter (`data/files/traces/latest_execution_trace.json`) and native Logfire MCP server integration (`https://logfire-eu.pydantic.dev/mcp`), enabling AI pair programmers to inspect root cause spans and query distributed traces without browser dependencies.

#### 2. Synchronization of Existing Knowledge Items
The following existing Knowledge Items must be updated to align with the new telemetry contracts:
- `@[ki_execution_record_ssot.md]`: Update the `ExecutionMetadata` domain model specification to document the addition of the `telemetry: TraceContextCarrierDTO | None` contract for distributed parent span linking.
- `@[ki_python_314_concurrency_strictness.md]`: Update the `asyncio.TaskGroup` concurrency section to document OpenTelemetry context attachment rules, ensuring concurrent worker branches propagate parent spans without cross-task context leakage.

---

### 7.2. Timeless As-Built Architecture Documentation Updates via /tier7-describe-architecture

Upon completion of `/tier2-execute` and validation of the quality gates, the physical architectural updates must be synthesized into Quorum's high-level architecture documentation using the `/tier7-describe-architecture` workflow.

#### 1. Target Architecture Documents
Execute the following Tier 7 commands sequentially:

1. **Primary Target: Resilience & Observability Pillar**:
   ```bash
   /tier7-describe-architecture docs/architecture/05_resilience_and_observability.md
   ```
   - **Target File**: `@[docs/architecture/05_resilience_and_observability.md]`
   - **Update Scope**:
     * Seamlessly integrate OpenTelemetry distributed tracing and Logfire observability into Section 2.9 (*Centralized Telemetry, Token Tracking & Multi-Tier Usage Accounting*).
     * Document W3C Trace Context propagation and distributed parent-child span linking across background workers and API boundaries.
     * Document OpenTelemetry GenAI Semantic Conventions for token metrics and context caching transparency in Section 2.8 (*Immutable System Audit Trails & Explainable AI Transparency*).

2. **Secondary Target: Cognitive Orchestration Engine Pillar**:
   ```bash
   /tier7-describe-architecture docs/architecture/03_cognitive_orchestration_engine.md
   ```
   - **Target File**: `@[docs/architecture/03_cognitive_orchestration_engine.md]`
   - **Update Scope**:
     * Document hierarchical DAG orchestration spans (`dag.orchestration`) and individual node-level execution spans (`dag.node.{step_id}`) within Section 2.3 (*DAG Step Lifecycle & State Management*).
     * Document structured exception recording on active node spans during failure states.

#### 2. Architectural Invariant Governance for Documentation
When executing `/tier7-describe-architecture`, the executing agent must strictly follow the `timeless_as_built_mandate`:
- **Strict Present-Tense Description**: Describe purely, directly, and authoritatively what the system currently has and how it operates right now ("kerro ainoastaan ja puhtaasti se mitä meillä on nyt").
- **Prohibited Patterns**:
  * NEVER include historical comparisons (specifically and exhaustively: "previously we used `llm_debug_logger`" or "we migrated from ad-hoc logging").
  * NEVER mention project phases, development stages, or roadmap iterations (specifically and exhaustively: "Phase 1", "Phase 2", "vaiheet").
  * NEVER include project identifiers (specifically and exhaustively: "Epic 94") or calendar dates.
  * NEVER use artificial meta-rules (specifically and exhaustively: "- **Law:**", "- **Enforcement:**") or label sections as "(The Laws)".
- **Directory Reference Synchronization**:
  * Update `@[.agents/rules/04_directory_reference.md]` using surgical file editing tools to register `backend_v2/core/telemetry.py` and `backend_v2/models/dtos/telemetry.py` under the appropriate capability clusters.

---

## 8. User Guidance & Next Steps

This implementation plan is locked and ready for architectural review.

You can either:
1. **Approve the plan directly for systematic execution**:
   ```bash
   /tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_OpenTelemetry_and_Logfire_Architecture.md]
   ```
2. **Red-team and stress-test the plan before execution**:
   ```bash
   /tier0-research-plan
   ```

