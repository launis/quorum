# EPIC 135: Schema Convergence & Legacy Matrix Eradication - Tracker

**Epic Reference**: `@[c:\src\quorum\docs\epic\EPIC_135_Schema_Convergence_Architecture.md]`
**Task Directory**: `@[c:\src\quorum\docs\epic\tasks_EPIC_135/]`

```xml
<required_context_rules>
  - `@[c:\src\quorum\.agents\rules\00-antigravity-core.md]`
  - `@[c:\src\quorum\.agents\rules\01-python-backend.md]`
  - `@[c:\src\quorum\.agents\rules\02_flutter_desktop.md]`
  - `@[c:\src\quorum\.agents\rules\04_directory_reference.md]`
</required_context_rules>
```

## Phase Execution Status

### Phase 1A: Enum Convergence (Backend)
**Plan:** `@[c:\src\quorum\docs\epic\tasks_EPIC_135\01a_enum_convergence_backend_plan.md]`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_135\01a_enum_convergence_backend_plan.md] @[c:\src\quorum\docs\epic\EPIC_135_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_135\01a_enum_convergence_backend_plan.md] @[c:\src\quorum\docs\epic\EPIC_135_tracker.md]`
  - [x] Step 0: STRATEGIC ALIGNMENT CHECK
  - [x] Step 1: MAP ENUMS AND SCORECARD ATOM
  - [x] Step 2: UPDATE REDUCED ATOM DTO
  - [x] Step 3: PRODUCER ATOMIC INTEGRITY
  - [x] Step 4: UPDATE TESTS
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_135\01a_enum_convergence_backend_plan.md] @[c:\src\quorum\docs\epic\EPIC_135_tracker.md]`

### Phase 1B: Enum Convergence (Frontend)
**Plan:** `@[c:\src\quorum\docs\epic\tasks_EPIC_135\01b_enum_convergence_frontend_plan.md]`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_135\01b_enum_convergence_frontend_plan.md] @[c:\src\quorum\docs\epic\EPIC_135_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_135\01b_enum_convergence_frontend_plan.md] @[c:\src\quorum\docs\epic\EPIC_135_tracker.md]`
  - [x] Step 0: STRATEGIC ALIGNMENT CHECK
  - [x] Step 1: UPDATE DART ENUMS AND MODELS
  - [x] Step 1.5: UPDATE UI WIDGET LOGIC
  - [x] Step 2: UPDATE FRONTEND TESTS
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_135\01b_enum_convergence_frontend_plan.md] @[c:\src\quorum\docs\epic\EPIC_135_tracker.md]`

### Phase 2: Producer Refactoring
**Plan:** `@[c:\src\quorum\docs\epic\tasks_EPIC_135\02_producer_refactoring_plan.md]`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_135\02_producer_refactoring_plan.md] @[c:\src\quorum\docs\epic\EPIC_135_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_135\02_producer_refactoring_plan.md] @[c:\src\quorum\docs\epic\EPIC_135_tracker.md]`
  - [x] Step 0: STRATEGIC ALIGNMENT CHECK
  - [x] Step 1: REWRITE PROCESS_ATOM_EVALUATION METHOD
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_135\02_producer_refactoring_plan.md] @[c:\src\quorum\docs\epic\EPIC_135_tracker.md]`

### Phase 3: Consumer Convergence (Scoring Hook Unification)
**Plan:** `@[c:\src\quorum\docs\epic\tasks_EPIC_135\03_consumer_convergence_plan.md]`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_135\03_consumer_convergence_plan.md] @[c:\src\quorum\docs\epic\EPIC_135_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_135\03_consumer_convergence_plan.md] @[c:\src\quorum\docs\epic\EPIC_135_tracker.md]`
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_135\03_consumer_convergence_plan.md] @[c:\src\quorum\docs\epic\EPIC_135_tracker.md]`

### Phase 4: Deletion & Sunset
**Plan:** `@[c:\src\quorum\docs\epic\tasks_EPIC_135\04_deletion_and_sunset_plan.md]` (Placeholder - Generate via /tier1-planner later)
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_135\04_deletion_and_sunset_plan.md] @[c:\src\quorum\docs\epic\EPIC_135_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_135\04_deletion_and_sunset_plan.md] @[c:\src\quorum\docs\epic\EPIC_135_tracker.md]`
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_135\04_deletion_and_sunset_plan.md] @[c:\src\quorum\docs\epic\EPIC_135_tracker.md]`

---

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK]** Backend E2E Validation via `backend_audit_loop.py`
- [ ] **[NOK]** Frontend Flutter `flutter_audit_loop.py`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Documentation & Knowledge Item Update
- [ ] **[NOK]** Create a Knowledge Item (KI) for new SSOTs in `<appDataDir>/knowledge/`.
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_135_Schema_Convergence_Architecture.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

---

