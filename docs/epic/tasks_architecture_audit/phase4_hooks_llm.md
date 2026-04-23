# Epic: Architecture Audit - Phase 4: Hooks & LLM

## Goal
Audit `04_hooks_and_llm.md` against the actual codebase (`backend_v2/hooks` and `backend_v2/llm`). The absolute rule is **Code is the Truth**. We will only update the documentation to match the current code, not the other way around. 

## Scope
*   **TARGET (Modify):** `docs/architecture/04_hooks_and_llm.md`
*   **CONTEXT (Read-Only):** `backend_v2/hooks/*`, `backend_v2/llm/*`

## Implementation Steps
1. **Analyze Document & Code:** Read the target document. Inspect the "PromptBlock" fusion architecture, the "De-Generator" model, and how LLM responses are shielded by strict Token Shield Pydantic validations.
2. **Compile Findings (Osa 1):** Document all discrepancies where the architecture document differs from the actual code. Create a findings report.
3. **Wait for Approval:** Present the findings report to the user and ask for explicit permission to proceed. Do NOT modify the document yet.
4. **Update Documentation (Osa 2):** Once the user approves the findings, precisely update `04_hooks_and_llm.md` to perfectly reflect the actual state of the code.

## Verification & Quality Gate
*   Verify that no Python code was modified.
*   Present the exact diff of the documentation update to the user.
