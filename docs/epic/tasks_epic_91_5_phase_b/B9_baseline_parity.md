# Epic 91.5 Phase B9: Baseline Parity & Zero-Loss Audit

## Objective
Mathematically verify that the final test count and coverage match or exceed the `[BASELINE]` recorded in Phase 1, proving no original functionality was accidentally destroyed. Document the new architecture.

## Context & Architectural Mandates
- **Zero Behavioral Change Mandate:** Refactoring must not break business logic.
- **Documentation & Knowledge Item Mandate:** New SSOT features or directory changes must be reflected in `docs/architecture/`, `.agents/rules/04_directory_reference.md`, and potentially Knowledge Items.

## Target Files (Modify)
- `docs/architecture/` (Various)
- `.agents/rules/04_directory_reference.md`

## Proposed Changes
### 1. Final Regression & Coverage Test
- Execute the global test suite: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- Verify that the test count and coverage have not degraded.
- Verify the Golden Master E2E tests specifically pass against the new `v2_core.ReportDataDTO` structures.

### 2. Architectural Documentation Update
- Check `.agents/rules/04_directory_reference.md` to ensure `backend_v2/models/v2_core.py` and the removal of the old `dtos/report` folder are documented.
- Verify if any Knowledge Item (`<appDataDir>/knowledge/`) needs updating regarding the new `ExecutionStatus` rules or SDUI layout principles established in Epic 91.5. If required, construct the update or leave instructions to do so.

## Testing & Quality Gate Plan
- The audit itself is the final test gate.

---

# Session Handover
To execute this Epic iteratively, start a NEW chat session and run the following command:
`/tier5-resume --workflow=/tier2-execute --target="docs/epic/epic_91_5_phase_b_tracker.md, docs/epic/tasks_epic_91_5_phase_b/B9_baseline_parity.md" --rules=".agents/rules/00-antigravity-core.md, .agents/rules/01-python-backend.md"`
