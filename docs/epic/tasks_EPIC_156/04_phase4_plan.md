# Phase 4: Universal AST Strictness Lockdown, Mathematical Proof & Permanent CI Enforcement

**Overview:** Lock strict mode as the permanent default in all quality gates, reclassify all AST visitor rules unconditionally to FATAL severity, verify the Exhaustive Violation Eradication Ledger, assert clean imports and DTO parity, and mathematically prove zero warnings across all 896 backend files.

**Source:** `@[docs/epic/EPIC_156_Universal_AST_Strictness_and_Advisory_Warning_Eradication.md#L315-L337]`

**Target Files:**
- `[MODIFY]` `@[scripts/backend_audit_loop.py#L282-L468]`
- `[MODIFY]` `@[scripts/_ast_guardrails.py#L351-L370]`, `@[scripts/_ast_guardrails.py#L405-L440]`, `@[scripts/_ast_guardrails.py#L665-L710]`, `@[scripts/_ast_guardrails.py#L770-L794]`, `@[scripts/_ast_guardrails.py#L1130-L1155]`, `@[scripts/_ast_guardrails.py#L1255-L1270]`, `@[scripts/_ast_guardrails.py#L1417-L1430]`, `@[scripts/_ast_guardrails.py#L1475-L1485]`, `@[scripts/_ast_guardrails.py#L1487-L1528]`
- `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_backend_audit_loop.py#L150-L215]`
- `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L684-L695]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L889-L927]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L942-L970]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1005-L1018]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1090-L1105]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1205-L1215]`
- `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py#L50-L120]`

