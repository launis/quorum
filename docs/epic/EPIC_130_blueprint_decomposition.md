# EPIC 130: Blueprint Transformer Decomposition into Modular SDUI Adapters

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
>
> Modern SDUI (Server-Driven UI) architecture in 2025-2026 mandates that the backend constructs explicit UI component blocks and ships them to thin rendering clients. Industry best practice (Clean Architecture + Interface Adapter Layer) dictates that the transformation from domain data to UI blocks MUST be isolated in dedicated **Presentation Adapters** — not inlined in a monolithic orchestrator. The "Anti-Corruption Layer" (ACL) pattern prevents dynamic JSON schemas from infecting business logic. Component-Based Decomposition ("Lego Blocks") treats each UI element as an independent, self-contained module encapsulating its own rendering rules and adapter logic. This document applies these principles to decompose `blueprint.py`'s God Method into modular, self-contained adapter files.

---

## 1. Goal Description & Background (Objective & Problem Statement)

### Business Objective
Decompose the monolithic `BlueprintTransformer` service (@[c:\src\quorum\backend_v2\services\blueprint.py]) from a 2012-line God Class into a clean, modular architecture where each report output block (executive summary, XAI extensions, penalties, matrices, audit trail, jargon ratio, printable sources) is handled by its own self-contained adapter file within a new `backend_v2/services/sdui/adapters/` directory.

### Problem Statement
The `_extract_matrices_and_extensions` method (lines 223-782, approximately 560 lines) and the various `_hydrate_*` methods (lines 783-840) currently inline ALL of the following concerns into a single file:

1. **Data Hydration**: Fetching and combining data from multiple caches (`profile_cache`, `row_explanations_cache`, `results` trace).
2. **Business Logic**: Score normalization, scale calculations, collision tracking, atom evaluation.
3. **Presentation Rules**: Determining which icon, color, and severity to assign to each SDUI component via hardcoded `if/else` chains.
4. **UI Construction**: Instantiating `AccordionBlock`, `AlertBlock`, `ParagraphBlock`, and `HeroInsightBlock` objects inline.

This violates the Open-Closed Principle (adding a new report section requires modifying `blueprint.py`), the Single Responsibility Principle (one file handles parsing, math, theming, and UI construction), and makes unit testing extremely difficult (testing icon color selection requires bootstrapping the entire Blueprint pipeline).

### Root Cause / Gap Analysis
- **God Method Anti-Pattern (Root Cause 1):** `_extract_matrices_and_extensions` (560 lines) combines LLM trace parsing, Pydantic validation, mathematical normalization, scale calculations, name collision resolution, atom evaluation mapping, and SDUI block construction in a single method with 15 parameters.
- **Hardcoded Presentation Rules (Root Cause 2):** Aesthetic decisions (icon names, severity colors) are embedded as `if "risk" in lower_ext` chains inside `_hydrate_grouped_extensions_block` (lines 830-841). Adding a new extension category requires editing this method.
- **Missing Adapter Layer (Root Cause 3):** The system lacks a dedicated Presentation Adapter layer between domain DTOs (specifically ALL input state models mapped from the execution trace) and SDUI view models (specifically ALL presentation models inheriting from the `AnySduiBlock` discriminated union defined in `models/view/sdui.py`). `blueprint.py` currently acts as both orchestrator AND adapter.
- **Untestable Theming Logic (Root Cause 4):** To test whether a "risk_flag" extension gets a "warning" severity and "balance" icon, a developer must mock 7+ repository dependencies and run the entire `build_report_dto` pipeline. The theming logic is not independently testable.

