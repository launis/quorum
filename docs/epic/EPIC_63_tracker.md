# Epic 63: Execution Model Decoupling & Parity Hardening — Master Tracker

> **Epic Source**: [EPIC_63_Execution_Model_Decoupling_and_Parity_Hardening.md](file:///c:/src/quorum/docs/epic/EPIC_63_Execution_Model_Decoupling_and_Parity_Hardening.md)
> **Generated**: 2026-06-04

---

## Execution Plan Status

- [NOK] [phase1_execution_core_leaf_module.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_63/phase1_execution_core_leaf_module.md) — Create `ExecutionCoreFields` leaf module & refactor `ExecutionRecord` inheritance
- [NOK] [phase2_workflow_state_domain_sync.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_63/phase2_workflow_state_domain_sync.md) — Refactor `WorkflowState` to inherit `ExecutionCoreFields` & remove duplicated fields
- [NOK] [phase3_factory_adapter_api_hardening.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_63/phase3_factory_adapter_api_hardening.md) — Implement `create_execution_record` factory & replace all direct instantiation sites
- [NOK] [phase4_ci_structural_parity_test.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_63/phase4_ci_structural_parity_test.md) — CI-level meta-test enforcing `ExecutionCoreFields` inheritance parity
- [NOK] [phase5_clean_slate_db_reset.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_63/phase5_clean_slate_db_reset.md) — Wipe & re-seed development database with new schema
- [NOK] [phase6_hardening_verification.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_63/phase6_hardening_verification.md) — Full audit loop, hardening compliance & regression testing

---

## Dependency Chain

```
Phase 1 (Leaf Module + ExecutionRecord) → Phase 2 (WorkflowState) → Phase 3 (Factory) → Phase 4 (Meta-Test) → Phase 5 (DB Reset) → Phase 6 (Verification)
```

Phases 1 and 2 can potentially be combined in a single session if context allows. Phase 3 depends on Phase 1 (needs `ExecutionCoreFields` to exist). Phase 4 depends on both Phase 1 and 2 (needs both child classes refactored). Phase 5 depends on all code phases (1-4). Phase 6 is the final verification gate.

---

## File Impact Matrix

| File | Phase | Action |
|---|---|---|
| `backend_v2/models/execution_core.py` | 1 | NEW |
| `backend_v2/models/v2_core.py` | 1 | MODIFY |
| `backend_v2/models/state.py` | 2 | MODIFY |
| `backend_v2/services/execution.py` | 3 | MODIFY |
| `backend_v2/services/orchestrator/dag_executor.py` | 3 | MODIFY |
| `backend_v2/tests/unit/test_v2_core_models.py` | 1, 2, 4 | MODIFY |
| `docs/architecture/02_domain_models.md` | 6 | MODIFY |
