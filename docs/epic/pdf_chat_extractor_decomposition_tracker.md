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
- **Target Monolith**: `@[backend_v2/services/ingress/pdf_chat_extractor.py#L81-L537]` -> `[NEW] @[backend_v2/services/ingress/pdf_extractor/__init__.py]` (682 lines; decomposing into a `< 150`-line package facade + 3 stage sub-modules under `backend_v2/services/ingress/pdf_extractor/` and relocating 4 inline DTOs to `@[backend_v2/models/dtos/ingress.py#L77-L92]`)
- **Monolith Archetype**: Archetype C — Ingress / Parser / Anti-Corruption Layer (ACL) with Sequential Pipeline Staging (`PdfChatExtractorService.extract_conversation`)
- **Planning Mode**: Single-File Fast-Track Mode (682 lines, 3 domain sub-modules + 1 package facade `< 150` lines, non-orchestrator)
- **Baseline Test Suite (`[BASELINE]`)**: `uv run python scripts/backend_audit_loop.py backend_v2/services/ingress/pdf_chat_extractor.py --test` -> **25 passed** in `@[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]`, 10/10 audit stages passed, **96% line coverage** (311 statements, 12 missed: lines `171, 209, 222-223, 242-244, 456-457, 479, 602, 618`)
- **Symbol & Blast-Radius Map**: `@[docs/epic/tasks_pdf_chat_extractor/symbol_migration_map.md]`

---

## Phase Execution Status