### Strategic Scope
This Epic introduces a **self-contained adapter pattern** where each report output block is a single Python file containing BOTH its aesthetic rules (as a module-level dictionary) AND its adapter class (with a single `build()` method). The orchestrator (`blueprint.py`) is reduced to a thin dispatcher that calls each adapter in sequence. No new external dependencies are introduced.

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)
- **Inline Presentation Logic in `blueprint.py`**: All `if "risk" in lower_ext` chains, icon/severity selection logic, and direct `AccordionBlock`/`AlertBlock` instantiation inside `_hydrate_grouped_extensions_block`, `_hydrate_penalties_block`, and the inline executive summary construction (lines 1079-1095) will be INTENTIONALLY MOVED to their respective adapter files.
- **`_extract_matrices_and_extensions` God Method**: This 560-line method (lines 222-782) will be decomposed in two sub-phases. Phase 6A strips extension formatting and moves it to `xai_highlights_adapter.py`. Phase 6B (Deferred) will extract the remaining matrix parsing logic into `matrix_graphs_adapter.py` and `matrix_summary_table_adapter.py`. Until Phase 6B, the remaining structural validation stays in a leaner `_parse_matrix_trace_results` orchestration method inside `blueprint.py`.
- **Legacy Layout Models**: `the historically removed Report Layout Data Transfer Object` has already been DEPRECATED and REMOVED. `OutputLayoutBlock` MUST BE RETAINED as it is part of the `OutputProfile` SSOT for database persistence, but its `preset_view` logic is ignored during presentation. The system transitions to a purely flat `inner_sdui_blocks` sequence containing `AnySduiBlock` types (specifically: `SduiRadarChartBlock`, `SduiScatterPlotBlock`) within `ReportDataDTO`, completely eliminating nested UI structure in the final client payload.
- **Placeholder Methods**: The empty placeholder methods `_hydrate_global_score_block`, `_hydrate_audit_trail_block`, and `_hydrate_jargon_ratio_block` (lines 802-812) will remain deferred until actual logic is introduced. The `_hydrate_printable_sources_block` (lines 814-828) is extracted to its own adapter.

### Retained SSOT Invariants (What We Will RETAIN)
- **Existing Base DTOs**: `MatrixScorecardRowDTO`, `XaiHighlightItem`, and all models in `@[c:\src\quorum\backend_v2\models\view\sdui.py]` remain completely unchanged. No internal fields of these components are altered.
- **`build_report_dto` Orchestration Contract**: The public async method signature returns `ReportDataDTO`, but its contents are MIGRATED to use the flat `inner_sdui_blocks: list[AnySduiBlock]` architecture exclusively. External callers (specifically `@[c:\src\quorum\backend_v2\services\execution.py]`, `@[c:\src\quorum\backend_v2\worker.py]`) require zero changes as they simply pass the DTO to the DB.
- **SDUI Polymorphic Serialization**: `AnySduiBlock` discriminated union remains the SSOT for all UI blocks.
- **Strict ICU Markdown Parity**: The Jinja template (`@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`) continues to render via `render_sdui_blocks()` macro, updated to iterate over the flat block array.
- **Flutter Frontend**: Dart/Freezed models (`Sdui Block DTO`) are naturally aligned with the flat array approach. The UI is a "Dumb Painter" that renders the array sequentially.

### Pre-Existing Code Smells Discovered (Out of Scope / Handled Naturally)
- **`VisualIntent.CRITICAL_OVERRIDE.value` at L794**: The `_hydrate_penalties_block` passes `.value` to the `AlertBlock` severity field instead of the native enum object. Per `strict_enum_hydration_and_validation`, this should be `VisualIntent.CRITICAL_OVERRIDE` directly. The Epic's Phase 3 extraction will naturally fix this.
- **`"default"` severity literal at L716**: The Literal type annotation includes `"default"` but `VisualIntent` enum has no `DEFAULT` member. It has `NEUTRAL = "NEUTRAL"`. This is a pre-existing enum gap. (This will be naturally resolved in Phase 6 when replacing the string literals with `VisualIntent` enum).
- **`workflow_steps: dict[str, StepRule]`**: Resolved. The type hint was corrected from `dict[str, Any]` to `dict[str, StepRule]` and the `.get()` anti-pattern was replaced with Fail-Fast direct subscript access. No new DTO was needed — `StepRule` was already the runtime type.
- **Phase 3 Strict Enum Hydration (Lax Pattern)**: Legacy SDUI models (e.g. `AlertBlock`) were found using `Literal` string typing instead of Enums, causing MyPy crashes when passing native Enum objects. Fixed upstream by converting model fields to use `LaxVisualIntent` (`Annotated[VisualIntent, Field(strict=False)]`), ensuring Pydantic coerces JSON strings while MyPy enforces native Enums in Python.

