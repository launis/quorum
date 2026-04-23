# Epic: Architecture Audit - Phase 1: Backend API & Core

## Goal
Audit `01_backend_api_and_core.md` against the actual codebase (`backend_v2/api` and `backend_v2/core`). The absolute rule is **Code is the Truth**. We will only update the documentation to match the current code, not the other way around. 

## Scope
*   **TARGET (Modify):** `docs/architecture/01_backend_api_and_core.md`
*   **CONTEXT (Read-Only):** `backend_v2/api/*`, `backend_v2/core/*`

## Implementation Steps
1. **Analyze Document & Code:** Read the target document. Use `grep_search` and `list_dir` to inspect the FastAPI routers, middleware, dependency injection patterns (`Depends()`), and `AppException` (RFC 7807) implementations in the context directories.
2. **Compile Findings (Osa 1):** Document all discrepancies where the architecture document differs from the actual code. Create a findings report.
3. **Wait for Approval:** Present the findings report to the user and ask for explicit permission to proceed. Do NOT modify the document yet.
4. **Update Documentation (Osa 2):** Once the user approves the findings, precisely update `01_backend_api_and_core.md` to perfectly reflect the actual state of the code.

## Verification & Quality Gate
*   Verify that no Python code was modified.
*   Run `uv run python scripts/backend_audit_loop.py backend_v2/api backend_v2/core` if there is any doubt about the codebase integrity, but primarily rely on static analysis.
*   Present the exact diff of the documentation update to the user.
