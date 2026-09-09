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
- [x] Constraint: `ConfigDict(strict=True, extra="forbid", frozen=True)` on all new DTOs in `models/dtos/ingress.py`.
- [x] Constraint: Dual geometric classifiers for PDF extraction (`Gemini Bubble Classifier` and `ChatGPT Wide Bubble Classifier`).
- [x] Constraint: Truncation Detection & Warning: Detect "Näytä lisää" / "Show more" overflow buttons in user bubbles; emit warning and raise `AppException(422)` with actionable prompt truncation guidance.
- [x] Constraint: Table/Drawing Overlap Defense via `page.find_tables()` to subordinate drawings inside tables to markdown tables.
- [x] Constraint: Cross-page bubble merging for contiguous blocks of identical role.
- [x] Constraint: Chrome print margin filtering (`y0 >= 36.0 pt`, `y1 <= page_height - 36.0 pt`) and coordinate span deduplication.
- [x] Constraint: Deterministic UI fluff stripping and Finnish + English fast-path regex vocabularies.
- [x] Constraint: Anchor-Based Slicing in `ChatParserService` using `ChatTurnAnchorsResponseDTO` and monotonic `str.find()`; Fail-Fast on anchor miss or out-of-order anchor.
- [x] Constraint: Single Source of Truth (SSOT) Invariant for user-only input: `LLMStrategy` passes canonical `inputs_unwrapped` into `hook_state.inputs.raw_inputs`; `detect_performative_patterns` strictly consumes `chat_log_user_only` from memory. Zero disk I/O fallbacks.
- [x] Constraint: Flutter `PdfExportGuideDialog` localized via `.arb` files; desktop pro-tool UX adherence in `OmniInputBox`.
- [x] Constraint: Seed data optimization: `input_modes: ["file", "paste"]` for `chat_log`, `product_text`, and `reflection_text`. Prompt Preservation Mandate: qualitative prompt texts in `ai_description` 100% preserved.

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

- [x] **Phase 5: Flutter UI Integration & Multi-Provider Ingress Guide**
  - [x] Step 5.1: Add localization keys in `client_app_v2/lib/l10n/app_fi.arb` and `app_en.arb`.
  - [x] Step 5.2: Create `PdfExportGuideDialog` in `client_app_v2/lib/shared/widgets/pdf_export_guide_dialog.dart`.
  - [x] Step 5.3: Update `OmniInputBox` in `client_app_v2/lib/shared/widgets/omni_input_box.dart` with help action and truncation warning banner.
  - [x] Step 5.4: Implement Flutter widget tests for `PdfExportGuideDialog` and `OmniInputBox`.
  - [x] Step 5.5: Run Flutter audit gate `flutter_audit_loop.py`.

- [x] **Phase 6: Seed Data Optimization for Multi-Model Support**
  - [x] Step 6.1: Update `expected_inputs` in `backend_v2/seed/seed_data.json` for `wf_9d68c573802341db` with dual input modes `["file", "paste"]`.
  - [x] Step 6.2: Run seeder dry-run and local reseed (`uv run python backend_v2/seed/run_seed.py local`).

- [x] **Phase 7: Knowledge Item Synchronization & Multi-Model Ingress Architecture**
  - [x] Step 7.1: Create Knowledge Item `ki_chat_ingress_and_provenance_architecture.md` and `metadata.json`.
  - [x] Step 7.2: Update `ki_cartesian_variance_and_authenticity.md` with user-only word count and jargon density rules.
  - [x] Step 7.3: Update `.agents/rules/04_directory_reference.md` with new ingress services.

- [x] **Phase 8: Full Suite Audit & Regression Testing**
  - [x] Step 8.1: Run `scripts/run_e2e_variance_test.py` with authentic dataset `docs/jwdatat`.
  - [x] Step 8.2: Run global backend and frontend audit loops (`backend_audit_loop.py` and `flutter_audit_loop.py`).
  - [x] Step 8.3: Instruct atomic commit and route to `/tier8-audit-plan`.

## Session Handover Context
- **Achieved**: Completed 100% of the Multi-Channel Ingress Architecture & UI PDF Export Guide plan across all 8 phases:
  1. Phase 1 (Ingress DTOs & User-Only Sourcing SSOT) - Commit `4c3a4441`
  2. Phase 2 (PDF Geometry & Vector Speech Bubble Extractor) - Commit `b5a73275`
  3. Phase 3 (Text & Clipboard Ingress with Fluff Stripping + Monotonic Anchor Slicing) - Commit `377cbc40`
  4. Phase 4 (MultiChannelIngressService Dispatcher & InputProcessingHook Delegation) - Commit `6ee5fec9`
  5. Phase 5 (Flutter UI Integration: PdfExportGuideDialog & OmniInputBox Truncation Banner) - Commit `34cb7199`
  6. Phase 6 (Seed Data Optimization: Dual Mode ["file", "paste"] & Prompt Preservation) - Commit `25f28a76`
  7. Phase 7 (Knowledge Item Synchronization & Directory Reference) - Commit `645cde2a`
  8. Phase 8 (E2E Variance & Live Dataset Regression Testing):
     - Executed against real multi-page evaluation files `docs/jwdatat` (`keskusteluhistoria.pdf`, `lopputuote.pdf`, `reflektiodokumentti.pdf`).
     - Live execution `exe_627dc0e8dc294eaf` succeeded with status `PASSED`, proving end-to-end vector extraction, user-turn segregation (`input_chat_log_user_only.md` 2,404 bytes), and synthesis report generation (`report.pdf` 195 KB).
     - Enhanced `ChatParserService` with whitespace-resilient verbatim anchor span resolution (`_find_anchor_span`) to transparently match Unicode space variants (`\u2002`, `\u00a0`, etc.).
     - Enhanced `ExecutionInputsDTO` with `_coerce_raw_inputs_dict` validator to safely encapsulate non-dict inputs.
     - Hardened PyMuPDF table overlap defense against empty cell collections in `PdfChatExtractorService._get_page_table_rects`.
     - Quality gates passed: `backend_audit_loop.py` passed (94.28% global test coverage), `flutter_audit_loop.py` passed (0 issues), and all Flutter widget tests passed (5/5).
- **Remaining**: All implementation plan tasks are 100% complete. Ready for Plan Audit via `/tier8-audit-plan`.
- **Recommended Command**:
  ```text
  /tier8-audit-plan @[C:\Users\risto\.gemini\antigravity-ide\brain\3e5c45b7-ed7b-458e-bbd6-68a913397047\implementation_plan.md]
  ```
