# Task Tracker: Unified Multi-Model Ingress Architecture

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_chat_ingress_and_provenance_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_cartesian_variance_and_authenticity.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[c:\Users\risto\.gemini\antigravity-ide\brain\271a97a9-62b3-4af4-9984-4b89d5a94d46\implementation_plan.md]

## Pre-Flight Checklist (<constraint> tags)
- [x] Constraint Step 1: Fix all unparenthesized exception tuples, update method signatures, eradicate silent except passes, and clean up 1-hop caller fallback chains.
- [x] Constraint Step 2: Enforce strict GitHub-Flavored Markdown pipe tables for tab-separated data grids with code fence isolation, prior to whitespace collapse.
- [ ] Constraint Step 3: Enforce relative geometry ratios, visual topological block sorting, table cell matrix fallback defense, shaded cell discrimination, and table block suppression.
- [ ] Constraint Step 4: Provide positive, boundary, and negative tests for table normalization, code fence protection, visual reading order, short prompts, shaded table cells, UI icon suppression, and red-team edge cases.
- [ ] Constraint Step 5: Synchronize Knowledge Items in knowledge/ to document the hardened multi-model ingress and cognitive baseline isolation.

## Execution Tasks

- [x] **Step 1: P0 PRE-FLIGHT: SYNTAX FIXES, SIGNATURE UPDATES & AST BOUNDS**
  - [x] Fix `except ValueError, AttributeError, TypeError:` in `pdf_chat_extractor.py` L80 and L82 to `except (ValueError, AttributeError, TypeError):` and add structured debug logging.
  - [x] Update `_is_user_bubble_drawing` signature in `pdf_chat_extractor.py` to accept `page_height: float` and update call sites (L105, L125).
  - [x] Define explicit module constants in `pdf_chat_extractor.py` (`_PRINT_MARGIN_VERTICAL_PT`, `_PAGE_ZERO_TITLE_MAX_Y0`, `_ATTACHMENT_BOX_DIM_PT`, `_ATTACHMENT_BOX_TOLERANCE_PT`).
  - [x] Fix `except ValidationError, ValueError:` in `chat_normalizer.py` (L165, L171) to `except (ValidationError, ValueError):`.
  - [x] Clean up `metadata = doc.metadata or {}` and chained `.get()` in `document_extraction.py#L64-L102`.
  - [x] Run regression test suite on `test_pdf_chat_extractor.py` and `test_chat_normalizer.py`.

- [x] **Step 2: CLIPBOARD TABLE NORMALIZATION & FLUFF STRIPPING**
  - [x] Implement `normalize_tables` in `chat_normalizer.py` with code fence tracking, newline sanitization, and pipe escaping.
  - [x] Integrate `normalize_tables` into `clean_turn_content` before whitespace collapsing.
  - [x] Expand `strip_known_ui_fluff` with UI buttons (`expand_more`, `expand_less`), feedback widgets, timestamps, sidebar paths, and attachment card normalization.

- [ ] **Step 3: PDF RELATIVE GEOMETRY, VISUAL SORTING & TABLE RECONSTRUCTION**
  - [ ] Define relative geometry constants in `pdf_chat_extractor.py`.
  - [ ] Refactor `_is_user_bubble_drawing` with relative geometry, short prompt support, centered widget rejection, and table rect shielding.
  - [ ] Implement table cell matrix fallback in `_get_page_table_rects`.
  - [ ] Decompose `extract_conversation` into sub-methods (`_sort_blocks_visual_order`, `_filter_table_text_blocks`, `_reconstruct_tables_as_markdown`, `_detect_attachment_cards`).
  - [ ] Integrate visual sorting, table suppression, table markdown, truncation detection, and UI button filtering into `extract_conversation`.

- [ ] **Step 4: UNIT TEST EXPANSION & ISTQB QUALITY GATE AUDIT**
  - [ ] Expand `test_chat_normalizer.py` with 8 unit tests covering tab tables, code fence preservation, fluff stripping, and boundary cases.
  - [ ] Expand `test_pdf_chat_extractor.py` with 11 unit tests covering visual sorting, borderless table defense, shaded cells, table markdown, and boundary cases.
  - [ ] Run `backend_audit_loop.py` on both services.

- [ ] **Step 5: KNOWLEDGE ITEM SYNCHRONIZATION & SSOT UPDATES**
  - [ ] Update `ki_chat_ingress_and_provenance_architecture.md` and `metadata.json`.
  - [ ] Update `ki_cartesian_variance_and_authenticity.md` and `metadata.json`.

## Session Handover Context
- **Achieved**: Verified baseline green test suite (37 tests passing). Initialized execution of Unified Multi-Model Ingress Architecture.
- **Learned**: None so far.
- **Remaining**: Steps 1 to 5.
