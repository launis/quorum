# Phase 4: Binäärilukko ja Arkkitehtuurinen Jitter (Seed Data Updates)

Source: Epic System 2 Variance Analysis Report (Liite 3.5 & 3.6)
Goal: Remove the cognitive double-bind regarding `CONTESTED` from the global protocol and eliminate the erratic "Best-of-3" fallback by upgrading analytical nodes strictly to the `strict` (Pro) strategy.

## Architectural Invariants (from .agents/rules & hardening.xml)
- **Database Schema Hallucination (Rule 75)**: The SSOT `seed_data.json` is law. Mutating it must be exact.
- **Seeding Command Mandate (Rule 17 in Tier 1 Planner)**: Database seed MUST include environment target `uv run python backend_v2/seed/run_seed.py local`.

## Proposed Changes

### Seed Data

#### [MODIFY] backend_v2/seed/seed_data.json (CONTEXT: None)
- **Requirement 1**: Remove the Binary Lock from `blk_573802341db9d68c` (Global Zero-Trust Evidence Extraction Protocol).
- **Details**: Update the `FINAL JSON BINDING RULE` to explicitly allow `CONTESTED` while adding a deterrent bias: `"Conclude strictly with 'CONDITION MET', 'CONDITION NOT MET', or 'CONTESTED' (only if explicit evidence BOTH supports and contradicts the condition). Excessive use of CONTESTED will result in failure."`
- **Requirement 2**: Eliminate Architectural Jitter for Intelligence Nodes.
- **Details**: Locate the routing configurations for Analyst (`sp_b5c751d1cbe24735`), Falsifier (`sp_6f40b964895c426b`), Logician (`sp_8daee218c6b14f02`), Overseer (`sp_dfc365994fa944b2`), and Judge (`sp_48974af1fc584407`). Update their `"model_strategy"` property from `"fast"` to `"strict"`.

## Verification Plan

### Manual Verification
- After applying the changes, the execution agent MUST run the seed script locally:
  `uv run python backend_v2/seed/run_seed.py local`
- Verify the DB `protocols` table and `workflow_steps` table correctly reflect the updated texts and strict routing.

---
**Session Handover**
To execute this phase, please start a NEW chat session and run:
`/tier5-resume --target docs/epic/system2_variance_analysis_report_tracker.md`
