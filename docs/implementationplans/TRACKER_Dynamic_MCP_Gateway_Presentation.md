# Tracker: Dynamic MCP Gateway Presentation & Executive Presentation Sanitization
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_MCP_Gateway_Presentation.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_hybrid_ui_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_MCP_Gateway_Presentation.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_MCP_Gateway_Presentation.md] @[docs/implementationplans/TRACKER_Dynamic_MCP_Gateway_Presentation.md]`
  - [x] Step 1: TECHNICAL DEBT RESOLUTION & BASELINE INTEGRATION GATE
  - [x] Step 2: CENTRAL CONFIGURATION SSOT EXTENSION
  - [x] Step 3: GENERIC MCP WIRE DTO EXTENSION
  - [x] Step 4: SYNTHESIS PROMPT DIRECTIVES SSOT EXTENSION
  - [x] Step 5: MCP PRESENTATION SANITIZER IMPLEMENTATION & UNIT TESTING
  - [x] Step 6: SOURCES ADAPTER & BLUEPRINT TRANSFORMER INTEGRATION
  - [x] Step 7: LOCALIZATION CLEANUP (ANTI-JARGON REFINEMENT)
  - [x] Step 8: FULL-DUPLEX SDUI SEMANTIC PARITY & GLOBAL QUALITY GATES
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_MCP_Gateway_Presentation.md] @[docs/implementationplans/TRACKER_Dynamic_MCP_Gateway_Presentation.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure zero `@pytest.mark.skip` or commented-out assertions remain in modified domains.
- [x] **[OK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` on modified and created backend files:
  - [x] @[backend_v2/settings.py]
  - [x] @[backend_v2/models/dtos/mcp.py]
  - [x] @[backend_v2/models/prompts/__init__.py]
  - [x] @[backend_v2/models/prompts/synthesis/__init__.py]
  - [x] @[backend_v2/models/prompts/synthesis/style_directives.py]
  - [x] @[backend_v2/workers/synthesis_worker.py]
  - [x] @[backend_v2/services/sdui/sanitizers/__init__.py]
  - [x] @[backend_v2/services/sdui/sanitizers/mcp_presentation_sanitizer.py]
  - [x] @[backend_v2/services/sdui/adapters/printable_sources_adapter.py]
  - [x] @[backend_v2/services/blueprint.py]
- [x] **[OK] Tier 2 Hardening (Frontend)**: No client Flutter/Dart files affected (Dumb Painter contract).
- [x] **[OK] Pre-Delete Audit**: Verify zero orphaned symbols, obsolete pseudo-MCP routes, or loopback endpoints.
- [x] **[OK] Semantic Parity Audit**: Verify 100% semantic parity between Flutter SDUI MarkdownBlock and WeasyPrint PDF output via `test_sdui_semantic_parity.py`.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Verify zero dropped fields, 100% semantic coverage, and cross-language DTO alignment via `scripts/audit_dto_parity.py`.

### Documentation & Knowledge Item Update

