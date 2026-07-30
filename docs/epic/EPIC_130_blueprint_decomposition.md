# EPIC 130: Blueprint Transformer Decomposition into Modular SDUI Adapters

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
>
> Modern SDUI (Server-Driven UI) architecture in 2025-2026 mandates that the backend constructs explicit UI component blocks and ships them to thin rendering clients. Industry best practice (Clean Architecture + Interface Adapter Layer) dictates that the transformation from domain data to UI blocks MUST be isolated in dedicated **Presentation Adapters** — not inlined in a monolithic orchestrator. The "Anti-Corruption Layer" (ACL) pattern prevents dynamic JSON schemas from infecting business logic. Component-Based Decomposition ("Lego Blocks") treats each UI element as an independent, self-contained module encapsulating its own rendering rules and adapter logic. This Epic applies these principles to decompose `blueprint.py`'s God Method into modular, self-contained adapter files.

---

## 1. Goal Description & Background (Objective & Problem Statement)

### Business Objective
Decompose the monolithic `BlueprintTransformer` service (@[c:\src\quorum\backend_v2\services\blueprint.py]) from a 1815-line God Class into a clean, modular architecture where each report output block (executive summary, XAI extensions, penalties, matrices, audit trail, jargon ratio, printable sources) is handled by its own self-contained adapter file within a new `backend_v2/services/sdui/adapters/` directory.

### Problem Statement
The `_extract_matrices_and_extensions` method (lines 218-745, approximately 530 lines) and the various `_hydrate_*` methods (lines 747-860) currently inline ALL of the following concerns into a single file:

1. **Data Hydration**: Fetching and combining data from multiple caches (`profile_cache`, `row_explanations_cache`, `results` trace).
2. **Business Logic**: Score normalization, scale calculations, collision tracking, atom evaluation.
3. **Presentation Rules**: Determining which icon, color, and severity to assign to each SDUI component via hardcoded `if/else` chains.
4. **UI Construction**: Instantiating `AccordionBlock`, `AlertBlock`, `ParagraphBlock`, and `HeroInsightBlock` objects inline.

This violates the Open-Closed Principle (adding a new report section requires modifying `blueprint.py`), the Single Responsibility Principle (one file handles parsing, math, theming, and UI construction), and makes unit testing extremely difficult (testing icon color selection requires bootstrapping the entire Blueprint pipeline).

### Root Cause / Gap Analysis
- **God Method Anti-Pattern (Root Cause 1):** `_extract_matrices_and_extensions` (530 lines) combines LLM trace parsing, Pydantic validation, mathematical normalization, scale calculations, name collision resolution, atom evaluation mapping, and SDUI block construction in a single method with 15 parameters.
- **Hardcoded Presentation Rules (Root Cause 2):** Aesthetic decisions (icon names, severity colors) are embedded as `if "risk" in lower_ext` chains inside `_hydrate_grouped_extensions_block` (lines 818-832). Adding a new extension category requires editing this method.
- **Missing Adapter Layer (Root Cause 3):** The system lacks a dedicated Presentation Adapter layer between domain DTOs (specifically `MatrixScorecardRowDTO`, `XaiHighlightItem`, `TraceScoringPayloadDTO`) and SDUI view models (specifically `AccordionBlock`, `AlertBlock`, `ParagraphBlock`). `blueprint.py` currently acts as both orchestrator AND adapter.
- **Untestable Theming Logic (Root Cause 4):** To test whether a "risk_flag" extension gets a "warning" severity and "balance" icon, a developer must mock 7+ repository dependencies and run the entire `build_report_dto` pipeline. The theming logic is not independently testable.

