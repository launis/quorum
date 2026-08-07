# Phase 4: Import Migration (Batched Strangler Fig Sunset)

<objective>
Update consumer imports from `lightweight_matrix` to `atom_evaluation` in bounded batches of max 5 files. Only migrate the 6 extracted models (`ReasoningStepDTO`, `LightweightExtractionAtom`, `MatrixEvaluationItemDTO`, `AtomEvaluationItemDTO`, `ReducedAtomDTO`, `LightweightMatrixDTO`). Keep the remaining models imported from `lightweight_matrix`. Finally, remove the Strangler Fig proxy re-exports.
</objective>

<validation_gate>
After each batch, you MUST run `uv run python scripts/backend_audit_loop.py backend_v2 --test` to verify type checking and test integrity.
</validation_gate>

<anti_targets>
- DO NOT migrate imports for `LevelStatsDTO`, `XAILogDto`, `OutputProfileConfig`, `LightweightMatrixOutput`, or `MergedFactsDTO`.
- DO NOT use generic or ambiguous find-and-replace tools that could mutate unrelated imports. Use surgical `multi_replace_file_content`.
</anti_targets>

<dod_checklist>
- [ ] Migrate Batch 1 (5 Test Files)
- [ ] Migrate Batch 2 (5 Core Files)
- [ ] Remove Proxy Re-exports from `lightweight_matrix.py`
- [ ] Final global audit loop (`backend_audit_loop.py`)
</dod_checklist>

## Implementation Details

### Batch 1: Test Dependencies
Modify the following files to import the 6 extracted models from `backend_v2.models.dtos.atom_evaluation` instead of `backend_v2.models.dtos.lightweight_matrix`. If they import models that stayed (like `LightweightMatrixOutput`), keep that import separate.

- `@[c:\src\quorum\backend_v2\tests\unit\test_bug_lightweight_atom_truncation.py]`
- `@[c:\src\quorum\backend_v2\tests\unit\services\test_execution.py]`
- `@[c:\src\quorum\backend_v2\tests\unit\models\dtos\test_lightweight_matrix.py]`
- `@[c:\src\quorum\backend_v2\tests\unit\models\dtos\test_lightweight_matrix_golden.py]`
- `@[c:\src\quorum\backend_v2\tests\unit\models\dtos\test_lightweight_matrix_schema.py]`

### Batch 2: Core Infrastructure
Modify the following files to import the 6 extracted models from `backend_v2.models.dtos.atom_evaluation`.
*Note: `matrix_domain_parser.py` and `scoring.py` import BOTH moved and retained models. You must split their imports explicitly.*

- `@[c:\src\quorum\backend_v2\tests\integration\test_lazy_llm_simulation.py]`
- `@[c:\src\quorum\backend_v2\services\matrix_domain_parser.py]`
- `@[c:\src\quorum\backend_v2\services\orchestrator\matrix_reducer.py]`
- `@[c:\src\quorum\backend_v2\models\v2_core.py]`
- `@[c:\src\quorum\backend_v2\hooks\scoring.py]`

### Sunset Proxy
- `@[c:\src\quorum\backend_v2\models\dtos\lightweight_matrix.py]`
  - Delete the 6 re-exports.