### Phase 1: Inline DTO Relocation & Bubble Geometry Stage Extraction (Epoch 1 — Phase 1A)
- **Plan:** @[docs/epic/tasks_pdf_chat_extractor/phase1_dtos_and_geometry_extraction.md]
- [x] **[SKIPPED] Research:** Single-File Fast-Track Mode (bypassed per Archetype C fast-track)
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_pdf_chat_extractor/phase1_dtos_and_geometry_extraction.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`
  - [x] Step 1: Relocate `PdfCellCoordinatesDTO`, `PdfTextBlockDTO`, `RawTurnDTO`, and `PdfBlockSignatureDTO` to `@[backend_v2/models/dtos/ingress.py#L77-L92]` and add unit tests in `@[backend_v2/tests/unit/models/dtos/test_ingress.py#L111-L119]`
  - [x] Step 2: Create `[NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]`
  - [x] Step 3: Wire DTO Re-Exports and Bubble Geometry Proxy Delegations in `@[backend_v2/services/ingress/pdf_chat_extractor.py#L81-L537]`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_pdf_chat_extractor/phase1_dtos_and_geometry_extraction.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`

### Phase 2: Table Markdown & Attachment Card Stage Extraction (Epoch 1 — Phase 1B)
- **Plan:** @[docs/epic/tasks_pdf_chat_extractor/phase2_table_and_card_stage_extraction.md]
- [x] **[SKIPPED] Research:** Single-File Fast-Track Mode (bypassed per Archetype C fast-track)
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_pdf_chat_extractor/phase2_table_and_card_stage_extraction.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`
  - [ ] Step 1: Create `[NEW] @[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py]`
  - [ ] Step 2: Wire Table and Attachment Card Proxy Delegations in `@[backend_v2/services/ingress/pdf_chat_extractor.py#L81-L537]`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_pdf_chat_extractor/phase2_table_and_card_stage_extraction.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`

### Phase 3: Turn Segmentation, Visual Ordering & Truncation Stage Extraction (Epoch 1 — Phase 1C)
- **Plan:** @[docs/epic/tasks_pdf_chat_extractor/phase3_turn_assembly_stage_extraction.md]
- [x] **[SKIPPED] Research:** Single-File Fast-Track Mode (bypassed per Archetype C fast-track)
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_pdf_chat_extractor/phase3_turn_assembly_stage_extraction.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`
  - [ ] Step 1: Create `[NEW] @[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py]`
  - [ ] Step 2: Wire Turn Assembly Proxy Delegations in `@[backend_v2/services/ingress/pdf_chat_extractor.py#L81-L537]`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_pdf_chat_extractor/phase3_turn_assembly_stage_extraction.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`

### Phase 4: Modular Test Suite Split, Atomic Package Cutover & AST Guardrail Lock (Epoch 1 — Cutover)
- **Plan:** @[docs/epic/tasks_pdf_chat_extractor/phase4_package_cutover_and_guardrails.md]
- [x] **[SKIPPED] Research:** Single-File Fast-Track Mode (bypassed per Archetype C fast-track)
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_pdf_chat_extractor/phase4_package_cutover_and_guardrails.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`
  - [ ] Step 1: Split `@[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]` into `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_bubble_geometry.py]`, `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_table_and_card_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_turn_assembly_stage.py]`, and `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_pdf_extractor_facade.py]`
  - [ ] Step 2: Execute Atomic Package Cutover (`[NEW] @[backend_v2/services/ingress/pdf_extractor/__init__.py]` and delete `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]`) and Rewire 1-Hop Consumers (`@[backend_v2/services/ingress/__init__.py]`, `@[backend_v2/services/ingress/multi_channel_ingress_service.py#L27-L197]`, `@[backend_v2/services/document_extraction.py#L93-L156]`, `@[scripts/run_e2e_variance_test.py#L277-L411]`, `@[backend_v2/tests/unit/test_document_extraction.py#L145-L175]`, `@[backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py#L1066-L1127]`)
  - [ ] Step 3: Lock Retired Monolith Path in `@[scripts/_ast_guardrails.py#L1865-L1910]` and `@[scripts/_ast_guardrails.py#L1912-L2011]` under `QGR017` and Synchronize `@[.agents/rules/04_directory_reference.md]`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_pdf_chat_extractor/phase4_package_cutover_and_guardrails.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`

---

### Post-Implementation Gates
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker docs/epic/pdf_chat_extractor_decomposition_tracker.md --gate backend`
  - [ ] @[backend_v2/models/dtos/ingress.py#L77-L92]
  - [ ] [NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]
  - [ ] [NEW] @[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py]
  - [ ] [NEW] @[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py]
  - [ ] [NEW] @[backend_v2/services/ingress/pdf_extractor/__init__.py]
  - [ ] [DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]
  - [ ] @[backend_v2/services/ingress/__init__.py]
  - [ ] @[backend_v2/services/ingress/multi_channel_ingress_service.py#L27-L197]
  - [ ] @[backend_v2/services/document_extraction.py#L93-L156]
  - [ ] @[scripts/run_e2e_variance_test.py#L277-L411]
  - [ ] @[scripts/_ast_guardrails.py#L1865-L1910]
- [x] **[SKIPPED] Tier 2 Hardening (Frontend)**: N/A — Pure Python Backend Service Decomposition (zero `.dart` files in target scope).
- [ ] **[NOK] Pre-Delete Audit**: Verify 0 remaining imports from `backend_v2.services.ingress.pdf_chat_extractor` and 100% green `uv run python scripts/backend_audit_loop.py backend_v2/services/ingress/ --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/services/document_extraction.py --test --ast-strict`.
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Verify all 25 baseline unit tests pass across the modularized test suites (`[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_bubble_geometry.py]`, `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_table_and_card_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_turn_assembly_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_pdf_extractor_facade.py]`) with `>= 96%` line coverage.
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
    - Enforce complete PEP 257 docstrings with explicit `Args:`, `Returns:`, and `Raises:` (`AppException` with `ErrorCodes.VALIDATION_FAILED`) across `[NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]`, `[NEW] @[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py]`, `[NEW] @[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py]`, and `[NEW] @[backend_v2/services/ingress/pdf_extractor/__init__.py]`.
3. - [ ] **Item 9 (Zero Inline Imports)**:
    - Promote the inline import of `PdfChatExtractorService` inside `DocumentExtractionService._extract_pdf_sync` (`@[backend_v2/services/document_extraction.py#L93-L156]`) to a module top-level import in `@[backend_v2/services/document_extraction.py]`.
4. - [ ] **Item 10 (ISTQB Negative Partition Expansion to >= 98% Line Coverage)**:
    - Add negative and boundary tests in `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_bubble_geometry.py]`, `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_table_and_card_stage.py]`, and `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_turn_assembly_stage.py]` covering the 12 baseline missed lines (`171, 209, 222-223, 242-244, 456-457, 479, 602, 618`).

---

### Final Epic Audit
- [ ] **[NOK] System 2 Red-Team Audit:** `/tier8-audit-plan @[docs/epic/tasks_pdf_chat_extractor/phase4_package_cutover_and_guardrails.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`
- [ ] **[NOK] Global Backend Completion Gate:** `uv run python scripts/backend_audit_loop.py backend_v2/ --test`

---

## Instructions for the Execution Agent
1. **Two-Epoch Firewall (`two_epoch_separation_mandate`)**: Execute Phases 1 through 4 (Epoch 1) as a **100% pure structural lift-and-shift** with zero behavioral mutations. Do NOT resolve the Epoch 2 12-Item Tech Debt Inventory until Phase 4 (Atomic Package Cutover and `QGR017` lockdown) is 100% complete and committed.
2. **Two-Phase Package Strangler Protocol (`strangler_fig_mandate`)**: Do NOT create `[NEW] @[backend_v2/services/ingress/pdf_extractor/__init__.py]` during Phases 1, 2, or 3 while `@[backend_v2/services/ingress/pdf_chat_extractor.py#L81-L537]` exists on disk. Create `[NEW] @[backend_v2/services/ingress/pdf_extractor/__init__.py]` and delete `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]` atomically in Phase 4 Step 2.
3. **500-Line Partitioning Gate**: Every extracted sub-module (`[NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]`, `[NEW] @[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py]`, `[NEW] @[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py]`) and the package facade (`[NEW] @[backend_v2/services/ingress/pdf_extractor/__init__.py]`) MUST remain strictly below 250 lines (and `< 150` lines for `__init__.py`).
4. **Atomic Checkpoints**: Run `uv run python scripts/backend_audit_loop.py <target> --test --ast-strict` after every step and perform an atomic `git commit` before advancing to the next step.

---

## Requirements Traceability Matrix

| Requirement ID | Architectural Requirement Description | Phase & Step Mapping | Verification Gate |
| :--- | :--- | :--- | :--- |
| `REQ-PCE-01` | Relocate `PdfCellCoordinatesDTO`, `PdfTextBlockDTO`, `RawTurnDTO`, and `PdfBlockSignatureDTO` to `@[backend_v2/models/dtos/ingress.py#L77-L92]` with PEP 593 `Annotated` typing | Phase 1, Step 1 | `backend_audit_loop.py backend_v2/models/dtos/ingress.py --test --ast-strict` |
| `REQ-PCE-02` | Extract vector bubble geometry, table bounding-box extraction, and conversation PDF detection into `[NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]` | Phase 1, Step 2 | `backend_audit_loop.py backend_v2/services/ingress/pdf_extractor/bubble_geometry.py --test --ast-strict` |
| `REQ-PCE-03` | Re-export DTOs and delegate bubble geometry methods in `@[backend_v2/services/ingress/pdf_chat_extractor.py#L81-L537]` | Phase 1, Step 3 | `backend_audit_loop.py backend_v2/services/ingress/pdf_chat_extractor.py --test --ast-strict` |
| `REQ-PCE-04` | Extract table text block filtering, Markdown table reconstruction, and attachment card detection into `[NEW] @[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py]` | Phase 2, Step 1 | `backend_audit_loop.py backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py --test --ast-strict` |
| `REQ-PCE-05` | Delegate table and attachment card stage methods in `@[backend_v2/services/ingress/pdf_chat_extractor.py#L81-L537]` | Phase 2, Step 2 | `backend_audit_loop.py backend_v2/services/ingress/pdf_chat_extractor.py --test --ast-strict` |
| `REQ-PCE-06` | Extract truncation detection, visual block ordering, and multi-turn conversation assembly into `[NEW] @[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py]` | Phase 3, Step 1 | `backend_audit_loop.py backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py --test --ast-strict` |
| `REQ-PCE-07` | Delegate `_check_truncation`, `_sort_blocks_visual_order`, and `extract_conversation` in `@[backend_v2/services/ingress/pdf_chat_extractor.py#L81-L537]` | Phase 3, Step 2 | `backend_audit_loop.py backend_v2/services/ingress/pdf_chat_extractor.py --test --ast-strict` |
| `REQ-PCE-08` | Split `@[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]` into 4 modular test suites under `backend_v2/tests/unit/services/ingress/pdf_extractor/` | Phase 4, Step 1 | `pytest backend_v2/tests/unit/services/ingress/pdf_extractor/` |
| `REQ-PCE-09` | Atomically cut over `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]` to `[NEW] @[backend_v2/services/ingress/pdf_extractor/__init__.py]` and rewire all 1-hop consumer imports | Phase 4, Step 2 | `backend_audit_loop.py backend_v2/services/ingress/pdf_extractor/__init__.py --test --ast-strict` |
| `REQ-PCE-10` | Ban `backend_v2.services.ingress.pdf_chat_extractor` in `@[scripts/_ast_guardrails.py#L1865-L1910]` and `@[scripts/_ast_guardrails.py#L1912-L2011]` under `QGR017` and update `@[.agents/rules/04_directory_reference.md]` | Phase 4, Step 3 | `backend_audit_loop.py scripts/_ast_guardrails.py --test --ast-strict` |

---

# Session Handover Context

## Achieved
- Completed Tier 3 Pre-Flight Baseline (`[BASELINE]`): 25/25 unit tests passing in `@[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]` with **96% line coverage** (311 statements, 12 missed) and 10/10 Universal Quality Gate stages passing.
- Completed Phase 1 (`@[docs/epic/tasks_pdf_chat_extractor/phase1_dtos_and_geometry_extraction.md]`):
  - Relocated `PdfCellCoordinatesDTO`, `PdfTextBlockDTO`, `RawTurnDTO`, and `PdfBlockSignatureDTO` to `@[backend_v2/models/dtos/ingress.py#L77-L92]` with `ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated` fields, and added 8 unit tests in `@[backend_v2/tests/unit/models/dtos/test_ingress.py#L111-L119]` (16/16 passing, 100% coverage).
  - Extracted `dlq_log_extraction_error`, `is_user_bubble_drawing`, `get_page_table_rects`, `is_conversation_pdf`, and `extract_page_user_bubbles` into `[NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]`.
  - Wired explicit DTO re-exports (`Symbol as Symbol`) and bubble geometry proxy delegations in `@[backend_v2/services/ingress/pdf_chat_extractor.py#L81-L537]` (25/25 unit tests passing, 10/10 Universal Quality Gate stages passing).

## Learned
- All 4 inline DTOs (`PdfCellCoordinatesDTO`, `PdfTextBlockDTO`, `RawTurnDTO`, `PdfBlockSignatureDTO`) relocate cleanly to `@[backend_v2/models/dtos/ingress.py#L77-L92]` in Phase 1 while preserving re-export parity via `from ... import Symbol as Symbol` in `pdf_chat_extractor.py`.
- `_CANVAS_MAX_SIZE_RATIO` is exported from `[NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]` and imported by `_reconstruct_tables_as_markdown` for full-page container table filtering.

## Resume Command
`/tier8-audit-plan @[docs/epic/tasks_pdf_chat_extractor/phase1_dtos_and_geometry_extraction.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`

## Remaining
- Audit Phase 1 via `/tier8-audit-plan @[docs/epic/tasks_pdf_chat_extractor/phase1_dtos_and_geometry_extraction.md] @[docs/epic/pdf_chat_extractor_decomposition_tracker.md]`.
- Execute Phase 2 through Phase 4 (`Epoch 1: Strangler Fig Structural Decomposition & Atomic Package Cutover`).
- Execute Epoch 2 (`Tier 2 Per-File Deterministic Hardening & Test Expansion`).
- Synchronize KIs and architecture documentation via `/tier7-describe-architecture`.
