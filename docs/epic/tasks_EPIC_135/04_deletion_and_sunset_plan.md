# Phase 4: Deletion & Sunset

**Objective:** Safely refactor remaining consumers of deprecated domain models, eradicate duck typing and legacy identifier lookups, and physically remove all deprecated schemas, enums, and dead test files from the codebase.
**Source:** @[c:\src\quorum\docs\epic\EPIC_135_Schema_Convergence_Architecture.md#L101-L112] Phase 4: Deletion & Sunset

## User Review Required
No major architectural breaking changes that haven't already been aligned upon in Epic 135. This phase finalizes the cleanup of dead code.

## Open Questions
None.

## Proposed Changes

---

### Phase 4 Target Definitions

#### [MODIFY] [matrix_domain_parser.py](file:///c:/src/quorum/backend_v2/services/matrix_domain_parser.py)
- Replace imports: Remove `MatrixEvaluationItemDTO` and use `AtomResultDTO` from `backend_v2.models.v2_core`.
- In `parse_matrices`:
  - Change the dictionary loop lookup from `if "atom_id" in ev:` to `if "tda_id" in ev:` (since the Phase 2 producer now emits `AtomResultDTO` which uses `tda_id`).
  - Change assignment to `step_evals_map[ev["tda_id"]] = ev`.
  - Validate using `val_data = AtomResultDTO.model_validate(ev_data)`.
  - Pass `semantic_reasoning=val_data.evaluation_reasoning` to `ScorecardAtomDTO` during extraction mapping.

#### [MODIFY] [test_lazy_llm_simulation.py](file:///c:/src/quorum/backend_v2/tests/integration/test_lazy_llm_simulation.py)
- Replace all `AtomEvaluationItemDTO` instantiations with `AtomResultDTO` instantiations.
- Ensure the arguments strictly conform to `AtomResultDTO` signature (e.g., replace `atom_id` with `tda_id`, replace string statuses with `ExecutionStatus`, add `depends_on_tda_ids=[]`, `short_circuit_reason_tda_ids=[]`).
- Update test logic and assertions to utilize the null-hypothesis design of `AtomResultDTO` rather than the old constraints (e.g., verifying `source_quote=None`).

#### [DELETE] [test_lightweight_matrix.py](file:///c:/src/quorum/backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py)
- Fully delete the file.

#### [DELETE] [test_lightweight_matrix_schema.py](file:///c:/src/quorum/backend_v2/tests/unit/models/dtos/test_lightweight_matrix_schema.py)
- Fully delete the file.

#### [DELETE] [test_bug_lightweight_atom_truncation.py](file:///c:/src/quorum/backend_v2/tests/unit/test_bug_lightweight_atom_truncation.py)
- Fully delete the file.

#### [DELETE] [test_atom_evaluation.py](file:///c:/src/quorum/backend_v2/tests/unit/models/dtos/test_atom_evaluation.py)
- Fully delete the file as it only tests `AtomEvaluationItemDTO`.

#### [MODIFY] [atom_evaluation.py](file:///c:/src/quorum/backend_v2/models/dtos/atom_evaluation.py)
- Delete `MatrixEvaluationItemDTO` class.
- Delete `AtomEvaluationItemDTO` class.
- Delete `LightweightExtractionAtom` class.
- *CRITICAL MAINTAIN*: Leave `ReasoningStepDTO` intact, as it is still required by `ScorecardAtomDTO` via `v2_core.py`.
- Remove `AtomEvaluationStatus` and `LaxAtomEvaluationStatus` imports and usages. Ensure the file correctly imports `ExecutionStatus`.

#### [MODIFY] [enums.py](file:///c:/src/quorum/backend_v2/models/enums.py)
- Delete `AtomEvaluationStatus` enum completely.
- Delete `LaxAtomEvaluationStatus` alias.

## Verification Plan

### Automated Tests
- Run `uv run python scripts/backend_audit_loop.py backend_v2/models backend_v2/services backend_v2/tests --test`

### Manual Verification
- N/A. Handover to Tier 2 Execution.
