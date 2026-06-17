# Phase 4: Seed Corrected Rules (Epic 60)

Source: Epic 60, ACTION-3

## 1. Goal
Seed the newly corrected cognitive extraction rules into the TinyDB local database. The rules have already been updated in `seed_data.json` to a deterministic ECA format, but the active database must be refreshed to use them.

## 2. Target Files
- `TARGET (Execute)`: `backend_v2/seed/run_seed.py`
- `TARGET (Modify)`: None (Data only)
- `CONTEXT (Read-Only)`: `backend_v2/seed/seed_data.json`

## 3. Architectural Invariants & Hardening Mandates
- **[tier1-planner rule]**: "SEEDING COMMAND MANDATE: If you instruct the execution agent or the user to run the database seed script, you MUST explicitly include the target environment argument (e.g. `uv run python backend_v2/seed/run_seed.py local`)."

## 4. Implementation Steps

### Step 1: Execute Seeding
- Run the command: `uv run python backend_v2/seed/run_seed.py local`.
- Confirm in the logs that the newly formulated extraction rules (without "Otherwise.") have been successfully ingested into `db_v2.json`.

## 5. Testing & Quality Gate Plan
- **Manual Verification:** Perform a test run of the LLM pipeline and verify that the system is properly enforcing the new explicit terminal directives.

---

### Session Handover
To execute this Epic iteratively, start a NEW chat session and run:
`/tier5-resume --target docs/epic/epic_60_tracker.md`
