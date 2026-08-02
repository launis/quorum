# EPIC 130 Tracker: Blueprint Transformer Decomposition into Modular SDUI Adapters

**Epic:** @[c:\src\quorum\docs\epic\EPIC_130_blueprint_decomposition.md]
**Task Directory:** @[c:\src\quorum\docs\epic\tasks_EPIC_130]
**Created:** 2026-08-02

---

## Phase Execution Status

### Phase 1: Foundation — New Directory Structure, Typed Protocol & AdapterContext DTO
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_130\00_foundation_adapter_context.md]

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_130\00_foundation_adapter_context.md] @[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\01-python-backend.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_130_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_130\00_foundation_adapter_context.md]`
  - [ ] Step 0: Strategic Alignment Check — verify sdui/adapters/ does not exist, verify dispatch table uses untyped `Callable[..., list[AnySduiBlock]]`
  - [ ] Step 1: Read Knowledge Item — load KI `sdui_adapter_decomposition` (`ki_sdui_adapter_pattern.md`)
  - [ ] Step 2: Create Directory Structure — create `sdui/__init__.py`, `sdui/adapters/__init__.py`, test `__init__.py` files
  - [ ] Step 3: Create `base_adapter.py` — define `AdapterContext` (frozen, strict, extra=forbid) and `SduiAdapterProtocol`
  - [ ] Step 4: Modify `blueprint.py` — move `Callable` import from inline to module level
  - [ ] Step 5: Modify `blueprint.py` — import `AdapterContext`, migrate dispatch table type to `Callable[[AdapterContext], list[AnySduiBlock]]`, wrap hydrators in lambda bridges
  - [ ] Step 6: Modify `blueprint.py` — migrate dispatch call site from kwargs scatter to single `AdapterContext` pass, bridge `mcp_audit_map=mcp_audit_data`
  - [ ] Step 7: Create `test_base_adapter.py` — positive construction test, frozen rejects mutation, forbids extra fields, missing required field raises, strict type enforcement
  - [ ] Step 8: Run Quality Gate — `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_130\00_foundation_adapter_context.md]`

---

### Phase 2: Extract XAI Highlights Adapter (Proof of Concept)
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_130\01_xai_highlights_adapter.md]

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_130\01_xai_highlights_adapter.md] @[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\01-python-backend.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_130_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_130\01_xai_highlights_adapter.md]`
  - [ ] Step 0: Strategic Alignment Check — verify Phase 1 completed (AdapterContext exists, dispatch table uses new type), verify `_hydrate_grouped_extensions_block` still exists
  - [ ] Step 1: Read Knowledge Item — load KI `sdui_adapter_decomposition`
  - [ ] Step 2: Create `xai_highlights_adapter.py` — Section 1: `XAI_AESTHETICS_RULES` dictionary (minimal placeholder for Phase 2, fully populated in Phase 6); Section 2: `XaiHighlightsAdapter.build(context)` that flattens `accumulated_extensions`
  - [ ] Step 3: Modify `blueprint.py` — import `XaiHighlightsAdapter`, wire into dispatch table, DELETE `_hydrate_grouped_extensions_block` method entirely
  - [ ] Step 4: Migrate Tests — move XAI extension tests from `test_blueprint.py` to `test_xai_highlights_adapter.py`; add negative tests (empty extensions → `[]`, multiple groups flatten, context immutability, `None` extensions raises `ValidationError`)
  - [ ] Step 5: Run Quality Gate — `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_130\01_xai_highlights_adapter.md]`

---

### Phase 3: Extract Penalties Adapter
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_130\02_penalties_adapter.md] *(placeholder — expand via `/tier1-planner` after Phase 2)*

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_130\02_penalties_adapter.md] @[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\01-python-backend.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_130_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_130\02_penalties_adapter.md]`
  - [ ] Create `penalties_adapter.py` — `PenaltiesAdapter.build(context)` with strict typing, `VisualIntent.CRITICAL_OVERRIDE` severity
  - [ ] Modify `blueprint.py` — wire adapter, DELETE `_hydrate_penalties_block`
  - [ ] Migrate Tests — move penalty tests from `test_blueprint.py` to `test_penalties_adapter.py`; add negative tests (missing `penalties_applied` raises `ValidationError`, empty list `[]` returns `[]`, positive `AlertBlock` mapping)
  - [ ] Run Quality Gate
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_130\02_penalties_adapter.md]`

