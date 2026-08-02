# EPIC 130: Blueprint Transformer Decomposition into Modular SDUI Adapters

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
>
> Modern SDUI (Server-Driven UI) architecture in 2025-2026 mandates that the backend constructs explicit UI component blocks and ships them to thin rendering clients. Industry best practice (Clean Architecture + Interface Adapter Layer) dictates that the transformation from domain data to UI blocks MUST be isolated in dedicated **Presentation Adapters** — not inlined in a monolithic orchestrator. The "Anti-Corruption Layer" (ACL) pattern prevents dynamic JSON schemas from infecting business logic. Component-Based Decomposition ("Lego Blocks") treats each UI element as an independent, self-contained module encapsulating its own rendering rules and adapter logic. This Epic applies these principles to decompose `blueprint.py`'s God Method into modular, self-contained adapter files.

---

## 1. Goal Description & Background (Objective & Problem Statement)

### Business Objective
Decompose the monolithic `BlueprintTransformer` service (@[c:\src\quorum\backend_v2\services\blueprint.py#L70-L2012]) from a 1815-line God Class into a clean, modular architecture where each report output block (executive summary, XAI extensions, penalties, matrices, audit trail, jargon ratio, printable sources) is handled by its own self-contained adapter file within a new `backend_v2/services/sdui/adapters/` directory.

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
- **Missing Adapter Layer (Root Cause 3):** The system lacks a dedicated Presentation Adapter layer between domain DTOs (specifically ALL input state models mapped from the execution trace) and SDUI view models (specifically ALL presentation models inheriting from the `AnySduiBlock` discriminated union defined in `models/view/sdui.py`). `blueprint.py` currently acts as both orchestrator AND adapter.
- **Untestable Theming Logic (Root Cause 4):** To test whether a "risk_flag" extension gets a "warning" severity and "balance" icon, a developer must mock 7+ repository dependencies and run the entire `build_report_dto` pipeline. The theming logic is not independently testable.

### Strategic Scope
This Epic introduces a **self-contained adapter pattern** where each report output block is a single Python file containing BOTH its aesthetic rules (as a module-level dictionary) AND its adapter class (with a single `build()` method). The orchestrator (`blueprint.py`) is reduced to a thin dispatcher that calls each adapter in sequence. No new external dependencies are introduced.

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)
- **Inline Presentation Logic in `blueprint.py`**: All `if "risk" in lower_ext` chains, icon/severity selection logic, and direct `AccordionBlock`/`AlertBlock` instantiation inside `_hydrate_grouped_extensions_block`, `_hydrate_penalties_block`, and the inline executive summary construction (lines 1072-1095) will be INTENTIONALLY MOVED to their respective adapter files.
- **`_extract_matrices_and_extensions` God Method**: This 530-line method will be decomposed. Matrix parsing logic moves to a dedicated `matrix_extractor.py` service. Extension accumulation moves to `xai_highlights_adapter.py`. The remaining structural validation stays in a leaner `_parse_matrix_trace_results` orchestration method inside `blueprint.py`.
- **Placeholder Methods**: The empty placeholder methods `_hydrate_global_score_block`, `_hydrate_audit_trail_block`, and `_hydrate_jargon_ratio_block` (lines 765-779) will remain deferred until actual logic is introduced. The `_hydrate_printable_sources_block` is extracted to its own adapter.

### Retained SSOT Invariants (What We Will RETAIN)
- **Existing Pydantic DTOs**: `MatrixScorecardRowDTO`, `XaiHighlightItem`, `ReportLayoutDTO`, `ReportDataDTO`, and all models in `@[c:\src\quorum\backend_v2\models\view\sdui.py]` remain completely unchanged. No fields are added, removed, or renamed.
- **`build_report_dto` Orchestration Contract**: The public async method signature and return type (`ReportDataDTO`) remain identical. External callers (specifically `@[c:\src\quorum\backend_v2\services\pdf_generator.py]` and `@[c:\src\quorum\backend_v2\api\routers\execution\report.py]`) require zero changes.
- **SDUI Polymorphic Serialization**: `AnySduiBlock` discriminated union remains the SSOT for all UI blocks.
- **Strict ICU Markdown Parity**: The Jinja template (`@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`) continues to render via `render_sdui_blocks()` macro unchanged.
- **Flutter Frontend**: No Dart/Freezed changes required. The JSON contract between backend and frontend remains byte-identical.

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
| Service `matrix_extractor.py` | `blueprint.py` orchestrator | Returns `MatrixExtractionResultDTO` (Strict Pydantic V2 DTO replacing naked tuple/dict state passing) |
| `blueprint.py` orchestrator | `pdf_generator.py`, Flutter client | Returns `ReportDataDTO` (unchanged contract) |

### Namespace Clarification
- **`backend_v2/services/sdui_mapper_service.py`** remains at its current location. It handles a different concern (Report View mapping for the Flutter SDUI client) than the adapter layer (individual block construction). These are intentionally separate namespaces and MUST NOT be merged.

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Foundation — New Directory Structure, Typed Protocol & AdapterContext DTO
**Target Directory**: `backend_v2/services/sdui/adapters/`
1. Create `@[c:\src\quorum\backend_v2\services\sdui\__init__.py]`
2. Create `@[c:\src\quorum\backend_v2\services\sdui\adapters\__init__.py]`
3. Create `@[c:\src\quorum\backend_v2\services\sdui\adapters\base_adapter.py]` defining:
   - A frozen Pydantic DTO `AdapterContext` containing the strictly typed fields that adapters need (specifically: `execution: ExecutionRecord`, `locale: str`, `penalties_applied: list[str]`, `mcp_audit_data: list[MCPAuditTrace]`, `global_score: float | None`, `accumulated_extensions: dict[str, list[AnySduiBlock]]`, `profile: OutputProfile`).
   - **MANDATORY**: `AdapterContext` MUST use `model_config = ConfigDict(frozen=True, strict=True, extra="forbid")` to adhere to the `frozen_state_mutability` invariant, preventing downstream side effects.
   - A `Protocol` class `SduiAdapterProtocol` with a single `@staticmethod build(context: AdapterContext) -> list[AnySduiBlock]` method.
   - **MANDATORY**: The dispatch table in `blueprint.py` (`_target_block_hydrators`) MUST be updated from `Callable[..., list[AnySduiBlock]]` to `dict[str, type[SduiAdapterProtocol] | Callable[..., list[AnySduiBlock]]]` to enforce typed dispatch while allowing a safe iterative transition state without breaking `mypy`.
4. **MANDATORY CODE QUALITY GATE**: All adapter files MUST:
   - Include negative tests for `AdapterContext` that explicitly assert `pytest.raises(ValidationError)` when attempting to pass unexpected kwargs or mutate frozen fields, to mathematically guarantee `extra="forbid"` and `frozen=True` mutability locks work natively in Rust.
   - Place ALL imports at the top of the file (no inline imports) and explicitly define them (no ambiguous "e.g." shorthand).
   - Use typed exception handlers (specifically `except ValueError`, `except ValidationError`, or `except KeyError`) — bare `except Exception:` is strictly forbidden.
   - Use `VisualIntent` enum values for severity parameters — bare string literals with `# type: ignore[arg-type]` are strictly forbidden.
   - Use strict dictionary key access (`RULES[key]`) — `.get(key, default)` fallbacks are strictly forbidden.

### Phase 2: Extract XAI Highlights Adapter (Proof of Concept)
1. Create `@[c:\src\quorum\backend_v2\services\sdui\adapters\xai_highlights_adapter.py]`.
   - **MANDATORY**: Lookups for aesthetics MUST use strict dictionary key access (specifically `XAI_AESTHETICS_RULES[extension_type]`). Fallbacks using `.get()` are strictly forbidden to ensure Fail-Fast `KeyError` crashes on unknown extension types.
   - **MANDATORY**: All imports MUST be explicitly listed at the top of the file without ambiguity. You MUST explicitly import `AppException`, `VisualIntent`, and `ErrorCodes`. The inline import `from backend_v2.models.enums import XaiExtensionType` MUST be moved to the top.
2. Modify `@[c:\src\quorum\backend_v2\services\blueprint.py#L830-L841]`: Delete `_hydrate_grouped_extensions_block` and route to the new adapter using `build(context)`.
   - **NOTE**: The actual complex `_add_ext` closure (where extensions are accumulated) lives inside the God Method. Extraction of `_add_ext` belongs to **Phase 6**. Phase 2 only extracts the simple flat-mapping done in `_hydrate_grouped_extensions_block`.
3. **ATOMIC TEST MIGRATION**: You MUST physically move all existing tests related to `_hydrate_grouped_extensions_block` from `@[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py]` into a new `@[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_xai_highlights_adapter.py]` file. You MUST NOT mock or delete the old tests.
   - **MANDATORY NEGATIVE TESTS**: You MUST write a negative test asserting that an unknown extension triggers `AppException` (coercion failure) and another asserting that an unmapped aesthetic key triggers a native `KeyError`.

### Phase 3: Extract Penalties Adapter
1. Create `@[c:\src\quorum\backend_v2\services\sdui\adapters\penalties_adapter.py]`.
   - Create a `PenaltiesAdapter` class with a static method `build(context: AdapterContext) -> list[AnySduiBlock]`.
   - Move the exact logic from `_hydrate_penalties_block` into this method.
   - Ensure strict typing and imports for `AnySduiBlock`, `AlertBlock`, and `VisualIntent`.
2. Modify `@[c:\src\quorum\backend_v2\services\blueprint.py#L784-L800]`:
   - Import `PenaltiesAdapter` and wire it into the `_target_block_hydrators` registry in `__init__`.
   - Delete `_hydrate_penalties_block` entirely.
3. **ATOMIC TEST MIGRATION**: You MUST physically move all existing tests related to `_hydrate_penalties_block` from `@[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py]` into a new `@[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_penalties_adapter.py]` file. You MUST NOT mock or delete the old tests.
   - **MANDATORY NEGATIVE TESTS**: Assert that `AdapterContext` correctly raises `ValidationError` if `penalties_applied` is entirely missing from instantiation, and that passing an empty list `[]` safely returns `[]` from the adapter.
   - **Positive Test**: Assert string mapping into `AlertBlock(severity=VisualIntent.CRITICAL_OVERRIDE)`.

### Phase 4: Extract Executive Summary Adapter
1. Create `@[c:\src\quorum\backend_v2\services\sdui\adapters\executive_summary_adapter.py]`.
   - **Strict Role Validation:** Enforce `RoleClassification(context.profile.user_role)`. Catch `ValueError` and raise `AppException`. No `except Exception:` duct-tape.
   - **Fail-Fast L10N Prefix:** Enforce `context.profile.user_role_label.resolve(context.locale)`. If `user_role_label` is missing, raise a Fail-Fast `AppException` rather than hardcoding English `"User Role"`.
   - **MANDATORY**: The bare `except Exception:` catch-all currently at [blueprint.py#L1086](file:///c:/src/quorum/backend_v2/services/blueprint.py#L1086) MUST be replaced with a typed handler (specifically `except KeyError` or `except ValueError`).
2. Modify `@[c:\src\quorum\backend_v2\services\blueprint.py#L1072-L1095]`: 
   - Delete inline summary logic and route to `ExecutiveSummaryAdapter.build(context)`.
3. **ATOMIC TEST MIGRATION**: You MUST physically move all existing tests related to the executive summary from `@[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py]` into a new `@[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_executive_summary_adapter.py]` file. You MUST NOT mock or delete the old tests.
   - **MANDATORY NEGATIVE TESTS**: Assert invalid `user_role` string triggers `AppException`. Assert missing `user_role_label` triggers `AppException`.

### Phase 5: Extract Printable Sources Adapter
1. Create `@[c:\src\quorum\backend_v2\services\sdui\adapters\printable_sources_adapter.py]`.
   - Create a `PrintableSourcesAdapter` class with a static method `build(context: AdapterContext) -> list[AnySduiBlock]`.
   - Move the logic from `_hydrate_printable_sources_block` into this method.
2. Modify `@[c:\src\quorum\backend_v2\services\blueprint.py#L814-L828]`:
   - Import `PrintableSourcesAdapter` and wire it into the `_target_block_hydrators` registry in `__init__`.
   - Delete `_hydrate_printable_sources_block` entirely.
3. **ATOMIC TEST MIGRATION**: You MUST physically move any tests related to `_hydrate_printable_sources_block` into a new `@[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_printable_sources_adapter.py]` file.

### Phase 5a: DEFERRED — Placeholder Adapters (No Extraction Until Real Logic Exists)
**STATUS: DEFERRED.** The methods `_hydrate_global_score_block`, `_hydrate_audit_trail_block`, and `_hydrate_jargon_ratio_block` at [blueprint.py#L765-L779](file:///c:/src/quorum/backend_v2/services/blueprint.py#L765-L779) are currently empty placeholders returning `[]` or dummy text. Extracting empty methods into separate adapter files is pure churn with zero architectural value.

**STRICT EXECUTION DIRECTIVE:**
- The execution agent MUST NOT attempt to extract or touch `_hydrate_global_score_block`, `_hydrate_audit_trail_block`, or `_hydrate_jargon_ratio_block` during this phase.
- Simply acknowledge this deferral and immediately proceed to Phase 6 or complete the current execution step.

### Phase 6: Decompose `_extract_matrices_and_extensions` God Method
1. Create a `MatrixExtractionContext` Pydantic model (`ConfigDict(frozen=True, strict=True, extra='forbid')`) in `@[c:\src\quorum\backend_v2\models\state.py]` to encapsulate the exact parameters of the God Method per the `structured_state_envelopes_mandate`. You MUST explicitly include these fields with their exact types: `results: list[StepOutputDTO]`, `locale: str`, `blocks_by_id: dict[str, PromptBlock]`, `workflow_steps: dict[str, V2StepDTO]`, `profile: OutputProfile`, `row_explanations_cache: dict[str, str]`, `workflow_ext_values: list[str]`, `row_curated_quotes_cache: dict[str, list[str]]`, `has_synthesis_cache: bool`, `rejected_evq_ids: set[str] | None`, `mcp_audit_map: dict[str, MCPAuditTrace] | None`, `source_identity_manifest: dict[str, str] | None`, `execution: ExecutionRecord | None` (Note: the use of `Any` is strictly forbidden).
2. Create `@[c:\src\quorum\backend_v2\services\sdui\matrix_extractor.py]` containing a **stateless utility class** `MatrixExtractorService` with a single `@staticmethod extract(context: MatrixExtractionContext) -> MatrixExtractionResultDTO`.
   - **Return type (exact)**: `MatrixExtractionResultDTO` (A frozen Pydantic DTO to enforce `no_naked_dicts_in_state`).
   - **MANDATORY**: You MUST define `MatrixExtractionResultDTO` in `backend_v2/models/state.py` containing strictly typed fields for `evaluative_matrices`, `informational_matrices`, `all_parsed_matrices`, `step_scorecard_atoms`, and `accumulated_extensions: dict[str, list[AnySduiBlock]]`. You are responsible for extracting the `_add_ext` closure from `blueprint.py` into this service.
   - **MANDATORY**: The `severity` strings at [blueprint.py#L715-L723](file:///c:/src/quorum/backend_v2/services/blueprint.py#L715-L723) inside the `_add_ext` closure MUST be replaced with `VisualIntent` enum values. The `except ValueError:` block at [blueprint.py#L757](file:///c:/src/quorum/backend_v2/services/blueprint.py#L757) MUST log the failure (`logger.error`) BEFORE re-raising `AppException(ErrorCodes.VALIDATION_FAILED)`.
   - **MANDATORY**: Strict parsing of LLM trace output (`TraceMatrixPayloadDTO`) using Pydantic `TypeAdapter` or `.model_validate()`. No `isinstance` dictionary fallbacks.
3. Modify `@[c:\src\quorum\backend_v2\services\blueprint.py#L218-L745]`: Delete the 530-line God Method and replace with a call to `MatrixExtractorService.extract(context)`.
4. **ATOMIC TEST MIGRATION**: You MUST physically move all existing tests related to `_extract_matrices_and_extensions` from `test_blueprint.py` into a new `test_matrix_extractor.py` file, updating them to directly test `MatrixExtractorService.extract()`. Additionally, you must write new negative tests asserting that missing fields and improperly structured payload dictionaries trigger Fail-Fast `AppException` / `ValidationError` per the `anti_happy_path_mandate`. You MUST NOT simply mock or delete the old tests in `test_blueprint.py`, as that would destroy test coverage.

### Phase 7: Verification & E2E Integration Gate

1. Run backend tests: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
2. Run frontend compilation: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`
3. Execute parity check: `uv run python scripts/run_e2e_variance_test.py`

---

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
1. `blueprint.py` contains ZERO direct `AccordionBlock`, `AlertBlock`, `ParagraphBlock`, or `MarkdownBlock` instantiation for the extracted adapters.
2. `blueprint.py` is reduced from 1815 lines to approximately 1000-1100 lines.
3. Every adapter file in `backend_v2/services/sdui/adapters/` is self-contained: it has its own module-level rules dictionary and strictly uses explicit Key-Access (`RULES[key]`) rather than `.get()`.
4. **Atomic Test Migration**: Any tests previously asserting on private methods are updated in the exact same phase. No test suite breakage between phases.
5. The `ReportDataDTO` JSON output is byte-identical before and after refactoring (verified by snapshot testing).
6. MyPy strict passes with zero new `# type: ignore` annotations.
7. Zero bare `except Exception:` catch-alls in any adapter file. All exception handlers MUST use typed exceptions and explicitly state them in the `Raises:` section of the Google-style docstring.
8. The word "Epic" (or "EPIC") does NOT appear in any added code, docstrings, or comments.
9. Zero inline imports in any adapter file. All imports MUST be at the top of the file.
10. The dispatch table `_target_block_hydrators` uses `dict[str, type[SduiAdapterProtocol] | Callable[..., list[AnySduiBlock]]]` to enforce typed dispatch while supporting deferred placeholders.

### Automated Unit Tests
```bash
uv run python scripts/backend_audit_loop.py backend_v2 --test
```

New unit tests to be added:
- `backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py`: Tests aesthetic rule lookup independently (no Blueprint dependencies).
- `backend_v2/tests/unit/services/sdui/adapters/test_penalties_adapter.py`: Tests penalty block construction independently.
- `backend_v2/tests/unit/services/sdui/adapters/test_executive_summary_adapter.py`: Tests summary block construction independently.
- `backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_adapter.py`: Tests printable sources formatting independently.
- `backend_v2/tests/unit/services/sdui/test_matrix_extractor.py`: Tests matrix extraction independently.

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
