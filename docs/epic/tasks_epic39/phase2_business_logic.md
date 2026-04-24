# Epic 39: Phase 2 - Business Logic Layer (Backend Hooks)

## Goal
Implement the business logic for Dynamic Reporting and Context Minimization. This phase ensures that the LLM is only fed relevant, minimized data and that mathematical computations are strictly isolated from the language models.

## Target Files (Modify)
- `backend_v2/hooks/reporting.py` (specifically `generate_report_hook.py` logic)
- `backend_v2/hooks/scoring.py`
- `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py`

## Context Files (Read-Only)
- `backend_v2/models/dtos/report.py`
- `backend_v2/models/domain/xai.py`

## Architectural Invariants (MANDATORY)
1. **The Anti-TDD Trap Mandate**: Do not attempt to preserve old Pytest fixtures if they rely on legacy `dict` structures or hardcoded strings. Rewrite the tests. A green test suite that violates architectural sovereignty is a failed state.
2. **De-Generator Mandate (`de_generator_mandate`)**: The UI is the ultimate authority. Do NOT hardcode system directives, output structures, or hook chains. They must be read dynamically from the `OutputProfile` / `global_context_vars`.
3. **UI Driven Synthesis Boundary (`ui_driven_synthesis_boundary`)**: The backend reporting hook MUST actively filter out unnecessary raw data (e.g., PDF dumps) and ONLY inject `target_blocks` matrices to the LLM.
4. **Safe Math Zero Division (`safe_math_zero_division`)**: Ensure all calculations in `ScoringHook` contain absolute zero-division protection. If `total_atoms == 0`, fallback to `math_min` gracefully.
5. **Frozen State Mutability (`frozen_state_mutability`)**: `ContextBuilder` and Hooks MUST NOT mutate `HookState` in-place. Use `.model_copy()` for the Amnesia Protocol.
6. **Clean Architecture Isolation (`clean_architecture_isolation`)**: No direct database calls in hook files.
7. **Zero Compromise Pledge (`the_zero_compromise_pledge`)**: Strict enforcement of rules without any legacy shortcuts or silent backwards compatibility logic.
8. **No Fallbacks (`the_duct_tape_ban`)**: No "duct tape" code. If data is malformed, let the system CRASH loudly. Never use default empty arrays `[]` or default dicts `{}`.
9. **Universal Fail-Fast (`universal_fail_fast`)**: The system must raise an explicit `AppException` instead of swallowing errors silently with generic `try/except Exception: pass`.

## Implementation Steps
1. [x] Refactor `scoring.py` to enforce safe math and calculate necessary values for `MatrixObservabilityDTO`.
2. [ ] Refactor `context_builder.py` to ruthlessly prune `evaluations` into a boolean array `evaluations_bool_only`.
3. [ ] Refactor `reporting.py` to read the dynamic output profile, filter context based on `target_blocks`, and generate multi-section synthesis logic.

## Verification Plan & Quality Gate
Run the backend audit loop to test business logic behavior:
```bash
uv run python scripts/backend_audit_loop.py backend_v2/hooks/reporting.py backend_v2/hooks/scoring.py backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py --test
```
