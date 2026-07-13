# Phase 4: Legacy Pipeline B Sunset (Erase God Code)

## Objective
Implement Part 1, Section 4 of Epic 93. Delete the legacy Pipeline B markdown generation files (`hooks/synthesis.py` and `hooks/reporting.py`) completely, as all synthesis is now handled natively within Pipeline A (DAG) and mapped via `sdui_mapper_service.py`.

## Architectural Constraints (Fail-Fast & Zero-Compromise)
- **Zero God-Objects:** Deletion of the massive `synthesis.py` (959 lines) and `reporting.py` (317 lines).
- **Clean Registry:** The `hook_registry.py` must no longer reference `text_consolidation_hook` or `generate_report_hook`.
- **Pre-Delete Audit:** Verify no orphaned dependencies remain. If anything breaks, Fail-Fast and fix the import tree before deletion.

## Execution Steps

### 1. Proxy Sunset & Consumer Migration
- **Action**: Search for any remaining imports of `backend_v2.hooks.synthesis` and `backend_v2.hooks.reporting`.
- **Action**: Remove the `text_consolidation_hook` and `generate_report_hook` registrations from `backend_v2/core/hook_registry.py` or wherever they are loaded.
- **Action**: Remove the invocation of these hooks from `backend_v2/services/execution.py` or the `DAGExecutor` pipeline.

### 2. Erase God Code
- **Action**: Delete `backend_v2/hooks/synthesis.py`.
- **Action**: Delete `backend_v2/hooks/reporting.py`.
- **Action**: Clean up any models in `backend_v2/models/dtos/synthesis.py` that are explicitly bound to the old `synthesis.py` structure (like `MatrixExplanationsResult` or `SynthesisOutputDTO` with `content_blocks`), making sure they are not used by the new `GlobalSynthesisDTO`.

### 3. Baseline Parity & Zero-Loss Audit
- **Action**: Run the full V2 test suite to mathematically verify that the deletion did not break core pipeline execution.
- **Action**: Validate that test counts and coverage match the Phase 0 baseline as recorded in the Epic Tracker.