- [x] **[OK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Dynamic_MCP_Gateway_Presentation.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_MCP_Gateway_Presentation.md] @[ki_mcp_tool_protocol.md] @[ki_hybrid_ui_sanitization.md] @[ki_system_audit_trail_xai.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_hybrid_ui_sanitization.md]`: Document `McpPresentationSanitizer` in `backend_v2/services/sdui/sanitizers/` for executive presentation sanitization, sentence-boundary budgeting, and CDATA stripping.
     - `@[ki_mcp_tool_protocol.md]`: Document wire DTO extension (`MCPSearchResultItemDTO`, `MCPStructuredContentDTO`) and `SYNTHESIS_EXTERNAL_EVIDENCE_MANDATE` SSOT.
     - `@[ki_system_audit_trail_xai.md]`: Document pre-sanitization of `MCPAuditTrace.response_summary` for executive reports while preserving immutable forensic evidence.
  2. **Directory Reference Sync:**
     - Register `backend_v2/services/sdui/sanitizers/` under Pillar 4 (SDUI & Presentation) in `@[.agents/rules/04_directory_reference.md]`.
  3. **Pillar Documentation Sync:**
     - Update `docs/architecture/04_presentation_tier_and_sdui.md` describing executive presentation sanitization and Dumb Painter parity in present tense.

### Final Plan Audit

- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_MCP_Gateway_Presentation.md] @[docs/implementationplans/TRACKER_Dynamic_MCP_Gateway_Presentation.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive step and running quality gates, instruct the user to execute an atomic `git commit` formatted according to Conventional Commits syntax (`<type>(<scope>): <summary>`). Explicitly list all staged files.
- **Single Pipeline Law**: All external tool findings and audit traces rendered to presentation tiers must flow through `McpPresentationSanitizer.sanitize_finding`. Bifurcated presentation or client-side regex patching is strictly prohibited.
- **Zero Permissive Typing**: All MCP response parsing must use `MCPStructuredContentDTO.model_validate_json()` with `extra="forbid"` and `strict=False` for Rust deserialization. Zero `json.loads()` and zero `isinstance(data, dict)`.
- **Zero Hardcoded Routers**: External research gateways (Wikipedia, Tavily) connect 100% dynamically through Quorum Studio. Zero loopback endpoints or backend pseudo-MCP routers.
- **Quality Gates**:
  - Python tests & static analysis: `uv run python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Semantic parity: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
  - Structural markdown audit: `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_MCP_Gateway_Presentation.md`
- **Execution Mode**: Supports Continuous Full-Auto Mode via `/tier2-execute --full-auto`.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Update legacy test assertion in `test_tavily_e2e_full_pipeline.py` to assert SSOT tool id `"tavily_search"` | Step 1 | [x] Verified |
| REQ-002 | Add `mcp_presentation_max_chars` setting to `Settings` class in `settings.py` (default 300) | Step 2 | [x] Verified |
| REQ-003 | Extend `MCPSearchResultItemDTO` and `MCPStructuredContentDTO` in `models/dtos/mcp.py` with standard content fields | Step 3 | [x] Verified |
| REQ-004 | Add `SYNTHESIS_EXTERNAL_EVIDENCE_MANDATE` to `style_directives.py`, re-export in `models/prompts/`, and inject into `synthesis_worker.py` | Step 4 | [x] Verified |
| REQ-005 | Implement `McpPresentationSanitizer` in `services/sdui/sanitizers/` with CDATA stripping, Rust JSON validation, and sentence budgeting | Step 5 | [x] Verified |
| REQ-006 | Integrate `McpPresentationSanitizer` into `PrintableSourcesAdapter` and `BlueprintTransformer`, wrap PDF template in conditional | Step 6 | [x] Verified |
| REQ-007 | Refine localization strings in `fi.json` and `en.json` removing technical acronym `"MCP"` from executive labels | Step 7 | [x] Verified |
| REQ-008 | Execute full backend quality gates, AST strictness, semantic parity, and tavily integration baseline | Step 8 | [x] Verified |

## Verification Gates & Telemetry

| Gate ID | Target / Boundary | Verification Command | Status |
| :--- | :--- | :--- | :--- |
| **GATE-01** | Integration Baseline | `uv run pytest backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py` | PASSED (2 passed in 13.03s) |
| **GATE-02** | Settings SSOT | `uv run pytest backend_v2/tests/unit/test_settings.py` | PASSED (24 passed in 0.65s) |
| **GATE-03** | MCP DTO AST Strictness | `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/mcp.py --test --ast-strict` | PASSED (100% coverage, 0 AST errors) |
| **GATE-04** | Synthesis Directives SSOT | `uv run pytest backend_v2/tests/unit/models/prompts/test_style_directives.py` | PASSED (38 passed in 0.27s) |
| **GATE-05** | Presentation Sanitizer | `uv run python scripts/backend_audit_loop.py backend_v2/services/sdui/sanitizers/mcp_presentation_sanitizer.py --test --ast-strict` | PASSED (93% coverage, 0 AST errors) |
| **GATE-06** | SDUI Presentation Parity | `uv run pytest backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_adapter.py backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_mcp_sanitization.py` | PASSED (22 passed in 0.52s) |
| **GATE-07** | Localization Parity | `uv run python -c "import json; fi=json.load(open('backend_v2/l10n/fi.json', encoding='utf-8')); en=json.load(open('backend_v2/l10n/en.json', encoding='utf-8')); assert fi['sources_mcp_result'] == 'Ulkoinen havainto:'; assert en['sources_mcp_result'] == 'External finding:'"` | PASSED (exit code 0) |
| **GATE-08** | Full-Duplex Parity Gate | `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py` | PASSED (2 passed in 35.56s) |

