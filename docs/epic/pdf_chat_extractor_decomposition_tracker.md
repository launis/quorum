<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_chat_ingress_and_provenance_architecture.md]</knowledge_item>
</required_context_rules>

# God Code Decomposition Tracker: `backend_v2/services/ingress/pdf_chat_extractor.py`

## 1. Executive Summary & Baseline Telemetry
- **Target Monolith**: `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]` -> `@[backend_v2/services/ingress/pdf_extractor/__init__.py#L46-L59]` (682 lines; decomposed into a 57-line package facade + 3 stage sub-modules under `backend_v2/services/ingress/pdf_extractor/` and relocated 4 inline DTOs to `@[backend_v2/models/dtos/ingress.py#L77-L92]`)
- **Monolith Archetype**: Archetype C — Ingress / Parser / Anti-Corruption Layer (ACL) with Sequential Pipeline Staging (`PdfChatExtractorService.extract_conversation`)
- **Planning Mode**: Single-File Fast-Track Mode (682 lines, 3 domain sub-modules + 1 package facade `< 150` lines, non-orchestrator)
- **Baseline Test Suite (`[BASELINE]`)**: `uv run python scripts/backend_audit_loop.py backend_v2/services/ingress/pdf_chat_extractor.py --test` -> **25 passed** in `[DELETE] @[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]`, 10/10 audit stages passed, **96% line coverage** (311 statements, 12 missed: lines `171, 209, 222-223, 242-244, 456-457, 479, 602, 618`)
- **Symbol & Blast-Radius Map**: `@[docs/epic/tasks_pdf_chat_extractor/symbol_migration_map.md]`

---

## Phase Execution Status

