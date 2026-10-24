<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_chat_ingress_and_provenance_architecture.md]</knowledge_item>
</required_context_rules>

# Phase 4: Modular Test Suite Split, Atomic Package Cutover & AST Guardrail Lock (`phase4_package_cutover_and_guardrails.md`)

## 1. Objective
Execute Epoch 1 Phase 1D (Final Package Cutover & Guardrail Lockdown) of the `PdfChatExtractorService` decomposition:
1. Split `[DELETE] @[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]` into 4 dedicated modular test suites under `backend_v2/tests/unit/services/ingress/pdf_extractor/` (`[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_bubble_geometry.py]`, `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_table_and_card_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_turn_assembly_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_pdf_extractor_facade.py]`) and delete `[DELETE] @[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]`.
2. Atomically create `[NEW] @[backend_v2/services/ingress/pdf_extractor/__init__.py]` (`< 150` lines) with explicit `__all__` and redundant aliases (`Symbol as Symbol`), delete `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]`, synchronize `@[backend_v2/services/ingress/__init__.py]`, and rewire all 1-hop consumers and test patch targets (`@[backend_v2/services/ingress/multi_channel_ingress_service.py#L27-L197]`, `@[backend_v2/services/document_extraction.py#L93-L156]`, `@[scripts/run_e2e_variance_test.py#L277-L411]`, `@[backend_v2/tests/unit/test_document_extraction.py#L145-L175]`, `@[backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py#L1066-L1127]`).
3. Lock the retired `backend_v2.services.ingress.pdf_chat_extractor` import path in `@[scripts/_ast_guardrails.py#L1865-L1910]` (`visit_Import`) and `@[scripts/_ast_guardrails.py#L1912-L2011]` (`visit_ImportFrom`) under `QGR017`, and synchronize `@[.agents/rules/04_directory_reference.md]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_bubble_geometry.py]` | Dedicated unit test suite for `bubble_geometry.py` |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_table_and_card_stage.py]` | Dedicated unit test suite for `table_and_card_stage.py` |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_turn_assembly_stage.py]` | Dedicated unit test suite for `turn_assembly_stage.py` |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_pdf_extractor_facade.py]` | Dedicated unit test suite for `PdfChatExtractorService` facade |
| `[DELETE]` | `[DELETE] @[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]` | Delete monolithic unit test file after 100% test migration |
| `[NEW]` | `[NEW] @[backend_v2/services/ingress/pdf_extractor/__init__.py]` | Canonical package facade (`< 150` lines) defining `PdfChatExtractorService` and explicit `__all__` |
| `[DELETE]` | `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]` | Delete transitional proxy module atomically with `__init__.py` creation |
| `[MODIFY]` | `[MODIFY]` `@[backend_v2/services/ingress/__init__.py]` | Re-export `PdfChatExtractorService as PdfChatExtractorService` |
| `[MODIFY]` | `[MODIFY]` `@[backend_v2/services/ingress/multi_channel_ingress_service.py#L27-L197]` | Rewire import to `backend_v2.services.ingress.pdf_extractor` |
| `[MODIFY]` | `[MODIFY]` `@[backend_v2/services/document_extraction.py#L93-L156]` | Promote and rewire `PdfChatExtractorService` import to `backend_v2.services.ingress.pdf_extractor` |
| `[MODIFY]` | `[MODIFY]` `@[scripts/run_e2e_variance_test.py#L277-L411]` | Rewire import to `backend_v2.services.ingress.pdf_extractor` |
| `[MODIFY]` | `[MODIFY]` `@[backend_v2/tests/unit/test_document_extraction.py#L145-L175]` | Update mock patch target for `PdfChatExtractorService` |
| `[MODIFY]` | `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py#L1066-L1127]` | Update mock patch targets for `PdfChatExtractorService` |
| `[MODIFY]` | `[MODIFY]` `@[scripts/_ast_guardrails.py#L1865-L1910]` | Ban `import backend_v2.services.ingress.pdf_chat_extractor` under `QGR017` |
| `[MODIFY]` | `[MODIFY]` `@[scripts/_ast_guardrails.py#L1912-L2011]` | Ban `from backend_v2.services.ingress.pdf_chat_extractor import ...` under `QGR017` |
| `[MODIFY]` | `[MODIFY]` `@[.agents/rules/04_directory_reference.md]` | Document `backend_v2/services/ingress/pdf_extractor/` subpackage |
| `[CONTEXT]` | `@[docs/epic/tasks_pdf_chat_extractor/symbol_migration_map.md]` | Canonical symbol and stage migration reference |
| `[CONTEXT]` | `@[backend_v2/models/dtos/ingress.py#L51-L68]` | Canonical ingress DTO definitions |
| `[CONTEXT]` | `[NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]` | Leaf bubble geometry stage |
| `[CONTEXT]` | `[NEW] @[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py]` | Leaf table and attachment card stage |
| `[CONTEXT]` | `[NEW] @[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py]` | Turn assembly stage |

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Split test_pdf_chat_extractor.py into Modular Sub-Module Test Suites">
    <constraint invariant="exhaustive_test_decomposition_mandate">Every unit test in test_pdf_chat_extractor.py MUST be migrated into a dedicated sub-module test file with zero lost assertions.</constraint>
    <action>Create `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_bubble_geometry.py]`, `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_table_and_card_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_turn_assembly_stage.py]`, and `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_pdf_extractor_facade.py]`, and delete `[DELETE] @[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]`:
      1. Migrate `TestConversationDetection` and bubble geometry helper tests into `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_bubble_geometry.py]`.
      2. Migrate table filtering, Markdown table reconstruction, and attachment card detection tests into `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_table_and_card_stage.py]`.
      3. Migrate `TestTurnSegmentation`, `TestHeaderFooterAndOrphanFiltering`, `TestTruncationGuard`, and `test_extract_conversation_edge_cases` into `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_turn_assembly_stage.py]`.
      4. Add facade delegation and re-export parity tests in `[NEW] @[backend_v2/tests/unit/services/ingress/pdf_extractor/test_pdf_extractor_facade.py]`.
      5. Delete `[DELETE] @[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/ingress/pdf_extractor/test_bubble_geometry.py backend_v2/tests/unit/services/ingress/pdf_extractor/test_table_and_card_stage.py backend_v2/tests/unit/services/ingress/pdf_extractor/test_turn_assembly_stage.py backend_v2/tests/unit/services/ingress/pdf_extractor/test_pdf_extractor_facade.py --test --ast-strict`.</verification>
  </step>

  <step id="2" name="Execute Atomic Package Cutover and Rewire 1-Hop Consumers">
    <constraint invariant="strangler_fig_mandate">Atomically create backend_v2/services/ingress/pdf_extractor/__init__.py (< 150 lines), delete backend_v2/services/ingress/pdf_chat_extractor.py, synchronize backend_v2/services/ingress/__init__.py, and rewire all 1-hop consumers.</constraint>
    <action>Execute the atomic package cutover:
      1. Create `[NEW] @[backend_v2/services/ingress/pdf_extractor/__init__.py]` (`< 150` lines) defining `PdfChatExtractorService` and explicit `__all__` with redundant alias imports (`Symbol as Symbol`).
      2. Delete `[DELETE] @[backend_v2/services/ingress/pdf_chat_extractor.py]`.
      3. Update `@[backend_v2/services/ingress/__init__.py]` to re-export `PdfChatExtractorService as PdfChatExtractorService`.
      4. Rewire 1-hop consumer imports and test patch targets in `@[backend_v2/services/ingress/multi_channel_ingress_service.py#L27-L197]`, `@[backend_v2/services/document_extraction.py#L93-L156]`, `@[scripts/run_e2e_variance_test.py#L277-L411]`, `@[backend_v2/tests/unit/test_document_extraction.py#L145-L175]`, and `@[backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py#L1066-L1127]`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/ingress/pdf_extractor/__init__.py backend_v2/services/ingress/__init__.py backend_v2/services/ingress/multi_channel_ingress_service.py backend_v2/services/document_extraction.py scripts/run_e2e_variance_test.py backend_v2/tests/unit/test_document_extraction.py backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py --test --ast-strict`.</verification>
  </step>

  <step id="3" name="Lock Retired Monolith Path in scripts/_ast_guardrails.py under QGR017 and Synchronize 04_directory_reference.md">
    <constraint invariant="qgr017_guardrail_lock">Register backend_v2.services.ingress.pdf_chat_extractor in visit_Import and visit_ImportFrom inside scripts/_ast_guardrails.py.</constraint>
    <action>Modify `@[scripts/_ast_guardrails.py#L1865-L1910]`, `@[scripts/_ast_guardrails.py#L1912-L2011]`, and `@[.agents/rules/04_directory_reference.md]`:
      1. Add `backend_v2.services.ingress.pdf_chat_extractor` to the retired monolith import bans in `@[scripts/_ast_guardrails.py#L1865-L1910]` (`visit_Import`) and `@[scripts/_ast_guardrails.py#L1912-L2011]` (`visit_ImportFrom`) under `QGR017`.
      2. Update `@[.agents/rules/04_directory_reference.md]` to list `backend_v2/services/ingress/pdf_extractor/`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py scripts/_ast_guardrails.py backend_v2/services/ingress/ --test --ast-strict`.</verification>
  </step>
</execution_protocol>
```
