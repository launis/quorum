# Epic: Architecture Audit - Phase 2: Domain Models

## Goal
Audit `02_domain_models.md` against the actual codebase (`backend_v2/models`). The absolute rule is **Code is the Truth**. We will only update the documentation to match the current code, not the other way around. 

## Scope
*   **TARGET (Modify):** `docs/architecture/02_domain_models.md`
*   **CONTEXT (Read-Only):** `backend_v2/models/*`

## Implementation Steps
1. **Analyze Document & Code:** Read the target document. Use `grep_search` and `list_dir` to inspect the implementation of Pydantic V2 schemas (`ConfigDict(strict=True)`), the "No-Naked-Dicts" mandate, and the usage of "Opaque Stripe IDs" in the context directories.
2. **Compile Findings (Osa 1):** Document all discrepancies where the architecture document differs from the actual code. Create a findings report.
3. **Wait for Approval:** Present the findings report to the user and ask for explicit permission to proceed. Do NOT modify the document yet.
4. **Update Documentation (Osa 2):** Once the user approves the findings, precisely update `02_domain_models.md` to perfectly reflect the actual state of the code.

## Verification & Quality Gate
*   Verify that no Python code was modified.
*   Present the exact diff of the documentation update to the user.
