<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_chat_ingress_and_provenance_architecture.md]</knowledge_item>
</required_context_rules>

# Phase 2: Table Markdown & Attachment Card Stage Extraction (`phase2_table_and_card_stage_extraction.md`)

## 1. Objective
Execute Epoch 1 Phase 1B of the `PdfChatExtractorService` decomposition:
1. Extract leaf table text block filtering, Markdown table reconstruction, and Gemini attachment card detection functions (`filter_table_text_blocks`, `reconstruct_tables_as_markdown`, `detect_attachment_cards`) into `[NEW] @[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py]`.
2. Delegate `PdfChatExtractorService._filter_table_text_blocks` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L359-L382]`), `PdfChatExtractorService._reconstruct_tables_as_markdown` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L384-L459]`), and `PdfChatExtractorService._detect_attachment_cards` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L461-L499]`) to `[NEW] @[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py]` | Leaf table and attachment card stage functions: `filter_table_text_blocks`, `reconstruct_tables_as_markdown`, and `detect_attachment_cards` |
| `[MODIFY]` | `[MODIFY]` `@[backend_v2/services/ingress/pdf_chat_extractor.py#L113-L682]` | Delegate `_filter_table_text_blocks`, `_reconstruct_tables_as_markdown`, and `_detect_attachment_cards` to `[NEW] @[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py]` |
| `[CONTEXT]` | `@[docs/epic/tasks_pdf_chat_extractor/symbol_migration_map.md]` | Canonical symbol and stage migration reference |
| `[CONTEXT]` | `@[backend_v2/models/dtos/ingress.py#L51-L68]` | Canonical ingress DTO definitions |
| `[CONTEXT]` | `[NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]` | Leaf bubble geometry stage |
| `[CONTEXT]` | `@[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]` | Existing 25-test unit suite verifying 100% behavioral parity |

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Create backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py">
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/services/ingress/pdf_extractor/__init__.py in Phase 2 while backend_v2/services/ingress/pdf_chat_extractor.py still exists on disk.</constraint>
    <action>Create `[NEW] @[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py]` containing the attachment card geometry constants and pure stage functions relocated verbatim from `@[backend_v2/services/ingress/pdf_chat_extractor.py#L113-L682]`:
      1. Relocate `_ATTACHMENT_BOX_DIM_PT: float = 36.0` and `_ATTACHMENT_BOX_TOLERANCE_PT: float = 4.0`.
      2. Relocate `filter_table_text_blocks(blocks: list[PdfTextBlockDTO], table_rects: list[fitz.Rect]) -> list[PdfTextBlockDTO]` from `@[backend_v2/services/ingress/pdf_chat_extractor.py#L359-L382]`.
      3. Relocate `reconstruct_tables_as_markdown(page: fitz.Page) -> list[tuple[fitz.Rect, str]]` from `@[backend_v2/services/ingress/pdf_chat_extractor.py#L384-L459]`.
      4. Relocate `detect_attachment_cards(page: fitz.Page, blocks: list[PdfTextBlockDTO]) -> list[tuple[fitz.Rect, str]]` from `@[backend_v2/services/ingress/pdf_chat_extractor.py#L461-L499]`.
      5. Declare `__all__` at the top of `[NEW] @[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py]`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py --test --ast-strict`.</verification>
  </step>

  <step id="2" name="Wire Table and Attachment Card Proxy Delegations in pdf_chat_extractor.py">
    <constraint invariant="two_epoch_separation_mandate">Maintain 100% identical method signatures and return values on PdfChatExtractorService during Epoch 1.</constraint>
    <action>Modify `@[backend_v2/services/ingress/pdf_chat_extractor.py#L113-L682]`:
      1. Import `detect_attachment_cards`, `filter_table_text_blocks`, and `reconstruct_tables_as_markdown` from `[NEW] @[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py]`.
      2. Delegate `_filter_table_text_blocks` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L359-L382]`), `_reconstruct_tables_as_markdown` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L384-L459]`), and `_detect_attachment_cards` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L461-L499]`) to `[NEW] @[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py]`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/ingress/pdf_chat_extractor.py backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py --test --ast-strict`.</verification>
  </step>
</execution_protocol>
```
