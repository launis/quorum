# EPIC 120: SDUI Strictness Hardening — Eradicating Unstructured Presentation Fields

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
> The industry standard for Server-Driven UI (SDUI) in 2026 explicitly relies on treating UI entirely as polymorphic data contracts (Data-as-UI). Modern architectures demand that both backend orchestration and client rendering rely on strict Discriminated Unions (sealed classes in Dart / `@Field(discriminator='type')` in Pydantic) to map dynamic JSON to a Catalog/Registry pattern. The A2UI (Agentic UI) protocol and frameworks like Stac enforce "Demand-Driven Schemas", eliminating `List<dynamic>` dumping grounds in favor of strict, statically validated layout schemas that prevent schema drift. This Epic aligns Quorum with the 2026 SDUI standard by eliminating all remaining `dict[str, Any]` and `List<dynamic>` fields in the SDUI persistence and rendering layers.

## 1. Goal Description & Background (Objective & Problem Statement)

**Objective**: Eradicate all remaining unstructured SDUI data fields (`content_blocks: list[dict[str, Any]]`, `synthesis_blocks: list[dict[str, Any]]`) across `OutputProfile`, `OutputLayoutBlock`, `ReportLayoutDTO`, `RenderedSynthesisCache`, and their DTOs by replacing them with strict Pydantic V2 Discriminated Unions and Dart 3 Freezed sealed classes.

**Problem Statement**: While Epic 111 achieved "Dumb Painter" rendering and the `OutputLayoutBlock` model is already strictly typed, multiple fields in the SDUI persistence and caching layers remain unstructured:

1. **`OutputProfile.content_blocks: list[dict[str, Any]]`** — Profile-level SDUI content injection slot. Typed as `List<dynamic>` in Flutter. Completely bypasses Fail-Fast architecture.
2. **`EmbeddedOutputProfile.content_blocks: list[dict[str, Any]]`** — Identical field on the embedded variant.
3. **`OutputLayoutBlock.synthesis_blocks: list[dict[str, Any]] | None`** — Section-level synthesis output. Produced by the LLM synthesis engine but persisted untyped.
4. **`ReportLayoutDTO.synthesis_blocks: list[dict[str, Any]] | None`** — The consumer-facing SDUI payload for synthesis blocks, also untyped.
5. **`RenderedSynthesisCache.content_blocks: list[dict[str, Any]]`** (`@[c:\src\quorum\backend_v2\models\v2_core.py#L1540]`) — Cached global synthesis SDUI blocks. Also untyped.
6. **`RenderedSynthesisCache.section_syntheses: dict[str, list[dict[str, Any]]]`** (`@[c:\src\quorum\backend_v2\models\v2_core.py#L1543-L1544]`) — Cached per-layout synthesis blocks. Also untyped.

These fields represent the last `Any`/`dynamic` contamination in the entire SDUI pipeline. The `SynthesisOutputDTO.content_blocks` is already typed as `list[AnySduiBlock]`, proving the discriminated union pattern works. This Epic extends that pattern to all remaining fields.

