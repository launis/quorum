# Epic 92: Enriched Atom Graph Architecture - Master Tracker

> **Source**: `c:\src\quorum\docs\epic\EPIC_92_Enriched_Atom_Graph_Architecture.md`

## 🔴 Baseline Metrics
- `[ ]` [BASELINE] Record current test count and coverage before starting execution. (Tier 2 must execute this).

## 🟡 Phase 1: Topological Engine & Deterministic Rules
- `[ ]` Implement Phase 1 (See `docs\epic\tasks_epic_92\Phase_1_Topological_Engine.md`)
- `[ ]` Legacy Migration & UI Validation: Refactor existing evaluation logic to use the new SSOT `TopologicalEvaluator` and verify E2E tests pass.
- `[ ]` Create Knowledge Item (KI) for `TopologicalEngine` in `<appDataDir>\knowledge\`.

## 🟡 Phase 2: Local Extraction & GECL (LLM Pipeline)
- `[ ]` Implement Phase 2 (See `docs\epic\tasks_epic_92\Phase_2_Local_Extraction.md`)

## 🟡 Phase 3: Global Sliding Window (The Synthesizer)
- `[NOK]` Invoke the Tier 1 Planner again to generate detailed plans for Phase 3 and beyond based on the updated codebase state.
- `[ ]` (Pending Plan)

## 🟡 Phase 4: The Graph Execution & Cascade (Full System Test)
- `[ ]` (Pending Plan)

## 🟡 Phase 5: Schema Projection (The Output)
- `[ ]` (Pending Plan)

## 🟢 End-of-Epic Audits
- `[ ]` Tier 2 Hardening: Run Tier 2 Hardening Loop against newly created backend directories.
- `[ ]` Proxy Sunset & Consumer Migration: Search/replace old import paths to bypass proxies before deleting legacy files.
- `[ ]` Pre-Delete Audit: Verify no orphaned dependencies remain and completely DELETE the original legacy files.
- `[ ]` Baseline Parity & Zero-Loss Audit: Mathematically verify that the final test count and coverage match or exceed the `[BASELINE]` recorded in Phase 1.

---

# Session Handover Context

**Instructions for the Execution Agent**:
To execute this Epic iteratively, start a NEW chat session and run the following command to bootstrap the correct Tier 2 execution workflow.

`/tier5-resume --workflow="/tier2-execute" --target="c:\src\quorum\docs\epic\epic_92_tracker.md, c:\src\quorum\docs\epic\EPIC_92_Enriched_Atom_Graph_Architecture.md" --achieved="Generated Phase 1 and Phase 2 Implementation Plans for Epic 92." --learned="Epic 92 introduces a Two-Pass Hybrid-DAG Pipeline to solve context loss in flattened atoms. Phase 1 focuses on the SSOT TopologicalEvaluator with native asyncio.TaskGroup cascade and strict Pydantic V2 schemas. Phase 2 introduces the LLM Map-Reduce Entity Ontology extraction." --remaining="Execute Phase 1: Topological Engine & Deterministic Rules, including the Legacy Migration First mandate." --rules="00-antigravity-core.md, 01-python-backend.md"`
