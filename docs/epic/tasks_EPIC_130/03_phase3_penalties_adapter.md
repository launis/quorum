# Phase 3: Extract Penalties Adapter

**Objective**: Extract the penalty block generation logic (`_hydrate_penalties_block`) from `blueprint.py` into a self-contained `penalties_adapter.py`.
**Source**: @[c:\src\quorum\docs\epic\EPIC_130_blueprint_decomposition.md#L103-L106]

**Root Cause**: `blueprint.py` is accumulating too many responsibilities, acting as both the overarching SDUI pipeline orchestrator and the low-level component hydrator.
**Architectural Justification**: Extracting the penalty hydration logic into a dedicated adapter (`PenaltiesAdapter`) enforces the Single Responsibility Principle (SRP). It decouples visual layout mapping from core orchestration, allowing penalty UI logic to be tested in complete isolation without bootstrapping the massive Blueprint context.

## User Review Required
No breaking changes. This is an internal structural refactor enforcing SRP.

## Open Questions
None.

## Proposed Changes

### SDUI Adapters
Extract the penalty block generation into a standalone module.

#### [NEW] [penalties_adapter.py](file:///c:/src/quorum/backend_v2/services/sdui/adapters/penalties_adapter.py)
- Create a `PenaltiesAdapter` class with a static method `hydrate(**kwargs: Any) -> list[AnySduiBlock]`.
- Move the exact logic from `_hydrate_penalties_block` into this method.
- Ensure strict typing and imports for `AnySduiBlock`, `AlertBlock`, and `VisualIntent`.

### Blueprint Orchestrator
Wire the new adapter into the overarching pipeline.

#### [MODIFY] [blueprint.py](file:///c:/src/quorum/backend_v2/services/blueprint.py)
- Import `PenaltiesAdapter` from `backend_v2.services.sdui.adapters.penalties_adapter`.
- In `__init__`, replace `self._hydrate_penalties_block` with `PenaltiesAdapter.hydrate` in the `self._target_block_hydrators` registry.
- **[DELETE]** Remove the `_hydrate_penalties_block` method from `BlueprintTransformer` entirely.

### Test Isolation
Migrate tests to achieve complete isolation.

#### [NEW] [test_penalties_adapter.py](file:///c:/src/quorum/backend_v2/tests/unit/services/sdui/adapters/test_penalties_adapter.py)
- Create isolated unit tests for `PenaltiesAdapter.hydrate`.
- **MANDATORY NEGATIVE TESTS**:
  1. **Missing Data**: Assert that calling `hydrate()` without `penalties_applied` in kwargs safely returns an empty list `[]` without raising KeyError.
  2. **Empty List**: Assert that passing `penalties_applied=[]` explicitly returns an empty list `[]`.
- **Positive Test**: Assert that passing `["Penalty A", "Penalty B"]` returns two `AlertBlock` instances with severity `CRITICAL_OVERRIDE` and the correct text.

#### [MODIFY] [test_blueprint.py](file:///c:/src/quorum/backend_v2/tests/unit/services/test_blueprint.py)
- **[DELETE]** Remove any unit tests specifically testing the internal string formatting of `_hydrate_penalties_block`, as this is now covered by the adapter tests.
- Maintain overarching pipeline tests to ensure the layout hydration still receives the blocks correctly.

## Verification Plan

### Automated Tests
- `uv run pytest backend_v2/tests/unit/services/sdui/adapters/test_penalties_adapter.py`
- `uv run pytest backend_v2/tests/unit/services/test_blueprint.py`
- `uv run python scripts/backend_audit_loop.py backend_v2/services/sdui/adapters --test`
