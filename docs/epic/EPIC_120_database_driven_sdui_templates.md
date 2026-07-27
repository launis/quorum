# EPIC 120: SDUI Strictness Hardening — Eradicating Unstructured Presentation Fields

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
> The industry standard for Server-Driven UI (SDUI) in 2026 explicitly relies on treating UI entirely as polymorphic data contracts (Data-as-UI). Modern architectures demand that both backend orchestration and client rendering rely on strict Discriminated Unions (sealed classes in Dart / `@Field(discriminator='type')` in Pydantic) to map dynamic JSON to a Catalog/Registry pattern. The A2UI (Agentic UI) protocol and frameworks like Stac enforce "Demand-Driven Schemas", eliminating `List<dynamic>` dumping grounds in favor of strict, statically validated layout schemas that prevent schema drift. This Epic aligns Quorum with the 2026 SDUI standard by eliminating all remaining `dict[str, Any]` and `List<dynamic>` fields in the SDUI persistence and rendering layers.

## 1. Goal Description & Background (Objective & Problem Statement)

**Objective**: Eradicate the final three unstructured data fields (`content_blocks: list[dict[str, Any]]`, `synthesis_blocks: list[dict[str, Any]]`) across `OutputProfile`, `OutputLayoutBlock`, and `ReportLayoutDTO` by replacing them with strict Pydantic V2 Discriminated Unions and Dart 3 Freezed sealed classes.

**Problem Statement**: While Epic 111 achieved "Dumb Painter" rendering and the `OutputLayoutBlock` model is already strictly typed, three fields in the SDUI persistence layer remain unstructured:

1. **`OutputProfile.content_blocks: list[dict[str, Any]]`** — Profile-level SDUI content injection slot. Typed as `List<dynamic>` in Flutter. Completely bypasses Fail-Fast architecture.
2. **`OutputLayoutBlock.synthesis_blocks: list[dict[str, Any]] | None`** — Section-level synthesis output. Produced by the LLM synthesis engine but persisted untyped.
3. **`ReportLayoutDTO.synthesis_blocks: list[dict[str, Any]] | None`** — The consumer-facing SDUI payload for synthesis blocks, also untyped.

These three fields represent the last `Any`/`dynamic` contamination in the entire SDUI pipeline. The `SynthesisOutputDTO.content_blocks` is already typed as `list[AnySduiBlock]`, proving the discriminated union pattern works. This Epic extends that pattern to the remaining three fields.

> [!IMPORTANT]
> **Architectural Constraint: The `layouts: list[OutputLayoutBlock]` field is already a strictly typed Pydantic model** with Literal-typed `preset_view`, `text_delivery_mode`, and nested `SynthesisConfigDTO`. It MUST NOT be removed or replaced. The established pattern (per KI: `ki_dumb_painter_penalty_layout`) is to use `preset_view: "text_only"` for non-matrix content within `layouts`. Any future admin reordering capability builds ON TOP of the existing `layouts` architecture.

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)
- **`OutputProfile.content_blocks: list[dict[str, Any]]`** — Replaced with `content_blocks: list[AnySduiBlock]` using the existing `AnySduiBlock` Discriminated Union from `@[c:\src\quorum\backend_v2\models\dtos\synthesis.py]`.
- **`OutputLayoutBlock.synthesis_blocks: list[dict[str, Any]] | None`** — Replaced with `synthesis_blocks: list[AnySduiBlock] | None`.
- **`ReportLayoutDTO.synthesis_blocks: list[dict[str, Any]] | None`** — Replaced with `synthesis_blocks: list[AnySduiBlock] | None`.
- **Flutter `List<dynamic> contentBlocks`** — In both `OutputProfile` and `EmbeddedOutputProfile` Freezed models, replaced with a `@Freezed(unionKey: 'block_type')` sealed class mirroring `AnySduiBlock`.
- **Unstructured Type Definitions**: After this Epic, ZERO instances of `dict[str, Any]` or `List<dynamic>` remain in any SDUI-related model.

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
- **Reuse AnySduiBlock SSOT**: The existing `AnySduiBlock` type alias in `synthesis.py` is the Single Source of Truth. New consumers MUST import and reuse it, not redefine it.

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
- Replace `content_blocks: list[dict[str, Any]]` with `content_blocks: list[AnySduiBlock]` in:
  - `OutputProfile` (line ~1330)
  - `EmbeddedOutputProfile` (line ~1373)
