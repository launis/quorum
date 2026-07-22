# Phase 0: Seed Data & Database Prerequisite / Migration
Source: Epic Phase 0

## Objective
Update the `seed_data.json` SSOT to restore the Executive Summary binding, populate localized text, and include `"xlsx"` exports.

## Target Files (Modify)
- @[c:\src\quorum\backend_v2\seed\seed_data.json#L9110-L9130]

## Context Files (Read-Only)
- @[c:\src\quorum\backend_v2\seed\run_seed.py]

## Implementation Steps
1. Modify profile `prf_5d6e7f8091a2b3c4` / `holistic_audit` in `seed_data.json`:
   - Populate `preamble_text` with localized `fi`/`en` intro text.
   - Set `synthesis_block_id: "blk_8f7e6d5c4b3a2019"` in `layouts[0].synthesis` to bind the executive summary layout.
   - Ensure section layout `preset_view`, `title`, and `description` objects contain valid `fi` and `en` dictionaries.
   - Update `allowed_exports` arrays to include `"xlsx"` alongside existing `"pdf"` where Excel export is intended.
2. Execute local re-seed: `uv run python backend_v2/seed/run_seed.py local`.

## Testing & Quality Gate Plan
- Manually run the seed script locally to ensure successful wiping and reloading.
- Run Universal Quality Gate (Backend Audit Loop): `uv run python scripts/backend_audit_loop.py backend_v2/seed/run_seed.py --test`

## Documentation & Knowledge Item Mandate
- No architectural docs to update in this pure data phase.