---

### Phase 4: Extract Executive Summary Adapter
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_130\03_executive_summary_adapter.md] *(placeholder — expand via `/tier1-planner` after Phase 2)*

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_130\03_executive_summary_adapter.md] @[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\01-python-backend.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_130_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_130\03_executive_summary_adapter.md]`
  - [ ] Create `executive_summary_adapter.py` — `ExecutiveSummaryAdapter.build(context)` with strict `RoleClassification` validation, Fail-Fast L10N prefix, typed exception handlers
  - [ ] Replace bare `except Exception:` at L1085 with typed `except KeyError` / `except ValueError`
  - [ ] Replace `.get()` fallback at L1080 with strict key access + `AppException`
  - [ ] Modify `blueprint.py` — delete inline executive summary role-mapping logic, wire adapter
  - [ ] Migrate Tests — move summary tests from `test_blueprint.py` to `test_executive_summary_adapter.py`; add negative tests (invalid `user_role` → `AppException`, missing `user_role_label` → `AppException`, missing `user_role_mappings` key → `AppException`)
  - [ ] Run Quality Gate
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_130\03_executive_summary_adapter.md]`

---

### Phase 5: Extract Printable Sources Adapter
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_130\04_printable_sources_adapter.md] *(placeholder — expand via `/tier1-planner` after Phase 2)*

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_130\04_printable_sources_adapter.md] @[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\01-python-backend.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_130_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_130\04_printable_sources_adapter.md]`
  - [ ] Create `printable_sources_adapter.py` — `PrintableSourcesAdapter.build(context)` extracting `_hydrate_printable_sources_block`
  - [ ] Modify `blueprint.py` — wire adapter, DELETE `_hydrate_printable_sources_block`
  - [ ] Migrate Tests — move printable sources tests to `test_printable_sources_adapter.py`
  - [ ] Run Quality Gate
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_130\04_printable_sources_adapter.md]`

**Phase 5a: DEFERRED** — Placeholder adapters (`_hydrate_global_score_block`, `_hydrate_audit_trail_block`, `_hydrate_jargon_ratio_block`) are NOT extracted. No action required until real logic exists.

---