### Compliance & Modernity Gates
| Gate | Status |
|---|---|
| Pydantic V2 Strictness | ✅ `AdapterContext` MUST use `model_config = ConfigDict(strict=True, extra='forbid', frozen=True)` |
| Cross-Domain DTO Parity | ✅ No DTO changes — Flutter untouched |
| Fail-Fast SDUI Serialization | ✅ Maintained — adapters produce strictly typed `AnySduiBlock` |
| Zero Duct Tape Rule | ✅ Adapter rules are explicit dictionaries, not `.get()` fallbacks. All `**kwargs: Any` signatures MUST be replaced with typed `AdapterContext` DTO parameters |
| RFC-7807 Dual-Reporting | ✅ All `AppException` raises preceded by `logger.error`. All bare `except Exception:` catch-alls in extracted code MUST be replaced with typed exception handlers |
| PEP 257 & Docstring Fail-Fast | ✅ All new adapter classes and functions documented using Google-style docstrings. Explicit `Raises:` blocks are REQUIRED. Do NOT repeat type hints in text descriptions |
| Terminology Ban | ✅ The word "Epic" (or "EPIC") MUST NOT be used in any source code comments, docstrings, or logs |
| `type: ignore` Zero-Tolerance | ✅ Extracted adapter code MUST NOT carry forward any `# type: ignore` annotations from `blueprint.py`. Specifically, `severity` parameters MUST use `VisualIntent` enum values instead of bare strings |
| `inline_imports_ban` | ✅ All adapter files MUST place imports at the top of the file. Inline imports from `blueprint.py` MUST NOT be perpetuated |

### Producer-Consumer Integration Check
| Producer | Consumer | Contract |
|---|---|---|
| Adapter `xai_highlights_adapter.py` | `blueprint.py` orchestrator | Returns `list[AnySduiBlock]` (`AccordionBlock` with nested `AlertBlock` children) |
| Adapter `penalties_adapter.py` | `blueprint.py` orchestrator | Returns `list[AnySduiBlock]` (`AlertBlock` with `CRITICAL_OVERRIDE` severity) |
| Adapter `executive_summary_adapter.py` | `blueprint.py` orchestrator | Returns `list[AnySduiBlock]` (`ParagraphBlock` instances) |
| Adapter `printable_sources_adapter.py` | `blueprint.py` orchestrator | Returns `list[AnySduiBlock]` (`MarkdownBlock` instances) |
| Adapter `matrix_graphs_adapter.py` (PHASE 6B) | `blueprint.py` orchestrator | Returns `list[AnySduiBlock]` (`SduiRadarChartBlock`, `SduiScatterPlotBlock`) |
| Adapter `matrix_summary_table_adapter.py` (PHASE 6B)| `blueprint.py` orchestrator | Returns `list[AnySduiBlock]` (`SduiMatrixTableBlock`) |
| `blueprint.py` orchestrator | `pdf_generator.py`, Flutter client | Returns `ReportDataDTO` (unchanged contract) |