> [!IMPORTANT]
> **Architectural Constraint: The `layouts: list[OutputLayoutBlock]` field is already a strictly typed Pydantic model** with Literal-typed `preset_view`, `text_delivery_mode`, and nested `SynthesisConfigDTO`. It MUST NOT be removed or replaced. The established pattern (per KI: `ki_dumb_painter_penalty_layout`) is to use `preset_view: "text_only"` for non-matrix content within `layouts`. Any future admin reordering capability builds ON TOP of the existing `layouts` architecture.

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)
- **`OutputProfile.content_blocks: list[dict[str, Any]]`** — Replaced with `content_blocks: list[AnySduiBlock]` using the existing `AnySduiBlock` Discriminated Union from `@[c:\src\quorum\backend_v2\models\view\sdui.py]`.
- **`EmbeddedOutputProfile.content_blocks: list[dict[str, Any]]`** — Same replacement as above.
- **`OutputLayoutBlock.synthesis_blocks: list[dict[str, Any]] | None`** — Replaced with `synthesis_blocks: list[AnySduiBlock] | None`. **CRITICAL**: The `| None` MUST be preserved (not collapsed to `list[AnySduiBlock] = []`) because `None` carries distinct semantics: "synthesis not yet executed" vs. `[]` meaning "synthesis executed but produced empty output". The Flutter renderer at `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart#L147]` explicitly gates on `synthesisBlocks != null`.
- **`ReportLayoutDTO.synthesis_blocks: list[dict[str, Any]] | None`** — Same as above, preserving `| None` semantics.
- **`RenderedSynthesisCache.content_blocks: list[dict[str, Any]]`** — Replaced with `content_blocks: list[AnySduiBlock]`.
- **`RenderedSynthesisCache.section_syntheses: dict[str, list[dict[str, Any]]]`** — Replaced with `section_syntheses: dict[str, list[AnySduiBlock]]`.
- **Flutter `List<dynamic> contentBlocks`** — In both `OutputProfile` and `EmbeddedOutputProfile` Freezed models, replaced with the shared `SduiBlockDTO` sealed class.
- **Flutter `List<Map<String, dynamic>>? synthesisBlocks`** — In `ReportLayoutDto`, replaced with `List<SduiBlockDTO>?` (preserving nullable semantics).
- **Unstructured Type Definitions**: After this Epic, ZERO instances of `dict[str, Any]` or `List<dynamic>` remain in any SDUI-related model.
- **Duck-typing remnants in `blueprint.py`**: All `hasattr()`, `isinstance(cb, dict)`, `c_block.get("id")`, and inline raw dict construction (`{"block_type": ..., "text": ...}`) MUST be replaced with typed model operations.

### Retained SSOT Invariants (What We Will RETAIN)
- **`layouts: list[OutputLayoutBlock]`** — The core structural rendering configuration remains exactly as-is. `OutputLayoutBlock` is NOT legacy — it is a Phase 9 strict Pydantic model with well-defined Literal types (`preset_view`, `text_delivery_mode`) and is the established mechanism for admin report ordering.
- **`ReportLayoutDTO` (Backend → Frontend SDUI Contract)** — The consumer-facing SDUI structure sent to the client remains structurally unchanged. Only the `synthesis_blocks` field type tightens from `list[dict] | None` to `list[AnySduiBlock] | None`.
- **`ReportDataDTO.layouts: list[ReportLayoutDTO]`** — Unchanged.
- **Dumb Painter UI**: The client-side Flutter rendering logic (`report_renderer_v2_widget.dart`) remains intact and oblivious to business logic.
- **Opaque Stripe IDs**: All blocks and profiles continue to use opaque `id` mapping.

### Legacy Support Ban (Zero Backward Compatibility)
- **Old Execution Traces**: There is ZERO requirement to support or render old execution traces that contain untyped `content_blocks` data as raw dicts. After re-seeding, old payloads must fail-fast. Do NOT write any Pydantic `@model_validator` fallbacks, migrations, or Python `try/except` chains to maintain backward compatibility.

### Compliance & Modernity Gates (Quorum 2026 Invariants)
- **Pydantic Strictness**: The `AnySduiBlock` Discriminated Union MUST use `Field(discriminator='block_type')` with `ConfigDict(strict=True, extra='forbid')` on each concrete block type.
- **Flutter Sealed Classes**: The Dart schema MUST use `@Freezed(unionKey: 'block_type')` with Dart 3 `switch` expressions. `fallbackUnion: 'unknown'` is strictly PROHIBITED.
- **Fail-Fast Boundary**: If any field receives an unrecognized block type, Pydantic/Freezed MUST instantly crash with a `ValidationError`.
- **Reuse AnySduiBlock SSOT**: The existing `AnySduiBlock` type alias in `models/view/sdui.py` is the Single Source of Truth. New consumers (including `v2_core.py` and `dtos/synthesis.py`) MUST import from `backend_v2.models.view.sdui`, not redefine it. Core domain MUST NEVER import from the DTO layer to avoid circular dependencies.