---

# Session Handover Context

## Achieved
- Executed 100% of all 8 implementation steps under `/tier2-execute --full-auto`.
- Created `McpPresentationSanitizer` in `backend_v2/services/sdui/sanitizers/` with CDATA stripping, markdown code fence stripping, structured JSON hydration via `MCPStructuredContentDTO`, HTML tag stripping, whitespace normalization, sentence-boundary budgeting via `enforce_sentence_boundary_budget`, and terminal sentence punctuation guarantee.
- Extended generic MCP wire DTOs (`MCPSearchResultItemDTO`, `MCPStructuredContentDTO`) in `backend_v2/models/dtos/mcp.py` with standard summary/text fields, passing AST strictness and 100% test coverage.
- Centralized `SYNTHESIS_EXTERNAL_EVIDENCE_MANDATE` in `backend_v2/models/prompts/synthesis/style_directives.py`, re-exported in prompt packages, and injected into `synthesis_worker.py`.
- Integrated `McpPresentationSanitizer` into `PrintableSourcesAdapter` and `BlueprintTransformer` (`mcp_audit_data`), guaranteeing that both Flutter SDUI MarkdownBlock and WeasyPrint PDF receive pre-sanitized text.
- Wrapped Jinja2 PDF template rendering in `{% if audit.response_summary %}`.
- Refined localization strings in `fi.json` and `en.json` replacing technical acronym "MCP" with clean executive labels ("Ulkoinen havainto:", "External finding:").
- Verified all 8 quality gates: unit tests, AST strictness, SDUI semantic parity, and full E2E Tavily pipeline integration with 100% passes.

## Learned
- In `GenericMCPClient.call_tool`, MCP tool responses are intentionally wrapped in CDATA (`f"<![CDATA[\n{budgeted}\n]]>"`) to protect Layer 4 prompt injection against injection attacks. When this raw `response_summary` is displayed without presentation-tier sanitization, it leaks raw CDATA and JSON to the UI and PDF.
- The presentation tier requires a dedicated, deterministic `McpPresentationSanitizer` in `backend_v2/services/sdui/sanitizers/` to strip CDATA fences, extract substantive text via `MCPStructuredContentDTO.model_validate_json`, apply sentence-boundary budgeting, and ensure Dumb Painter parity between Flutter and WeasyPrint PDF.
- AST guardrail QGR003 requires any `try...except` block in domain services to either re-raise or return a typed result ending in `("DTO", "Result", "Response", "Failure")`. Encapsulating JSON validation in `McpExtractionResult(V2CoreBase)` satisfies this invariant.
- Whole-string quote stripping preserves query strings and proper nouns quoted inside tool responses.

## Remaining
- Execute System 2 Red-Team audit: `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_MCP_Gateway_Presentation.md] @[docs/implementationplans/TRACKER_Dynamic_MCP_Gateway_Presentation.md]`.
- Execute As-Built Architectural documentation sync: `/tier7-describe-architecture @[docs/implementationplans/TRACKER_Dynamic_MCP_Gateway_Presentation.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_MCP_Gateway_Presentation.md] @[ki_mcp_tool_protocol.md] @[ki_hybrid_ui_sanitization.md] @[ki_system_audit_trail_xai.md]`.

## Resume Command
```powershell
/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_MCP_Gateway_Presentation.md] @[docs/implementationplans/TRACKER_Dynamic_MCP_Gateway_Presentation.md]
```