### Phase 1: Inline DTO Relocation & Bubble Geometry Stage Extraction (Epoch 1 — Phase 1A)
- **Plan:** @[docs/epic/tasks_pdf_chat_extractor/phase1_dtos_and_geometry_extraction.md]
- [x] **[SKIPPED] Research:** Single-File Fast-Track Mode (bypassed per Archetype C fast-track)
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_pdf_chat_extractor/phase1_dtos_and_geometry_extraction.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`
  - [x] Step 1: Relocate `PdfCellCoordinatesDTO`, `PdfTextBlockDTO`, `RawTurnDTO`, and `PdfBlockSignatureDTO` to `@[backend_v2/models/dtos/ingress.py#L77-L92]` and add unit tests in `@[backend_v2/tests/unit/models/dtos/test_ingress.py#L111-L119]`
  - [x] Step 2: Create `@[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py#L42-L49]`
  - [x] Step 3: Wire DTO Re-Exports and Bubble Geometry Proxy Delegations in `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_pdf_chat_extractor/phase1_dtos_and_geometry_extraction.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`

### Phase 2: Table Markdown & Attachment Card Stage Extraction (Epoch 1 — Phase 1B)
- **Plan:** @[docs/epic/tasks_pdf_chat_extractor/phase2_table_and_card_stage_extraction.md]
- [x] **[SKIPPED] Research:** Single-File Fast-Track Mode (bypassed per Archetype C fast-track)
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_pdf_chat_extractor/phase2_table_and_card_stage_extraction.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`
  - [x] Step 1: Create `@[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py#L33-L55]`
  - [x] Step 2: Wire Table and Attachment Card Proxy Delegations in `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_pdf_chat_extractor/phase2_table_and_card_stage_extraction.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`

### Phase 3: Turn Segmentation, Visual Ordering & Truncation Stage Extraction (Epoch 1 — Phase 1C)
- **Plan:** @[docs/epic/tasks_pdf_chat_extractor/phase3_turn_assembly_stage_extraction.md]
- [x] **[SKIPPED] Research:** Single-File Fast-Track Mode (bypassed per Archetype C fast-track)
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_pdf_chat_extractor/phase3_turn_assembly_stage_extraction.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`
  - [x] Step 1: Create `@[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py#L55-L91]`
  - [x] Step 2: Wire Turn Assembly Proxy Delegations in `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_pdf_chat_extractor/phase3_turn_assembly_stage_extraction.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`

### Phase 4: Modular Test Suite Split, Atomic Package Cutover & AST Guardrail Lock (Epoch 1 — Cutover)
- **Plan:** @[docs/epic/tasks_pdf_chat_extractor/phase4_package_cutover_and_guardrails.md]
- [x] **[SKIPPED] Research:** Single-File Fast-Track Mode (bypassed per Archetype C fast-track)
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_pdf_chat_extractor/phase4_package_cutover_and_guardrails.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]` (`5af373477`)
  - [x] Step 1: Split `[DELETE] @[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]` into `@[backend_v2/tests/unit/services/ingress/pdf_extractor/test_bubble_geometry.py#L27-L37]`, `@[backend_v2/tests/unit/services/ingress/pdf_extractor/test_table_and_card_stage.py#L24-L50]`, `@[backend_v2/tests/unit/services/ingress/pdf_extractor/test_turn_assembly_stage.py#L68-L82]`, and `@[backend_v2/tests/unit/services/ingress/pdf_extractor/test_pdf_extractor_facade.py#L23-L55]`
  - [x] Step 2: Execute Atomic Package Cutover (`@[backend_v2/services/ingress/pdf_extractor/__init__.py#L46-L59]` and delete `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]`) and Rewire 1-Hop Consumers (`@[backend_v2/services/ingress/__init__.py]`, `@[backend_v2/services/ingress/multi_channel_ingress_service.py#L27-L197]`, `@[backend_v2/services/document_extraction.py#L94-L156]`, `@[scripts/run_e2e_variance_test.py#L277-L411]`, `@[backend_v2/tests/unit/test_document_extraction.py#L145-L175]`, `@[backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py#L1069-L1131]`)
  - [x] Step 3: Lock Retired Monolith Path in `@[scripts/_ast_guardrails.py#L1865-L1923]` and `@[scripts/_ast_guardrails.py#L1925-L2047]` under `QGR017` and Synchronize `@[.agents/rules/04_directory_reference.md]`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_pdf_chat_extractor/phase4_package_cutover_and_guardrails.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`

---

### Post-Implementation Gates
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker docs/epic/pdf_chat_extractor_decomposition_tracker.md --gate backend`
  - [x] @[backend_v2/models/dtos/ingress.py#L77-L92]
  - [x] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py#L42-L49]
  - [x] @[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py#L33-L55]
  - [x] @[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py#L55-L91]
  - [x] @[backend_v2/services/ingress/pdf_extractor/__init__.py#L46-L59]
  - [x] [DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]
  - [x] @[backend_v2/services/ingress/__init__.py]
  - [x] @[backend_v2/services/ingress/multi_channel_ingress_service.py#L27-L197]
  - [x] @[backend_v2/services/document_extraction.py#L94-L156]
  - [ ] @[scripts/run_e2e_variance_test.py#L277-L411]
  - [ ] @[scripts/_ast_guardrails.py#L1865-L1923]
- [x] **[SKIPPED] Tier 2 Hardening (Frontend)**: N/A — Pure Python Backend Service Decomposition (zero `.dart` files in target scope).
- [ ] **[NOK] Pre-Delete Audit**: Verify 0 remaining imports from `backend_v2.services.ingress.pdf_chat_extractor` and 100% green `uv run python scripts/backend_audit_loop.py backend_v2/services/ingress/ --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/services/document_extraction.py --test --ast-strict`.
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Verify all 25 baseline unit tests pass across the modularized test suites (`@[backend_v2/tests/unit/services/ingress/pdf_extractor/test_bubble_geometry.py#L27-L37]`, `@[backend_v2/tests/unit/services/ingress/pdf_extractor/test_table_and_card_stage.py#L24-L50]`, `@[backend_v2/tests/unit/services/ingress/pdf_extractor/test_turn_assembly_stage.py#L68-L82]`, `@[backend_v2/tests/unit/services/ingress/pdf_extractor/test_pdf_extractor_facade.py#L23-L55]`) with `>= 96%` line coverage.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Verify 100% symbol parity ($\mathcal{I}_{orig} \subseteq \bigcup \mathcal{I}_{sub}$) and execute `uv run python scripts/audit_dict_eradication.py` and `uv run python scripts/audit_clean_imports.py`.
- [ ] **[NOK] As-Built Architectural Sync**:
  `/tier7-describe-architecture @[docs/epic/pdf_chat_extractor_decomposition_tracker.md] @[ki_chat_ingress_and_provenance_architecture.md] @[ki_god_code_prevention.md]`
  - **Target KIs to Synchronize**: `@[ki_chat_ingress_and_provenance_architecture.md]`, `@[ki_god_code_prevention.md]`
  - **Directory Reference Sync**: Verify `@[.agents/rules/04_directory_reference.md]` reflects `backend_v2/services/ingress/pdf_extractor/` (`bubble_geometry.py`, `table_and_card_stage.py`, `turn_assembly_stage.py`, `__init__.py` facade).
  - **Pillar Documentation Sync**: Synchronize Pillar 2 architectural documentation to reflect the modular `backend_v2/services/ingress/pdf_extractor/` stage pipeline.

#### Epoch 2: 12-Item Technical Debt Inventory (To Resolve During Tier 2 Hardening ONLY After Epoch 1 Cutover Completes)
1. - [ ] **Item 5 (PEP 593 `Annotated` Field Typing on Relocated DTOs)**:
    - Enforce `Annotated[T, Field(description=...)]` across `PdfCellCoordinatesDTO`, `PdfTextBlockDTO`, `RawTurnDTO`, and `PdfBlockSignatureDTO` inside `@[backend_v2/models/dtos/ingress.py#L77-L92]`.
2. - [ ] **Item 8 (PEP 257 Google-Style Docstrings & `Raises:` Completeness)**:
    - Enforce complete PEP 257 docstrings with explicit `Args:`, `Returns:`, and `Raises:` (`AppException` with `ErrorCodes.VALIDATION_FAILED`) across `@[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py#L42-L49]`, `@[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py#L33-L55]`, `@[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py#L55-L91]`, and `@[backend_v2/services/ingress/pdf_extractor/__init__.py#L46-L59]`.
3. - [ ] **Item 9 (Zero Inline Imports)**:
    - Promote the inline import of `PdfChatExtractorService` inside `DocumentExtractionService._extract_pdf_sync` (`@[backend_v2/services/document_extraction.py#L94-L156]`) to a module top-level import in `@[backend_v2/services/document_extraction.py]`.
4. - [ ] **Item 10 (ISTQB Negative Partition Expansion to >= 98% Line Coverage)**:
    - Add negative and boundary tests in `@[backend_v2/tests/unit/services/ingress/pdf_extractor/test_bubble_geometry.py#L27-L37]`, `@[backend_v2/tests/unit/services/ingress/pdf_extractor/test_table_and_card_stage.py#L24-L50]`, and `@[backend_v2/tests/unit/services/ingress/pdf_extractor/test_turn_assembly_stage.py#L68-L82]` covering the 12 baseline missed lines (`171, 209, 222-223, 242-244, 456-457, 479, 602, 618`).

---

### Final Epic Audit
- [ ] **[NOK] System 2 Red-Team Audit:** `/tier8-audit-plan @[docs/epic/tasks_pdf_chat_extractor/phase4_package_cutover_and_guardrails.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`
- [ ] **[NOK] Global Backend Completion Gate:** `uv run python scripts/backend_audit_loop.py backend_v2/ --test`

---

## Instructions for the Execution Agent
1. **Two-Epoch Firewall (`two_epoch_separation_mandate`)**: Execute Phases 1 through 4 (Epoch 1) as a **100% pure structural lift-and-shift** with zero behavioral mutations. Do NOT resolve the Epoch 2 12-Item Tech Debt Inventory until Phase 4 (Atomic Package Cutover and `QGR017` lockdown) is 100% complete and committed.
2. **Two-Phase Package Strangler Protocol (`strangler_fig_mandate`)**: Do NOT create `@[backend_v2/services/ingress/pdf_extractor/__init__.py#L46-L59]` during Phases 1, 2, or 3 while `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]` exists on disk. Create `@[backend_v2/services/ingress/pdf_extractor/__init__.py#L46-L59]` and delete `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]` atomically in Phase 4 Step 2.
3. **500-Line Partitioning Gate**: Every extracted sub-module (`@[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py#L42-L49]`, `@[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py#L33-L55]`, `@[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py#L55-L91]`) and the package facade (`@[backend_v2/services/ingress/pdf_extractor/__init__.py#L46-L59]`) MUST remain strictly below 250 lines (and `< 150` lines for `__init__.py`).
4. **Atomic Checkpoints**: Run `uv run python scripts/backend_audit_loop.py <target> --test --ast-strict` after every step and perform an atomic `git commit` before advancing to the next step.

---

## Requirements Traceability Matrix

| Requirement ID | Architectural Requirement Description | Phase & Step Mapping | Verification Gate |
| :--- | :--- | :--- | :--- |
| `REQ-PCE-01` | Relocate `PdfCellCoordinatesDTO`, `PdfTextBlockDTO`, `RawTurnDTO`, and `PdfBlockSignatureDTO` to `@[backend_v2/models/dtos/ingress.py#L77-L92]` with PEP 593 `Annotated` typing | Phase 1, Step 1 | `backend_audit_loop.py backend_v2/models/dtos/ingress.py --test --ast-strict` |
| `REQ-PCE-02` | Extract vector bubble geometry, table bounding-box extraction, and conversation PDF detection into `@[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py#L42-L49]` | Phase 1, Step 2 | `backend_audit_loop.py backend_v2/services/ingress/pdf_extractor/bubble_geometry.py --test --ast-strict` |
| `REQ-PCE-03` | Re-export DTOs and delegate bubble geometry methods in `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]` | Phase 1, Step 3 | `backend_audit_loop.py backend_v2/services/ingress/pdf_chat_extractor.py --test --ast-strict` |
| `REQ-PCE-04` | Extract table text block filtering, Markdown table reconstruction, and attachment card detection into `@[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py#L33-L55]` | Phase 2, Step 1 | `backend_audit_loop.py backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py --test --ast-strict` |
| `REQ-PCE-05` | Delegate table and attachment card stage methods in `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]` | Phase 2, Step 2 | `backend_audit_loop.py backend_v2/services/ingress/pdf_chat_extractor.py --test --ast-strict` |
| `REQ-PCE-06` | Extract truncation detection, visual block ordering, and multi-turn conversation assembly into `@[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py#L55-L91]` | Phase 3, Step 1 | `backend_audit_loop.py backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py --test --ast-strict` |
| `REQ-PCE-07` | Delegate `_check_truncation`, `_sort_blocks_visual_order`, and `extract_conversation` in `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]` | Phase 3, Step 2 | `backend_audit_loop.py backend_v2/services/ingress/pdf_chat_extractor.py --test --ast-strict` |
| `REQ-PCE-08` | Split `[DELETE] @[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]` into 4 modular test suites under `backend_v2/tests/unit/services/ingress/pdf_extractor/` | Phase 4, Step 1 | `pytest backend_v2/tests/unit/services/ingress/pdf_extractor/` |
| `REQ-PCE-09` | Atomically cut over `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]` to `@[backend_v2/services/ingress/pdf_extractor/__init__.py#L46-L59]` and rewire all 1-hop consumer imports | Phase 4, Step 2 | `backend_audit_loop.py backend_v2/services/ingress/pdf_extractor/__init__.py --test --ast-strict` |
| `REQ-PCE-10` | Ban `backend_v2.services.ingress.pdf_chat_extractor` in `@[scripts/_ast_guardrails.py#L1865-L1923]` and `@[scripts/_ast_guardrails.py#L1925-L2047]` under `QGR017` and update `@[.agents/rules/04_directory_reference.md]` | Phase 4, Step 3 | `backend_audit_loop.py scripts/_ast_guardrails.py --test --ast-strict` |

---

# Session Handover Context

## Achieved
- Completed Tier 3 Pre-Flight Baseline (`[BASELINE]`): 25/25 unit tests passing in `[DELETE] @[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]` with **96% line coverage** (311 statements, 12 missed) and 10/10 Universal Quality Gate stages passing.
- Completed Phase 1 (`@[docs/epic/tasks_pdf_chat_extractor/phase1_dtos_and_geometry_extraction.md]`):
  - Relocated `PdfCellCoordinatesDTO`, `PdfTextBlockDTO`, `RawTurnDTO`, and `PdfBlockSignatureDTO` to `@[backend_v2/models/dtos/ingress.py#L77-L92]` with `ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated` fields, and added 8 unit tests in `@[backend_v2/tests/unit/models/dtos/test_ingress.py#L111-L119]` (16/16 passing, 100% coverage).
  - Extracted `dlq_log_extraction_error`, `is_user_bubble_drawing`, `get_page_table_rects`, `is_conversation_pdf`, and `extract_page_user_bubbles` into `@[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py#L42-L49]`.
- Completed Phase 2 (`@[docs/epic/tasks_pdf_chat_extractor/phase2_table_and_card_stage_extraction.md]`):
  - Extracted `_ATTACHMENT_BOX_DIM_PT`, `_ATTACHMENT_BOX_TOLERANCE_PT`, `filter_table_text_blocks`, `reconstruct_tables_as_markdown`, and `detect_attachment_cards` into `@[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py#L33-L55]` (169 lines, 96% line coverage).
- Completed Phase 3 (`@[docs/epic/tasks_pdf_chat_extractor/phase3_turn_assembly_stage_extraction.md]`):
  - Extracted `_ORPHAN_TOKEN_MAX_WIDTH`, `_ORPHAN_TOKEN_MAX_CHARS`, `_PRINT_MARGIN_VERTICAL_PT`, `_PAGE_ZERO_TITLE_MAX_Y0`, `_TRUNCATION_INDICATORS`, `check_truncation`, `sort_blocks_visual_order`, and `extract_conversation_from_doc` into `@[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py#L55-L91]` (235 lines, 99% line coverage).
- Completed Phase 4 (`@[docs/epic/tasks_pdf_chat_extractor/phase4_package_cutover_and_guardrails.md]`):
  - Split `[DELETE] @[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]` into 4 dedicated modular test suites (`@[backend_v2/tests/unit/services/ingress/pdf_extractor/test_bubble_geometry.py#L27-L37]`, `@[backend_v2/tests/unit/services/ingress/pdf_extractor/test_table_and_card_stage.py#L24-L50]`, `@[backend_v2/tests/unit/services/ingress/pdf_extractor/test_turn_assembly_stage.py#L68-L82]`, `@[backend_v2/tests/unit/services/ingress/pdf_extractor/test_pdf_extractor_facade.py#L23-L55]`) with 29/29 tests passing.
  - Executed atomic package cutover: created `@[backend_v2/services/ingress/pdf_extractor/__init__.py#L46-L59]` (57 lines `< 150` lines), deleted `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]`, synchronized `@[backend_v2/services/ingress/__init__.py]`, and rewired all 1-hop consumers and test patch targets.
  - Locked `backend_v2.services.ingress.pdf_chat_extractor` in `@[scripts/_ast_guardrails.py#L1865-L1923]` (`visit_Import`) and `@[scripts/_ast_guardrails.py#L1925-L2047]` (`visit_ImportFrom`) under `QGR017`, added 3 unit tests in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1432-L1439]`, and updated `@[.agents/rules/04_directory_reference.md]`.

## Learned
- Binding static stage functions directly via `staticmethod(...)` on `PdfChatExtractorService` inside `@[backend_v2/services/ingress/pdf_extractor/__init__.py#L46-L59]` keeps the package facade at 57 lines (`< 150` lines), preserves 100% of method signatures and `unittest.mock.patch` compatibility, and guarantees 100% statement coverage when `backend_v2/services/ingress/__init__.py` is audited via `test___init__.py`.

## Resume Command
`/tier8-audit-plan @[docs/epic/tasks_pdf_chat_extractor/phase4_package_cutover_and_guardrails.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`

## Remaining
- Audit Phase 4 via `/tier8-audit-plan @[docs/epic/tasks_pdf_chat_extractor/phase4_package_cutover_and_guardrails.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`.
- Execute Epoch 2 (`Tier 2 Per-File Deterministic Hardening & Test Expansion`).
- Synchronize KIs and architecture documentation via `/tier7-describe-architecture`.
