<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_chat_ingress_and_provenance_architecture.md]</knowledge_item>
</required_context_rules>

# Phase 3: Turn Segmentation, Visual Ordering & Truncation Stage Extraction (`phase3_turn_assembly_stage_extraction.md`)

## 1. Objective
Execute Epoch 1 Phase 1C of the `PdfChatExtractorService` decomposition:
1. Extract truncation guard detection, visual reading-order block sorting, header/footer/orphan filtering, and multi-turn conversation assembly (`check_truncation`, `sort_blocks_visual_order`, `extract_conversation_from_doc`) into `[NEW] @[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py]`.
2. Delegate `PdfChatExtractorService._check_truncation` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L299-L340]`), `PdfChatExtractorService._sort_blocks_visual_order` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L342-L357]`), and `PdfChatExtractorService.extract_conversation` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L501-L682]`) to `[NEW] @[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py]`, reducing `@[backend_v2/services/ingress/pdf_chat_extractor.py#L113-L682]` to a `< 150`-line transitional proxy.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py]` | Turn assembly functions: `check_truncation`, `sort_blocks_visual_order`, and `extract_conversation_from_doc` |
| `[MODIFY]` | `[MODIFY]` `@[backend_v2/services/ingress/pdf_chat_extractor.py#L113-L682]` | Delegate `_check_truncation`, `_sort_blocks_visual_order`, and `extract_conversation` to `[NEW] @[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py]` |
| `[CONTEXT]` | `@[docs/epic/tasks_pdf_chat_extractor/symbol_migration_map.md]` | Canonical symbol and stage migration reference |
| `[CONTEXT]` | `@[backend_v2/models/dtos/ingress.py#L51-L68]` | Canonical ingress DTO definitions |
| `[CONTEXT]` | `[NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]` | Leaf bubble geometry stage |
| `[CONTEXT]` | `[NEW] @[backend_v2/services/ingress/pdf_extractor/table_and_card_stage.py]` | Leaf table and attachment card stage |
| `[CONTEXT]` | `@[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]` | Existing 25-test unit suite verifying 100% behavioral parity |

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Create backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py">
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/services/ingress/pdf_extractor/__init__.py in Phase 3 while backend_v2/services/ingress/pdf_chat_extractor.py still exists on disk.</constraint>
    <action>Create `[NEW] @[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py]` containing the turn assembly constants and functions relocated verbatim from `@[backend_v2/services/ingress/pdf_chat_extractor.py#L113-L682]`:
      1. Relocate `_ORPHAN_TOKEN_MAX_WIDTH`, `_ORPHAN_TOKEN_MAX_CHARS`, `_PRINT_MARGIN_VERTICAL_PT`, `_PAGE_ZERO_TITLE_MAX_Y0`, and `_TRUNCATION_INDICATORS`.
      2. Relocate `check_truncation(page: fitz.Page, page_number: int) -> None` from `@[backend_v2/services/ingress/pdf_chat_extractor.py#L299-L340]`.
      3. Relocate `sort_blocks_visual_order(blocks: list[PdfTextBlockDTO]) -> list[PdfTextBlockDTO]` from `@[backend_v2/services/ingress/pdf_chat_extractor.py#L342-L357]`.
      4. Relocate `extract_conversation_from_doc(doc: fitz.Document) -> list[ChatTurnAnchorDTO]` from `@[backend_v2/services/ingress/pdf_chat_extractor.py#L501-L682]`.
      5. Declare `__all__` at the top of `[NEW] @[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py]`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py --test --ast-strict`.</verification>
  </step>

  <step id="2" name="Wire Turn Assembly Proxy Delegations in pdf_chat_extractor.py">
    <constraint invariant="two_epoch_separation_mandate">Maintain 100% identical method signatures, exception messages, and return values on PdfChatExtractorService during Epoch 1.</constraint>
    <action>Modify `@[backend_v2/services/ingress/pdf_chat_extractor.py#L113-L682]`:
      1. Import `check_truncation`, `extract_conversation_from_doc`, and `sort_blocks_visual_order` from `[NEW] @[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py]`.
      2. Delegate `_check_truncation` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L299-L340]`), `_sort_blocks_visual_order` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L342-L357]`), and `extract_conversation` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L501-L682]`) to `[NEW] @[backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py]`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/ingress/pdf_chat_extractor.py backend_v2/services/ingress/pdf_extractor/turn_assembly_stage.py --test --ast-strict`.</verification>
  </step>
</execution_protocol>
```
