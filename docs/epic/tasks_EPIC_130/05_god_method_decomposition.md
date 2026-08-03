# Phase 6A: Decompose God Method & XAI Highlights Adapter

**Overview:** We pivot from a monolithic extraction service to a true Dumb Painter pattern by extracting the XAI extension logic from the God Method directly into the `XaiHighlightsAdapter`. 
*Note: The MatrixGraphsAdapter extraction has been deferred to Phase 6B because it requires re-architecting `AdapterContext` to support per-layout instantiation (to remove the 3D-to-2D "duct tape" fallbacks).*

**Target Files:**
- @[c:\src\quorum\backend_v2\services\sdui\adapters\xai_highlights_adapter.py]
- @[c:\src\quorum\backend_v2\services\blueprint.py]
- @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_xai_highlights_adapter.py]
- @[c:\src\quorum\backend_v2\models\enums.py]
- @[c:\src\quorum\backend_v2\services\sdui\adapters\base_adapter.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by the previous phase. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    - [ ] `blueprint.py` contains ZERO direct `AccordionBlock`, `AlertBlock`, `ParagraphBlock`, or `MarkdownBlock` instantiation for XAI extensions.
    - [ ] `XaiHighlightsAdapter.py` is self-contained: it has its own module-level rules dictionary and strictly uses explicit Key-Access (`RULES[key]`) rather than `.get()`.
    - [ ] Atomic Test Migration: Any tests previously asserting on private XAI methods in `test_blueprint.py` are migrated.
    - [ ] MyPy strict passes with zero new `# type: ignore` annotations.
    - [ ] Zero bare `except Exception:` catch-alls in any adapter file.
    - [ ] Zero "duct-tape" fallbacks (specifically: `except ValueError: pass` has been eradicated).
  </dod_checklist>

  <anti_targets>
    - `backend_v2/models/view/sdui.py` (Do not modify the SDUI models)
    - `backend_v2/services/execution.py`
  </anti_targets>

  <step id="1" name="BLOCKING PREREQUISITE: Cross-reference Seed Data">
    <action>Use `grep_search` to enumerate ALL extension type strings in `c:\src\quorum\backend_v2\seed\seed_data.json`.</action>
    <action>Verify they exist in `XaiExtensionType` enum in `backend_v2/models/enums.py`. If any are missing, add them to the enum first.</action>
  </step>

  <step id="2" name="REFACTOR XaiHighlightsAdapter (NO DUCT TAPE)">
    <action>Refactor `XaiHighlightsAdapter` in `c:\src\quorum\backend_v2\services\sdui\adapters\xai_highlights_adapter.py` to completely parse extensions natively from `context.execution.results`.</action>
    <action>Replace bare string severity literals (specifically: "info", "success", "error", "warning") with `VisualIntent` enum values.</action>
    <demolish>REMOVE the duct-tape fallback: Delete `except ValueError: pass` in the extension parsing logic. REPLACE WITH: `logger.error` + `raise AppException(..., details={"error_code": ErrorCodes.VALIDATION_FAILED.value}) from v_err`.</demolish>
    <constraint>ZERO DUCT-TAPE FALLBACKS: The adapter must fail fast on malformed extensions. No silent swallowing of errors.</constraint>
    <action>Ensure strict attribute access (no `hasattr` or default `getattr`).</action>
  </step>

  <step id="3" name="REFACTOR blueprint.py: Strip God Method">
    <action>In `c:\src\quorum\backend_v2\services\blueprint.py`, rename `_extract_matrices_and_extensions` to `_parse_matrix_trace_results`.</action>
    <action>Remove the `accumulated_extensions` dict and the entire `_add_ext` closure from this method. The method should now purely focus on structural validation and returning `evaluative_matrices, informational_matrices, all_parsed_matrices, step_scorecard_atoms`.</action>
    <action>Remove `accumulated_extensions` from `AdapterContext`.</action>
    <constraint>DO NOT extract Matrix graphs or tables yet. They remain in `_build_visualization_blocks` until `AdapterContext` is redesigned to support per-layout instantiation.</constraint>
  </step>

  <step id="4" name="MIGRATE TESTS">
    <action>Migrate XAI tests from `test_blueprint.py` to `test_xai_highlights_adapter.py`.</action>
    <action>Add negative tests for the new strict ValueError crash in XaiHighlightsAdapter.</action>
  </step>

  <test_contracts>
    <test name="test_build_unknown_extension_raises_app_exception" category="error_path">
      <input>AdapterContext with trace payload containing unknown extension string</input>
      <expected>raises AppException (Fail-Fast, no fallback)</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/sdui/adapters/ --test`</action>
    <action>Run backend audit loop on blueprint: `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test`</action>
  </validation_gate>
</execution_protocol>