### Strategic Scope
This Epic introduces a **self-contained adapter pattern** where each report output block is a single Python file containing BOTH its aesthetic rules (as a module-level dictionary) AND its adapter class (with a single `build()` method). The orchestrator (`blueprint.py`) is reduced to a thin dispatcher that calls each adapter in sequence. No new external dependencies are introduced.

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)
- **Inline Presentation Logic in `blueprint.py`**: All `if "risk" in lower_ext` chains, icon/severity selection logic, and direct `AccordionBlock`/`AlertBlock` instantiation inside `_hydrate_grouped_extensions_block`, `_hydrate_penalties_block`, and the inline executive summary construction (lines 1072-1095) will be INTENTIONALLY MOVED to their respective adapter files.
- **`_extract_matrices_and_extensions` God Method**: This 530-line method will be decomposed. Matrix parsing logic moves to a dedicated `matrix_extractor.py` service. Extension accumulation moves to `xai_highlights_adapter.py`. The remaining structural validation stays in a leaner `_parse_matrix_trace_results` orchestration method inside `blueprint.py`.
- **Placeholder Methods**: The empty placeholder methods `_hydrate_global_score_block`, `_hydrate_audit_trail_block`, `_hydrate_jargon_ratio_block`, and `_hydrate_printable_sources_block` (lines 765-779) will be DELETED from `blueprint.py` and replaced by dedicated adapter files.

### Retained SSOT Invariants (What We Will RETAIN)
- **Existing Pydantic DTOs**: `MatrixScorecardRowDTO`, `XaiHighlightItem`, `ReportLayoutDTO`, `ReportDataDTO`, and all models in `@[c:\src\quorum\backend_v2\models\view\sdui.py]` remain completely unchanged. No fields are added, removed, or renamed.
- **`build_report_dto` Orchestration Contract**: The public async method signature and return type (`ReportDataDTO`) remain identical. External callers (specifically `@[c:\src\quorum\backend_v2\services\pdf_generator.py]` and `@[c:\src\quorum\backend_v2\api\routers\execution\report.py]`) require zero changes.
- **SDUI Polymorphic Serialization**: `AnySduiBlock` discriminated union remains the SSOT for all UI blocks.
- **Strict ICU Markdown Parity**: The Jinja template (`@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`) continues to render via `render_sdui_blocks()` macro unchanged.
- **Flutter Frontend**: No Dart/Freezed changes required. The JSON contract between backend and frontend remains byte-identical.

### Compliance & Modernity Gates
| Gate | Status |
|---|---|
| Pydantic V2 `ConfigDict(strict=True, extra='forbid')` | ✅ No new models introduced |
| Cross-Domain DTO Parity | ✅ No DTO changes — Flutter untouched |
| Fail-Fast SDUI Serialization | ✅ Maintained — adapters produce strictly typed `AnySduiBlock` |
| Zero Duct Tape Rule | ✅ Adapter rules are explicit dictionaries, not `.get()` fallbacks |
| RFC-7807 Dual-Reporting | ✅ All `AppException` raises preceded by `logger.error` |
| PEP 257 Google-Style Docstrings | ✅ All new adapter classes and functions documented |

### Producer-Consumer Integration Check
| Producer | Consumer | Contract |
|---|---|---|
| Adapter `xai_highlights_adapter.py` | `blueprint.py` orchestrator | Returns `list[AnySduiBlock]` (specifically `AccordionBlock` with nested `AlertBlock` children) |
| Adapter `penalties_adapter.py` | `blueprint.py` orchestrator | Returns `list[AnySduiBlock]` (specifically `AlertBlock` with `CRITICAL_OVERRIDE` severity) |
| Adapter `executive_summary_adapter.py` | `blueprint.py` orchestrator | Returns `list[AnySduiBlock]` (specifically `ParagraphBlock` instances) |
| Service `matrix_extractor.py` | `blueprint.py` orchestrator | Returns structured tuples of `MatrixScorecardRowDTO` lists and `ScorecardAtomDTO` maps |
| `blueprint.py` orchestrator | `pdf_generator.py`, Flutter client | Returns `ReportDataDTO` (unchanged contract) |

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Foundation — New Directory Structure & Base Adapter

**Target Directory**: `backend_v2/services/sdui/adapters/`

