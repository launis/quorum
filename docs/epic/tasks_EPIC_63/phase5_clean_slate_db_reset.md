# Phase 5: Clean-Slate Database Reset & Re-Seed

> **Source**: Epic 63 – Phase 5 (Tietokannan ja Siemenaineiston Pyyhintä / Clean-Slate DB Reset)

---

## Objective

Wipe the development TinyDB database and re-seed it using the updated schema. Since no legacy execution data needs to be preserved (Clean-Slate Mandate), this is a straightforward database reset that validates the new `ExecutionCoreFields` inheritance chain works end-to-end with Pydantic V2 strict validation.

---

## Architectural Invariants (Injected from `.agents/rules/`)

| Rule ID | Rule | Enforcement |
|---|---|---|
| `live_database_mutation` (03_seed_vault.md) | NEVER modify `data/db_v2.json` directly | Reset via `run_seed.py` only |
| `the_no_legacy_mandate` (00-antigravity-core.md) | No backwards compatibility or fallback logic | Clean wipe, no migration |
| `zero_legacy_fallback_hacks` (01-python-backend.md) | No `@model_validator(mode="before")` to scrub legacy fields | Models must be pure |

---

## Scoping

### TARGET Files (Modify)
- **None** — No code files are modified in this phase. This is a pure operational phase.

### CONTEXT Files (Read-Only)
- `backend_v2/seed/run_seed.py` — Seed execution script
- `backend_v2/seed/seed_data.json` — SSOT seed data
- `data/db_v2.json` — Local TinyDB database (will be wiped)

---

## Milestones

### Milestone 5.1: Wipe Development Database (Source: Epic Phase 5, Toimenpide)

Execute the following command to wipe and re-seed the database:

```powershell
uv run python backend_v2/seed/run_seed.py local
```

This command:
1. Wipes the local `data/db_v2.json` TinyDB database
2. Re-seeds all system configs, prompt blocks, workflows, steps, and output profiles from `seed_data.json`
3. Validates all seeded data against Pydantic V2 strict schemas

### Milestone 5.2: Validate Clean-Slate Integrity (Source: Epic Phase 5, Polymorphic Seed)

After re-seeding, verify the database integrity:

```powershell
uv run pytest backend_v2/tests/unit/test_seed_architectural_guardrails.py -v
```

And verify the schema alignment test:

```powershell
uv run pytest backend_v2/tests/unit/test_run_seed.py -v
```

---

## Documentation Update

No documentation changes needed for this phase — it's a pure operational reset.

---

## Testing & Quality Gate Plan

### Automated Verification
- Seed script MUST complete without errors
- `test_seed_architectural_guardrails.py` MUST pass
- `test_run_seed.py` MUST pass
- The new structural parity meta-test from Phase 4 MUST pass:
  ```powershell
  uv run pytest backend_v2/tests/unit/test_v2_core_models.py::test_strict_schema_parity_for_core_execution_fields -v
  ```

---

## Session Handover

```
To execute this plan, start a NEW chat session and run:
/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_63\phase5_clean_slate_db_reset.md]
```
