# Phase 1.1: DTO-Kannan Rakentaminen - Shared, Enums, Settings
Source: Epic Phase 1

## Objective
Build the core foundational blocks of the new Single Source of Truth (SSOT) DTOs, specifically focusing on global states, shared structures, and configurations.

## Target Files (Modify)
- `backend_v2/models/enums.py` [MODIFY]
- `backend_v2/settings.py` [MODIFY]
- `backend_v2/models/dtos/report/shared.py` [NEW]

## Context Files (Read-Only)
- `c:\src\quorum\docs\epic\EPIC_91_5_DTO_Bridge.md`

## Architectural Invariants Injected
1. `strict_configuration_segregation`: `enums.py` for string/int constants; `settings.py` for global bounds/limits. No logic in enums.
2. `strict_enum_l10n_mapping`: `ExecutionStatus` and `SDUIComponentType` in `enums.py` must include an `@property def l10n_key(self) -> str:` method to map to Flutter ARB keys.
3. `strict_pydantic_v2_rust`: `ErrorDetailsDTO` must use `model_config = ConfigDict(strict=True, frozen=True, extra='forbid')`.

## Proposed Changes
### `backend_v2/models/enums.py`
- **[MODIFY]**: Add `ExecutionStatus` with states (PASSED, FAILED, N_A, SYSTEM_ERROR, BLOCKED, PENDING) and its `l10n_key` property (`status_{name}`).
- **[MODIFY]**: Add `SDUIComponentType` with states (BOOLEAN_CARD, EXTRACTED_VALUE_CARD, ERROR_CARD, N_A_CARD) and its `l10n_key` property (`sdui_{name}`).

### `backend_v2/settings.py`
- **[MODIFY]**: Centralize new global configurations like `AUTO_RESOLVE_POLICY` and `MINIMUM_COMPLETENESS_THRESHOLD` as specified by Epic needs.

### `backend_v2/models/dtos/report/shared.py`
- **[NEW]**: Create `ErrorDetailsDTO` using strict Pydantic rules containing `error_code` and `message`.

## Destructive Operation Inventory
- None in this phase.

## Bidirectional Integration Check
- Producer: Settings and Enums define the global constants.
- Consumer: The DTOs in Phase 1.2 will consume these constants.

## Testing & Quality Gate Plan
- Command: `uv run python scripts/backend_audit_loop.py backend_v2/models/ --test`
- Goal: Ensure all syntax, mypy strictness, and basic instantation of Enums pass without errors.

# Session Handover Context
**Achieved:** Phase 1.1 planned.
**Learned:** Tripartite Configuration Architecture enforced.
**Remaining:** Execute Phase 1.1 and proceed to Phase 1.2.

> To execute this Epic iteratively, start a NEW chat session and run the /tier5-resume command found at the bottom of your tracker.