### Producer-Consumer Integration Check
- **Producer (Admin Studio / Database)**: Admin configures `OutputProfile.layouts` (ordered rendering blocks) and optionally `OutputProfile.content_blocks` (typed SDUI blocks). Saved to `seed_data.json` / `db_v2.json`.
- **Intermediary (Blueprint Generator)**: `blueprint.py` reads `profile.layouts` (already typed `OutputLayoutBlock`), generates `ReportLayoutDTO` instances. `content_blocks` are injected as typed `AnySduiBlock` objects into the synthesis/global_synthesis pipeline.
- **Consumer (Flutter Report Viewer)**: Blindly renders the `ReportLayoutDTO` exactly as before.

---

## 3. Phased Execution Plan (Implementation Strategy)

> [!WARNING]
> **Scope Boundary: Admin Studio Block Builder UI is OUT OF SCOPE.** Building a drag-and-drop block builder UI is a new feature that MUST NOT be mixed with structural refactoring. If desired, it should be a separate Epic (e.g., EPIC 121) that builds on top of the typed foundation this Epic establishes.

### Phase 1: Backend Model Strictness Hardening
- **Target**: `@[c:\src\quorum\backend_v2\models\v2_core.py]`
- **Import**: `from backend_v2.models.view.sdui import AnySduiBlock` (view layer → safe for Core; NEVER import from `dtos/synthesis.py` to avoid circular dependency).
- Replace `content_blocks: list[dict[str, Any]]` with `content_blocks: list[AnySduiBlock] = Field(default_factory=list)` in:
  - `OutputProfile` (`@[c:\src\quorum\backend_v2\models\v2_core.py#L1330]`)
  - `EmbeddedOutputProfile` (`@[c:\src\quorum\backend_v2\models\v2_core.py#L1373]`)
  - `RenderedSynthesisCache` (`@[c:\src\quorum\backend_v2\models\v2_core.py#L1540]`)
- Replace `synthesis_blocks: list[dict[str, Any]] | None` with `synthesis_blocks: list[AnySduiBlock] | None = Field(default=None)` in:
  - `OutputLayoutBlock` (`@[c:\src\quorum\backend_v2\models\v2_core.py#L1267]`) — **PRESERVE `| None` semantics**
  - `ReportLayoutDTO` (`@[c:\src\quorum\backend_v2\models\v2_core.py#L1067]`) — **PRESERVE `| None` semantics**
- Replace `section_syntheses: dict[str, list[dict[str, Any]]]` with `section_syntheses: dict[str, list[AnySduiBlock]]` in:
  - `RenderedSynthesisCache` (`@[c:\src\quorum\backend_v2\models\v2_core.py#L1543-L1544]`)
- **Target**: `@[c:\src\quorum\backend_v2\models\dtos\output_profile.py]`
- Update `OutputProfileCreateDTO.content_blocks`, `OutputProfileUpdateDTO.content_blocks`, and `OutputProfileResponseDTO.content_blocks` to `list[AnySduiBlock]`.
- Execute `uv run python scripts/backend_audit_loop.py backend_v2/ --test`.

### Phase 2: Frontend Freezed Sealed Class Synchronization
- **CRITICAL**: `SduiBlockDTO` MUST be defined in `shared/models/` (NOT inside `features/studio/`). Both `features/studio/` (`OutputProfile`, `OutputLayoutBlock`) and `features/execution/` (`ReportLayoutDto`) consume this type. Placing it inside a feature directory would create a cross-feature dependency, violating Flutter feature isolation.

> [!WARNING]
> **Flutter Sealed Class Parity Gap**: The Python `AnySduiBlock` includes **9 types** (`HeroInsightBlock`, `ParagraphBlock`, `BulletListBlock`, `AlertBlock`, `MarkdownBlock`, `SduiQuoteCard`, `SduiWarningCard`, `SduiNACard`, `SduiGridBlock`), but the current Flutter `SduiBlockDTO` only defines **5 types**. The 4 missing types (`quoteCard`, `warningCard`, `naCard`, `grid`) MUST be added to the Flutter sealed class. Failure to add them means the Freezed parser will crash with an `UnrecognizedUnionKey` error when the backend sends one of these block types.

