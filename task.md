# Task Tracker: Multi-Channel Ingress Architecture & UI PDF Export Guide

<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_cartesian_variance_and_authenticity.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[C:\Users\risto\.gemini\antigravity-ide\brain\3e5c45b7-ed7b-458e-bbd6-68a913397047\implementation_plan.md]

## Pre-Flight Checklist (<constraint> tags)
- [ ] Constraint: `ConfigDict(strict=True, extra="forbid", frozen=True)` on all new DTOs in `models/dtos/ingress.py`.
- [ ] Constraint: Dual geometric classifiers for PDF extraction (`Gemini Bubble Classifier` and `ChatGPT Wide Bubble Classifier`).
- [ ] Constraint: Truncation Detection & Warning: Detect "Näytä lisää" / "Show more" overflow buttons in user bubbles; emit warning and raise `AppException(422)` with actionable prompt truncation guidance.
- [ ] Constraint: Table/Drawing Overlap Defense via `page.find_tables()` to subordinate drawings inside tables to markdown tables.
- [ ] Constraint: Cross-page bubble merging for contiguous blocks of identical role.
- [ ] Constraint: Chrome print margin filtering (`y0 >= 36.0 pt`, `y1 <= page_height - 36.0 pt`) and coordinate span deduplication.
- [ ] Constraint: Deterministic UI fluff stripping and Finnish + English fast-path regex vocabularies.
- [ ] Constraint: Anchor-Based Slicing in `ChatParserService` using `ChatTurnAnchorsResponseDTO` and monotonic `str.find()`; Fail-Fast on anchor miss or out-of-order anchor.
- [ ] Constraint: Single Source of Truth (SSOT) Invariant for user-only input: `LLMStrategy` passes canonical `inputs_unwrapped` into `hook_state.inputs.raw_inputs`; `detect_performative_patterns` strictly consumes `chat_log_user_only` from memory. Zero disk I/O fallbacks.
- [ ] Constraint: Flutter `PdfExportGuideDialog` localized via `.arb` files; desktop pro-tool UX adherence in `OmniInputBox`.
- [ ] Constraint: Seed data optimization: `input_modes: ["file", "paste"]` for `chat_log`, `product_text`, and `reflection_text`. Prompt Preservation Mandate: qualitative prompt texts in `ai_description` 100% preserved.

## Execution Tasks

- [x] **Phase 1: Pre-Implementation Cleanups, Ingress DTOs & User-Only Sourcing SSOT**
  - [x] Step 1.1: Fix syntax technical debt in `backend_v2/services/chat_normalizer.py` (`except (ValidationError, ValueError):`) and `backend_v2/services/chat_parser.py` (explicit `except AppException:`).
  - [x] Step 1.2: Generalize `get_text_to_scan()` in `backend_v2/models/domain/linguistics.py` to check any key ending with `_user_only`.
  - [x] Step 1.3: Create strict anchor DTOs `ChatTurnAnchorDTO` and `ChatTurnAnchorsResponseDTO` in `backend_v2/models/dtos/ingress.py`.
  - [x] Step 1.4: Update `LLMStrategy` in `backend_v2/services/orchestrator/strategies/llm.py` to pass canonical `inputs_unwrapped` to `hook_state.inputs.raw_inputs`.
  - [x] Step 1.5: Enforce zero-fallback user-only input verification in `backend_v2/hooks/linguistics.py`.
  - [x] Step 1.6: Add regression tests for linguistics user-only prioritization and missing user-only Fail-Fast in `backend_v2/tests/unit/hooks/test_linguistics.py`.
  - [x] Step 1.7: Run quality gate `backend_audit_loop.py` on Phase 1 targets.

- [x] **Phase 2: PDF Geometry & Vector Bubble Extraction Service**
  - [x] Step 2.1: Implement `PdfChatExtractorService` in `backend_v2/services/ingress/pdf_chat_extractor.py` with dual classifiers, margin filtering, span deduplication, truncation detection, table overlap defense, cross-page merging, and markdown table reconstruction.
  - [x] Step 2.2: Wire `PdfChatExtractorService` into `_extract_pdf_sync` in `backend_v2/services/document_extraction.py`.
  - [x] Step 2.3: Implement comprehensive unit and golden master tests in `backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py`.
  - [x] Step 2.4: Update `backend_v2/tests/unit/test_document_extraction.py`.
  - [x] Step 2.5: Run quality gate `backend_audit_loop.py` on Phase 2 targets.

