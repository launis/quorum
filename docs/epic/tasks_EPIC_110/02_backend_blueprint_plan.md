# Phase 3: Backend Intelligence Delegation (Epic 110)

## Objective
Implement Phase 3 (Backend Intelligence Delegation & Data Restoration) in Python as per `@[c:\src\quorum\docs\epic\EPIC_110_dumb_painter_sdui_architecture.md]`.

## Architectural Invariants
- **Rule Injection**: Must adhere to `@[c:\src\quorum\.agents\rules\00-antigravity-core.md]`, `@[c:\src\quorum\.agents\rules\01-python-backend.md]`.
- **Producer-Consumer Integration**: `blueprint.py` must take on the full cognitive load of resolving synthesis titles from the database and loading system labels from the `.arb` dictionaries. It produces a fully self-contained payload.

## Targets

### 1. `@[c:\src\quorum\backend_v2\services\blueprint.py]` (TARGET)
- Modify mapping logic to loop through `content_blocks` and `layout.synthesis_blocks`.
- Resolve `matrix_column_labels` and `extension_labels` from the layout block and pass them exactly as required into the SDUI payload.
- Ensure `row_explanations_cache` (Selite), `level_breakdown` (Tasojakauma), and `raw_score` / `normalized_score` are correctly mapped from `MatrixPayload` to `ScoreAxisDTO`.
- Re-implement extraction of `coaching`, `falsification`, `missing_context`, etc., from `MatrixPayload.extensions` into `ReportDataDTO.grouped_extensions`.
- Fix the Amnesia Bug: Prevent overwriting AI-generated scores with zero when `evaluated_atoms` are missing.

## Testing & Quality Gate Plan
- Run Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test`
- Ensure no regressions occur in existing report generation logic.