- **Step 2a — Extract to shared layer**:
  - **Target**: `@[c:\src\quorum\client_app_v2\lib\shared\models\sdui_block_dto.dart]` [NEW]
  - Extract the existing `SduiBlockDTO` sealed class from `@[c:\src\quorum\client_app_v2\lib\features\studio\models\output_profile.dart]` into a new shared file, using `@Freezed(unionKey: 'block_type')` with ALL concrete types matching the Python `AnySduiBlock` union: `ParagraphBlock`, `BulletListBlock`, `AlertBlock`, `HeroInsightBlock`, `MarkdownBlock`, `QuoteCardBlock`, `WarningCardBlock`, `NACardBlock`, `GridBlock`.
- **Step 2b — Rewire studio imports**:
  - **Target**: `@[c:\src\quorum\client_app_v2\lib\features\studio\models\output_profile.dart]`
  - Remove the inline `SduiBlockDTO` definition and replace with `import '../../../shared/models/sdui_block_dto.dart';`.
  - Replace `List<dynamic> contentBlocks` with `@Default([]) List<SduiBlockDTO> contentBlocks` in both `OutputProfile` (line ~162) and `EmbeddedOutputProfile` (line ~191).
- **Step 2c — Rewire execution imports**:
  - **Target**: `@[c:\src\quorum\client_app_v2\lib\features\execution\models\report_layout_dto.dart]`
  - Replace `List<Map<String, dynamic>>? synthesisBlocks` with `List<SduiBlockDTO>? synthesisBlocks` by importing from `shared/models/sdui_block_dto.dart`. **PRESERVE nullable `?`** to maintain the `null` vs `[]` semantic distinction used by the report renderer.
