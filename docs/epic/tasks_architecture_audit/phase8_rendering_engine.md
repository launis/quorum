# Epic: Architecture Audit - Phase 8: Dynamic Rendering Engine

## Goal
Audit `08_dynamic_rendering_engine.md` against the actual codebase (`backend_v2/services/synthesis`). The absolute rule is **Code is the Truth**. We will only update the documentation to match the current code, not the other way around. 

## Scope
*   **TARGET (Modify):** `docs/architecture/08_dynamic_rendering_engine.md`
*   **CONTEXT (Read-Only):** `backend_v2/services/synthesis/*`, PDF templating/rendering.

## Implementation Steps
1. **Analyze Document & Code:** Read the target document. Inspect the reporting and synthesis pipeline, Multi-Profile Caching (FinOps), and how data structures flow to the UI via `RenderedSynthesisCache`.
2. **Compile Findings (Osa 1):** Document all discrepancies where the architecture document differs from the actual code. Create a findings report.
3. **Wait for Approval:** Present the findings report to the user and ask for explicit permission to proceed. Do NOT modify the document yet.
4. **Update Documentation (Osa 2):** Once the user approves the findings, precisely update `08_dynamic_rendering_engine.md` to perfectly reflect the actual state of the code.

## Verification & Quality Gate
*   Verify that no Python code was modified.
*   Present the exact diff of the documentation update to the user.
