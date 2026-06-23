# Epic 82 & Phase 0 Tracker

- `[ ]` **Phase 1: Backend Implementation** (Lue ohjeet: `c:\src\quorum\tasks_epic82\phase1_backend.md`)
  - `[x]` Luo `CitationExtractionResult` -malli
  - `[x]` Toteuta Phase 0 extraction `mcp_tool_loop.py`:ssä
  - `[x]` Lisää `str.find` -validointi ja Fail-Fast (`SemanticEvidenceError`)
  - `[x]` Lisää `system_audit_trail` `WorkflowDTO`:hon ja päivitä `seed_data.json`
  - `[x]` Lisää XAI injektio `context_router.py`:hyn
  - `[x]` Kirjoita yksikkötestit ja aja `backend_audit_loop.py`
  - `[x]` Integrate `MCPAuditTrace` into `context_router.py` for XAI synthesis.
  - `[x]` Write and verify tests via `backend_audit_loop.py`.

- `[ ]` **Phase 2: Frontend Implementation (Completed)**
  - `[x]` Update Flutter DTOs (`system_audit_trail`).
  - `[x]` Regenerate Freezed models (build_runner running).
  - `[x]` Add "Järjestelmän Faktantarkistusloki" Checkbox to Admin Studio.
  - `[x]` Verify via `flutter_audit_loop.py`.
