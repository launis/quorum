# EPIC 104: TDA Pipeline Extraction — Master Tracker

> **Epic Source**: [EPIC_104_tda_pipeline_extraction.md](file:///c:/src/quorum/docs/epic/EPIC_104_tda_pipeline_extraction.md)
> **Task Directory**: [tasks_tda_pipeline_extraction/](file:///c:/src/quorum/docs/epic/tasks_tda_pipeline_extraction)
> **Domain**: Backend (Python) only — no Flutter changes.
> **Created**: 2026-07-20

---

## Execution Tracker

### Phase 0: Protocol Prerequisites & Directory Structure
- [ ] **[Tier 0 Red-Team]** Run `/tier0-research-plan` on [phase_0_protocol_prerequisites.md](file:///c:/src/quorum/docs/epic/tasks_tda_pipeline_extraction/phase_0_protocol_prerequisites.md) in a fresh context window. *(High-risk: new SSOT Protocol + DTOs)*
- [x] **[BASELINE]** Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test` and record passing test count: 1110 tests passed.
- [x] Execute [phase_0_protocol_prerequisites.md](file:///c:/src/quorum/docs/epic/tasks_tda_pipeline_extraction/phase_0_protocol_prerequisites.md) via `/tier2-execute`
- [x] Atomic `git commit` after quality gate passes.

### Phase 1: TDA Engine Extraction & Settings Migration
- [x] Execute [phase_1_tda_engine_extraction.md](file:///c:/src/quorum/docs/epic/tasks_tda_pipeline_extraction/phase_1_tda_engine_extraction.md) via `/tier2-execute`
- [x] Atomic `git commit` after quality gate passes.

### Phase 2: LLMNodeStrategy Refactoring & Engine Delegation
- [ ] Execute [phase_2_strategy_refactoring.md](file:///c:/src/quorum/docs/epic/tasks_tda_pipeline_extraction/phase_2_strategy_refactoring.md) via `/tier2-execute`
- [ ] Atomic `git commit` after quality gate passes.

### Integration Checkpoint: Backend End-to-End Validation
- [ ] Run full backend test suite: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
- [ ] Verify existing execution workflows operate identically through the new engine delegation path. Compare test count against `[BASELINE]`.

### Re-Plan Remaining Phases
- [ ] **[NOK]** Invoke the Tier 1 Planner (`/tier1-planner`) again to generate detailed plans for Phase 3 (DAG Executor Wiring) and Phase 4 (Testing) based on the updated codebase state.

### Phase 3: DAG Executor Wiring & Fail-Fast Routing (PLACEHOLDER)
- [ ] Execute [phase_3_dag_executor_wiring.md](file:///c:/src/quorum/docs/epic/tasks_tda_pipeline_extraction/phase_3_dag_executor_wiring.md) via `/tier2-execute` *(after detailed plan is generated)*
- [ ] Atomic `git commit` after quality gate passes.

### Phase 4: Engine Unit Tests & Strategy Test Modernization (PLACEHOLDER)
- [ ] Execute [phase_4_testing.md](file:///c:/src/quorum/docs/epic/tasks_tda_pipeline_extraction/phase_4_testing.md) via `/tier2-execute` *(after detailed plan is generated)*
- [ ] Atomic `git commit` after quality gate passes.

---

## Post-Extraction Pipeline

### Tier 2 Hardening
- [ ] Run `/tier2-hardening-backend` targeted at `backend_v2/services/orchestrator/engines/` and `backend_v2/models/dtos/engine.py`. After structural extraction (Zero Behavioral Change), modernize the new code's architecture to strict Pydantic V2, Push models, and PEP 257 docstrings via the Tier 2 Hardening Loop.

### Proxy Sunset & Consumer Migration
- [ ] Codebase-wide search for any remaining direct references to the old inline TDA pipeline pattern in `llm.py`. Verify no orphaned imports reference the 5 sub-services from within `llm.py`. Remove any deprecated proxy imports.

### Pre-Delete Audit
- [ ] Verify no orphaned dependencies remain from the old inline pipeline.
- [ ] Confirm `llm.py` no longer contains any inline `from backend_v2.services.orchestrator.two_pass_atomizer import` or similar.
- [ ] Confirm all consumers route through `TDAEngine`.

### Semantic Coverage & Zero-Loss Audit
- [ ] Mathematically verify that line coverage of the *surviving business logic* remains >90%.
- [ ] Verify all old inline pipeline tests have been replaced by strict `EngineExecutionResult` Pydantic V2 boundary tests.
- [ ] Compare final passing test count against `[BASELINE]`.

### Documentation & Knowledge Item Update
- [ ] Update `docs/architecture/` with the new `ExecutionEngine` Protocol and `engines/` directory.
- [ ] Update `.agents/rules/04_directory_reference.md` to include the `engines/` subdirectory under the orchestrator module.
- [ ] Create a Knowledge Item (KI) for the `ExecutionEngine` Protocol SSOT in `<appDataDir>/knowledge/`.

---

## Instructions for the Execution Agent

1. You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session.
2. After completing each phase, mark the corresponding items as `[x]`.
3. After completing Phase 2, run the Integration Checkpoint before proceeding to Phase 3.
4. Phase 3 and Phase 4 are PLACEHOLDER plans — invoke `/tier1-planner` to generate detailed plans before executing.

---

## Requirements Traceability Matrix

| Epic Requirement | Phase/Plan |
|-----------------|-----------|
| Create `engines/` directory structure | Phase 0 |
| Define `EngineExecutionRequest` DTO (dataclass, frozen) | Phase 0 |
| Define `EngineExecutionResult` DTO (Pydantic V2, strict, frozen) | Phase 0 |
| Epic 105 forward compatibility (`compiled_schema`, `hydrated_messages`) | Phase 0 |
| Define `ExecutionEngine` Protocol | Phase 0 |
| Extract TDA pipeline into `TDAEngine` | Phase 1 |
| Top-level imports for 5 sub-services in `tda_engine.py` | Phase 1 |
| Migrate `SlidingWindowLinker` hardcoded config to `settings.py` | Phase 1 |
| Exception ACL (wrap sub-service errors in `AppException`) | Phase 1 |
| Engine statelessness across `execute()` calls | Phase 1 |
| Live telemetry flush via `trace_callback` | Phase 1 (field defined), Phase 2+ (wiring) |
| Override `LLMNodeStrategy.__init__` with mandatory `engine` | Phase 2 |
| Replace inline pipeline with `await self._engine.execute(...)` | Phase 2 |
| Retain anomaly retry loop, post-hooks, telemetry in `llm.py` | Phase 2 |
| Update all existing `test_llm.py` tests to inject mock engine | Phase 2 |
| `TYPE_CHECKING` for engine type hint in `llm.py` | Phase 2 |
| Explicit DI injection in `dag_executor.py` (`TDAEngine(compiler=...)`) | Phase 3 |
| Lazy DI import of `TDAEngine` inside routing branch | Phase 3 |
| Remove default fallback `else` → Fail-Fast `UnknownStrategyError` | Phase 3 |
| Preserve `engine_override` routing for `PRE_HYDRATED_SYNTHESIS` | Phase 3 |
| Preserve `DYNAMIC_TOOL_AGENT` awareness | Phase 3 |
| Engine unit tests (`test_tda_engine.py`) | Phase 4 |
| Progress callback routing verification (0-15%, 15-35%, 35-60%, 60-100%) | Phase 4 |
| Parameter Object pattern (single `EngineExecutionRequest` DTO) | Phase 0 + Phase 1 |
| Concurrency & cancellation integrity (`semaphore`, `running_event`) | Phase 0 (DTO fields) + Phase 1 (propagation) |
| Dependency starvation prevention (only `PromptCompiler` in constructor) | Phase 1 |
| Observability black hole prevention (`trace_callback`) | Phase 0 (field) + Phase 1 (flush mechanism) |
| Append-Only Law & Seed Data — No execution migration needed | N/A (Epic explicitly states disposable) |
| Cross-Epic Sync: Preserve `synthesis` branch for Epic 105 | Phase 3 |
| Cross-Epic Sync: Epic 104 executes FIRST | This tracker (entire execution) |

---

# Session Handover Context

## Achieved
- Phase 0 Executed: Created `engines/` directory structure, ExecutionEngine Protocol, EngineExecutionRequest DTO, and strict EngineExecutionResult Pydantic V2 DTO.
- Phase 1 Executed: Extracted the inline TDA pipeline into `TDAEngine`. Migrated hardcoded `SlidingWindowLinker` settings to `settings.py`. Added unit tests for `TDAEngine` to verify the exception ACL and basic pipeline execution. Passed strict 30% coverage and Universal Quality Gate.

## Learned
- `LLMNodeStrategy` does NOT have its own `__init__` — it inherits from `NodeStrategy` which accepts 10 positional args. Phase 2 must override `__init__`.
- `TwoPassAtomizer` and others do not accept `semaphore` in their method signatures; they create their own using settings. The `running_event` was handled directly in the engine before delegation.

## Remaining
- Phase 2: LLMNodeStrategy Refactoring (detailed plan ready)
- Integration Checkpoint: Backend End-to-End Validation
- Phase 3: DAG Executor Wiring (placeholder — re-plan after Phase 2)
- Phase 4: Testing (placeholder — re-plan after Phase 3)
- Post-phases: Tier 2 Hardening, Proxy Sunset, Pre-Delete Audit, Semantic Coverage Audit, Documentation/KI update.

---

## Resume Command

```
/tier5-resume --workflow=/tier2-execute --target="docs\epic\EPIC_104_tda_pipeline_extraction_tracker.md, docs\epic\tasks_tda_pipeline_extraction\phase_2_strategy_refactoring.md" --rules="00-antigravity-core.md, 01-python-backend.md, 04_directory_reference.md"
```
