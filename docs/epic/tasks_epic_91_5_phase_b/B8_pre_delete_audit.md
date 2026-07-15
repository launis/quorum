# Epic 91.5 Phase B8: Pre-Delete Audit

## Objective
Perform a final audit to verify that no orphaned dependencies remain and completely DELETE the original legacy files as mandated by Epic 91.5 (Hard Cutover).

## Context & Architectural Mandates
- **Hard Cutover / Big Bang:** The `backend_v2/models/dtos/report` directory and `result_projector.py` must be completely eradicated.
- **Fail-Fast:** Do not leave unused code "just in case". Orphaned code decays and causes confusion.

## Target Directories (Modify)
- `backend_v2/models/dtos/`
- `backend_v2/services/`

## Proposed Changes
### 1. Legacy File Eradication
- Verify that `backend_v2/models/dtos/report/` no longer exists. If it does, recursively delete it.
- Verify that `backend_v2/services/orchestrator/result_projector.py` (or similar location) no longer exists. If it does, delete it.

### 2. Dependency Graph Audit
- Perform a final search (e.g., using `grep_search`) across `backend_v2/` for any hardcoded strings, relative imports, or references to the deleted legacy files.
- Purge or fix any lingering dangling references.

## Testing & Quality Gate Plan
- Run MyPy or the audit script globally over the backend to catch any broken imports caused by the deletions.
- `uv run python scripts/backend_audit_loop.py backend_v2 --test`

---

# Session Handover
To execute this Epic iteratively, start a NEW chat session and run the following command:
`/tier5-resume --workflow=/tier2-execute --target="docs/epic/epic_91_5_phase_b_tracker.md, docs/epic/tasks_epic_91_5_phase_b/B8_pre_delete_audit.md" --rules=".agents/rules/00-antigravity-core.md, .agents/rules/01-python-backend.md"`
