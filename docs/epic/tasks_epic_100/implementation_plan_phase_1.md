# Epic 100 Phase 1: SlidingWindowLinker Output-Aware Windowing

## Source: Epic 100, Phase 1

## Architectural Invariants
- **Global Config Sovereignty**: `LINKER_MAX_ATOMS_PER_WINDOW` must be in `settings.py`.
- **Zero-Compromise Pledge**: No fallback hacks. Pydantic constraints are absolute.
- **Fail-Fast**: Enforce immediate failure on configuration mismatch.

## Target Files (Modify)
- `backend_v2/settings.py`
- `backend_v2/services/orchestrator/sliding_window_linker.py`

## Context Files (Read-Only)
- `backend_v2/models/dtos/dag_models.py`
- `backend_v2/models/enums.py`

## Proposed Changes

### 1. `backend_v2/settings.py`
- **[MODIFY]**: Add `linker_max_atoms_per_window` under `# --- System Concurrency (Migrated from Enums) ---`.
- **Detail**:
  ```python
  linker_max_atoms_per_window: Annotated[int, Field(description="Max atoms per LLM sliding window to prevent output truncation")] = 20
  ```
- **Dropped Symbols**: None.

### 2. `backend_v2/services/orchestrator/sliding_window_linker.py`
- **[MODIFY]**: Refactor `_get_sliding_windows` for Dynamic Atom-Aware Windowing.
- **Detail**:
  - Update the logic to dynamically limit the window by `get_settings().linker_max_atoms_per_window`.
  - **CRITICAL RED-TEAM MITIGATION**: To prevent the sliding window overlap logic from failing (e.g., zero overlap or skipping chunks when windows dynamically early-exit), you MUST implement a precise two-step algorithm:
    1. **Pre-subdivide Oversized Chunks**: Before building windows, iterate over the incoming `chunks` list. If any single chunk exceeds `linker_max_atoms_per_window`, you MUST slice it into multiple sequential sub-chunks (e.g. `chunk[i:i+max_atoms]`) and build a new `subdivided_chunks` list.
    2. **Dynamic Overlap While-Loop**: Build the windows using a `while i < len(subdivided_chunks):` loop. The inner loop adds chunks until `len(window) == self.window_size` OR `current_atoms + len(next_chunk) > max_atoms`. Finally, advance the main index `i` by calculating `step = max(1, chunks_taken - self.overlap)` to ensure exact overlap is maintained regardless of dynamic early exits.
  - Make sure to import `get_settings` globally at the top of the file: `from backend_v2.settings import get_settings`.
- **Dropped Symbols**: None.

## Testing & Quality Gate Plan
1. **Unit Tests**:
   - Write/Update tests in `backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py` ensuring windows strictly do not exceed 20 atoms.
   - Add explicit test case for the edge case where a single chunk contains >20 atoms, verifying it is subdivided.
   - Run the Universal Quality Gate.
2. **Quality Gate Command**:
   ```bash
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/sliding_window_linker.py --test
   uv run python scripts/backend_audit_loop.py backend_v2/settings.py --test
   ```
3. **Baseline**: Run tests first and record the passing test count and coverage as a `[BASELINE]` metric.

## Documentation & Knowledge Item Mandate
- Update `docs/architecture/` with the new output-aware windowing limits for the Linker.

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
