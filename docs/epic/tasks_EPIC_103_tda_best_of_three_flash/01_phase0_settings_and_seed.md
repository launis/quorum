# Implementation Plan: Phase 0 - Model Registry & Pacing Lock Resolution

## Goal Description
Implement the foundation for the Best-Of-Three Flash architecture by introducing the required global settings for ensemble concurrency and updating the `seed_data.json` to utilize the `fast` strategy for downstream tasks. This eliminates the global Pacing Lock bottleneck.

## Open Questions
None.

## Red-Team Audit Notes
- **User Corrected SSOT Violation:** Initially, this plan proposed adding `ensemble_strategy_name` to `settings.py` alongside updating `seed_data.json`. However, as correctly pointed out, defining the strategy in two places violates the **Single Source of Truth (SSOT)**. The orchestrator must strictly respect the `step.model_strategy` defined in the database. Therefore, `ensemble_strategy_name` has been purged from `settings.py`. Only the purely mathematical limits (`ensemble_parallelism`, `ensemble_min_consensus`) remain in settings, adhering to `global_config_sovereignty`.

## User Review Required
- Modifying `seed_data.json` requires explicit environment targeting when running the seed script.

## Architectural Invariants Injected
- `global_config_sovereignty`: All system limits MUST be centralized in `settings.py`. No magic numbers in business logic.
- `pydantic_annotated_fields_mandate`: Use `Annotated[int, Field(...)]` for all new settings in `settings.py`.
- `seeding_command_mandate`: When instructing the user to run the database seed script, you MUST explicitly include the target environment argument (e.g., `uv run python backend_v2/seed/run_seed.py local`).

## Scope
- TARGET (Modify): `backend_v2/settings.py`
- TARGET (Modify): `backend_v2/seed/seed_data.json`
- CONTEXT (Read-Only): `backend_v2/models/v2_core.py`

## Proposed Changes

### Configuration
#### [MODIFY] [settings.py](file:///c:/src/quorum/backend_v2/settings.py)
- Inject the following variables explicitly typed with `Annotated` into the `Settings` class:
  - `ensemble_parallelism: Annotated[int, Field(description="Number of parallel Bo3 calls")] = 3`
  - `ensemble_min_consensus: Annotated[int, Field(description="Minimum agreeing votes for consensus")] = 2`

### Seed Data Vault
#### [MODIFY] [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)
- Navigate to the `steps` array and update the `model_strategy` field for the downstream TDA tasks (e.g., `step_causal_analyst`, `step_performativity_detector`, `step_xai_reporter`, `step_fact_checker`) to `"fast"`. Previously they were set to slower strategies like `"reasoning"`, `"strict"`, or `"deep"`. 
- **Execution Note for Tier 2**: Since `seed_data.json` is massive (~9000 lines) and encoded in UTF-16 in PowerShell, standard text tools might fail. The execution agent should modify the file directly or use a Python script to patch these values.

## Testing & Quality Gate Plan
### Automated Tests
- Run `uv run python scripts/backend_audit_loop.py backend_v2/settings.py --test` to ensure strict typing is preserved.

### Manual Verification
- Run `uv run python backend_v2/seed/run_seed.py local` to enforce the seed JSON changes into the local database.

## Documentation & Knowledge Item Mandate
- No direct directory structural changes; no update to `04_directory_reference.md` needed.

---
## Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
