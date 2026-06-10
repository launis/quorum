# Phase 3: Offline Database Migration (Tietokantamigraatio)
Source: Epic Phase 2: Tietokantamigraatio

## Objective
Create and execute a standalone, offline Python script to migrate the `seed_data.json` database into the new Pydantic structures. This must be done BEFORE the Pydantic schemas in the main codebase are updated, to avoid the Chicken-and-Egg validation crash. The output will be a draft JSON file.

## Targets (Modify)
- `c:\src\quorum\tmp\migrate_seed_data.py` [NEW]
- `backend_v2/seed/seed_data_v2_draft.json` [NEW]

## Context (Read-Only)
- `backend_v2/seed/seed_data.json`

## Architectural Invariants
- **Rule 59 (No Multiprocessing)**: Must use threads or `asyncio`.
- **Rule 61 (TaskGroup Mandate)**: `asyncio.gather` is forbidden; use `asyncio.TaskGroup`.
- **Rule 110 & 28**: Do not use direct SDK calls. The ETL script MUST use `LLMTaskExecutor.execute_structured_task()` to parse old string data into new schemas.
- **Rule 25 & 26 (Opaque Stripe ID Mandate)**: No md5 hashing. All missing IDs must be generated as `uuid4().hex`.

## Implementation Steps
1. Write a standalone Python script in `tmp\` that loads `seed_data.json` and navigates to `prompt_blocks -> scales -> claims -> tda_assertions`.
2. Convert the 186 `ai_rule_description` strings into the new structured JSON representation:
   - `concept_description`
   - `acceptance_criteria`
   - `anti_patterns`
   - `contrastive_example`
   - `syntactic_anchors`
   - Set `enforce_pre_flight = false`.
3. The script must use `LLMTaskExecutor` for the conversion, applying the Opaque Stripe ID mandate for missing `tda_id` fields.
4. Add the new `Lightweight JSON Extraction` instruction block (`blk_lightweight_extract_01`) to the DB seed file.
5. Save the output as `backend_v2/seed/seed_data_v2_draft.json` and request manual human review.

## Testing & Quality Gate Plan
- **Verification**: Ensure `backend_audit_loop.py` still passes since the actual codebase is untouched.
- **Visual Diff**: Ask the user to verify the `seed_data_v2_draft.json` differences.

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run:
`/tier2-execute docs/epic/tasks_bilingual_schema_refactor/phase3_db_migration_offline.md`
