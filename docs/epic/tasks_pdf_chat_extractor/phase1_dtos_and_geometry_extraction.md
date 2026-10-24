<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_chat_ingress_and_provenance_architecture.md]</knowledge_item>
</required_context_rules>

# Phase 1: Inline DTO Relocation & Bubble Geometry Stage Extraction (`phase1_dtos_and_geometry_extraction.md`)

## 1. Objective
Execute Epoch 1 Phase 1A (Bottom-Up Leaf-First Extraction) of the `PdfChatExtractorService` decomposition:
1. Relocate `PdfCellCoordinatesDTO` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L63-L71]`), `PdfTextBlockDTO` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L74-L85]`), `RawTurnDTO` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L88-L94]`), and `PdfBlockSignatureDTO` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L97-L107]`) into the canonical ingress DTO module `@[backend_v2/models/dtos/ingress.py#L51-L68]` with `ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated` fields (`strict_model_location` / `QGR029`).
2. Extract leaf bubble geometry and PDF vector inspection functions (`dlq_log_extraction_error`, `is_user_bubble_drawing`, `get_page_table_rects`, `is_conversation_pdf`, `extract_page_user_bubbles`) into `[NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]` without creating `[NEW] @[backend_v2/services/ingress/pdf_extractor/__init__.py]` (Two-Phase Package Strangler Protocol).
3. Re-export `PdfCellCoordinatesDTO`, `PdfTextBlockDTO`, `RawTurnDTO`, and `PdfBlockSignatureDTO` in `@[backend_v2/services/ingress/pdf_chat_extractor.py#L113-L682]` using explicit redundant aliases (`from ... import Symbol as Symbol`) and delegate `_dlq_log_extraction_error` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L175-L183]`), `_is_user_bubble_drawing` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L116-L173]`), `_get_page_table_rects` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L185-L248]`), `is_conversation_pdf` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L250-L272]`), and `_extract_page_user_bubbles` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L274-L297]`) to `[NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[MODIFY]` | `[MODIFY]` `@[backend_v2/models/dtos/ingress.py#L51-L68]` | Define relocated `PdfCellCoordinatesDTO`, `PdfTextBlockDTO`, `RawTurnDTO`, and `PdfBlockSignatureDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated` fields |
| `[MODIFY]` | `[MODIFY]` `@[backend_v2/tests/unit/models/dtos/test_ingress.py#L97-L108]` | Unit tests for strict validation, `extra="forbid"`, and `frozen=True` immutability of the 4 relocated DTOs |
| `[NEW]` | `[NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]` | Leaf geometry functions: `dlq_log_extraction_error`, `is_user_bubble_drawing`, `get_page_table_rects`, `is_conversation_pdf`, and `extract_page_user_bubbles` |
| `[MODIFY]` | `[MODIFY]` `@[backend_v2/services/ingress/pdf_chat_extractor.py#L113-L682]` | Re-export DTOs via `Symbol as Symbol` and delegate bubble geometry methods to `[NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]` |
| `[CONTEXT]` | `@[docs/epic/tasks_pdf_chat_extractor/symbol_migration_map.md]` | Canonical symbol and stage migration reference |
| `[CONTEXT]` | `@[backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py]` | Existing 25-test unit suite verifying 100% behavioral parity |

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Relocate PdfCellCoordinatesDTO, PdfTextBlockDTO, RawTurnDTO, and PdfBlockSignatureDTO to backend_v2/models/dtos/ingress.py">
    <constraint invariant="strict_model_location">All Pydantic V2 DTOs MUST reside in backend_v2/models/dtos/ingress.py; zero BaseModel subclasses are permitted inside backend_v2/services/.</constraint>
    <constraint invariant="pydantic_annotated_fields_mandate">All DTO fields MUST use PEP 593 Annotated[T, Field(description=...)] with ConfigDict(strict=True, extra="forbid", frozen=True).</constraint>
    <action>Modify `@[backend_v2/models/dtos/ingress.py#L51-L68]` and `@[backend_v2/tests/unit/models/dtos/test_ingress.py#L97-L108]`:
      1. Define `PdfCellCoordinatesDTO(V2CoreBase)`, `PdfTextBlockDTO(V2CoreBase)`, `RawTurnDTO(V2CoreBase)`, and `PdfBlockSignatureDTO(V2CoreBase)` in `@[backend_v2/models/dtos/ingress.py#L51-L68]` with `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated` field annotations.
      2. Export all 4 DTO classes in `@[backend_v2/models/dtos/ingress.py#L51-L68]`.
      3. Add unit tests in `@[backend_v2/tests/unit/models/dtos/test_ingress.py#L97-L108]` verifying instantiation, `extra="forbid"` rejection, and `frozen=True` hashability for all 4 DTOs.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/ingress.py backend_v2/tests/unit/models/dtos/test_ingress.py --test --ast-strict`.</verification>
  </step>

  <step id="2" name="Create backend_v2/services/ingress/pdf_extractor/bubble_geometry.py">
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/services/ingress/pdf_extractor/__init__.py in Phase 1 while backend_v2/services/ingress/pdf_chat_extractor.py still exists on disk.</constraint>
    <action>Create `[NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]` containing the bubble geometry constants and pure functions relocated verbatim from `@[backend_v2/services/ingress/pdf_chat_extractor.py#L113-L682]`:
      1. Relocate `_USER_BUBBLE_MIN_WIDTH_RATIO`, `_USER_BUBBLE_MIN_X0_RATIO`, `_USER_BUBBLE_MIN_X1_RATIO`, `_CANVAS_MAX_SIZE_RATIO`, `_SHORT_PROMPT_MIN_WIDTH`, and `type DrawingItemValue`.
      2. Relocate `dlq_log_extraction_error(stage: str, page_index: int, exc: Exception) -> None` from `@[backend_v2/services/ingress/pdf_chat_extractor.py#L175-L183]`.
      3. Relocate `is_user_bubble_drawing(drawing: Mapping[str, DrawingItemValue], page_width: float, page_height: float, table_rects: list[fitz.Rect] | None = None) -> fitz.Rect | None` from `@[backend_v2/services/ingress/pdf_chat_extractor.py#L116-L173]`.
      4. Relocate `get_page_table_rects(page: fitz.Page) -> list[fitz.Rect]` from `@[backend_v2/services/ingress/pdf_chat_extractor.py#L185-L248]`.
      5. Relocate `is_conversation_pdf(doc: fitz.Document) -> bool` from `@[backend_v2/services/ingress/pdf_chat_extractor.py#L250-L272]`.
      6. Relocate `extract_page_user_bubbles(page: fitz.Page) -> list[fitz.Rect]` from `@[backend_v2/services/ingress/pdf_chat_extractor.py#L274-L297]`.
      7. Declare `__all__` at the top of `[NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/ingress/pdf_extractor/bubble_geometry.py --test --ast-strict`.</verification>
  </step>

  <step id="3" name="Wire DTO Re-Exports and Bubble Geometry Proxy Delegations in pdf_chat_extractor.py">
    <constraint invariant="two_epoch_separation_mandate">Maintain 100% identical method signatures, exception messages, and return values on PdfChatExtractorService during Epoch 1.</constraint>
    <action>Modify `@[backend_v2/services/ingress/pdf_chat_extractor.py#L113-L682]`:
      1. Replace inline definitions of `PdfCellCoordinatesDTO` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L63-L71]`), `PdfTextBlockDTO` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L74-L85]`), `RawTurnDTO` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L88-L94]`), and `PdfBlockSignatureDTO` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L97-L107]`) with explicit redundant alias imports (`from backend_v2.models.dtos.ingress import ... as ...`).
      2. Delegate `_is_user_bubble_drawing` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L116-L173]`), `_dlq_log_extraction_error` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L175-L183]`), `_get_page_table_rects` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L185-L248]`), `is_conversation_pdf` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L250-L272]`), and `_extract_page_user_bubbles` (`@[backend_v2/services/ingress/pdf_chat_extractor.py#L274-L297]`) to `[NEW] @[backend_v2/services/ingress/pdf_extractor/bubble_geometry.py]`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/ingress/pdf_chat_extractor.py backend_v2/services/ingress/pdf_extractor/bubble_geometry.py --test --ast-strict`.</verification>
  </step>
</execution_protocol>
```
