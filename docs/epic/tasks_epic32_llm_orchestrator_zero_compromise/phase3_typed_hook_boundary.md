# Phase 3: Typing the Post-Hook State Boundary

## Objective
Convert `final_dict: dict[str, Any]` inside `NodeStrategy.run_post_hooks` and `run_pre_hooks` to a fully typed `StatefulExecutionDTO`. This enforces the "No Naked Dicts in State" mandate for the hook boundary layer and provides rigid Pydantic structures to prevent downstream rendering crashes.

## Architecture Sequence
1. **Pydantic Models**: Define `StatefulExecutionDTO` (in `backend_v2/models/state.py` or similar).
2. **API/Service**: Update `base.py` and `llm.py` to type the boundaries safely.

## Scope Definitions
### TARGET (Modify)
- `c:\src\quorum\backend_v2\services\orchestrator\strategies\base.py`
- `c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py`
- `c:\src\quorum\backend_v2\models\state.py` (Add new DTO)
- `c:\src\quorum\backend_v2\tests\unit\test_strategies.py` (or existing base tests)

### CONTEXT (Read-Only)
- `c:\src\quorum\docs\epic\epic32_llm_orchestrator_zero_compromise.md`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

## Implementation Steps
1. Open `backend_v2/models/state.py`.
2. Implement `class StatefulExecutionDTO(BaseModel)` to encapsulate the merged state payloads passing through hooks.
3. Open `backend_v2/services/orchestrator/strategies/base.py`.
4. Modify `run_post_hooks` to accept and return `StatefulExecutionDTO` instead of `dict[str, Any]`.
5. Modify `run_pre_hooks` similarly if state definitions warrant it (based on Epic requirements for typing the post-hook state boundary).
6. Update `LLMNodeStrategy.execute` in `llm.py` to marshal `final_dict` into `StatefulExecutionDTO` before sending it to hooks, and to unpack/utilize it cleanly on return.
7. Ensure `HookState` handles `StatefulExecutionDTO` mapping cleanly or stays as dict if required by the legacy hook registry architecture (if we only type the immediate strategy output).

## Verification & Quality Gate Plan
- **New Unit Tests:** Update existing strategy unit tests to pass `StatefulExecutionDTO` objects instead of raw dictionaries.
- **Audit Tooling:** 
  - `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/base.py backend_v2/services/orchestrator/strategies/llm.py backend_v2/models/state.py --test`
  - Ensure OpenAPI generator parity is updated if this changes router outputs: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/base.py --openapi`
- **Criteria:** Strict typing compliance `mypy --strict` enforcing the boundary transitions successfully.