### Namespace Clarification
- **`backend_v2/services/sdui_mapper_service.py`** remains at its current location. It handles a different concern (Report View mapping for the Flutter SDUI client) than the adapter layer (individual block construction). These are intentionally separate namespaces and MUST NOT be merged.

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Foundation — New Directory Structure, Typed Protocol & AdapterContext DTO
**Target Directory**: `backend_v2/services/sdui/adapters/`
1. Create `@[c:\src\quorum\backend_v2\services\sdui\__init__.py]` [NEW]
2. Create `@[c:\src\quorum\backend_v2\services\sdui\adapters\__init__.py]` [NEW]
3. Create `@[c:\src\quorum\backend_v2\services\sdui\adapters\base_adapter.py]` [NEW] defining:
   - A frozen Pydantic DTO `AdapterContext` containing the strictly typed fields that adapters need (specifically: `execution: ExecutionRecord | None`, `locale: str`, `penalties_applied: list[str]`, `mcp_audit_map: dict[str, MCPAuditTrace] | None`, `global_score: float | None`, `accumulated_extensions: dict[str, list[AnySduiBlock]]`, `profile: OutputProfile`, `profile_cache: RenderedSynthesisCache | None`).
   - **MANDATORY**: `AdapterContext` MUST use `model_config = ConfigDict(frozen=True, strict=True, extra="forbid")` to adhere to the `frozen_state_mutability` invariant, preventing downstream side effects.
   - A `Protocol` class `SduiAdapterProtocol` with a single `@staticmethod build(context: AdapterContext) -> list[AnySduiBlock]` method.
   - **MANDATORY**: The dispatch table in `blueprint.py` (`_target_block_hydrators` at [blueprint.py#L104-L111](file:///c:/src/quorum/backend_v2/services/blueprint.py#L104-L111)) MUST be refactored to `dict[str, Callable[[AdapterContext], list[AnySduiBlock]]]` using a uniform calling convention. Adapter classes MUST be registered via lambda wrappers (specifically `lambda ctx: XaiHighlightsAdapter.build(ctx)`) to avoid `isinstance` branching at the call site. Deferred placeholder methods MUST be wrapped identically (specifically `lambda ctx: []`). This supersedes the old `Callable[..., list[AnySduiBlock]]` signature. **NOTE**: The `from collections.abc import Callable` inline import at [blueprint.py#L102](file:///c:/src/quorum/backend_v2/services/blueprint.py#L102) inside `__init__` MUST be moved to the top-level imports per the `inline_imports_ban`.
   - **MANDATORY CALL-SITE MIGRATION**: The hydrator dispatch loop at [blueprint.py#L1948-L1960](file:///c:/src/quorum/backend_v2/services/blueprint.py#L1948-L1960) MUST be refactored from the current keyword-argument scatter pattern (`execution=execution, locale=locale, penalties_applied=penalties_applied, ...`) to `adapter_fn(context)` where `context` is a pre-constructed `AdapterContext` instance. The current scatter-pattern MUST be replaced with a single DTO construction before the dispatch loop.
   - **MANDATORY NAMING BRIDGE**: The dispatch call site at [blueprint.py#L1953](file:///c:/src/quorum/backend_v2/services/blueprint.py#L1953) passes the kwarg `mcp_audit_data` as a list, but the `AdapterContext` field is named `mcp_audit_map` and typed as a dict. When constructing `AdapterContext`, the executing agent MUST bridge this AND convert the list to a dictionary: `AdapterContext(..., mcp_audit_map={t.id: t for t in mcp_audit_data if t.id} if mcp_audit_data else None, ...)`.
4. **MANDATORY CODE QUALITY GATE**: All adapter files MUST:
   - Include negative tests for `AdapterContext` that explicitly assert `pytest.raises(ValidationError)` when attempting to pass unexpected kwargs or mutate frozen fields, to mathematically guarantee `extra="forbid"` and `frozen=True` mutability locks work natively in Rust.
   - Verify that `test_blueprint.py` and `test_blueprint_sdui_crash.py` still pass after `AdapterContext` injection, ensuring orchestration pipelines are not broken by the strict context switch.
   - Place ALL imports at the top of the file (no inline imports) and explicitly define them (no ambiguous "e.g." shorthand).
   - Use typed exception handlers (specifically `except ValueError`, `except ValidationError`, or `except KeyError`) — bare `except Exception:` is strictly forbidden.
   - Use `VisualIntent` enum values for severity parameters — bare string literals with `# type: ignore[arg-type]` are strictly forbidden.
   - Use strict dictionary key access (`RULES[key]`) — `.get(key, default)` fallbacks are strictly forbidden.

### Phase 2: Extract XAI Highlights Adapter (Proof of Concept)
1. Create `@[c:\src\quorum\backend_v2\services\sdui\adapters\xai_highlights_adapter.py]` [NEW].
   - **MANDATORY**: Lookups for aesthetics and profile mappings MUST use strict dictionary key access (specifically `XAI_AESTHETICS_RULES[extension_type]` and `profile.extension_labels[ext_enum]`). Fallbacks using `.get()` are strictly forbidden to ensure Fail-Fast `KeyError` crashes on unknown extension types.
   - **MANDATORY**: All imports MUST be explicitly listed at the top of the file without ambiguity. You MUST explicitly import `AppException`, `VisualIntent`, `ErrorCodes`, and `XaiExtensionType`.
2. Modify `@[c:\src\quorum\backend_v2\services\blueprint.py]`: Delete `_hydrate_grouped_extensions_block` and route to the new adapter using `build(context)`.
   - **NOTE**: The actual complex `_add_ext` closure (where extensions are accumulated) lives inside the God Method. Extraction of `_add_ext` belongs to **Phase 6**. Phase 2 only extracts the simple flat-mapping done in `_hydrate_grouped_extensions_block`.
3. **ATOMIC TEST MIGRATION**: You MUST physically move all existing tests related to `_hydrate_grouped_extensions_block` from `@[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py]` into a new `@[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_xai_highlights_adapter.py]` [NEW] file. You MUST NOT mock or delete the old tests.
   - **MANDATORY NEGATIVE TESTS**: You MUST write a negative test asserting that an unknown extension triggers `AppException` (coercion failure) and another asserting that an unmapped aesthetic key triggers a native `KeyError`.

### Phase 3: Extract Penalties Adapter
1. Create `@[c:\src\quorum\backend_v2\services\sdui\adapters\penalties_adapter.py]` [NEW].
   - Create a `PenaltiesAdapter` class with a static method `build(context: AdapterContext) -> list[AnySduiBlock]`.
   - Move the exact logic from `_hydrate_penalties_block` into this method.
   - Ensure strict typing and imports for `AnySduiBlock`, `AlertBlock`, and `VisualIntent`.
2. Modify `@[c:\src\quorum\backend_v2\services\blueprint.py]`:
   - Import `PenaltiesAdapter` and wire it into the `_target_block_hydrators` registry in `__init__`.
   - Delete `_hydrate_penalties_block` entirely.
3. **ATOMIC TEST MIGRATION**: You MUST physically move all existing tests related to `_hydrate_penalties_block` from `@[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py]` into a new `@[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_penalties_adapter.py]` [NEW] file. You MUST NOT mock or delete the old tests.
   - **MANDATORY NEGATIVE TESTS**: Assert that `AdapterContext` correctly raises `ValidationError` if `penalties_applied` is entirely missing from instantiation, and that passing an empty list `[]` safely returns `[]` from the adapter.
   - **Positive Test**: Assert string mapping into `AlertBlock(severity=VisualIntent.CRITICAL_OVERRIDE)`.

### Phase 4: Extract Executive Summary Adapter
1. Create `@[c:\src\quorum\backend_v2\services\sdui\adapters\executive_summary_adapter.py]` [NEW].
   - **Strict Role Validation:** Enforce `RoleClassification(context.profile.user_role)`. Catch `ValueError` and raise `AppException`. No `except Exception:` duct-tape.
   - **Fail-Fast L10N Prefix:** Enforce `context.profile.user_role_label.resolve(context.locale)`. If `user_role_label` is missing, raise a Fail-Fast `AppException` rather than hardcoding English `"User Role"`.
   - **MANDATORY**: The bare `except Exception:` catch-all currently at [blueprint.py#L1085](file:///c:/src/quorum/backend_v2/services/blueprint.py#L1085) MUST be replaced with a typed handler (specifically `except KeyError` or `except ValueError`).
   - **MANDATORY .get() ERADICATION**: The `profile.user_role_mappings.get(profile_cache.user_role)` at [blueprint.py#L1080](file:///c:/src/quorum/backend_v2/services/blueprint.py#L1080) MUST be replaced with strict key access `profile.user_role_mappings[profile_cache.user_role]`, with `KeyError` handled explicitly via `AppException`.
   - **ADAPTER SCOPE CLARIFICATION**: `ExecutiveSummaryAdapter.build()` returns ONLY the role-prefix `ParagraphBlock` (specifically the `**{prefix}:** {role_val}` block). It does NOT handle `synthesis_md` resolution, `content_blocks` aggregation, or `section_syntheses` mapping. These remain in `blueprint.py`'s orchestration flow at [blueprint.py#L1060-L1077](file:///c:/src/quorum/backend_v2/services/blueprint.py#L1060-L1077).
2. Modify `@[c:\src\quorum\backend_v2\services\blueprint.py]` (within `build_report_dto`): 
   - Delete inline executive summary role-mapping logic (starting at the `if profile_cache.user_role:` block at L1078) and route to `ExecutiveSummaryAdapter.build(context)`. The `synthesis_md` resolution at L1077 remains in `blueprint.py` as part of the orchestration flow.
3. **ATOMIC TEST MIGRATION**: You MUST physically move all existing tests related to the executive summary from `@[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py]` into a new `@[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_executive_summary_adapter.py]` [NEW] file. You MUST NOT mock or delete the old tests.
   - **MANDATORY NEGATIVE TESTS**: Assert invalid `user_role` string triggers `AppException`. Assert missing `user_role_label` triggers `AppException`. Assert missing `user_role_mappings` key triggers `AppException`.

### Phase 5: Extract Printable Sources Adapter
1. Create `@[c:\src\quorum\backend_v2\services\sdui\adapters\printable_sources_adapter.py]` [NEW].
   - Create a `PrintableSourcesAdapter` class with a static method `build(context: AdapterContext) -> list[AnySduiBlock]`.
   - Move the logic from `_hydrate_printable_sources_block` into this method.
2. Modify `@[c:\src\quorum\backend_v2\services\blueprint.py]`:
   - Import `PrintableSourcesAdapter` and wire it into the `_target_block_hydrators` registry in `__init__`.
   - Delete `_hydrate_printable_sources_block` entirely.
3. **ATOMIC TEST MIGRATION**: You MUST physically move any tests related to `_hydrate_printable_sources_block` into a new `@[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_printable_sources_adapter.py]` [NEW] file.

### Phase 5a: DEFERRED — Placeholder Adapters (No Extraction Until Real Logic Exists)
**STATUS: DEFERRED.** The methods `_hydrate_global_score_block`, `_hydrate_audit_trail_block`, and `_hydrate_jargon_ratio_block` at [blueprint.py#L802-L812](file:///c:/src/quorum/backend_v2/services/blueprint.py#L802-L812) are currently empty placeholders returning `[]` or dummy text. Extracting empty methods into separate adapter files is pure churn with zero architectural value.

**STRICT EXECUTION DIRECTIVE:**
- The execution agent MUST NOT attempt to extract or touch `_hydrate_global_score_block`, `_hydrate_audit_trail_block`, or `_hydrate_jargon_ratio_block` during this phase.
- Simply acknowledge this deferral and immediately proceed to Phase 6 or complete the current execution step.

### Phase 6A: Decompose God Method (XAI Extensions & Fail-Fast Refactor)
**Architectural Pivot**: Extracting the Matrix logic was found to be premature because chart-type routing (3D vs 2D) is layout-coupled, not domain-coupled, risking the introduction of duct-tape fallbacks. Thus, Phase 6 is split. Phase 6A focuses solely on extracting the extension formatting from the God Method and refactoring the `XaiHighlightsAdapter`.

1. Refactor `@[c:\src\quorum\backend_v2\services\sdui\adapters\xai_highlights_adapter.py]` (created in Phase 2) to directly read from `context.execution.results` and extract the `_add_ext` logic natively, removing the need for any upstream pre-processing of extensions.
   - **MANDATORY**: Because extensions are now parsed directly from results, the `accumulated_extensions` field MUST be removed from `AdapterContext` during this phase.
   - **MANDATORY SEVERITY ENUM MIGRATION**: The bare string severity literals (`"info"`, `"success"`, `"error"`, `"warning"`) inside the `_add_ext` closure MUST be replaced with `VisualIntent` enum values (`VisualIntent.INFO`, etc.).
   - **MANDATORY SILENT SWALLOW ERADICATION**: Replace `except ValueError: pass` with `logger.error` + `raise AppException` for unknown extensions.

> [!WARNING]
> **DELIBERATE BEHAVIORAL CHANGE**: This is NOT a pure structural refactoring. Previously, unknown extension types were silently ignored (`except ValueError: pass`). After this change, they will crash immediately per the Fail-Fast mandate.
>
> **MANDATORY BLOCKING PREREQUISITE (Must Execute BEFORE Enabling Crash Path)**:
> 1. Enumerate ALL extension type strings currently used in `seed_data.json` and cross-reference them against `XaiExtensionType` enum members.
> 2. Add missing strings to the enum BEFORE enabling the crash path.
> 3. Write a specific negative test asserting the `AppException` crash for an unknown extension string.

   - **MANDATORY DUCK-TYPING ERADICATION**: Ensure no `hasattr` or `getattr` with default fallbacks are used in the refactored code. Use strict typed attribute access.
2. Modify `@[c:\src\quorum\backend_v2\services\blueprint.py]`: Rename `_extract_matrices_and_extensions` to `_parse_matrix_trace_results`. Strip ALL extension logic (`_add_ext` closure, iteration over highlights) from this method. It now ONLY returns the raw matrix payloads.
3. **ATOMIC TEST MIGRATION**: You MUST physically move all existing tests related to `_add_ext` and extension formatting from `test_blueprint.py` into `test_xai_highlights_adapter.py`.

### Phase 6B: Matrix Adapters (DEFERRED)
**STATUS: DEFERRED.** Extracting `MatrixGraphsAdapter` and `MatrixSummaryTableAdapter` is deferred until `AdapterContext` and the `OutputLayoutBlock.preset_view` routing are redesigned to support Dumb Painter decoupling without silent fallbacks.

**STRICT EXECUTION DIRECTIVE:**
- The execution agent MUST NOT attempt to create `MatrixGraphsAdapter` or `MatrixSummaryTableAdapter` during this epic.
- Do not extract the matrix logic from `_parse_matrix_trace_results` yet.

### Phase 7: SDUI Layout Flattening (Dumb Painter Architecture & Strict Ordering)

> [!IMPORTANT]
> **MANDATORY TIER 1 SUB-PHASE SPLIT**: This phase is the largest in the Epic and combines dispatch configuration with block ordering logic. The `/tier1-planner` MUST split Phase 7 into at minimum 2 separate implementation plans: (7A) Dispatch loop refactoring and adapter wiring, and (7B) Block ordering configuration and PDF/Jinja parity verification. This prevents context saturation during execution.

1. **CRITICAL GUARDRAIL**: `ReportDataDTO` in `@[c:\src\quorum\backend_v2\models\v2_core.py#L1125-L1199]` ALREADY uses `inner_sdui_blocks` and `the historically removed Report Layout Data Transfer Object` has already been removed. You MUST NOT delete `OutputLayoutBlock` from `backend_v2/models/v2_core.py` because it is an SSOT entity required by `OutputProfile.layouts` for database authoring.
2. **PRIORITY TARGET**: The Flutter/UI rendering is the primary presentation target. It MUST be fixed and verified first to achieve parity with `raportti 2.pdf`. Modify `blueprint.py`'s final assembly to concatenate all extracted adapter blocks directly into a single `inner_sdui_blocks` list. **MANDATORY**: You MUST preserve the dynamic dispatch loop architecture defined in Phase 1 (`_target_block_hydrators`), but you MUST configure the loop execution order to exactly match `raportti 2.pdf`:
   - **Step 1 (Metadata):** `HeaderBlock`
     - *Source*: Derived from `context.execution` metadata (specifically `created_at` and `org_name`).
   - **Step 2 (Executive Summary):** Blocks from `executive_summary_adapter` (`HeroInsightBlock` / `MarkdownBlock`).
     - *Source*: Read directly from `context.profile_cache.synthesis_blocks` or `execution.global_synthesis`.
     - *LLM Instruction Mandate*: **CRITICAL**: The genuine LLM instruction rule MUST be applied exactly as before. The output must strictly follow the existing instruction, where output is adjusted by paragraphs and `user_role` is declared at the end.
   - **Step 3 (Matrix Graphs & Justifications):** First output those matrices that contain a graph (`SduiRadarChartBlock`, `SduiScatterPlotBlock`), immediately followed by their text justifications (`ParagraphBlock`).
     - *Source*: Graph structures are generated via `matrix_graphs_adapter` from `context.execution.results`. Text justifications are mapped via `context.row_explanations_cache`.
     - *LLM Instruction Mandate*: **CRITICAL**: The genuine LLM instruction rule MUST be applied. The text content for all of these must be formed AI-assisted according to current highly regulated instructions (specifically, graphs have very strict rules for forming text content).
   - **Step 4 (Extensions):** Blocks from `xai_highlights_adapter` and `penalties_adapter` (`AccordionBlock`, `AlertBlock`).
     - *Source*: Read mapped data directly from `context.accumulated_extensions` and `context.penalties_applied`.
     - *LLM Instruction Mandate*: **CRITICAL**: The genuine LLM instruction rule MUST be applied. The text content, explicit rows per extension, and exact data fetch patterns are tightly regulated and must be executed by the LLM exactly as currently implemented.
   - **Step 5 (Matrix Summary Table):** Matrix Summary Table (`SduiMatrixTableBlock` from `matrix_summary_table_adapter`).
     - *Source*: Dynamically aggregated directly from `context.execution.results` by the matrix summary table adapter.
     - *LLM Instruction Mandate*: **CRITICAL**: The genuine LLM instruction rule MUST be applied. The explanation column must be formed AI-assisted exactly as before.
   - **Step 6 (Workflow Extensions):** Workflow evaluation blocks (`SduiMetrics1DBlock` + text).
     - *Source*: Map `context.workflow_ext_values` to the defined global scoring components.
   - **Step 7 (Sources):** Printable Sources from `printable_sources_adapter` (`MarkdownBlock` containing Tavily search results etc.).
     - *Source*: Mapped directly from `context.mcp_audit_map`.
     - *LLM Instruction Mandate*: **CRITICAL**: The genuine LLM instruction rule MUST be applied. This must be processed taking language into account as always before.
   The flattening is achieved by using `.extend()` on the adapter results during the configured loop.
3. **GLOBAL LINGUISTIC MANDATE**: Always fetch the language and format strictly according to `@[c:\src\quorum\backend_v2\models\prompts\global_mandates.py]` and `@[c:\src\quorum\backend_v2\models\prompts\linguistic_directives.py]`, exactly as done previously.
4. **GLOBAL ANTI-TRUNCATION MANDATE (NO SHORTENING)**: Under NO circumstances may the executing LLM shorten, summarize, simplify, or truncate any of the textual content, paragraphs, or logic defined in the steps above. You MUST pass the generated texts through identically. The tendency to "tighten" text is strictly forbidden.
5. Modify `pdf_generator.py` and the Jinja macros to expect the flat layout structure sequentially, eliminating legacy `preset_view` strings.

### Phase 8: Verification & E2E Integration Gate

1. Run backend tests: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
2. Run frontend compilation: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`
3. Execute parity check: `uv run python scripts/run_e2e_variance_test.py`

---

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
1. `blueprint.py` contains ZERO direct `AccordionBlock`, `AlertBlock`, `ParagraphBlock`, or `MarkdownBlock` instantiation for the extracted adapters.
2. `blueprint.py` is reduced from 2012 lines to approximately 1200-1300 lines.
3. Every adapter file in `backend_v2/services/sdui/adapters/` is self-contained: it has its own module-level rules dictionary and strictly uses explicit Key-Access (`RULES[key]`) rather than `.get()`.
4. **Atomic Test Migration**: Any tests previously asserting on private methods are updated in the exact same phase. No test suite breakage between phases.
5. The `ReportDataDTO` JSON output is MIGRATED to the flat `inner_sdui_blocks` architecture (as per `output_profile_layout_v2.md`), entirely eliminating `the historically removed Report Layout Data Transfer Object`. Snapshot tests must be explicitly rewritten to expect the flat `AnySduiBlock` output.
6. MyPy strict passes with zero new `# type: ignore` annotations.
7. Zero bare `except Exception:` catch-alls in any adapter file. All exception handlers MUST use typed exceptions and explicitly state them in the `Raises:` section of the Google-style docstring.
8. The word "Epic" (or "EPIC") does NOT appear in any added code, docstrings, or comments.
9. Zero inline imports in any adapter file. All imports MUST be at the top of the file.
10. The dispatch table `_target_block_hydrators` uses `dict[str, Callable[[AdapterContext], list[AnySduiBlock]]]` with uniform lambda-wrapped calling convention for both adapter classes and deferred placeholders.

### Automated Unit Tests
```bash
uv run python scripts/backend_audit_loop.py backend_v2 --test
```

New unit tests to be added:
- `backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py`: Tests aesthetic rule lookup independently (no Blueprint dependencies).
- `backend_v2/tests/unit/services/sdui/adapters/test_penalties_adapter.py`: Tests penalty block construction independently.
- `backend_v2/tests/unit/services/sdui/adapters/test_executive_summary_adapter.py`: Tests summary block construction independently.
- `backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_adapter.py`: Tests printable sources formatting independently.
- `backend_v2/tests/unit/services/sdui/adapters/test_matrix_graphs_adapter.py`: Tests matrix graph construction independently.
- `backend_v2/tests/unit/services/sdui/adapters/test_matrix_summary_table_adapter.py`: Tests matrix summary table construction independently.

### Manual Verification Steps
1. Run a full execution and generate a PDF report. Visually compare against `@[c:\src\quorum\docs\jwvastaus\raportti 2.pdf]` to confirm identical output.
2. Verify the Flutter app renders the report identically (no Dart changes, same JSON contract).

### MANDATORY Final E2E REST API Verification Gate
```bash
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

---

## 5. Knowledge Item Mandate

This Epic introduces a new architectural pattern (Self-Contained SDUI Adapter with Co-Located Rules). The Knowledge Item has been **pre-created before execution** to serve as a canonical reference template during all phases:
- **KI Name**: `sdui_adapter_decomposition`
- **KI Title**: SDUI Self-Contained Adapter Pattern
- **Summary**: Defines the locked two-section file structure (Section 1: AESTHETICS_RULES dictionary, Section 2: Adapter class), locked terminology (`build`, `context`, `AdapterContext`, `_RULES`, `blocks`), canonical reference implementation, forbidden anti-patterns, and AdapterContext schema.

**MANDATORY COMPLIANCE DIRECTIVE**: The executing agent MUST read KI `sdui_adapter_decomposition` (specifically `ki_sdui_adapter_pattern.md`) BEFORE creating any adapter file in Phases 1–6. Every adapter file MUST be structurally identical to the canonical reference template defined in the KI. Deviation from the locked terminology or two-section structure is a blocking failure.
