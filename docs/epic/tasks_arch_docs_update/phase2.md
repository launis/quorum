# Implementation Plan: Phase 2 - Update Hooks & LLM Architecture Docs

## Goal
Update `c:\src\quorum\docs\architecture\04_hooks_and_llm.md` to perfectly match the current Phase 9 architecture.

## Architectural Invariants
- **Rule 1**: No code changes allowed. Modify only documentation.
- **Rule 2**: Emphasize the Centralized Routing rule (`LLMTaskExecutor.execute_structured_task`) and the elimination of Naked Dicts (Anti-TDD Trap).

## Target Files
- `TARGET (Modify)`: `c:\src\quorum\docs\architecture\04_hooks_and_llm.md`

## Proposed Changes
1. **The Hook Layer**: Update references to async calls and direct client abstractions to point to `LLMTaskExecutor`.
2. **LLM Integrations**: Update the text to mention that ALL internal LLM tools are now routed through the `LLMTaskExecutor` rather than directly through `LLMClient.from_strategy()`.
3. **Model Context Protocol (MCP)**: Add documentation on the MCP tool loop pattern, which isolates dynamic verification into a secure, logged Pydantic sandbox loop.

## Verification & Quality Gate Plan
- Review the resulting markdown file formatting.
