# Phase 5: Schema Projection (The Output)

Source: Epic Phase 5.5 & 6.2

## Objective
To transform the internal mathematical graph (`AtomExecutionState`) and static extracted data into the Epic 91.5 compatible `ReportDataDto` using the `ResultProjector`. This ensures strict ICU Markdown Parity and decoupling of rendering logic.

## Architectural Rules Injected
- **Epic 91.5: Strict ICU Markdown Parity:** The backend must output a Flat Adjacency List to prevent Flutter UI serialization loops and enable predictable Markdown rendering.
- **01-python-backend.md: Zero ORM Bleed:** Ensure output schemas strictly match `AtomResultDTO` and `HydratedAtomDTO` using `ConfigDict(frozen=True)`.

## Proposed Changes

### Target: `backend_v2/services/orchestrator/result_projector.py` [MODIFY]
- Update `ResultProjector` to map the `EnrichedAtomGraph` outputs into `ReportDataDto`.
- **Mapping Logic:**
  - Iterate through `AtomExecutionState` results.
  - Map status to UI-friendly representation (PASSED, FAILED, N_A, SYSTEM_ERROR).
  - Map `short_circuit_reason_tda_ids`.
  - Extract static data (`resolved_claim`, `source_quote`) into the `hydrated_references` dictionary mapping by `tda_id`.
  - Compile the final `ReportDataDto` enforcing Pydantic strictness (`model_validate`).

### Target: `docs/architecture/06_enriched_atom_graph_engine.md` [NEW]
- Create architectural documentation mapping out the Two-Pass DAG Builder, Sliding Window, and 6-State Tilakone. Update `04_directory_reference.md` if any new directories were created.

### Target: `knowledge/dag_engine_dto_projection_rules/artifacts/ki_dag_engine_dto_projection_rules.md` [MODIFY]
- Update the Knowledge Item to reflect the finalized Enriched Atom Graph structures, overriding the old legacy matrix projection rules.

## Verification & Quality Gate
- **Unit Tests:** `tests/unit/services/orchestrator/test_result_projector.py` ensuring that `ReportDataDto` generated is 100% compliant with Epic 91.5 specifications.
- **Universal Quality Gate:** Run `backend_audit_loop.py`.

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
