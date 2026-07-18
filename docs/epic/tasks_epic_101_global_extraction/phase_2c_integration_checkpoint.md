# Phase 2C: Integration Checkpoint — End-to-End UI Validation

> **Source:** Tier 1 Workflow `ssot_ui_validation_mandate` — "Legacy Migration First"

## Goal

Validate the complete backend-to-frontend pipeline end-to-end by executing an existing workflow through the UI. This checkpoint ensures the new `engine_override` field, `"progress"` TraceEvent type, and Virtual Step injection work correctly across the full stack WITHOUT breaking any existing functionality.

## Preconditions

- Phase 1A, 1B, 2A, 2B ALL completed and committed.
- Database re-seeded: `uv run python backend_v2/seed/run_seed.py local`
- Flutter `build_runner` completed: `cd client_app_v2; dart run build_runner build -d;`

---

## Validation Steps

### 1. Backend Smoke Test
```
uv run python scripts/backend_audit_loop.py backend_v2/ --test
```
All tests must pass.

### 2. Flutter Analysis
```
uv run python scripts/flutter_audit_loop.py client_app_v2/
```
Zero analysis errors.

### 3. Manual UI Validation

The user MUST perform the following manual validation:

1. **Start the Quorum Tripartite Stack**: You MUST use the local launcher with `FAST_DEV_MODE` disabled to ensure the background Worker starts and the Vertex Reasoning adapter is actually triggered.
   ```powershell
   $env:DEV_EXECUTION_MODE="full"
   .\run_local.bat
   ```
2. **Execute an existing workflow** (any workflow that has analytical steps mapped with `PRE_HYDRATED_SYNTHESIS`)
4. **Verify**:
   - [ ] The Virtual Step ("Asiakirjan Esianalyysi") appears in the execution UI as a loading card
   - [ ] Progress events stream to the UI during RAG extraction
   - [ ] The Virtual Step completes and transitions to PASSED
   - [ ] All subsequent analytical steps execute via the Pre-Hydrated path (single LLM call per step)
   - [ ] The final report renders correctly with all SDUI components
   - [ ] Steps with `DYNAMIC_TOOL_AGENT` override still execute with tool access (Tavily)
   - [ ] No `AppErrorBoundary` crashes occur

---

## Session Handover
```
Achieved: End-to-end integration validation of Epic 101 RAG pipeline.
Remaining: Phase 3+ (deferred — Tier 1 re-invocation needed for detailed plans).
```
