# Epic: System 2 Reliability Fixes - Phase 2: Universal Prompt Structural Audit

**Source:** Epic Phase 2

## Goal
Implement a universal standardization across the entire rule library (Seed Data) to prevent attention breakdown and test data leakage. Introduce abstract `contrastive_example` fields for all complex causality-evaluating atoms.

## Target Files
- `[MODIFY] c:\src\quorum\backend_v2\seed\seed_data.json`

## Context Files
- `c:\src\quorum\backend_v2\seed\run_seed.py`

## Architectural Invariants & Hardening Mandates
- **Domain-Agnosticism & Test Data Leak (from Context Handover):** We do not optimize rules based on single test docs ("Whack-a-mole"). Seed data `contrastive_example` examples must be completely universal (X/Y/Z) and not reference any specific domain.
- **Database Schema Hallucination (from 00-antigravity-core.md):** The SSOT structure in `seed_data.json` is immutable architectural law. Do not autonomously migrate relational arrays. Add the required fields strictly within the existing JSON architecture.
- **Seeding Command Mandate (from tier1-planner.md):** The seed script MUST explicitly include the target environment argument (e.g., `local`).

## Implementation Steps

### 1. Standardize Seed Data (`seed_data.json`)
- Audit all `tda_assertions` inside the matrix categories (e.g., `matrix_toulmin` and others).
- For every atom/assertion that evaluates causality or complex mechanisms, ensure a `contrastive_example` field exists and is populated.
- **Domain-Agnostic Format:** The contrastive examples MUST use universal abstract variables (X, Y, Z). 
  - *Acceptable:* "X affects Y via Z"
  - *Unacceptable:* "X is associated with Y"
- Remove any domain-specific references from existing `contrastive_example` fields to prevent test data leakage.

### 2. Local Seeding Execution
- Execute the seeding script to propagate changes to the local development database:
  `uv run python backend_v2/seed/run_seed.py local`

### 3. Update Documentation
- **Target:** `c:\src\quorum\docs\architecture\system_quality_standards.md`
- Document the rule that all complex assertions MUST have domain-agnostic (X/Y/Z) contrastive examples.

## Testing & Quality Gate Plan
- **Verification:** Ensure the `run_seed.py local` command executes without schema validation errors.
- **Quality Gate:** Run the backend audit loop on the seed directory: `uv run python scripts/backend_audit_loop.py backend_v2/seed/ --test`

---

### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_system2_reliability_fixes_tracker.md`