**Context Files:**
- `[READ-ONLY]` `@[docs/epic/EPIC_156_Universal_AST_Strictness_and_Advisory_Warning_Eradication.md#L315-L376]`
- `[READ-ONLY]` `@[docs/epic/EPIC_156_tracker.md#L74-L81]`
- `[READ-ONLY]` `@[scripts/audit_warning_baseline.py]`
- `[READ-ONLY]` `@[scripts/audit_clean_imports.py]`
- `[READ-ONLY]` `@[scripts/audit_dto_parity.py]`
- `[READ-ONLY]` `@[scripts/audit_mutation_coverage.py]`
- `[READ-ONLY]` `@[backend_v2/tests/unit/scripts/test_clean_imports.py]`
- `[READ-ONLY]` `@[backend_v2/tests/unit/scripts/test_audit_mutation_coverage.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[scripts/backend_audit_loop.py#L320-L355]` | Opt-in `--ast-strict` CLI flag allowing advisory AST warnings to bypass local audit loop executions unless explicitly flagged. | Invert argument parsing default so that `ast_strict` defaults to `True` unconditionally; provide temporary `--permissive-warn` flag (`action="store_false", dest="ast_strict"`) for emergency diagnostics only per `universal_fail_fast`. | Pruned complex dynamic flag inheritance trees; implement direct boolean argument mapping in `argparse.ArgumentParser`. | `uv run python scripts/backend_audit_loop.py backend_v2/services/execution.py` (executes strict AST validation by default without flags). |
| `@[scripts/_ast_guardrails.py#L351-L370]`, `@[scripts/_ast_guardrails.py#L405-L1528]` | Permissive WARNING severity assignments for QGR013, QGR015, boundary exemption files, and test files allowing soft warnings to accumulate without breaking builds. | Reclassify all 12 visitor methods and `_add_violation` default parameter in `QuorumGuardrailVisitor` to assign FATAL severity unconditionally, ensuring every architectural violation emits fatal severity per `the_zero_compromise_pledge`. | Pruned conditional severity branching based on boundary exemption or test file status; instantiate `GuardrailViolation` with invariant FATAL severity. | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` (asserts 0 fatal errors, 0 warnings across all 896 modules). |
| `@[backend_v2/tests/unit/scripts/test_backend_audit_loop.py#L150-L215]` | Test cases asserting that `backend_audit_loop.py` ignores warnings by default in advisory mode without flags. | Update test cases to assert that `backend_audit_loop.py` enforces strict AST validation by default, that `--ast-strict` continues to enforce strict mode, and that advisory mode is triggered exclusively when `--permissive-warn` is passed (still failing on fatal violations). | Pruned redundant environment variable override fixtures; test direct CLI arguments via `sys.argv` mocking. | `uv run pytest backend_v2/tests/unit/scripts/test_backend_audit_loop.py` |
| `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L684-L1215]` | Test assertions expecting WARNING severity for QGR013 (TypeVar), QGR015 (TypeGuard), boundary exemption files, and test file duck-typing. | Update test assertions to assert FATAL severity for all QGR rules across all visitor evaluations, proving zero advisory warning emissions. | Pruned multi-severity matrix test fixtures; assert uniform fatal severity on all detected anti-patterns. | `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py` |
| `@[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py#L50-L120]` | Permissive warning tolerance assertions allowing nonzero baseline warning thresholds. | Lock test assertions to `CURRENT_WARNING_CEILING = 0` and verify that any nonzero warning count triggers `is_under_ceiling is False` under `--verify-zero`. | Pruned dynamic baseline migration math; enforce binary zero-defect validation. | `uv run pytest backend_v2/tests/unit/scripts/test_audit_warning_baseline.py` |

## Phase 4: Pre-Implementation Cleanups

All preparatory prerequisites across target files and test suites are quarantined and queued for pre-implementation verification:
1. **Strategic State Baseline Audit**: Verify that Phase 1 established QGR024, QGR025, clean imports, and the 8-stage audit loop, Phase 2 eradicated all 319 deceptive mocks, and Phase 3 eradicated all duct-tape anti-patterns (QGR020, QGR012, QGR016, QGR002, QGR001, QGR019, QGR003, QGR010) with 100% mutant kill rate on mathematical cores. Verified in Step 0.
2. **Audit Loop Strict Inversion (`scripts/backend_audit_loop.py#L320-L355`)**: Invert `ast_strict` parameter parsing to default to `True`, adding `--permissive-warn` flag for emergency diagnostics. Update docstrings and CLI examples (`#L1-L36`). Cleaned in Step 4.1.
3. **AST Guardrail Visitor Reclassification (`scripts/_ast_guardrails.py#L351-L1528`)**: Refactor `_add_violation` default parameter (`#L357`) and all 12 visitor method severity assignments (QGR001 in `#L408-L428`, QGR012 in `#L670-L687` and `#L1256-L1260`, QGR013 in `#L707`, QGR018 in `#L782-L786`, QGR016 in `#L1143-L1153` and `#L1504-L1526`, QGR015 in `#L1427` and `#L1483`) to assign FATAL severity unconditionally. Cleaned in Step 4.2.
4. **Ledger & Repository Verification (`scripts/audit_warning_baseline.py`)**: Assert 0 fatal violations and 0 warnings across all 896 modules in `backend_v2`. Verified in Step 4.3.
5. **Clean Imports, DTO Parity & Mutation Invariance**: Execute `audit_clean_imports.py`, `audit_dto_parity.py`, and `audit_mutation_coverage.py`. Verified in Step 4.4.
6. **Full Test Suite & Quality Gate Lockdown**: Execute `backend_audit_loop.py backend_v2 --test` in default strict mode through all 8 stages. Verified in Step 4.5.
7. **Mandatory Final E2E REST API Verification**: Execute live integration suite. Verified in Step 4.6.

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 1 established QGR024, QGR025, clean imports, and the 8-stage audit loop; Phase 2 eradicated all 319 deceptive repository persistence mocks in test suites; and Phase 3 eradicated all duct-tape rules (QGR020, QGR012, QGR016, QGR002, QGR001, QGR019, QGR003, QGR010) while achieving a 100% mutant kill rate on UnifiedScoringEngine and TopologicalEvaluator.</action>
    <action>Look forward: Verify updated codebase state before executing Phase 4 universal strictness lockdown: ensure all 896 modules pass strict AST guardrails with 0 fatal violations and 0 warnings before locking default strict execution flags.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_156_Universal_AST_Strictness_and_Advisory_Warning_Eradication.md]) and the Tracker document (@[docs/epic/EPIC_156_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_156/04_phase4_plan.md] @[docs/epic/EPIC_156_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>Invert default flag in scripts/backend_audit_loop.py: ast_strict=True by default, providing --permissive-warn for emergency diagnostics only.</item>
    <item>Reclassify all visitor methods in scripts/_ast_guardrails.py to unconditionally emit FATAL severity for all rules QGR000 through QGR025.</item>
    <item>Update unit test assertions in test_backend_audit_loop.py, test_ast_guardrails.py, and test_audit_warning_baseline.py to reflect strict defaults and fatal severity.</item>
    <item>Execute Exhaustive Violation Eradication Ledger: prove 0 FATAL errors and 0 WARNINGS across all 896 backend files via scripts/audit_warning_baseline.py --verify-zero.</item>
    <item>Execute full repository strict AST scan via uv run python scripts/_ast_guardrails.py backend_v2 --strict passing with 0 violations.</item>
    <item>Execute clean imports gate via uv run python scripts/audit_clean_imports.py passing with 0 circular dependencies across all 896 modules.</item>
    <item>Execute cross-language DTO parity gate via uv run python scripts/audit_dto_parity.py passing with 100% contract parity.</item>
    <item>Execute mutation testing gate via uv run python scripts/audit_mutation_coverage.py passing with 100% mutant kill rate on mathematical cores.</item>
    <item>Execute 8-stage backend audit loop via uv run python scripts/backend_audit_loop.py backend_v2 --test in default strict mode with 100% green status.</item>
    <item>Execute mandatory final live E2E REST API verification gate.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Permissive warning shims or fallback bypass flags in production quality gates.</anti_target>
    <anti_target>Altering established public API schemas or DTO serialization contracts.</anti_target>
    <anti_target>Allowing any AST visitor method to emit WARNING severity in domain or test scans.</anti_target>
    <anti_target>Permitting bifurcated execution pipelines or conditional strictness escapes.</anti_target>
  </anti_targets>

  <touched_artifacts>
    <backend>@[scripts/backend_audit_loop.py#L282-L468]</backend>
    <backend>@[scripts/_ast_guardrails.py#L351-L370]</backend>
    <backend>@[scripts/_ast_guardrails.py#L405-L440]</backend>
    <backend>@[scripts/_ast_guardrails.py#L665-L710]</backend>
    <backend>@[scripts/_ast_guardrails.py#L770-L794]</backend>
    <backend>@[scripts/_ast_guardrails.py#L1130-L1155]</backend>
    <backend>@[scripts/_ast_guardrails.py#L1255-L1270]</backend>
    <backend>@[scripts/_ast_guardrails.py#L1417-L1430]</backend>
    <backend>@[scripts/_ast_guardrails.py#L1475-L1485]</backend>
    <backend>@[scripts/_ast_guardrails.py#L1487-L1528]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_backend_audit_loop.py#L150-L215]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L684-L695]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L889-L927]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L942-L970]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1005-L1018]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1090-L1105]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1205-L1215]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py#L50-L120]</backend>
  </touched_artifacts>

  <step id="4.1" name="Invert Strict Default Flag in backend_audit_loop.py &amp; Add Permissive Diagnostic Mode">
    <action>Modify argument parsing in `@[scripts/backend_audit_loop.py#L320-L355]`: configure `ast_strict` to default to `True` unconditionally. Add `--permissive-warn` flag mapping to `action="store_false", dest="ast_strict"` for emergency diagnostics only.</action>
    <action>Update docstrings and CLI examples in `@[scripts/backend_audit_loop.py#L282-L468]` to document that AST strict mode executes by default on every invocation.</action>
    <action>Update CLI usage error message in `@[scripts/backend_audit_loop.py#L347-L350]` to reflect `[--permissive-warn]`.</action>
    <action>Update unit test cases in `@[backend_v2/tests/unit/scripts/test_backend_audit_loop.py#L150-L215]`: assert that invoking `backend_audit_loop.py` without flags executes strict AST validation (`strict=True`), assert that `--ast-strict` continues to enforce strict mode, assert that `--permissive-warn` enables advisory mode (`strict=False`), and verify that `--permissive-warn` still fails fast on FATAL violations.</action>
    <constraint invariant="universal_fail_fast">Default execution must fail fast on any unsuppressed AST violation without requiring explicit CLI flags.</constraint>
  </step>

  <step id="4.2" name="Reclassify All Visitor Rules to FATAL Severity in scripts/_ast_guardrails.py">
    <action>Modify `_add_violation` default parameter in `@[scripts/_ast_guardrails.py#L351-L370]`: set default severity to `GuardrailSeverity.FATAL`.</action>
    <action>Refactor all 12 visitor method locations assigning WARNING severity in `@[scripts/_ast_guardrails.py]`: reclassify QGR001 reflection in `visit_Attribute` (`#L405-L420`) and `visit_Call` (`#L422-L440`), QGR012 duck-typing in `visit_Call` (`#L669-L695`) and `visit_Match` (`#L1255-L1268`), QGR013 TypeVar in `visit_Call` (`#L696-L709`), QGR018 TypeAdapter in `visit_Call` (`#L771-L794`), QGR016 ternary fallback in `visit_IfExp` (`#L1143-L1153`), QGR015 TypeGuard in `visit_ImportFrom` (`#L1417-L1429`) and `visit_Name` (`#L1475-L1485`), and QGR016 lazy/chained fallbacks in `visit_BoolOp` (`#L1487-L1528`) to emit `GuardrailSeverity.FATAL` unconditionally across all visitor calls.</action>
    <action>Update unit test assertions in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`: update test cases for QGR013 (`#L684-L695`, `#L960-L970`), QGR012 (`#L889-L906`), boundary exemptions (`#L942-L950`, `#L1205-L1215`), QGR015 (`#L1005-L1018`), and QGR016 (`#L1090-L1105`) to assert `GuardrailSeverity.FATAL` instead of `GuardrailSeverity.WARNING`.</action>
    <constraint invariant="the_zero_compromise_pledge">All architectural rules defined in scripts/_ast_guardrails.py must unconditionally emit FATAL severity with zero advisory warning demotions.</constraint>
  </step>

  <step id="4.3" name="Execute Exhaustive Violation Eradication Ledger Verification">
    <action>Update unit test assertions in `@[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py#L50-L120]` to verify that any nonzero warning count fails under `verify_zero=True`.</action>
    <action>Execute baseline ledger verification: `uv run python scripts/audit_warning_baseline.py --verify-zero`.</action>
    <action>Mathematically verify that total unsuppressed fatal violations equals 0 and total advisory warnings equals 0 across all 896 backend modules.</action>
    <action>Execute full repository strict scan: `uv run python scripts/_ast_guardrails.py backend_v2 --strict`.</action>
    <action>Assert: 0 violations detected across 896 files. Strict mode PASS.</action>
    <constraint invariant="zero_naked_dicts_and_permissive_typing">Every single violation category in the Exhaustive Violation Eradication Ledger must be mathematically proven to have reached exactly 0 violations.</constraint>
  </step>

  <step id="4.4" name="Execute Clean Imports, DTO Parity, and Mutation Gates">
    <action>Execute Clean Module Import scan: `uv run python scripts/audit_clean_imports.py` asserting 100% clean module imports with zero circular dependencies across all 896 modules.</action>
    <action>Execute Cross-Language DTO Parity scan: `uv run python scripts/audit_dto_parity.py` asserting 100% schema parity between backend Pydantic models and frontend Freezed models.</action>
    <action>Execute Mathematical Core Mutation audit: `uv run python scripts/audit_mutation_coverage.py` asserting 100% mutant kill rate on UnifiedScoringEngine (25/25 killed) and TopologicalEvaluator (13/13 killed).</action>
    <constraint invariant="single_pipeline_invariant_mandate">All modules must load cleanly and all mathematical invariants must detect synthetic mutations with 100% kill rate.</constraint>
  </step>

  <step id="4.5" name="Full Test Suite &amp; 8-Stage Quality Gate Execution">
    <action>Execute full 8-stage universal quality gate in default strict mode: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.</action>
    <action>Verify Stage 1/8: Ruff check passes with zero errors.</action>
    <action>Verify Stage 2/8: Ruff format passes with zero formatting diffs.</action>
    <action>Verify Stage 3/8: MyPy strict passes across all modules with zero type errors.</action>
    <action>Verify Stage 4/8: AST Codebase Guardrails execute in default strict mode with zero violations.</action>
    <action>Verify Stage 5/8: UI template Dumb Painter validation passes with zero fallback expressions.</action>
    <action>Verify Stage 6/8: Seed Data Dry-Run and Database Atom audit execute with 100% pass rate.</action>
    <action>Verify Stage 7/8: Clean module imports execute with zero circular dependencies.</action>
    <action>Verify Stage 8/8: Cross-language DTO parity executes with zero contract discrepancies.</action>
    <action>Verify unit and integration test suite passes with 100% green status and greater than 90% branch and line coverage.</action>
    <constraint invariant="zero_tolerance_audit_loop">The entire 8-stage quality gate must execute and pass cleanly without skipping stages or bypassing coverage thresholds.</constraint>
  </step>

  <step id="4.6" name="Mandatory Final E2E REST API Verification Gate">
    <action>Execute live E2E REST API integration test suite under live environment flags:</action>
    <action>Windows (PowerShell): `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`</action>
    <action>Unix (Bash): `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`</action>
    <action>Assert: Full end-to-end workflow execution, trace generation, and output profile synthesis pass cleanly.</action>
    <constraint invariant="universal_fail_fast">Live REST API endpoints must validate end-to-end pipeline execution against live mock fixtures.</constraint>
  </step>

  <test_contracts>
    <test name="test_backend_audit_loop_defaults_to_strict" category="positive">
      <input>Invoke backend_audit_loop.py without --ast-strict or --strict flags.</input>
      <expected>scan_files_for_guardrails is invoked with strict=True; execution fails if any unsuppressed violation exists.</expected>
    </test>
    <test name="test_backend_audit_loop_permissive_warn_flag_allows_advisory_mode" category="positive">
      <input>Invoke backend_audit_loop.py with --permissive-warn flag.</input>
      <expected>scan_files_for_guardrails is invoked with strict=False; execution passes if only advisory warnings exist.</expected>
    </test>
    <test name="test_backend_audit_loop_fails_fast_on_any_unsuppressed_violation" category="negative">
      <input>Invoke backend_audit_loop.py without flags when an unsuppressed violation is detected.</input>
      <expected>Process terminates immediately with exit code 1 and formats violation table.</expected>
    </test>
    <test name="test_backend_audit_loop_permissive_warn_still_fails_on_fatal" category="negative">
      <input>Invoke backend_audit_loop.py with --permissive-warn when a FATAL violation is detected.</input>
      <expected>Process terminates immediately with exit code 1 due to fatal violation detection.</expected>
    </test>
    <test name="test_qgr013_qgr015_emit_fatal_severity" category="positive">
      <input>Scan code snippets containing TypeVar instantiation (QGR013) or TypeGuard annotation (QGR015).</input>
      <expected>Emitted GuardrailViolation instances have FATAL severity.</expected>
    </test>
    <test name="test_warning_baseline_ledger_rejects_any_nonzero_warning_violation" category="negative">
      <input>Execute generate_baseline_report with verify_zero=True on a dataset containing 1 unsuppressed violation.</input>
      <expected>report.is_under_ceiling is False, report.warning_count == 1, and report.warning_ceiling == 0.</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute full repository strict scan: `uv run python scripts/_ast_guardrails.py backend_v2 --strict` (Assert: 0 FATAL, 0 WARNING across 896 files)</action>
    <action>Execute baseline zero verification: `uv run python scripts/audit_warning_baseline.py --verify-zero`</action>
    <action>Execute clean module import scan: `uv run python scripts/audit_clean_imports.py`</action>
    <action>Execute cross-language DTO parity scan: `uv run python scripts/audit_dto_parity.py`</action>
    <action>Execute mathematical core mutation audit: `uv run python scripts/audit_mutation_coverage.py`</action>
    <action>Execute 8-stage audit loop across entire backend: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
    <action>Execute final live E2E REST API gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`</action>
  </validation_gate>
</execution_protocol>
```
