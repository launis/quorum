# Implementation Plan: Phase 1 - Update Directory Reference

## Goal
Update `c:\src\quorum\.agents\rules\04_directory_reference.md` to perfectly match the current Phase 9 architecture. 

## Architectural Invariants
- **Rule 1**: No code changes allowed. Modify only documentation.
- **Rule 2**: Maintain strict XML tag semantics within `04_directory_reference.md`.

## Target Files
- `TARGET (Modify)`: `c:\src\quorum\.agents\rules\04_directory_reference.md`

## Proposed Changes
1. **API Routers**: Add `studio/mcp_gateways.py`, `studio/system_configs.py`, and `studio/workflows.py` to the `<directory path="api/routers/">` block.
2. **Database Repositories**: Update the `<directory path="database/">` to explicitly mention the Interface Segregation Principle (ISP) and the decoupled `<directory path="repositories/">` (e.g., `audit.py`, `execution.py`).
3. **Services Layer**: Replace the generic orchestrator description with the explicit mention of `services/llm_task_executor.py` as the central orchestration point. Mention `services/mcp/` as the Model Context Protocol loop directory.

## Verification & Quality Gate Plan
- Manually review the XML structure of `04_directory_reference.md` to ensure validity.
