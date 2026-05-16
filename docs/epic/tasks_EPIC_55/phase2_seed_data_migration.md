# Phase 2: Data Cleanup and Migration

## Source
Epic Phase 2, Steps 1-4

## Context
- `backend_v2/core/v2_core.py` (CONTEXT)

## Targets
- `tmp/v5_1_prompt_slimming.py` (TARGET - New)
- `backend_v2/seed/seed_data.json` (TARGET)

## Architectural Laws
- **Rule 00 - database_schema_hallucination**: The SSOT structure in `seed_data.json` is immutable architectural law. Changes must strictly follow the roadmap mandate.
- **Rule 00 - temporary_workspace_sandbox**: Temporary migration scripts must be executed from `tmp/`.

## Implementation Steps
1. **Script Creation**: Write a script `tmp/v5_1_prompt_slimming.py` that loads `backend_v2/seed/seed_data.json`.
2. **Iteration**: Iterate through all `PromptBlock` items within the appropriate arrays (e.g. `matrices`, `components`).
3. **Enum Injection**: Add the new field `"execution_persona": "DETERMINISTIC_PARSER"` to every block.
4. **String Truncation**: Search the `ai_description` field for the large `<global_framework>` / Zero-Interpretation text and mathematically strip it out, leaving only the core matrix-specific instruction.
5. **Execution**: Execute the script and safely overwrite the updated `seed_data.json`.

## Testing & Quality Gate Plan
- **Integration**: Run `uv run python scripts/backend_audit_loop.py backend_v2/seed/seed_data.json` if applicable. 
- **Pydantic Validation**: Run `uv run python backend_v2/seed/run_seed.py local` to verify that database seeding passes without Pydantic failures and the new Enum maps correctly.