### Phase 6: Decompose `_extract_matrices_and_extensions` God Method
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_130\05_god_method_decomposition.md] *(placeholder — expand via `/tier1-planner` after Phase 2)*

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_130\05_god_method_decomposition.md] @[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\01-python-backend.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_130_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_130\05_god_method_decomposition.md]`
  - [ ] BLOCKING PREREQUISITE: Enumerate ALL extension type strings in `seed_data.json` and cross-reference against `XaiExtensionType` enum at @[c:\src\quorum\backend_v2\models\enums.py#L138-L171]
  - [ ] Create `dtos.py` — `MatrixExtractionContext` (frozen, strict, extra=forbid) with 13 strictly typed fields, `MatrixExtractionResultDTO`
  - [ ] Create `matrix_extractor.py` — `MatrixExtractorService.extract(context)` → `MatrixExtractionResultDTO`; extract `_add_ext` closure
  - [ ] SEVERITY ENUM MIGRATION: Replace bare string severity literals at L714-L719, L742, L751 with `VisualIntent` enum values
  - [ ] SILENT SWALLOW ERADICATION: Replace `except ValueError: pass` at L756-L757 with `logger.error` + `raise AppException`
  - [ ] DUCK-TYPING ERADICATION: Replace `hasattr(profile, \"max_extension_items\")` with direct access, `getattr(b, \"title\", None)` with `b.title`, `getattr(c, \"text\", \"\")` with typed `isinstance(c, AlertBlock)` narrowing
  - [ ] Modify `blueprint.py` — DELETE 560-line God Method, replace with `MatrixExtractorService.extract(context)`
  - [ ] Migrate Tests — move God Method tests from `test_blueprint.py` to `test_matrix_extractor.py`; add negative tests (missing fields → `ValidationError`, unknown extension → `AppException`, malformed payload → Fail-Fast)
  - [ ] Run Quality Gate
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_130\05_god_method_decomposition.md]`

---

### Phase 7A: SDUI Layout Flattening — Dispatch Loop Refactoring & Adapter Wiring
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_130\06a_sdui_layout_dispatch.md] *(placeholder — expand via `/tier1-planner` after Phase 6)*

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_130\06a_sdui_layout_dispatch.md] @[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\01-python-backend.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_130_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_130\06a_sdui_layout_dispatch.md]`
  - [ ] Refactor `blueprint.py` final assembly to concatenate all adapter blocks into flat `inner_sdui_blocks` list
  - [ ] Configure dispatch loop execution order: Metadata → Executive Summary → Matrix Graphs & Justifications → Extensions & Penalties → Matrix Summary Table → Workflow Extensions → Sources
  - [ ] Preserve Global Linguistic Mandate (global_mandates.py, linguistic_directives.py)
  - [ ] Enforce Global Anti-Truncation Mandate (zero shortening of text content)
  - [ ] Run Quality Gate
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_130\06a_sdui_layout_dispatch.md]`

---

### Phase 7B: SDUI Layout Flattening — Block Ordering & PDF/Jinja Parity
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_130\06b_sdui_layout_ordering.md] *(placeholder — expand via `/tier1-planner` after Phase 7A)*

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_130\06b_sdui_layout_ordering.md] @[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\01-python-backend.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_130_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_130\06b_sdui_layout_ordering.md]`
  - [ ] Configure block ordering to match `raportti 2.pdf` exactly
  - [ ] Modify `pdf_generator.py` — flat layout iteration
  - [ ] Modify `report_template.jinja2` — flat block rendering via `render_sdui_blocks()` macro
  - [ ] Verify Flutter rendering parity (Dumb Painter sequential render)
  - [ ] Run Quality Gate
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_130\06b_sdui_layout_ordering.md]`

---

### Phase 8: Verification & E2E Integration Gate
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_130\07_verification_e2e_gate.md] *(placeholder — expand via `/tier1-planner` after Phase 7B)*

- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_130_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_130\07_verification_e2e_gate.md]`
  - [ ] Backend audit: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
  - [ ] Frontend compilation: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`
  - [ ] E2E parity check: `uv run python scripts/run_e2e_variance_test.py`
  - [ ] Live E2E gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
  - [ ] Manual: Generate full PDF report and visually compare against @[c:\src\quorum\docs\jwvastaus\raportti 2.pdf]
  - [ ] Manual: Verify Flutter app renders report identically

---

### Integration Checkpoint: Full-Stack Validation

- [ ] **[NOK]** Backend full-suite passes: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- [ ] **[NOK]** Frontend full-suite passes: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`

---

### Post-Implementation Gates

- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide `grep_search` for old import paths referencing deleted methods (`_hydrate_grouped_extensions_block`, `_hydrate_penalties_block`, `_hydrate_printable_sources_block`, `_extract_matrices_and_extensions`) and delete any deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified backend files:
  - @[c:\src\quorum\backend_v2\services\sdui\adapters\base_adapter.py]
  - @[c:\src\quorum\backend_v2\services\sdui\adapters\xai_highlights_adapter.py]
  - @[c:\src\quorum\backend_v2\services\sdui\adapters\penalties_adapter.py]
  - @[c:\src\quorum\backend_v2\services\sdui\adapters\executive_summary_adapter.py]
  - @[c:\src\quorum\backend_v2\services\sdui\adapters\printable_sources_adapter.py]
  - @[c:\src\quorum\backend_v2\services\sdui\dtos.py]
  - @[c:\src\quorum\backend_v2\services\sdui\matrix_extractor.py]
  - @[c:\src\quorum\backend_v2\services\blueprint.py]
  - @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_base_adapter.py]
  - @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_xai_highlights_adapter.py]
  - @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_penalties_adapter.py]
  - @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_executive_summary_adapter.py]
  - @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_printable_sources_adapter.py]
  - @[c:\src\quorum\backend_v2\tests\unit\services\sdui\test_matrix_extractor.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` — No Flutter files are expected to change in this Epic (Dumb Painter contract is preserved). Verify by grepping for any modified `.dart` files.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain. `grep_search` for all deleted method names across the entire `backend_v2/` directory.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for all surviving business logic in `backend_v2/services/sdui/` and `backend_v2/services/blueprint.py`.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

---

### Documentation & Knowledge Item Update

- [ ] **[NOK]** Create/Update Knowledge Item (KI) for new SSOTs: `AdapterContext`, `MatrixExtractionContext`, `MatrixExtractionResultDTO`, `MatrixExtractorService` in `<appDataDir>/knowledge/`.
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

---

### Final Epic Audit

- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_130_blueprint_decomposition.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

---

## Instructions for the Execution Agent

1. **Atomic Commit Mandate**: After each phase's quality gate passes, instruct the user to perform an atomic `git commit` BEFORE proceeding. Specify exact relative file paths (e.g., `git add backend_v2/services/sdui/adapters/base_adapter.py`).
2. **Seeding Environment**: If database seeding is needed, run: `uv run python backend_v2/seed/run_seed.py local`
3. **`@-reference` Syntax**: When providing file paths to the AI, use the `@[c:\src\quorum\...]` syntax for precise file binding.
4. **KI Preflight**: Before creating ANY adapter file, the executing agent MUST read KI `sdui_adapter_decomposition` (`ki_sdui_adapter_pattern.md`).
5. **Placeholder Plans**: Phases 3-8 currently have placeholder plans. Before executing each phase, the user MUST first run `/tier1-planner` to expand the placeholder into a full detailed plan with execution protocol XML, test contracts, and demolition inventory.
6. **Session Handover Mandate**: You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session. Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the `/tier5-resume` command in your chat response so the user can easily copy-paste it to continue. The mandatory workflow loop is: `/tier0-research-plan` (Phase N) → `/tier2-execute` (Phase N) → `/tier8-audit-plan` (Phase N) → `/tier0-research-plan` (Phase N+1). Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` → `/tier2-hardening-frontend` → `/tier7-describe-architecture` → `/tier8-audit-epic`.

---

## Requirements Traceability Matrix

| Req ID | Requirement | Epic Section | Plan File | Step ID(s) |
|--------|-------------|-------------|-----------|------------|
| R1 | Create `backend_v2/services/sdui/adapters/` directory structure with `__init__.py` files | §3 Phase 1 | [00_foundation_adapter_context.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/00_foundation_adapter_context.md) | Step 2 |
| R2 | Define frozen `AdapterContext` Pydantic DTO with `ConfigDict(frozen=True, strict=True, extra="forbid")` | §3 Phase 1 | [00_foundation_adapter_context.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/00_foundation_adapter_context.md) | Step 3 |
| R3 | Define `SduiAdapterProtocol` with `@staticmethod build(context: AdapterContext) → list[AnySduiBlock]` | §3 Phase 1 | [00_foundation_adapter_context.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/00_foundation_adapter_context.md) | Step 3 |
| R4 | Move `from collections.abc import Callable` from inline (L103) to module-level imports | §3 Phase 1 | [00_foundation_adapter_context.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/00_foundation_adapter_context.md) | Step 4 |
| R5 | Migrate dispatch table type from `Callable[..., list[AnySduiBlock]]` to `Callable[[AdapterContext], list[AnySduiBlock]]` with lambda bridges | §3 Phase 1 | [00_foundation_adapter_context.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/00_foundation_adapter_context.md) | Step 5 |
| R6 | Migrate dispatch call site from kwargs scatter (L1948-L1960) to single `AdapterContext` pass with `mcp_audit_map=mcp_audit_data` naming bridge | §3 Phase 1 | [00_foundation_adapter_context.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/00_foundation_adapter_context.md) | Step 6 |
| R7 | Negative tests for `AdapterContext`: frozen mutation, extra fields forbidden, missing required fields, strict type enforcement | §3 Phase 1 | [00_foundation_adapter_context.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/00_foundation_adapter_context.md) | Step 7 |
| R8 | Create `XaiHighlightsAdapter` with two-section structure (AESTHETICS_RULES + build method) per KI template | §3 Phase 2 | [01_xai_highlights_adapter.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/01_xai_highlights_adapter.md) | Step 2 |
| R9 | DELETE `_hydrate_grouped_extensions_block` from `blueprint.py` and wire `XaiHighlightsAdapter.build(ctx)` into dispatch table | §3 Phase 2 | [01_xai_highlights_adapter.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/01_xai_highlights_adapter.md) | Step 3 |
| R10 | Migrate XAI extension tests from `test_blueprint.py` to `test_xai_highlights_adapter.py`; add negative tests (empty extensions, context immutability, None raises) | §3 Phase 2 | [01_xai_highlights_adapter.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/01_xai_highlights_adapter.md) | Step 4 |
| R11 | Create `PenaltiesAdapter` with strict typing, `VisualIntent.CRITICAL_OVERRIDE` severity, `build(context)` method | §3 Phase 3 | [02_penalties_adapter.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/02_penalties_adapter.md) | — |
| R12 | DELETE `_hydrate_penalties_block` from `blueprint.py` and wire `PenaltiesAdapter` into dispatch table | §3 Phase 3 | [02_penalties_adapter.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/02_penalties_adapter.md) | — |
| R13 | Penalties negative tests: missing `penalties_applied` → `ValidationError`, empty list `[]` → `[]`, positive `AlertBlock` mapping | §3 Phase 3 | [02_penalties_adapter.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/02_penalties_adapter.md) | — |
| R14 | Create `ExecutiveSummaryAdapter` with strict `RoleClassification` validation, Fail-Fast L10N prefix, typed exception handlers | §3 Phase 4 | [03_executive_summary_adapter.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/03_executive_summary_adapter.md) | — |
| R15 | Replace bare `except Exception:` at L1085 with typed handler; replace `.get()` at L1080 with strict key access + `AppException` | §3 Phase 4 | [03_executive_summary_adapter.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/03_executive_summary_adapter.md) | — |
| R16 | Executive summary negative tests: invalid `user_role` → `AppException`, missing `user_role_label` → `AppException`, missing `user_role_mappings` key → `AppException` | §3 Phase 4 | [03_executive_summary_adapter.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/03_executive_summary_adapter.md) | — |
| R17 | Create `PrintableSourcesAdapter` extracting `_hydrate_printable_sources_block`; DELETE original method from `blueprint.py` | §3 Phase 5 | [04_printable_sources_adapter.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/04_printable_sources_adapter.md) | — |
| R18 | BLOCKING PREREQUISITE: Enumerate ALL extension type strings in `seed_data.json` and cross-reference against `XaiExtensionType` enum BEFORE enabling crash path | §3 Phase 6 | [05_god_method_decomposition.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/05_god_method_decomposition.md) | — |
| R19 | Create `MatrixExtractionContext` frozen Pydantic DTO with 13 strictly typed fields in `dtos.py` | §3 Phase 6 | [05_god_method_decomposition.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/05_god_method_decomposition.md) | — |
| R20 | Create `MatrixExtractionResultDTO` in `dtos.py` with fields: `evaluative_matrices`, `informational_matrices`, `all_parsed_matrices`, `step_scorecard_atoms`, `accumulated_extensions` | §3 Phase 6 | [05_god_method_decomposition.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/05_god_method_decomposition.md) | — |
| R21 | Create `MatrixExtractorService.extract(context) → MatrixExtractionResultDTO` extracting `_add_ext` closure from `blueprint.py` | §3 Phase 6 | [05_god_method_decomposition.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/05_god_method_decomposition.md) | — |
| R22 | SEVERITY ENUM MIGRATION: Replace bare string severity literals at L714-L719, L742, L751 with `VisualIntent` enum values; DO NOT change SDUI model field types | §3 Phase 6 | [05_god_method_decomposition.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/05_god_method_decomposition.md) | — |
| R23 | SILENT SWALLOW ERADICATION: Replace `except ValueError: pass` at L756-L757 with `logger.error` + `raise AppException` (deliberate behavioral change) | §3 Phase 6 | [05_god_method_decomposition.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/05_god_method_decomposition.md) | — |
| R24 | DUCK-TYPING ERADICATION: Replace `hasattr(profile, \"max_extension_items\")`, `getattr(b, \"title\", None)`, `getattr(c, \"text\", \"\")` with direct/typed access | §3 Phase 6 | [05_god_method_decomposition.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/05_god_method_decomposition.md) | — |
| R25 | DELETE 560-line God Method `_extract_matrices_and_extensions` from `blueprint.py` | §3 Phase 6 | [05_god_method_decomposition.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/05_god_method_decomposition.md) | — |
| R26 | Refactor `blueprint.py` final assembly to flat `inner_sdui_blocks` list; configure dispatch loop order matching `raportti 2.pdf` (7 steps: metadata → exec summary → matrices → extensions → summary table → workflow ext → sources) | §3 Phase 7 | [06a_sdui_layout_dispatch.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/06a_sdui_layout_dispatch.md) | — |
| R27 | Modify `pdf_generator.py` and `report_template.jinja2` Jinja macros to iterate over flat block array; eliminate legacy `preset_view` strings | §3 Phase 7 | [06b_sdui_layout_ordering.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/06b_sdui_layout_ordering.md) | — |
| R28 | Final E2E verification: backend audit, frontend compilation, parity check, live E2E gate, visual PDF comparison against `raportti 2.pdf`, Flutter rendering parity | §4 DoD | [07_verification_e2e_gate.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_130/07_verification_e2e_gate.md) | — |

---

# Session Handover Context

## Achieved
- Tracker file `EPIC_130_tracker.md` generated from 9 implementation plans and the parent Epic document.
- All 8 phases (including 7A/7B sub-split) mapped with per-step checkboxes.
- Requirements Traceability Matrix extracted with 28 granular requirements (R1-R28).
- Post-Implementation Gates, Documentation & KI Update, and Final Epic Audit sections populated.
- **[2026-08-02]** Tier 0 Research Analysis completed on `00_foundation_adapter_context.md`. Identified a critical type mismatch on `mcp_audit_map` (list vs dict) and provided corrective mutations (M1, M2).

## Learned
- **Baseline State Snapshot**: `blueprint.py` is currently ~2012 lines with a 560-line God Method `_extract_matrices_and_extensions` (L222-L782). The dispatch table at L104-L111 uses `Callable[..., list[AnySduiBlock]]` with kwargs scatter at L1948-L1960. The inline `Callable` import is at L103 inside `__init__`. Six hydrator methods exist: `_hydrate_penalties_block`, `_hydrate_global_score_block`, `_hydrate_audit_trail_block`, `_hydrate_jargon_ratio_block`, `_hydrate_printable_sources_block`, `_hydrate_grouped_extensions_block`.
- **Phase 1 Defect (M1)**: `mcp_audit_data` at the `blueprint.py` call site (L1729) is `list[MCPAuditTrace]`, while `AdapterContext.mcp_audit_map` is locked to `dict[str, MCPAuditTrace] | None`. Constructing the context must include a list-to-dict conversion: `mcp_audit_map={t.id: t for t in mcp_audit_data} if mcp_audit_data else None`.
- **Phase 1 Missing Guard (M2)**: Execution must verify `test_blueprint.py` and `test_blueprint_sdui_crash.py` still pass after `AdapterContext` injection to ensure no circular import or mock failures occur.
- Phases 3-8 have placeholder plans that MUST be expanded via `/tier1-planner` before execution.
- Phase 5a is DEFERRED (placeholder adapters for empty methods).
- Phase 7 is MANDATORILY split into 7A (dispatch loop) and 7B (ordering + PDF parity).
- The KI `sdui_adapter_decomposition` MUST be read before creating any adapter file.

## Remaining
- **[IMMEDIATE]** Execute Phase 1 (foundation) using `/tier2-execute` on the mutated `00_foundation_adapter_context.md`.
- Expand placeholder plans for Phases 3-8 via `/tier1-planner` (incrementally, after each preceding phase completes).
- Execute all 8 phases through the mandatory workflow loop.
- Complete all Post-Implementation Gates.
- Run Final Epic Audit.

## Resume Command
`/tier5-resume --workflow=/tier2-execute --target="@[c:\src\quorum\docs\epic\tasks_EPIC_130\00_foundation_adapter_context.md]" --rules="@[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\01-python-backend.md]"`
