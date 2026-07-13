# Epic 92 Tracker: Enriched Atom Graph Architecture (Phase 2/3)

## Task List
- [x] Phase 1.1: SSOT Models & Topological Evaluator Core (`docs\epic\tasks_EPIC_92_Enriched_Atom_Graph_Architecture\phase_1_1_ssot_models_and_engine.md`)
- [x] Phase 1.2: Legacy Migration & KI Registration (`docs\epic\tasks_EPIC_92_Enriched_Atom_Graph_Architecture\phase_1_2_legacy_migration.md`)
- [ ] Phase 2.1: GECL Prompts & Atomizer Pipeline (`docs\epic\tasks_EPIC_92_Enriched_Atom_Graph_Architecture\phase_2_1_gecl_and_prompts.md`)
- [ ] Phase 2.2: Alias Engine Integration (`docs\epic\tasks_EPIC_92_Enriched_Atom_Graph_Architecture\phase_2_2_alias_engine_integration.md`)
- [ ] [NOK] Tier 1 Planner Invocation: "Invoke the Tier 1 Planner again to generate detailed plans for Phase 3 (Global Sliding Window), Phase 4 (Graph Execution & Cascade), and Phase 5 (Schema Projection) based on the updated codebase state."
- [ ] [NOK] Tier 2 Hardening: "Run the Tier 2 Hardening Loop (e.g. `/tier2-hardening-backend`) specifically targeted at the newly created/modified directories (`backend_v2/services/orchestrator` and `backend_v2/models/dtos/`). Ensure architecture is modernized to Pydantic V2 and Push models."
- [ ] [NOK] Pre-Delete Audit: "Verify no orphaned dependencies remain. Delete any original legacy files that were fully replaced, ensuring strict SSOT."
- [ ] [NOK] Baseline Parity & Zero-Loss Audit: "Mathematically verify that the final test count and coverage match or exceed the [BASELINE] recorded in Phase 1.1, proving no original functionality was accidentally destroyed."

# Session Handover Context
## Achieved
Epic 92 Phase 1.1 & Phase 1.2 are fully complete. `TopologicalEvaluator` and strict DAG models (`LinkedAtomGraph`, `ExtractedAtom`) are active. Legacy chunk loops in `llm.py` have been migrated to the SSOT DAG engine.
Baseline Parity Audit ran successfully with 1099 passed tests and 79.87% total backend test coverage.

## Learned
Legacy chunks must be wrapped with padded hex `tda_id` (e.g., `tda_0000000000000000`) to pass Pydantic Regex validation when integrated into the `LinkedAtomGraph`.
MyPy strict mode requires explicit type annotations and closure parameter binding (`_syn_instr: dict[str, Any] | None = syn_instr`) inside TaskGroup evaluation callbacks (Ruff B023/MyPy untyped-def fixes).
The Topological Evaluator prevents deadlocks effectively but mandates all nodes eventually resolve to `PASSED` or `SYSTEM_ERROR` via strict `ExecutionStatus`.

## Remaining
Execute Phase 2 micro-plans to build the GECL Prompts & Atomizer Pipeline, integrating the `AliasEngine` for node evaluation.

---
**Instructions for the Execution Agent:**
To execute this Epic iteratively, update your session handover context and run the following command in a new session:
`/tier5-resume --workflow=/tier2-execute --target="c:\src\quorum\docs\epic\EPIC_92_Enriched_Atom_Graph_Architecture_tracker.md, c:\src\quorum\docs\epic\EPIC_92_Enriched_Atom_Graph_Architecture.md" --rules="00-antigravity-core.md, 01-python-backend.md"`
