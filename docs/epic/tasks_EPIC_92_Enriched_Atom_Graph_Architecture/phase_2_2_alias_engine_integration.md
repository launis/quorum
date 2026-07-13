# Phase 2.2: Alias Engine Integration

## Goal
Elevate the `AliasEngine` to be the absolute memory manager for the DAG engine. Enable it to handle `CausalEdge` mapping and prevent Token Bloat by providing short `a0`, `a1` aliases to the LLM and hydrating them back to full UUIDs.

## Context (Read-Only)
- `backend_v2/models/dtos/dag_models.py`
- `backend_v2/services/orchestrator/schema_factory.py`

## Target (Modify)
- `[MODIFY] backend_v2/utils/alias_engine.py`
- `[MODIFY] backend_v2/tests/unit/utils/test_alias_engine.py`

## Destructive Operation Inventory
- Extending `AliasEngine` capabilities natively. No legacy symbols are dropped.

## Architectural Rules Injected
- **01-python-backend.md**: AliasEngine LLM Isolation Mandate. Pydantic Pure Hydration Boundary (`AliasEngine.hydrate_dict_list()` MUST run on native dicts before Pydantic `model_validate`).

## Implementation Steps
1. **Alias Engine Extensions (`alias_engine.py`)**:
   - Add capability to track and map DAG atom identifiers (e.g. mapping `tda_abcd...` to `a0`).
   - Ensure `AliasEngine` can natively map and hydrate `depends_on` (list of `CausalEdge` objects) by replacing any short aliases (`tda_id` field in the edge) with full UUIDs.
   - Implement `hydrate_dict_list` to recursively handle the nested dictionary structure produced by the LLM for `LinkedAtomGraph`.
   - Update docstrings to explicitly state that AliasEngine must be instantiated per-request or per-job to avoid global state memory leaks.
2. **Schema Factory Tie-ins**:
   - Ensure `AliasEngine.build_quote_ids_literal()` or equivalent schema-building methods can generate standard JSON schema patterns to constrain the LLM to valid short aliases for the current Context Window.
3. **Unit Tests (`test_alias_engine.py`)**:
   - Add tests specifically for recursive hydration of `CausalEdge` structures within a `LinkedAtomGraph` dictionary.
   - Verify that invalid or unregistered aliases raise appropriate trace errors.

## Testing & Quality Gate Plan
- Run `uv run python scripts/backend_audit_loop.py backend_v2/utils/alias_engine.py --test`
- Verify 100% pass rate.

---
**Session Handover**
To execute this Epic iteratively, start a NEW chat session and run the /tier5-resume command found at the bottom of your tracker.