- Replace `synthesis_blocks: list[dict[str, Any]] | None` with `synthesis_blocks: list[AnySduiBlock] | None` in:
  - `OutputLayoutBlock` (line ~1267)
  - `ReportLayoutDTO` (line ~1067)
- **Target**: `@[c:\src\quorum\backend_v2\models\dtos\output_profile.py]`
- Update `OutputProfileCreateDTO.content_blocks`, `OutputProfileUpdateDTO.content_blocks`, and `OutputProfileResponseDTO.content_blocks` to `list[AnySduiBlock]`.
- Execute `uv run python scripts/backend_audit_loop.py backend_v2/ --test`.

### Phase 2: Frontend Freezed Sealed Class Synchronization
- **Target**: `@[c:\src\quorum\client_app_v2\lib\features\studio\models\output_profile.dart]`
- Define a `SduiContentBlock` sealed class mirroring `AnySduiBlock` (using `@Freezed(unionKey: 'block_type')`) with concrete types: `ParagraphBlock`, `BulletListBlock`, `AlertBlock`, `QuoteBlock`.
- Replace `List<dynamic> contentBlocks` with `List<SduiContentBlock> contentBlocks` in both `OutputProfile` (line ~162) and `EmbeddedOutputProfile` (line ~191).
- Replace `List<dynamic>?` synthesis_blocks references in `OutputLayoutBlock` Freezed model.
- Execute `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.

### Phase 3: Blueprint Generator Strictness Hardening
- **Target**: `@[c:\src\quorum\backend_v2\services\blueprint.py]`
- Refactor `content_blocks` processing (lines ~888-897) to work with typed `AnySduiBlock` objects instead of raw dicts.
- Eliminate all `.copy()` calls on dict elements — use `block.model_copy()` or `block.model_dump(mode='json')` for Pydantic-typed blocks.
- Eliminate `hasattr(cache_b, "copy")` duck-typing (line ~1173) — replace with typed model operations.
- **Target**: `@[c:\src\quorum\backend_v2\worker.py]`
- Update synthesis result handling (lines ~877-893) to use typed `AnySduiBlock` instead of raw dict manipulation.
- Execute `uv run python scripts/backend_audit_loop.py backend_v2/ --test`.

### Phase 4: Seed Data & Test Fixture Migration
- **Target**: `@[c:\src\quorum\backend_v2\seed\seed_data.json]`
- Verify all `output_profiles` entries have `content_blocks` arrays that conform to the `AnySduiBlock` discriminated union schema (each element must have a `block_type` discriminator field). Currently `content_blocks` is empty (`[]`) in seed data, so no structural migration is needed.
- **Target**: `@[c:\src\quorum\backend_v2\tests\unit\test_tier4_profile_dto_bug.py]`
- Rewrite test fixtures to use typed `AnySduiBlock` dicts (with `block_type` discriminator) instead of raw dicts.
- Execute full audit and re-seed: `uv run python backend_v2/seed/run_seed.py local`.

---

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- ZERO instances of `list[dict[str, Any]]` remain in `OutputProfile`, `EmbeddedOutputProfile`, `OutputLayoutBlock`, `ReportLayoutDTO`, or their DTOs.
- ZERO instances of `List<dynamic>` remain in the Flutter `OutputProfile` and `EmbeddedOutputProfile` Freezed models.
- `AnySduiBlock` Discriminated Union is the single reused SSOT type for all SDUI content block fields.
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
