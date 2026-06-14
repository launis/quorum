# Phase 2: ETL Migration (Seed Data)

**Source:** Epic Phase 2 (ETL-Migraatio)

## Objective
Parse the existing `seed_data.json` database SSOT to extract the hardcoded string steps from `concept_description` into the new granular fields.

## Scope
- **TARGET (Modify):**
  - `scratch/migrate_tda_schema.py` (New script to be created)
  - `backend_v2/seed/seed_data.json` (The SSOT to be migrated)
- **CONTEXT (Read-Only):**
  - `backend_v2/models/v2_core.py` (Reference for the new schema)

## Architectural Mandates
- **<rule num="46" id="zero_db_hardcoding_mandate">**: Database entity IDs or literal names MUST NEVER be hardcoded or used in conditional logic. Hardcoded index references in lists are prohibited. When refactoring hardcoded logic, you MUST preserve its functional behavior by translating it into a dynamic check (e.g. comparing against active workflow step IDs or metadata schemas) rather than blindly deleting the bypass.
- **<rule num="17" id="the_duct_tape_ban">**: "God Blocks" (`except Exception: pass`) are ruthlessly forbidden. All errors MUST be caught, logged, and re-raised. All file handles (`open()`), network sessions, and external resources MUST be initialized via context managers (`with` or `async with`) to eliminate resource leaks. Anti-pattern: `except Exception: return {}`. Pro-pattern: `except Exception as e: logger.error(e); raise`.
- **Seeding Command Mandate:** If running seeds, explicitly use the target environment `uv run python backend_v2/seed/run_seed.py local`.

## Implementation Steps
1. Create `scratch/migrate_tda_schema.py`.
2. Load `backend_v2/seed/seed_data.json`.
3. Iterate through `system_configs`, `prompt_blocks`, and nested `TDAAssertion` elements.
4. Implement Regex parsing to detect:
   - `STEP 1:(.*)STEP 2` -> Map to `anchor_target`
   - `STEP 2 \(Bounding Box\):(.*)EXTRACTION CONDITION:` -> Map to `bounding_box_scope` (convert text to Literal values).
   - `EXTRACTION CONDITION:(.*)` -> Map to `extraction_rule`.
5. Clean up the original `concept_description` to only contain the preamble text.
6. Write the mutated dictionary back to `seed_data.json`.
7. Execute the script from the scratch directory.
8. Manually inspect `seed_data.json` git diff to ensure successful migration.
9. Execute `uv run python backend_v2/seed/run_seed.py local` to re-seed the TinyDB locally.

## Testing & Quality Gate Plan
- **Integration Tests:** Ensure `run_seed.py` passes without Pydantic validation errors (meaning the new JSON matches the Phase 1 schema).
- **Universal Quality Gate:** Run `uv run python scripts/backend_audit_loop.py backend_v2/seed --test`.

---
### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_tda_granular_schema_refactor_tracker.md`