## Instructions for the Execution Agent
- Enforce ATOMIC COMMITS per file/domain as dictated by `00-antigravity-core.md`.
- Ensure you run Database Seeding (`uv run python backend_v2/seed/run_seed.py local`) when explicitly needed.
- Always use `@-reference` syntax when referring to files in commands or paths.
- You MUST update the `/tier5-resume` or `/tier0-research-plan` command at the bottom of this tracker before handing over the session. Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the next command in your chat response so the user can easily copy-paste it to continue. 
- The mandatory workflow loop is: `/tier0-research-plan` (Phase N) -> `/tier2-execute` (Phase N) -> `/tier8-audit-plan` (Phase N) -> `/tier0-research-plan` (Phase N+1). You MUST ALWAYS pass BOTH the plan and the tracker file in the `/tier0-research-plan` command. 
- Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`. 
- Note: You do not need to specify `--rules` in the resume command; context rules are self-hydrating.

---

## Requirements Traceability Matrix

| Req ID | Epic Detail | Phase | Target Plan Step |
|--------|-------------|-------|------------------|
| R1 | Map `AtomEvaluationStatus.PASS` to `ExecutionStatus.PASSED`. | 1A / 1B | 01a (Step 4), 01b (Step 2) |
| R2 | Map `AtomEvaluationStatus.FAIL` to `ExecutionStatus.FAILED`. | 1A / 1B | 01a (Step 4), 01b (Step 2) |
| R3 | Map `AtomEvaluationStatus.CONTESTED` to `ExecutionStatus.PASSED` (with `contextual_override=True`). | 1A | 01a (Step 1) |
| R4 | Map `AtomEvaluationStatus.DLQ` to `ExecutionStatus.SYSTEM_ERROR`. | 1A / 1B | 01a (Step 1), 01b (Step 1) |
| R5 | Update `ScorecardAtomDTO.status` to `LaxExecutionStatus | None`. | 1A | 01a (Step 1) |
| R6 | Ensure `ScorecardAtomDTO` explicitly sets `visual_intent=VisualIntent.WARNING` for Contested parity. | 1A | 01a (Step 1) |
| R7 | Update `HumanOverrideRequest.new_status` to `LaxExecutionStatus` and its Pydantic descriptions. | 1A | 01a (Step 1) |
| R8 | Update `HumanOverrideDTO.new_status` to `ExecutionStatus` and its Pydantic descriptions. | 1A | 01a (Step 1) |
| R9 | Update `ReducedAtomDTO.status` to `LaxExecutionStatus`. | 1A | 01a (Step 2) |
| R10 | Migrate Dart `client_app_v2/.../enums.dart` to use `ExecutionStatus` and delete old enums. | 1B | 01b (Step 1) |
| R11 | Update Dart `matrix_scorecard_dto.dart` usages to `ExecutionStatus` and rebuild freezed. | 1B | 01b (Step 1) |
| R12 | Modify `anchor_validation_service.py` to strongly type `atom: AtomResultDTO` and `-> AtomResultDTO`. | 2 | 02 (Step 1) |
| R13 | Update `matrix_domain_parser.py` to use `ExecutionStatus.FAILED` retaining `ScorecardAtomDTO`. | 1A | 01a (Step 3) |
| R14 | Update `matrix_reducer.py` to use `ExecutionStatus.PASSED`. | 1A | 01a (Step 3) |
| R15 | Update `test_lazy_llm_simulation.py` to construct `AtomResultDTO` fixtures. | 2 | 02 (Step 3) |
| R16 | Remove `is_dag_mode` and `results/evaluations` branching in `scoring.py`. | 3 | 03 |
| R17 | Remove legacy fallback chain and duct-tape model `LightweightExtractionAtom` from `scoring.py`. | 3 | 03 |
| R18 | Eradicate `getattr()` duck-typing and Finnish constants from `scoring.py`. | 3 | 03 |
| R19 | Delete `LightweightExtractionAtom`, `MatrixEvaluationItemDTO`, `AtomEvaluationItemDTO`. | 4 | 04 |
| R20 | Delete `AtomEvaluationStatus` entirely from backend enums. | 4 | 04 |

---

# Session Handover Context
## Achieved
- Formally executed Epic 135 planning phase via `/tier1-planner`.
- Generated 3 granular Micro-Chunked execution plans for Phase 1A, Phase 1B, and Phase 2.
- Created placeholder plans for Phase 3 and 4.
- Passed all mandatory XML bounds checks and format audits.
- Generated the centralized Tracker for Tier 2 execution orchestration.
- Successfully executed Phase 1A Enum Convergence (Backend), strictly mapping `AtomEvaluationStatus` to `ExecutionStatus` while passing the `backend_audit_loop.py` quality gate with 30% coverage and MyPy strict checks.
- Completed `/tier8-audit-plan` for Phase 1A Enum Convergence (Backend). Epic boundaries were preserved perfectly and 82.82% codebase coverage was achieved on the quality gate.
- Successfully executed Phase 1B Enum Convergence (Frontend), strictly mapping `AtomEvaluationStatus` to `ExecutionStatus` in UI logic and tests, passing the `flutter_audit_loop.py` quality gate with pixel-perfect matching in golden snapshots.
- Completed `/tier8-audit-plan` for Phase 1B Frontend Convergence. Epic boundaries were preserved perfectly and all frontend tests passed natively.
- Successfully executed Phase 2 Producer Refactoring (Epic 135), strictly typing the payload to `AtomResultDTO` and enforcing the Null Hypothesis constraint for overridden atoms. Passed the `backend_audit_loop.py` quality gate with 100% test coverage.
- Completed `/tier8-audit-plan` for Phase 2 Producer Refactoring. Epic boundaries were preserved, no duck-typing remains, and global quality gate execution passed.

## Learned
- **Baseline State Snapshot**: `AtomEvaluationStatus` and `LaxAtomEvaluationStatus` exist in both `enums.py` and `enums.dart` and are deeply coupled in the presentation layer (`ScorecardAtomDTO`). `matrix_domain_parser.py` and `matrix_reducer.py` explicitly rely on `AtomEvaluationStatus.PASS`/`FAIL`. The dual pipeline is active in `scoring.py` relying on `is_dag_mode` and `getattr` duck-typing. The system is structurally sound but burdened with this technical debt, causing the "Override Inflation" bug.
- **Pydantic Frozen Integrity**: Encountered and solved an immutability constraint where `ScorecardAtomDTO` is `frozen=True`. The `visual_intent` override for `CONTESTED` was solved using a `mode="before"` `@model_validator` to safely map values via dictionary preprocessing.
- **Flutter Enum Semantic Parity**: Enum names need consistent handling (e.g., `ExecutionStatus.systemError.name` instead of raw strings like `'dlq'`) in filtering logic in `atom_matrix_table_widget.dart` to maintain semantic equality with the backend.
- **Pydantic Validation (Phase 2)**: Relying on Pydantic `ConfigDict(frozen=True)` and validators ensures that no corrupted state persists across the execution lifecycle. The null-hypothesis rule for quoted evidence is strongly enforced both at instantiation and hydration logic.

  - Completed `/tier0-research-plan` for Phase 2 (Producers). The Tier 0 analysis identified 3 critical flaws and 3 moderate issues. The plan has been fully rewritten: Step 1 expanded from type-hint swap to full method rewrite (eradicating duck-typing, adapting to `source_quote` string, `evaluation_reasoning`, dropping `internal_logic_en`). Step 2 (test update) removed and deferred to Phase 3. Target files pruned of already-migrated `matrix_domain_parser.py` and `matrix_reducer.py`. DoD and test_contracts expanded with negative test cases.
  
## Achieved (Continued)
- Completed `/tier0-research-plan` for Phase 3 Consumer Convergence. Overwrote the placeholder plan with a strict execution strategy that eradicates `is_dag_mode` and duck-typing, enforcing Pydantic V2 Fail-Fast rules.
- Successfully executed Phase 3 Consumer Convergence Execution. Fully removed `is_dag_mode`, `getattr` duck-typing, and legacy data models from `scoring.py`. Successfully migrated all tests in `test_scoring.py` to use strict validation rules and expected `AppException` exceptions for Fail-Fast behavior. Passed the backend quality gate with 88% coverage.
- Completed `/tier8-audit-plan` for Phase 3 Consumer Convergence. Epic boundaries were preserved perfectly, `is_dag_mode` and duck-typing completely eradicated.

## Remaining
- Phase 4 Deletion & Sunset Audit.
- Post-Implementation Gates (Hardening, E2E, Architecture Sync).

## Achieved (Phase 4)
- Completed `/tier0-research-plan` for Phase 4 Deletion & Sunset. The Tier 0 analysis identified two missing dependencies (`matrix_domain_parser.py` and `test_lazy_llm_simulation.py`) that still used deprecated DTOs and legacy `"atom_id"` extraction. The Phase 4 plan was updated to mandate refactoring these consumers before safely deleting the dead models, preventing a catastrophic Fail-Fast runtime crash.
- Successfully executed Phase 4 Deletion & Sunset. Replaced `MatrixEvaluationItemDTO` with `AtomResultDTO` in `matrix_domain_parser.py` and `test_lazy_llm_simulation.py`. Deleted legacy test files. Removed deprecated models (`MatrixEvaluationItemDTO`, `AtomEvaluationItemDTO`, `LightweightExtractionAtom`) from `atom_evaluation.py` and `AtomEvaluationStatus` from `enums.py`. Passed the backend quality gate with 82.72% coverage.

## Course Correction (Phase 2) — RESOLVED
- Both directives from the prior session have been addressed in the mutated plan:
  1. ✅ Step 1 now mandates a COMPLETE method rewrite with exact field mappings (`source_quote` instead of `exact_quotes`, `evaluation_reasoning` instead of `semantic_reasoning`, dropped `internal_logic_en` hydration).
  2. ✅ `test_lazy_llm_simulation.py` removed from Phase 2 scope entirely. Deferred to Phase 3.


## Resume Command
/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_135\04_deletion_and_sunset_plan.md] @[c:\src\quorum\docs\epic\EPIC_135_tracker.md]