#### [NEW] `@[c:\src\quorum\backend_v2\services\sdui\__init__.py]`
Empty package init file.

#### [NEW] `@[c:\src\quorum\backend_v2\services\sdui\adapters\__init__.py]`
Empty package init file.

#### [NEW] `@[c:\src\quorum\backend_v2\services\sdui\adapters\base_adapter.py]`
Defines the abstract base class `BaseSduiAdapter` with a single abstract `build()` classmethod returning `list[AnySduiBlock]`. All concrete adapters inherit from this. Estimated size: 20-30 lines.

### Phase 2: Extract XAI Highlights Adapter (Proof of Concept)

#### [NEW] `@[c:\src\quorum\backend_v2\services\sdui\adapters\xai_highlights_adapter.py]`
This file contains BOTH the aesthetic rules AND the adapter logic for the XAI highlights report section. Structure:
1. **Module-Level Rules Dictionary** (`XAI_AESTHETICS_RULES`): Maps extension type keywords to `{"accordion_severity": str, "icon_name": str, "alert_severity": str}` tuples. Replaces the hardcoded `if "risk" in lower_ext` chains.
2. **`XaiHighlightsAdapter(BaseSduiAdapter)` class**: Single `build()` classmethod that accepts `synthesis_cache`, `profile`, and `locale`, groups `XaiHighlightItem` instances by `extension_type`, looks up aesthetics from the rules dictionary, and returns `list[AnySduiBlock]`.

Estimated size: 60-80 lines.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\blueprint.py]`
- Delete `_hydrate_grouped_extensions_block` method (lines 781-859, approximately 80 lines).
- Replace its call site in `_build_layouts` / `build_report_dto` with `XaiHighlightsAdapter.build(...)`.

### Phase 3: Extract Penalties Adapter

#### [NEW] `@[c:\src\quorum\backend_v2\services\sdui\adapters\penalties_adapter.py]`
1. **Module-Level Rules**: Penalty prefix mapping and severity constants.
2. **`PenaltiesAdapter(BaseSduiAdapter)` class**: Accepts `penalties_applied: list[str]`, returns `list[AnySduiBlock]` (specifically `AlertBlock` with `CRITICAL_OVERRIDE` severity).

Estimated size: 30-40 lines.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\blueprint.py]`
- Delete `_hydrate_penalties_block` method (lines 747-763).
- Replace with `PenaltiesAdapter.build(...)`.

### Phase 4: Extract Executive Summary Adapter

#### [NEW] `@[c:\src\quorum\backend_v2\services\sdui\adapters\executive_summary_adapter.py]`
1. **Module-Level Rules**: User role prefix labels, paragraph styling constants.
2. **`ExecutiveSummaryAdapter(BaseSduiAdapter)` class**: Accepts `profile_cache`, `profile`, and `locale`. Produces the executive summary `ParagraphBlock`, user role `ParagraphBlock`, and user role justification `ParagraphBlock`.

Estimated size: 50-70 lines.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\blueprint.py]`
- Delete inline executive summary construction logic (lines 1072-1095).
- Replace with `ExecutiveSummaryAdapter.build(...)`.

### Phase 5: Extract Remaining Placeholder Adapters

#### [NEW] `@[c:\src\quorum\backend_v2\services\sdui\adapters\audit_trail_adapter.py]`
Replaces the empty `_hydrate_audit_trail_block` placeholder. Estimated size: 20-30 lines.

#### [NEW] `@[c:\src\quorum\backend_v2\services\sdui\adapters\jargon_ratio_adapter.py]`
Replaces the empty `_hydrate_jargon_ratio_block` placeholder. Estimated size: 20-30 lines.

#### [NEW] `@[c:\src\quorum\backend_v2\services\sdui\adapters\printable_sources_adapter.py]`
Replaces the empty `_hydrate_printable_sources_block` placeholder. Estimated size: 20-30 lines.

#### [NEW] `@[c:\src\quorum\backend_v2\services\sdui\adapters\global_score_adapter.py]`
Replaces the empty `_hydrate_global_score_block` placeholder. Estimated size: 20-30 lines.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\blueprint.py]`
- Delete all four placeholder `_hydrate_*` methods (lines 765-779).
- Replace with adapter calls.