- Execute `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.

### Phase 3: Blueprint Generator & Worker Strictness Hardening
- **Target**: `@[c:\src\quorum\backend_v2\services\blueprint.py]`
- Refactor `content_blocks` processing (lines ~888-897) to work with typed `AnySduiBlock` objects instead of raw dicts.
- Eliminate all `.copy()` calls on dict elements — use `block.model_copy()` for Pydantic-typed blocks.
- Eliminate `hasattr(cache_b, "copy")` duck-typing (`@[c:\src\quorum\backend_v2\services\blueprint.py#L1173]`) — replace with `cache_b.model_copy()`.
- Eliminate `c_block.get("id")` raw dict access (`@[c:\src\quorum\backend_v2\services\blueprint.py#L1169]`) — replace with typed attribute access.
- Eliminate `isinstance(cb, dict)` duck-typing (`@[c:\src\quorum\backend_v2\services\blueprint.py#L1248]`) — all blocks are now typed `AnySduiBlock`, iterate directly.
- Eliminate inline raw dict construction at lines ~1244 and ~1415 (e.g., `{"block_type": "markdown", "text": resolved_preamble, "id": "preamble"}`) — replace with `MarkdownBlock(block_type="markdown", text=resolved_preamble)` model instantiation.
- Eliminate `c_block["text"] = safe_md` in-place dict mutation (`@[c:\src\quorum\backend_v2\services\blueprint.py#L1212]`) — replace with `c_block.model_copy(update={...})` or reconstruct as a new `MarkdownBlock`.
- **Target**: `@[c:\src\quorum\backend_v2\services\orchestrator\synthesis_distiller.py]`
- Refactor `json.dumps(best_cache.content_blocks, ensure_ascii=False)` (`@[c:\src\quorum\backend_v2\services\orchestrator\synthesis_distiller.py#L169]`) — After migration, `content_blocks` are `list[AnySduiBlock]` which cannot be directly serialized via `json.dumps`. Use `[b.model_dump(mode='json') for b in best_cache.content_blocks]` or the `TypeAdapter` pattern.
- **Target**: `@[c:\src\quorum\backend_v2\worker.py]`
- Update synthesis result handling (lines ~877-893) to use typed `AnySduiBlock` instead of raw dict manipulation.
- **CRITICAL**: Enforce strict error handling for `ValidationError`. When parsing the LLM response into `SynthesisSectionDTO` (or similar containing `AnySduiBlock`), you MUST catch `pydantic.ValidationError` and package it into an internal `AppException`. This is required to trigger the orchestrator's automated "Schema Healing" / LLM Adaptive Retry loop. If unhandled, a hallucinated block type will crash the worker process entirely into DLQ (Dead Letter Queue).
- Execute `uv run python scripts/backend_audit_loop.py backend_v2/ --test`.

### Phase 4: Seed Data & Test Fixture Migration
- **Target**: `@[c:\src\quorum\backend_v2\seed\seed_data.json]`
- Verify all `output_profiles` entries have `content_blocks` arrays that conform to the `AnySduiBlock` discriminated union schema (each element must have a `block_type` discriminator field). Currently `content_blocks` is empty (`[]`) in seed data, so no structural migration is needed.
- **Target**: `ALL Backend Unit and Integration Tests`
- Identify all tests (e.g., `test_tier4_profile_dto_bug.py`, `test_blueprint.py`, `test_worker.py`, `test_sdui_semantic_parity.py`) that mock `content_blocks` or `synthesis_blocks` payload data using raw dictionaries.
- Rewrite these mock fixtures to either instantiate proper `AnySduiBlock` (e.g., `ParagraphBlock(text="...")`) models directly, or if mocking JSON payloads, ensure the dictionaries include a valid `block_type` discriminator field. Failure to update test mocks will result in massive `ValidationError` crashes across the test suite due to the new `strict=True` enforcement.
- Execute full audit and re-seed: `uv run python backend_v2/seed/run_seed.py local`.

---

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- ZERO instances of `list[dict[str, Any]]` remain in `OutputProfile`, `EmbeddedOutputProfile`, `OutputLayoutBlock`, `ReportLayoutDTO`, `RenderedSynthesisCache`, or their DTOs.
- ZERO instances of `List<dynamic>` or `List<Map<String, dynamic>>` remain in the Flutter `OutputProfile`, `EmbeddedOutputProfile`, or `ReportLayoutDto` Freezed models.
- `AnySduiBlock` Discriminated Union is the single reused SSOT type for all SDUI content block fields.
- Flutter `SduiBlockDTO` sealed class has **full parity** with Python `AnySduiBlock` (all 9 block types mirrored).
- Nullability semantics preserved: `synthesis_blocks` fields remain `| None` (Python) / `?` (Dart), never collapsed to non-nullable empty lists.
- ZERO instances of `hasattr()`, `isinstance(cb, dict)`, or `.get()` duck-typing remain in `blueprint.py` for SDUI blocks.
- All existing tests pass with the tightened types.
- The `layouts: list[OutputLayoutBlock]` field remains unchanged and fully functional.

### Verification Plan
- **Automated Tests**:
  - Run global backend audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
  - Run global frontend audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/`
  - Run SDUI parity tests: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
- **Manual Verification**:
  - Re-seed database (`uv run python backend_v2/seed/run_seed.py local`).
  - Generate a report and verify no rendering regressions.
- **MANDATORY Final E2E REST API Verification Gate**:
  - `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

---

## 5. Deferred Scope (Future Epics)

> [!NOTE]
> The following features are intentionally deferred to prevent mixing structural refactoring with feature addition (per `ZERO-BEHAVIORAL CHANGE FALSIFICATION` gate).

- **EPIC 121 (Proposed): Admin Studio Block Builder UI** — A drag-and-drop visual editor allowing Admins to construct and reorder `layouts` and `content_blocks` within `OutputProfile`. Builds on the typed foundation established by this Epic.
- **Typed `synthesis_blocks` inside `synthesis` configs in `seed_data.json`** — The runtime synthesis engine produces these blocks dynamically. Full seed data migration of synthesis outputs is deferred until the synthesis pipeline is stabilized.
