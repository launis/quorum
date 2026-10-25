# Tracker: ReportService Decomposition (Two-Epoch Strangler Fig Protocol)

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Phase Execution Status

### Phase 1: Lifecycle Extraction
**Plan:** @[docs/epic/tasks_report_service/phase1_lifecycle_extraction.md]
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_report_service/phase1_lifecycle_extraction.md] @[docs/epic/report_service_decomposition_tracker.md]` (`7a680476b`)
- [ ] **[NOK] Audit:** /tier8-audit-plan @[docs/epic/tasks_report_service/phase1_lifecycle_extraction.md] @[docs/epic/report_service_decomposition_tracker.md]
  - [x] Step 1.1: Create target domain file `lifecycle_service.py` and transplant CRUD methods
  - [x] Step 1.2: Update `ReportService` proxy delegations and verify test baseline

### Phase 2: Compilation Extraction
**Plan:** @[docs/epic/tasks_report_service/phase2_compilation_extraction.md]
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_report_service/phase2_compilation_extraction.md] @[docs/epic/report_service_decomposition_tracker.md]` (`c19a5b55f`)
- [ ] **[NOK] Audit:** /tier8-audit-plan @[docs/epic/tasks_report_service/phase2_compilation_extraction.md] @[docs/epic/report_service_decomposition_tracker.md]
  - [x] Step 2.1: Create target domain file `compilation_service.py` and transplant compiler methods
  - [x] Step 2.2: Update `ReportService` proxy delegations and verify test baseline

### Phase 3: Format Reader Extraction
**Plan:** @[docs/epic/tasks_report_service/phase3_format_reader_extraction.md]
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_report_service/phase3_format_reader_extraction.md] @[docs/epic/report_service_decomposition_tracker.md]` (`e2d53ac48`)
- [ ] **[NOK] Audit:** /tier8-audit-plan @[docs/epic/tasks_report_service/phase3_format_reader_extraction.md] @[docs/epic/report_service_decomposition_tracker.md]
  - [x] Step 3.1: Create target domain file `format_reader_service.py` and transplant reader methods
  - [x] Step 3.2: Update `ReportService` proxy delegations and verify test baseline

### Phase 4: Atomic Cutover & Consumer Rewiring
**Plan:** @[docs/epic/tasks_report_service/phase4_cutover.md]
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_report_service/phase4_cutover.md] @[docs/epic/report_service_decomposition_tracker.md]` (`ae46aed27`)
- [ ] **[NOK] Audit:** /tier8-audit-plan @[docs/epic/tasks_report_service/phase4_cutover.md] @[docs/epic/report_service_decomposition_tracker.md]
  - [x] Step 4.1: Mechanically rewire 1-hop consumer imports per `symbol_migration_map.md`
  - [x] Step 4.2: Partition monolithic test file into focused modular test suites
  - [x] Step 4.3: Create package facade `report/__init__.py` and delete `report_service.py`
  - [x] Step 4.4: Register QGR017 lockdown in `scripts/_ast_guardrails.py` and run global audit loop

### Post-Implementation Gates

#### Tier 2 Hardening (Backend)
- [ ] **[NOK] Tier 2 Hardening (Backend):** /tier2-hardening-backend
  - [x] @[backend_v2/services/report/lifecycle_service.py]
  - [ ] @[backend_v2/services/report/compilation_service.py]
  - [ ] @[backend_v2/services/report/format_reader_service.py]

#### Conditional SDUI Semantic Parity Gate
- [ ] **[NOK] SDUI Parity Test:** `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`

#### Final Documentation Sync
- [ ] **[NOK] Tier 7 Architecture Sync:** `/tier7-describe-architecture`

### Final Epic Audit
- [ ] **[NOK] Global Audit Gate:** `uv run python scripts/backend_audit_loop.py backend_v2/services/report/ --test`

## Instructions for the Execution Agent
1. Execute Epoch 1 sequentially through Phases 1 to 4 with zero behavioral mutations.
2. Verify all 29 baseline tests remain 100% green after each phase.
3. In Phase 4, execute the atomic cutover from `report_service.py` to `report/__init__.py`.
4. Proceed to Epoch 2 Post-Implementation Gates only after the proxy file is deleted.
5. In Epoch 2, synchronize 1-hop callers if method signatures are tightened during hardening.

## Requirements Traceability Matrix
- **REQ-001:** Extract lifecycle and CRUD operations to `backend_v2/services/report/lifecycle_service.py`.
- **REQ-002:** Extract multi-format compilation and DLQ dispatch to `backend_v2/services/report/compilation_service.py`.
- **REQ-003:** Extract artifact reading and format byte streams to `backend_v2/services/report/format_reader_service.py`.
- **REQ-004:** Maintain 100% green test baseline against proxy `report_service.py` throughout Epoch 1.
- **REQ-005:** Rewire 1-hop consumers mechanically and delete external proxy `report_service.py`.
- **REQ-006:** Execute Tier 2 Hardening on all 3 extracted sub-modules in Epoch 2.

# Session Handover Context