### Phase 6: Decompose `_extract_matrices_and_extensions` God Method

> [!WARNING]
> This is the most complex and highest-risk phase. It decomposes the 530-line method into dedicated components. This phase MUST be executed with extreme caution, running the full backend audit loop after each sub-step.

#### [NEW] `@[c:\src\quorum\backend_v2\services\sdui\matrix_extractor.py]`
1. **Module-Level Rules**: Scale display constants, visual intent mappings.
2. **`MatrixExtractorService` class**: Contains the core matrix parsing logic currently in `_extract_matrices_and_extensions`. Specifically:
   - LLM trace parsing and `TraceMatrixPayloadDTO` validation.
   - Score normalization and `ui_plot_ratio` calculation.
   - Scale label resolution and `level_names` mapping.
   - `MatrixScorecardRowDTO` construction.
   - `ScorecardAtomDTO` assembly from evaluation data.
*Architectural Note: This is explicitly NOT an SDUI Adapter because it returns `tuple[list[MatrixScorecardRowDTO], ...]`, not `list[AnySduiBlock]`. It sits one layer above the adapters in the `sdui` module.*

Estimated size: 200-250 lines (the irreducible complexity of matrix parsing).

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\blueprint.py]`
- Delete `_extract_matrices_and_extensions` (lines 218-745).
- Replace with `MatrixExtractorService.extract(...)` call in `build_report_dto`.
- `blueprint.py` is reduced to approximately 800-900 lines (from 1815).

### Phase 7: Verification & E2E Integration Gate

- Run full `backend_audit_loop.py --test` (Ruff, MyPy strict, Pytest with coverage).
- Verify PDF output via `pdf_generator.py` renders identically.
- Verify no Flutter Freezed changes required (JSON contract parity).

---

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
1. `blueprint.py` contains ZERO direct `AccordionBlock`, `AlertBlock`, or `ParagraphBlock` instantiation. All SDUI block construction is delegated to adapters.
2. `blueprint.py` is reduced from 1815 lines to approximately 800-900 lines.
3. Every adapter file in `backend_v2/services/sdui/adapters/` is self-contained: it has its own module-level rules dictionary AND its own adapter class.
4. No adapter file exceeds 250 lines.
5. All existing 1173 unit tests pass without modification.
6. MyPy strict passes with zero new `# type: ignore` annotations.
7. The `ReportDataDTO` JSON output is byte-identical before and after refactoring (verified by snapshot testing).

### Automated Unit Tests
```bash
uv run python scripts/backend_audit_loop.py backend_v2 --test
```

New unit tests to be added:
- `backend_v2/tests/unit/test_xai_highlights_adapter.py`: Tests aesthetic rule lookup independently (no Blueprint dependencies).
- `backend_v2/tests/unit/test_penalties_adapter.py`: Tests penalty block construction independently.
- `backend_v2/tests/unit/test_executive_summary_adapter.py`: Tests summary block construction independently.

### Manual Verification Steps
1. Run a full execution and generate a PDF report. Visually compare against `@[c:\src\quorum\docs\jwvastaus\raportti 2.pdf]` to confirm identical output.
2. Verify the Flutter app renders the report identically (no Dart changes, same JSON contract).

### MANDATORY Final E2E REST API Verification Gate
```bash
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

---

## 5. Knowledge Item Mandate

This Epic introduces a new architectural pattern (Self-Contained SDUI Adapter with Co-Located Rules). Upon completion, a new Knowledge Item MUST be created:
- **KI Name**: `sdui_adapter_decomposition`
- **Summary**: Documents the Self-Contained Adapter Pattern where each report output block has its own file containing co-located aesthetic rules and adapter logic within `backend_v2/services/sdui/adapters/`.
