# Epic 91.5 Phase B6: Tier 2 Hardening

## Objective
Modernize and harden the newly created or updated code from Phase B against the Phase 9 architectural standards using the Tier 2 Hardening loop. Ensure strict Pydantic V2 and Push models are enforced across all updated directories.

## Context & Architectural Mandates
- **Fail-Fast & Strictness:** Ensure all Pydantic models have `model_config = ConfigDict(strict=True, frozen=True, extra='forbid')`.
- **Modern Python 3.14 Syntax:** Ensure PEP 695 generics, bitwise unions (`| None`), and `TaskGroup`s are used in updated code.

## Target Directories (Modify)
- `backend_v2/models/`
- `backend_v2/services/`
- `backend_v2/api/`
- `backend_v2/hooks/`

## Proposed Changes
### 1. Hardening Execution
- Execute the backend audit loop on the core directories modified during Epic 91.5 Phase B.
- Command: `uv run python scripts/backend_audit_loop.py backend_v2/models/`
- Command: `uv run python scripts/backend_audit_loop.py backend_v2/services/`
- Command: `uv run python scripts/backend_audit_loop.py backend_v2/hooks/`
- Automatically resolve any Ruff formatting, MyPy strict typing errors, or deprecated logic identified.
- Ensure all docstrings meet the PEP 257 Google-style mandate.

## Testing & Quality Gate Plan
- The audit loop will automatically run Pytest.
- Resolve any test failures immediately. Ensure no functionality was degraded.

---

# Session Handover
To execute this Epic iteratively, start a NEW chat session and run the following command:
`/tier5-resume --workflow=/tier2-execute --target="docs/epic/epic_91_5_phase_b_tracker.md, docs/epic/tasks_epic_91_5_phase_b/B6_tier_2_hardening.md" --rules=".agents/rules/00-antigravity-core.md, .agents/rules/01-python-backend.md"`
