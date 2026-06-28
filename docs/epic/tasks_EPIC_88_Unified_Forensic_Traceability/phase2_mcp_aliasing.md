# Phase 2: MCP Aliasing & Unified Source Pipeline

Source: Epic Phase 2.2 & Appendix A.2

## Target Files (Modify)
- `backend_v2/services/mcp/alias_registry.py` [NEW]
- `backend_v2/services/mcp/mcp_tool_loop.py`
- `backend_v2/services/orchestrator/strategies/llm.py`

## Context Files (Read-Only)
- `backend_v2/models/domain/mcp.py`

## Requirements
1. **Alias Registry (`alias_registry.py`)**: Create this new service.
   - Implement `wrap_source_chunks(text: str, source_id: str) -> list[str]`.
   - Register source and assign alias `<<QRM-SRC-N>>`.
   - **CRITICAL REQUIREMENT**: Chunk text into ~1000-1500 tokens with a **150-200 token overlap**. Without overlap, fuzzy matching will fail.
   - Wrap chunks in `<search_result ID="<<QRM-SRC-N>>" chunk="M/T">`.
   - Implement `resolve(alias, alias_map)` that validates the alias and raises `SemanticEvidenceError` if unknown (include dynamic Escape Hatch in error message: "JOS nämä lähteet eivät oikeasti sisällä väitettäsi, PALAUTA TYHJÄ LISTA []. Älä keksi lähteitä.").
2. **Unified Injection**: 
   - In `mcp_tool_loop.py` (Phase 2 injection), use `wrap_source_chunks` for MCP search results.
   - In `llm.py` (or where source PDFs are injected), use the **same** `wrap_source_chunks` for internal source documents.
3. **Unified Storage**:
   - Ensure both internal source PDFs and external MCP searches register their raw payloads in the execution context under the same structure (e.g. `FrozenContext.mcp_tool_audit`), so BlueprintTransformer can read them uniformly via `MCPAuditTrace`. Use pointer logic (`gs://...` or `file://...`) for raw text to avoid the 1 MiB Firestore limit (Rule: No raw document text in DB).

## Architectural Invariants & Hardening Mandate
- **Rule 17 (the_duct_tape_ban)**: Ensure proper error handling and re-raising of `SemanticEvidenceError`.
- **Rule 19 (dlq_arq_fallback_routing)**: The `SemanticEvidenceError` must cleanly bubble up to trigger the DLQ retry loop without crashing the overall TaskGroup.

## Documentation Update
Update `docs/architecture/05_llm_and_hooks.md` with the new unified `AliasRegistry` and Sandwich Prompting chunking logic.

## Testing & Quality Gate Plan
- **Unit Tests**: Test `wrap_source_chunks` in `tests/unit/services/mcp/test_alias_registry.py` to verify the 150-token overlap logic works accurately and `<search_result>` tags are perfectly formed.
- **Verification**: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/mcp/alias_registry.py backend_v2/services/mcp/mcp_tool_loop.py --test`

---
### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/EPIC_88_Unified_Forensic_Traceability_tracker.md`