## Achieved
- Completed AST symbol extraction and call-graph analysis of `backend_v2/services/report_service.py` (749 lines, 19 symbols).
- Established verified test baseline: 29 passed, 95% line coverage under `pytest --cov`.
- Generated `symbol_migration_map.md` mapping 19 symbols across 3 target bounded contexts.
- Generated Fast-Track decomposition plans: Phase 1 (Lifecycle), Phase 2 (Compilation), Phase 3 (Format Reader), Phase 4 (Cutover).
- Generated master tracker strictly partitioned into Epoch 1 (Phases 1-4) and Epoch 2 (Post-Implementation Gates).
- Completed Phase 1 (Lifecycle Extraction): Created `backend_v2/services/report/lifecycle_service.py` (`ReportLifecycleService`), wired 1-line proxy delegations in `backend_v2/services/report_service.py`, added Phase 1 test contracts and unit test suite `backend_v2/tests/unit/services/report/test_lifecycle_service.py`, and passed `backend_audit_loop.py` with 100% test pass rate and >95% coverage.
- Completed Phase 2 (Compilation Extraction): Created `backend_v2/services/report/compilation_service.py` (`ReportCompilationService`), wired 1-line proxy delegations in `backend_v2/services/report_service.py`, added Phase 2 test contracts (`test_compile_and_persist_artifact_success`, `test_compile_execution_not_ready`) and unit test suite `backend_v2/tests/unit/services/report/test_compilation_service.py`, and passed `backend_audit_loop.py` with 100% test pass rate and 100% coverage on `compilation_service.py`.
- Completed Phase 3 (Format Reader Extraction): Created `backend_v2/services/report/format_reader_service.py` (`ReportFormatReaderService`), wired 1-line proxy delegations in `backend_v2/services/report_service.py`, added Phase 3 test contracts (`test_get_report_sdui_success`, `test_get_report_pdf_bytes_success`) and unit test suite `backend_v2/tests/unit/services/report/test_format_reader_service.py`, and passed `backend_audit_loop.py` with 100% test pass rate and 100% coverage on `format_reader_service.py`.
- Completed Phase 4 (Atomic Cutover & Consumer Rewiring): Rewired 1-hop consumers (`backend_v2/api/dependencies.py`, `backend_v2/workers/report_worker.py`, `backend_v2/workers/synthesis_worker.py`, `backend_v2/workers/synthesis_reducers.py`, and unit tests) to import from `backend_v2.services.report`, created package facade `backend_v2/services/report/__init__.py`, partitioned monolithic test suite into `test_lifecycle_service.py`, `test_compilation_service.py`, `test_format_reader_service.py`, and `test_report_facade.py` (47 tests, 100.00% coverage across all 4 modules in `backend_v2/services/report/`), deleted external proxy `backend_v2/services/report_service.py`, registered `QGR017` lockdown in `scripts/_ast_guardrails.py`, and updated `.agents/rules/04_directory_reference.md`.
- Completed Epoch 2 Tier 2 Hardening on `@[backend_v2/services/report/lifecycle_service.py]`: Decomposed `_get_validated_profile` and `_resolve_default_profile_id` (<50 lines per method), enforced RFC 7807 structured `extra` logging and `exc_info=True`, replaced `or` coalescing with explicit `is not None` conditional, documented explicit `ErrorCodes` in PEP 257 `Raises:` blocks, and verified 182/182 rules plus 100% test coverage via `backend_audit_loop.py`.

## Learned
- `ReportService` exhibits high internal cohesion within its 3 domains; leaf models are already cleanly separated in `models/dtos/` and `models/domain/`.
- Fast-Track mode cleanly eliminates planning latency: all 4 phase plans were generated without mid-flight halts.
- Standard TRK001-TRK006 tracker structure seamlessly accommodates the Two-Epoch protocol when Epoch 1 is mapped to `## Phase Execution Status` and Epoch 2 is mapped to `### Post-Implementation Gates`.
- When adding `QGR017` unit tests for a retired module in `backend_v2/tests/unit/scripts/test_ast_guardrails.py`, avoid placing the literal retired module path string in test docstrings so codebase-wide substring regression checks (`test_zero_legacy_report_service_imports`) pass with zero false positives.

## Resume Command
`/tier2-hardening-backend @[backend_v2/services/report/compilation_service.py] @[docs/epic/report_service_decomposition_tracker.md]`

## Remaining
- Audit Phase 1: `/tier8-audit-plan @[docs/epic/tasks_report_service/phase1_lifecycle_extraction.md] @[docs/epic/report_service_decomposition_tracker.md]`
- Audit Phase 2: `/tier8-audit-plan @[docs/epic/tasks_report_service/phase2_compilation_extraction.md] @[docs/epic/report_service_decomposition_tracker.md]`
- Audit Phase 3: `/tier8-audit-plan @[docs/epic/tasks_report_service/phase3_format_reader_extraction.md] @[docs/epic/report_service_decomposition_tracker.md]`
- Audit Phase 4: `/tier8-audit-plan @[docs/epic/tasks_report_service/phase4_cutover.md] @[docs/epic/report_service_decomposition_tracker.md]`
- Execute Epoch 2 Tier 2 Hardening on `@[backend_v2/services/report/compilation_service.py]` and `@[backend_v2/services/report/format_reader_service.py]`

### Hardening State Snapshot
- **TARGETS:** `@[backend_v2/services/report/lifecycle_service.py]`, `@[backend_v2/services/report/compilation_service.py]`, `@[backend_v2/services/report/format_reader_service.py]`
- **DONE:** `@[backend_v2/services/report/lifecycle_service.py]`
- **REMAINING:** `@[backend_v2/services/report/compilation_service.py]`, `@[backend_v2/services/report/format_reader_service.py]`
