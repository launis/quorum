# Phase 7: Global Quality Gate & Final Verification

**Overview:** Execute Quorum's complete quality gate verification pipeline across all Python backend, Flutter client, AST guardrail, Theme Sovereignty, dictionary eradication, and Markdown boundary standards. Resolve pre-implementation technical debt in `dashboard_view.dart` regarding asynchronous BuildContext usage. Execute `scripts/backend_audit_loop.py` with strict AST and pytest validation, run `scripts/flutter_audit_loop.py` with the Freezed build runner, run `scripts/audit_flutter_theme_sovereignty.py` asserting zero raw colors or naked TextStyles, verify AST guardrail compliance via `scripts/_ast_guardrails.py` and `scripts/audit_dict_eradication.py`, execute markdown boundary auditing on all documents, and perform the live E2E REST API integration gate.

**Source:** @[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md] Section 3, Phase 7: Global Quality Gate & Final Verification

**Target Files:**
- `[MODIFY] @[client_app_v2/lib/features/execution/views/dashboard_view.dart#L464-L536]`
- `[VALIDATION] @[scripts/backend_audit_loop.py]`
- `[VALIDATION] @[scripts/flutter_audit_loop.py]`
- `[VALIDATION] @[scripts/audit_flutter_theme_sovereignty.py]`
- `[VALIDATION] @[scripts/_ast_guardrails.py]`
- `[VALIDATION] @[scripts/audit_dict_eradication.py]`
- `[VALIDATION] @[scripts/audit_markdown_boundaries.py]`
- `[VALIDATION] @[backend_v2/tests/integration/test_integration_real_llm.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[client_app_v2/lib/features/execution/views/dashboard_view.dart]` | Using `Localizations.localeOf(context).languageCode` across an asynchronous gap (`await dio.get`) without mounted check, triggering Dart analyzer `use_build_context_synchronously`. | Pre-fetch `final fallbackLocale = Localizations.localeOf(context).languageCode;` before the async network call, and verify `if (!context.mounted) return;` before UI mutations. | Refactoring the entire `DashboardView` state machine or creating complex helper delegates when localized inline pre-fetch solves the invariant cleanly. | `dart analyze client_app_v2/lib/features/execution/` returns zero issues for `use_build_context_synchronously`. |
| `@[scripts/backend_audit_loop.py]` | Skipping automated audit loops, omitting `--test` or `--ast-strict` flags, or claiming changes are too small to test. | Execute 10-stage automated audit testing: Ruff check and format, MyPy strict, AST guardrails, Jinja template validation, seed integrity, clean imports, DTO parity, baseline ledger, dict eradication, and Pytest with 90% TDD coverage. | Manual checklists without deterministic tooling or ad-hoc custom test runner scripts. | `uv run python scripts/backend_audit_loop.py backend_v2/ --test` exits code 0 with 0 lint, type, AST, or test failures. |
| `@[scripts/flutter_audit_loop.py]` | Running raw flutter test without Freezed model generation, ignoring Dart guardrails (DGR001-DGR005), or leaving analyzer warnings. | Execute 5-stage Flutter quality gate: code generation (`flutter gen-l10n`, `build_runner build -d`), Dart guardrails (`_dart_guardrails.py`), `dart format`, `dart analyze`, and `flutter test`. | Manual build runner commands or bypassing code generation in automated CI. | `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build` exits code 0. |
| `@[scripts/audit_flutter_theme_sovereignty.py]` | Hardcoded hex colors, raw `Color(0x...)`, `Colors.*`, or naked `TextStyle(...)` in widgets. | 100% Theme Sovereignty: all colors derive from `Theme.of(context).colorScheme` or `AppSemanticColors`, typography from `Theme.of(context).textTheme`. | Permissive visual linting suppressions or custom color wrappers outside the theme system. | `uv run python scripts/audit_flutter_theme_sovereignty.py client_app_v2/` exits code 0 with 0 violations. |
| `@[scripts/_ast_guardrails.py]` | Bare script execution without target arguments, raw dict fixtures violating `QGR029`, and naked dictionaries in state transit. | Static AST guardrail enforcement with explicit targets (`backend_v2/ --strict`), asserting zero naked dictionaries, Pydantic `extra='forbid'`, and Polyfactory fixtures. | Advisory-only warning suppressions or ad-hoc AST parsers duplicating the guardrail suite. | `uv run python scripts/_ast_guardrails.py backend_v2/ --strict` exits code 0 with 0 fatal violations. |
| `@[scripts/audit_dict_eradication.py]` | Loose dictionary annotations, nested Primitive Obsession dicts (`dict[str, dict[...]]`), duck-typing `isinstance(..., dict)`, unexempt `.get()` calls, or reflection. | Strict multi-layer AST scanning across all 12 metrics in `backend_v2` with `--strict` flag. | Permissive `# noqa` suppressions in domain code or shadow dictionary accumulators. | `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` exits code 0 with 100% mathematical zero violations. |
| `@[scripts/audit_markdown_boundaries.py]` | Ambiguous documentation ("e.g.", "etc.", "such as", "like"), missing `<action>` tags for table targets (MBD008), broken AST line bounds, or truncated XML blocks. | 100% compliance with MBD001-MBD009 markdown boundary rules verified on parent Epic and all plan files in `docs/epic/tasks_EPIC_154/`. | Informal plan prose or speculative unstructured planning documentation. | `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md` and `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/tasks_EPIC_154/07_phase7_plan.md` exit code 0. |
| `@[backend_v2/tests/integration/test_integration_real_llm.py]` | Untested live LLM API pipelines or relying solely on unit test mocks for end-to-end verification. | Execute final Live E2E REST API Verification Gate with `$env:RUN_LIVE_E2E="true"` when credentials are present. | Bespoke ad-hoc live test harnesses outside the standard Pytest suite. | Pytest exits code 0 for live E2E run (`test_integration_real_llm.py`). |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 6. Verify all implementation and test files exist and pass localized unit tests.</action>
    <action>Look forward: Verify if all global completion gates, Theme Sovereignty, and AST guardrails pass 100% before closing Epic 154.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]) and the Tracker document (@[docs/epic/EPIC_154_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_154/07_phase7_plan.md] @[docs/epic/EPIC_154_tracker.md]`.</directive>
  </step>

  <dod_checklist>
    <item>Resolve use_build_context_synchronously in dashboard_view.dart.</item>
    <item>backend_audit_loop.py passes 100% across all touched backend files with --test and --ast-strict.</item>
    <item>flutter_audit_loop.py passes 100% across client with --build.</item>
    <item>audit_flutter_theme_sovereignty.py passes 100% across client_app_v2 verifying zero raw colors or naked TextStyles.</item>
    <item>_ast_guardrails.py passes 100% with backend_v2/ --strict verifying QGR029 Polyfactory fixture compliance and zero naked dicts.</item>
    <item>audit_dict_eradication.py passes 100% with backend_v2 --strict verifying zero naked dicts across all causal DTOs and orchestrators.</item>
    <item>audit_markdown_boundaries.py passes 100% on EPIC_154_Dynamic_Causal_Discovery_Engine.md and all plan files.</item>
    <item>Final Live E2E REST API Verification Gate passes with $env:RUN_LIVE_E2E="true" when credentials are configured.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_decompose_verify.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
    <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_synthesis_payload_compression.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do not bypass failing tests with skip markers or test suppression flags.</forbidden>
    <forbidden>Do not suppress AST guardrail errors with noqa comments.</forbidden>
    <forbidden>Do not approve Phase 7 without executing all quality gate scripts.</forbidden>
    <forbidden>Do not execute _ast_guardrails.py without specifying target path and strict flag.</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[scripts/backend_audit_loop.py]</backend>
    <frontend>@[scripts/flutter_audit_loop.py]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/dashboard_view.dart]</frontend>
  </touched_artifacts>

  <step id="1" name="PRE_IMPLEMENTATION_CLEANUPS">
    <action>In @[client_app_v2/lib/features/execution/views/dashboard_view.dart#L464-L536], refactor _cloneAndRunExecution to pre-fetch fallbackLocale = Localizations.localeOf(context).languageCode prior to the asynchronous gap await dio.get('/execution/executions/$id'), and enforce if (!context.mounted) return; before any BuildContext access, eliminating the dart analyze use_build_context_synchronously info warning.</action>
    <constraint invariant="async_build_context_mounted_ban">Never use BuildContext across an asynchronous gap without verifying context.mounted.</constraint>
  </step>

  <step id="7.1" name="BACKEND_AUDIT_EXECUTION">
    <action>In @[scripts/backend_audit_loop.py], execute: uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict. Verify Ruff formatting, MyPy strict typing, clean imports, AST guardrails, and Pytest suites exit with code 0.</action>
    <constraint invariant="backend_audit_execution">Zero tolerance for failing tests or type check violations.</constraint>
  </step>

  <step id="7.2" name="FLUTTER_AUDIT_EXECUTION">
    <action>In @[scripts/flutter_audit_loop.py], execute: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build. Verify Freezed code generation, Flutter analyze, and Flutter test suites exit with code 0.</action>
    <constraint invariant="flutter_audit_execution">Build runner must generate Freezed models cleanly with zero unrecognized key failures.</constraint>
  </step>

  <step id="7.3" name="THEME_SOVEREIGNTY_VERIFICATION">
    <action>In @[scripts/audit_flutter_theme_sovereignty.py], execute: uv run python scripts/audit_flutter_theme_sovereignty.py client_app_v2/. Verify zero raw Color(0x...), Colors.*, or naked TextStyle(...) violations in SduiCausalGraphWidget, CausalInspectorModal, or any other widget.</action>
    <constraint invariant="theme_sovereignty">All colors and typography derive from Theme.of(context).</constraint>
  </step>

  <step id="7.4" name="AST_GUARDRAIL_AND_FIXTURE_AUDIT">
    <action>In @[scripts/_ast_guardrails.py], execute: uv run python scripts/_ast_guardrails.py backend_v2/ --strict. Verify QGR029 Polyfactory fixture compliance and zero naked dictionary violations across all new and modified Python files.</action>
    <constraint invariant="the_zero_compromise_pledge">Zero naked dictionaries in state transit or test fixtures.</constraint>
  </step>

  <step id="7.5" name="DICTIONARY_ERADICATION_AUDIT">
    <action>In @[scripts/audit_dict_eradication.py], execute: uv run python scripts/audit_dict_eradication.py backend_v2 --strict. Verify zero naked dictionaries across backend_v2/models/dtos/causal_discovery.py and all orchestrator engines.</action>
    <constraint invariant="the_zero_compromise_pledge">All transit payloads must be strictly typed Pydantic V2 DTOs.</constraint>
  </step>

  <step id="7.6" name="MARKDOWN_BOUNDARY_AUDITING">
    <action>In @[scripts/audit_markdown_boundaries.py], execute: uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md and uv run python scripts/audit_markdown_boundaries.py --file docs/epic/tasks_EPIC_154/07_phase7_plan.md. Verify zero MBD001-MBD009 boundary or ambiguity violations across the parent Epic and all generated plan files in docs/epic/tasks_EPIC_154/.</action>
    <constraint invariant="anti_ambiguity_mandate">Zero ambiguous language or malformed XML tags in markdown documents.</constraint>
  </step>

  <step id="7.7" name="FINAL_LIVE_E2E_REST_API_VERIFICATION_GATE">
    <action>In @[backend_v2/tests/integration/test_integration_real_llm.py], if LIVE credentials are configured, execute the final Live E2E REST API Verification Gate: $env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py.</action>
    <constraint invariant="universal_fail_fast">Live LLM execution verifies end-to-end extraction and causal discovery pipeline.</constraint>
  </step>

  <test_contracts>
    <test name="test_backend_audit_loop_exits_zero" category="positive">
      <input>uv run python scripts/backend_audit_loop.py backend_v2/services/export_service.py --test --ast-strict</input>
      <expected>exit code 0</expected>
    </test>
    <test name="test_flutter_audit_loop_exits_zero" category="positive">
      <input>uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/</input>
      <expected>exit code 0</expected>
    </test>
    <test name="test_theme_sovereignty_audit_exits_zero" category="positive">
      <input>uv run python scripts/audit_flutter_theme_sovereignty.py client_app_v2/</input>
      <expected>exit code 0, 0 violations</expected>
    </test>
    <test name="test_ast_guardrails_audit_exits_zero" category="positive">
      <input>uv run python scripts/_ast_guardrails.py backend_v2/ --strict</input>
      <expected>exit code 0, 0 violations</expected>
    </test>
    <test name="test_dict_eradication_audit_exits_zero" category="positive">
      <input>uv run python scripts/audit_dict_eradication.py backend_v2 --strict</input>
      <expected>exit code 0, 0 violations across all 12 metrics</expected>
    </test>
    <test name="test_markdown_boundary_audit_exits_zero" category="positive">
      <input>uv run python scripts/audit_markdown_boundaries.py --file docs/epic/tasks_EPIC_154/07_phase7_plan.md</input>
      <expected>exit code 0, SUCCESS</expected>
    </test>
    <test name="test_ast_guardrails_fails_without_target_negative" category="negative">
      <input>uv run python scripts/_ast_guardrails.py</input>
      <expected>exit code 1, Usage error</expected>
    </test>
    <test name="test_theme_sovereignty_detects_raw_color_negative" category="negative">
      <input>Simulated raw Color(0xFF000000) in a Flutter widget file</input>
      <expected>audit_flutter_theme_sovereignty.py exits code 1 with Theme Sovereignty violation</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/ --test</action>
    <action>Execute: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build</action>
    <action>Execute: uv run python scripts/audit_flutter_theme_sovereignty.py client_app_v2/</action>
    <action>Execute: uv run python scripts/_ast_guardrails.py backend_v2/ --strict</action>
    <action>Execute: uv run python scripts/audit_dict_eradication.py backend_v2 --strict</action>
    <action>Execute: uv run python scripts/audit_markdown_boundaries.py --file docs/epic/tasks_EPIC_154/07_phase7_plan.md</action>
  </validation_gate>
</execution_protocol>
