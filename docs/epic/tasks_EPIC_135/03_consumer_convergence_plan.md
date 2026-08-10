# Phase 3: Consumer Convergence (Scoring Hook Unification)

**Objective:** Remove all dual-path branching from scoring.py.
**Source:** @[c:\src\quorum\docs\epic\EPIC_135_Schema_Convergence_Architecture.md#L90-L99] Phase 3: Consumer Convergence (Scoring Hook Unification)

**Expected Target Files:**
- `@[c:\src\quorum\backend_v2\hooks\scoring.py]`
- `@[c:\src\quorum\backend_v2\tests\unit\hooks\test_scoring.py]`

<required_context_rules>
- `@[c:\src\quorum\.agents\rules\00-antigravity-core.md]`
- `@[c:\src\quorum\.agents\rules\01-python-backend.md]`
</required_context_rules>

## Proposed Changes

### 1. `backend_v2/hooks/scoring.py`
- **Root Cause & Justification**: `scoring.py` maintains an `is_dag_mode` flag to bifurcate between the legacy `AtomEvaluationItemDTO` model and the new `AtomResultDTO` DAG model. This dual path causes "Override Inflation" bugs because the legacy path relies on `getattr()`/`hasattr()` duck-typing which bypasses strict validation. We must enforce strict Pydantic V2 validations, meaning all incoming data must be processed as `AtomResultDTO` (Fail-Fast).
- **Execution Directives**:
  - **Lines 644-660**: Remove the `is_dag_mode` flag. Force the payload check to exclusively expect the `"results"` key. If it is missing, raise a validation error instantly.
  - **Lines 821-870**: Delete the `is_dag_mode` check and the legacy fallback block attempting to parse `AtomEvaluationItemDTO` and `LightweightExtractionAtom`. Unconditionally parse `ev_dto` as `AtomResultDTO.model_validate(ev_dict, strict=True, context=val_context)`.
  - **Lines 871+**: Refactor atom evaluation checks to directly access properties on `AtomResultDTO` (e.g. `ev_dto.tda_id` instead of duck-typing `aid`), removing all `getattr` and `hasattr` usage.
  - **Lines 913-932**: Unify quote processing. Read quotes strictly from `ev_dto.source_quote`.
  - **Lines 961-967**: Unify contextual override checking. Access `ev_dto.structural_location` and `ev_dto.evaluation_reasoning` directly. Replace the Finnish hardcoded defaults `"Tuntematon sijainti"` with `"Unknown location"` and `"Ei perustelua"` with `"No reasoning provided"`.

### 2. `backend_v2/tests/unit/hooks/test_scoring.py`
- **Root Cause & Justification**: Test fixtures explicitly set `metadata={"is_dag_mode": True}` to trigger the new path. Since the new path is now the only path, this flag is obsolete and its presence obscures the fact that the entire system has natively converged to DAG schemas.
- **Execution Directives**:
  - **Lines 1143, 1207, 1272**: Remove `metadata={"is_dag_mode": True},` from the `HookState` mock setups entirely in `test_scoring_matrix_namespace_isolation`, `test_scoring_regular_tda_path_bypasses_namespace_check`, and `test_failed_atom_with_override_does_not_inflate_score`.

<anti_targets>
- Do NOT add fallback schemas if `AtomResultDTO` validation fails. The system must Fail-Fast.
- Do NOT use regex or fuzzy matching to extract values from `evaluations`.
</anti_targets>

<dod_checklist>
- [ ] `is_dag_mode` completely removed from `scoring.py`.
- [ ] `"results"` is the only accepted payload key.
- [ ] `AtomEvaluationItemDTO` and `LightweightExtractionAtom` usages deleted from `scoring.py`.
- [ ] `getattr` / `hasattr` duck-typing eradicated in the scoring loop.
- [ ] Finnish string literals replaced with English constants.
- [ ] Test fixtures updated to remove the `is_dag_mode` flag.
</dod_checklist>

<validation_gate>
- Execute `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring.py --test`
- Execute `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/hooks/test_scoring.py --test`
- Execute `uv run pytest backend_v2/tests/unit/hooks/test_scoring.py`
</validation_gate>