- [x] **Phase 3: Text & Clipboard Ingress (Fluff Stripping + Anchor Slicing)**
  - [x] Step 3.1: Implement `strip_known_ui_fluff` and clean Fi/En fast-path regex in `backend_v2/services/chat_normalizer.py`.
  - [x] Step 3.2: Implement Anchor-Based Slicing in `backend_v2/services/chat_parser.py` with monotonic `str.find()` and Fail-Fast on missing/out-of-order anchors.
  - [x] Step 3.3: Expand unit tests in `backend_v2/tests/unit/services/test_chat_normalizer.py` and `test_chat_parser.py`.
  - [x] Step 3.4: Run quality gate `backend_audit_loop.py` on Phase 3 targets.

- [x] **Phase 4: Multi-Channel Ingress Service & Pipeline Delegation**
  - [x] Step 4.1: Implement `MultiChannelIngressService` in `backend_v2/services/ingress/multi_channel_ingress_service.py`.
  - [x] Step 4.2: Delegate chat parsing in `backend_v2/hooks/input_processing.py` to `MultiChannelIngressService` while preserving NLP pipeline.
  - [x] Step 4.3: Add unit tests in `backend_v2/tests/unit/services/ingress/test_multi_channel_ingress_service.py`.
  - [x] Step 4.4: Run quality gate `backend_audit_loop.py` on Phase 4 targets.

- [ ] **Phase 5: Flutter UI Integration & Multi-Provider Ingress Guide**
  - [ ] Step 5.1: Add localization keys in `client_app_v2/lib/l10n/app_fi.arb` and `app_en.arb`.
  - [ ] Step 5.2: Create `PdfExportGuideDialog` in `client_app_v2/lib/shared/widgets/pdf_export_guide_dialog.dart`.
  - [ ] Step 5.3: Update `OmniInputBox` in `client_app_v2/lib/shared/widgets/omni_input_box.dart` with help action and truncation warning banner.
  - [ ] Step 5.4: Implement Flutter widget tests for `PdfExportGuideDialog` and `OmniInputBox`.
  - [ ] Step 5.5: Run Flutter audit gate `flutter_audit_loop.py`.

- [ ] **Phase 6: Seed Data Optimization for Multi-Model Support**
  - [ ] Step 6.1: Update `expected_inputs` in `backend_v2/seed/seed_data.json` for `wf_9d68c573802341db` with dual input modes `["file", "paste"]`.
  - [ ] Step 6.2: Run seeder dry-run and local reseed (`uv run python backend_v2/seed/run_seed.py local`).

- [ ] **Phase 7: Knowledge Item Synchronization & Multi-Model Ingress Architecture**
  - [ ] Step 7.1: Create Knowledge Item `ki_chat_ingress_and_provenance_architecture.md` and `metadata.json`.
  - [ ] Step 7.2: Update `ki_cartesian_variance_and_authenticity.md` with user-only word count and jargon density rules.
  - [ ] Step 7.3: Update `.agents/rules/04_directory_reference.md` with new ingress services.

- [ ] **Phase 8: Full Suite Audit & Regression Testing**
  - [ ] Step 8.1: Run `scripts/run_e2e_variance_test.py`.
  - [ ] Step 8.2: Run global backend and frontend audit loops.
  - [ ] Step 8.3: Instruct atomic commit and route to `/tier8-audit-plan`.

## Session Handover Context
- **Achieved**: Initialized execution of Multi-Channel Ingress plan. Completed pre-flight verification and codebase scan.
- **Learned**: The system enforces pure in-memory SSOT for `chat_log_user_only`. All planned ingress modules (`ingress.py`, `pdf_chat_extractor.py`, `multi_channel_ingress_service.py`) are confirmed absent and ready for implementation.
- **Remaining**: Phase 1 through Phase 8.
- **Resume Command**:
  ```text
  /tier2-execute @[C:\Users\risto\.gemini\antigravity-ide\brain\3e5c45b7-ed7b-458e-bbd6-68a913397047\implementation_plan.md]
  ```
