# EPIC 68: XAI Extension Scope Separation & Polymorphic Routing Hardening

## 1. Background & Motivation
In the current Quorum architecture, both Block-level extensions (e.g., `falsification`, `emotional_sentiment`) and Workflow-level global extensions (e.g., `variance_validation`) are compressed into a single data model field: `OutputProfileConfig.visible_extensions`.

This "Domain Model Collision" forced the `ContextRouter` (which should act strictly as a dumb data extraction layer) to implement hardcoded "Leaky Abstractions":
```python
if ext_str == XaiExtensionType.VARIANCE_VALIDATION.value:
    continue
```
This violates the Open/Closed Principle (SOLID). Adding new global metrics in the future would require manually modifying the routing logic. This Epic aims to pay off this technical debt by restructuring the data model to natively separate these concerns.

## 2. Architectural Objectives
1. **SOLID Compliance:** Ensure `ContextRouter` is open for extension but closed for modification.
2. **Domain Segregation:** Split extensions into `visible_block_extensions` (handled by ContextRouter) and `visible_workflow_extensions` (handled by the Orchestrator/VarianceEngine).
3. **Context-Aware UI Filtering (Poka-yoke):** Ensure the UI only allows selecting block extensions that the underlying Workflow's target matrices are explicitly configured to produce.
4. **Fail-Fast Safety:** Migrate existing database seeds seamlessly without triggering Pydantic crashes.

## 3. Implementation Phases

### Phase 1: Domain Model Refactoring (Backend)
- **Files Affected:** `backend_v2/models/dtos/output_profile.py`, `backend_v2/models/v2_core.py`, `backend_v2/api/routers/system/workflow.py`
- **Actions:**
  - Introduce `visible_block_extensions: list[str]`.
  - Introduce `visible_workflow_extensions: list[str]`.
  - Create a new backend computation logic (e.g., in `WorkflowService`) that calculates the union of all `output_extensions` defined across all Target Matrices within a specific DAG.
  - Expose this via a new endpoint (e.g. `/api/v2/workflows/{id}/available-extensions`) or append it to the existing Workflow DTO to serve the Frontend.
  - Ensure strict Pydantic V2 schemas are maintained without autonomous `extra="allow"` enforcement.

### Phase 2: Orchestration & Routing Cleanup
- **Files Affected:** `backend_v2/services/orchestrator/context_router.py`, `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
- **Actions:**
  - Strip all `variance_validation` domain logic out of `ContextRouter`.
  - Refactor the router to blindly iterate over `visible_block_extensions`.
  - Update the final report compilation logic to read `visible_workflow_extensions` and execute global evaluations (like the `VarianceEngine`) separately.

### Phase 3: Database & Seed Migration
- **Files Affected:** `backend_v2/seed/seed_data.json`, `data/db_v2.json` (via migration script)
- **Actions:**
  - Write a one-off Python migration script to safely remap existing `"visible_extensions"` containing `"variance_validation"` into the new two-list structure.
  - Update the `kokonaisvaltainen_auditointi` UI profile in `seed_data.json` to establish the new SSOT.

### Phase 4: Flutter Admin Studio Updates
- **Files Affected:** Frontend UI Editor components.
- **Actions:**
  - Split the "XAI Extensions" multiselect into two distinct semantic UI blocks:
    - *Vaihekohtaiset laajennokset* (Block-level)
    - *Globaalit työnkulun laajennokset* (Workflow-level)
  - **Dynamic Dropdown Population:** The Block-level dropdown MUST be dynamically populated based on the selected `workflow_id`. If a workflow does not produce `emotional_sentiment`, it MUST NOT appear as a selectable option, physically preventing users from configuring unfulfillable demands.
  - The Workflow-level dropdown will remain populated by the statically supported global metrics (e.g. `variance_validation`).
  - Ensure Optimistic UI updates handle the new dual-array state payload.

## 4. Zero-Compromise Pledges
- **Migration Integrity:** No existing output profiles will be corrupted.
- **Fail-Fast:** All changes will be validated via strict Pydantic parsing.
- **Anti-Hallucination:** Hardcoded strings in routing layers will be strictly prohibited going forward.
