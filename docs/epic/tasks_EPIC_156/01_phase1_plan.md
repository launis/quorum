# Phase 1: Tooling Infrastructure, Blindspot Elimination & Scoped Boy Scout CI Enforcement

**Overview:** Implement QGR024 and QGR025 in `_ast_guardrails.py`, build the Clean Import smoke test tool, expand `backend_audit_loop.py` to an 8-stage mandatory pipeline with hardened Jinja Dumb Painter regex, eliminate 79 pre-existing domain fatal violations, clean low-count warning violations (QGR007, QGR023, QGR009, QGR008, QGR006, QGR011), clean 22 active tooling violations, promote cleaned rules to FATAL severity, build the warning baseline ledger, and synchronize agentic workflows.

**Target Files:**
- `[MODIFY]` `@[scripts/_ast_guardrails.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`
- `[NEW]` `@[scripts/audit_clean_imports.py]`
- `[NEW]` `@[backend_v2/tests/unit/scripts/test_clean_imports.py]`
- `[MODIFY]` `@[scripts/backend_audit_loop.py]`
- `[MODIFY]` `@[backend_v2/templates/report_template.jinja2]`
- `[NEW]` `@[scripts/audit_warning_baseline.py]`
- `[MODIFY]` `@[scripts/audit_database_atoms.py]`
- `[MODIFY]` `@[scripts/reconcile_storage.py]`
- `[MODIFY]` `@[scripts/audit_rules_staleness.py]`
- `[MODIFY]` `@[scripts/audit_matrix_auto_filler.py]`
- `[MODIFY]` `@[scripts/audit_matrix_manager.py]`
- `[MODIFY]` `@[scripts/matrix_slice_engine.py]`
- `[MODIFY]` `@[backend_v2/run_worker.py]`
- `[MODIFY]` `@[backend_v2/database/wrapper.py]`
- `[MODIFY]` `@[backend_v2/hooks/llm.py]`
- `[MODIFY]` `@[backend_v2/llm/handler.py]`
- `[MODIFY]` `@[backend_v2/llm/ingress_pipeline.py]`
- `[MODIFY]` `@[backend_v2/hooks/source_verification_hook.py]`
- `[MODIFY]` `@[AGENTS.md]`
- `[MODIFY]` `@[.agents/workflows/tier2-execute.md]`
- `[MODIFY]` `@[.agents/workflows/tier1-tracker-generator.md]`
- `[MODIFY]` `@[.agents/workflows/tier1-plan-tracker-generator.md]`
- `[MODIFY]` `@[.agents/workflows/tier8-audit-plan.md]`
- `[MODIFY]` `@[.agents/workflows/tier8-red-teaming-audit.md]`
- `[MODIFY]` `@[.agents/workflows/tier2-hardening-knowledge.md]`
- `[MODIFY]` `@[.agents/workflows/tier0-create-epic.md]`
- `[MODIFY]` `@[.agents/workflows/tier0-research-epic.md]`
- `[MODIFY]` `@[.agents/workflows/tier3-minify-customization.md]`
- `[MODIFY]` `@[.agents/workflows/tier3-database-reset.md]`

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state. Verify baseline violation count across 896 backend files (79 FATAL, 1,254 WARNING) and 26 tooling scripts.</action>
    <action>Look forward: Verify that adding QGR024, QGR025, Clean Imports, and 8-stage audit loop provides the foundation for subsequent zero-warning eradication without destabilizing offline diagnostic suites.</action>
    <constraint>If alignment is broken or baseline diverges unexpectedly, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_156_Universal_AST_Strictness_and_Advisory_Warning_Eradication.md]) and the Tracker document (@[docs/epic/EPIC_156_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_156/01_phase1_plan.md] @[docs/epic/EPIC_156_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>QGR024 implemented in scripts/_ast_guardrails.py banning string-quoted annotations while exempting Literal[...] slices and Annotated[...] metadata arguments.</item>
    <item>QGR025 implemented in scripts/_ast_guardrails.py banning untyped dictionaries in model_copy(update=...) while permitting static typed dictionary literals.</item>
    <item>Comprehensive unit test suite for QGR013 through QGR025 implemented in backend_v2/tests/unit/scripts/test_ast_guardrails.py.</item>
    <item>Clean import verification tool scripts/audit_clean_imports.py and test backend_v2/tests/unit/scripts/test_clean_imports.py implemented.</item>
    <item>Expanded 8-stage backend_audit_loop.py pipeline functional with Clean Imports (Stage 7) and DTO Parity (Stage 8), hardened Jinja Dumb Painter regex, and 7 Jinja template fallbacks eradicated.</item>
    <item>All 79 pre-existing domain fatal violations in backend_v2 eradicated.</item>
    <item>Low-count advisory warning violations (46 instances: QGR007, QGR023, QGR009, QGR008, QGR006, QGR011) eradicated in domain code.</item>
    <item>Active tooling script violations (22 instances across 6 scripts) eradicated.</item>
    <item>Rules QGR007, QGR023, QGR009, QGR008, QGR006, QGR011, QGR024, and QGR025 promoted to FATAL severity in scripts/_ast_guardrails.py.</item>
    <item>Warning baseline ledger script scripts/audit_warning_baseline.py implemented asserting warning counts do not exceed 1,208 warnings and 0 fatals.</item>
    <item>Agentic workflows in AGENTS.md and .agents/workflows/ synchronized with mandatory strict quality gates, plan-tracker parity, and rule staleness auditing.</item>
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
    <anti_target>Offline statistical research suites: scripts/diff_executions.py (3,260 LOC) and scripts/run_e2e_variance_test.py (2,108 LOC) are quarantined under _is_domain_code = False.</anti_target>
    <anti_target>Test suite repository mocks under QGR014 (quarantined strictly for Phase 2).</anti_target>
    <anti_target>Broad domain .get() lookups under QGR002 and duck-typing under QGR012 (quarantined strictly for Phase 3).</anti_target>
    <anti_target>Third-party mutation frameworks (mutmut, cosmic-ray) - banned per Axis 4.</anti_target>
  </anti_targets>

  <touched_artifacts>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>[NEW] @[scripts/audit_clean_imports.py]</backend>
    <backend>@[scripts/backend_audit_loop.py]</backend>
    <backend>[NEW] @[scripts/audit_warning_baseline.py]</backend>
    <backend>@[scripts/audit_database_atoms.py]</backend>
    <backend>@[scripts/reconcile_storage.py]</backend>
    <backend>@[scripts/audit_rules_staleness.py]</backend>
    <backend>@[scripts/audit_matrix_auto_filler.py]</backend>
    <backend>@[scripts/audit_matrix_manager.py]</backend>
    <backend>@[scripts/matrix_slice_engine.py]</backend>
    <backend>@[backend_v2/run_worker.py]</backend>
    <backend>@[backend_v2/database/wrapper.py]</backend>
    <backend>@[backend_v2/hooks/llm.py]</backend>
    <backend>@[backend_v2/llm/handler.py]</backend>
    <backend>@[backend_v2/llm/ingress_pipeline.py]</backend>
    <backend>@[backend_v2/hooks/source_verification_hook.py]</backend>
  </touched_artifacts>

  <step id="1.1" name="Implement QGR024 (String-Quoted Annotation Ban)">
    <action>In `@[scripts/_ast_guardrails.py]`, add AST visitor inspection for `ast.AnnAssign` and `FunctionDef.returns` detecting string literal constants (`ast.Constant` with string value) used as type annotations.</action>
    <action>Enforce False-Positive Defense: The AST visitor MUST explicitly exclude string constants that are slice arguments to `Literal[...]` (specifically: `Literal['development', 'production']`) or metadata arguments to `Annotated[T, 'Description']` and `Annotated[T, Field(description='...')]`.</action>
    <constraint invariant="deferred_annotations_and_typing">Python 3.14 natively compiles annotations into lazy annotate functions evaluated on-demand via annotationlib; string quotation forward-reference hacks are strictly prohibited.</constraint>
  </step>

  <step id="1.2" name="Implement QGR025 (Untyped Dict in model_copy Ban)">
    <action>In `@[scripts/_ast_guardrails.py]`, add AST visitor inspection for calls to `model_copy(update=...)`.</action>
    <action>Flag calls passing dynamic dictionary variables, function return calls, or unvalidated dictionary unpacking.</action>
    <action>Enforce Concurrency Progress Defense: The AST visitor MUST explicitly permit dictionary literals (`ast.Dict`) whose keys and values are statically known and typed (specifically: `{'status': ExecutionStatus.RUNNING, 'progress': 100}`), preserving atomic progress tracking within `async with _update_lock:`.</action>
    <constraint invariant="safe_model_copy_concurrency_boundary">Untyped dictionary state injection is banned; progress dictionary literals with statically known keys are explicitly permitted.</constraint>
  </step>

  <step id="1.3" name="Comprehensive Unit Tests for AST Engine">
    <action>In `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`, add explicit positive and negative test cases for every rule from QGR013 through QGR025.</action>
    <action>Include explicit false-positive defense assertions for QGR024 verifying `Literal['a', 'b']` and `Annotated[T, 'desc']` pass with zero violations.</action>
    <action>Include explicit false-positive defense assertions for QGR025 verifying typed dictionary literals in `model_copy(update={'status': ExecutionStatus.RUNNING})` pass with zero violations.</action>
    <constraint invariant="zero_tolerance_audit_loop">100% unit test coverage for the AST engine is mandatory.</constraint>
  </step>

  <step id="1.4" name="Implement Clean Import Smoke Test Tool">
    <action>Create [NEW] `@[scripts/audit_clean_imports.py]` implementing a deterministic scanner that recursively imports every module across all 896 files in `backend_v2/` via `importlib.import_module()`.</action>
    <action>Create [NEW] `@[backend_v2/tests/unit/scripts/test_clean_imports.py]` to test the clean import scanner with synthetic isolated modules.</action>
    <action>Assert zero `ImportError`, zero `AttributeError`, and zero circular dependency deadlocks.</action>
    <constraint invariant="the_no_legacy_mandate">Module imports must be side-effect free and pass cleanly in isolation.</constraint>
  </step>

  <step id="1.5" name="Expand backend_audit_loop.py to 8-Stage Mandatory Pipeline">
    <action>In `@[scripts/backend_audit_loop.py]`, integrate Stage 7/8 executing `scripts/audit_clean_imports.py`.</action>
    <action>In `@[scripts/backend_audit_loop.py]`, integrate Stage 8/8 executing `scripts/audit_dto_parity.py`.</action>
    <action>In `@[scripts/backend_audit_loop.py]`, expand Stage 5/8 Jinja Dumb Painter regex to detect fallback expressions (`or ''`, `or []`, `or {}`).</action>
    <action>In `@[backend_v2/templates/report_template.jinja2]`, eliminate 7 Jinja fallback violations (specifically: lines 390, 391, 413, 421, 422, 440, 461) by replacing `or ''`, `or []`, and `or {}` expressions with backend DTO-guaranteed non-None defaults.</action>
    <action>Equip `backend_audit_loop.py` with Scoped Boy Scout strictness: fail-fast if any actively touched target contains unsuppressed warnings.</action>
    <constraint invariant="single_pipeline_invariant_mandate">Quality gates execute sovereignly through exactly one deterministic pipeline.</constraint>
  </step>

  <step id="1.6" name="Eradicate Pre-Existing Domain FATAL Violations">
    <action>Eliminate 53 instances of QGR003: Replace silent exception swallowing in handlers (specifically: `backend_v2/run_worker.py`, `backend_v2/database/wrapper.py`, `backend_v2/hooks/llm.py`, `backend_v2/llm/handler.py`) with explicit `raise` or typed failure dispatch (`dlq_service.push()`).</action>
    <action>Eliminate 10 instances of QGR000: Remove unauthorized `# noqa: QGR*` comment suppressions in domain code (specifically: `backend_v2/llm/ingress_pipeline.py`) and resolve the underlying architectural violations.</action>
    <action>Eliminate 7 instances of QGR012: Eradicate banned `isinstance(..., dict)` duck-typing checks in domain code (specifically: `backend_v2/llm/ingress_pipeline.py`).</action>
    <action>Eliminate 4 instances of QGR002: Replace unexempted dictionary `.get()` calls in domain code (specifically: `backend_v2/database/wrapper.py`).</action>
    <action>Eliminate 4 instances of QGR018: Replace banned type laundering via `TypeAdapter(dict)` in domain code (specifically: `backend_v2/hooks/source_verification_hook.py`) with typed Pydantic V2 DTOs.</action>
    <action>Eliminate 1 instance of QGR022: Replace unshielded f-string prompt interpolation in domain code with structured PromptBlock assembly.</action>
    <constraint invariant="universal_fail_fast">Zero tolerance for silent bypasses or fatal AST errors in domain code.</constraint>
  </step>

  <step id="1.7" name="Eradicate Low-Count Advisory Warning Violations">
    <action>QGR007 (7 instances): Audit all models lacking `ConfigDict(strict=True, extra="forbid")` and add explicit Pydantic V2 `model_config`.</action>
    <action>QGR023 (22 instances): Audit methods returning 3+ element tuples; define dedicated frozen Pydantic V2 DTOs (specifically: defining `ChunkPacketDTO`).</action>
    <action>QGR009 (11 instances): Audit `AppException` instantiations missing an explicit `ErrorCodes` enum member; bind canonical error codes from `@[backend_v2/models/enums.py]`.</action>
    <action>QGR008 (3 instances): Import timeouts and retry intervals centrally from `backend_v2/settings.py` instead of hardcoded numbers.</action>
    <action>QGR006 (2 instances): Replace unguarded dictionary subscripting with positive membership validation.</action>
    <action>QGR011 (1 instance): Replace mutable default argument in function definitions with `= None` and factory initialization.</action>
    <constraint invariant="the_zero_compromise_pledge">Enforce strict Pydantic V2 schemas and eliminate tuple state transit.</constraint>
  </step>

  <step id="1.8" name="Eradicate Advisory Warnings in Active Tooling &amp; Audit Scripts">
    <action>In `@[scripts/audit_database_atoms.py]` (12 instances of QGR012): Replace `isinstance(..., dict)` duck-typing with typed schema validation; update prompt ambiguity inspection to exempt illustrative examples per `@[.agents/rules/05_llm_architecture.md]`; enforce fail-fast exit on structural defects when `--strict` is enabled.</action>
    <action>In `@[scripts/reconcile_storage.py]` (2 instances of QGR007): Add explicit `model_config = ConfigDict(strict=True, extra="forbid")` to `TraceEventContent` and `TraceEventHeader`.</action>
    <action>In `@[scripts/audit_rules_staleness.py]` (2 instances): Replace `hasattr()` with typed attribute access and replace broad exception swallowing with structured logging and re-raise.</action>
    <action>In `@[scripts/audit_matrix_auto_filler.py]` (2 instances of QGR002): Replace `.get()` calls with typed dictionary key indexing.</action>
    <action>In `@[scripts/audit_matrix_manager.py]` (2 instances of QGR001): Replace `vars()` reflection with `.model_dump()` or explicit attribute mapping.</action>
    <action>In `@[scripts/matrix_slice_engine.py]` (2 instances of QGR002): Replace `.get()` calls with bracket indexing.</action>
    <constraint invariant="ssot_reusability_mandate">Active audit scripts must pass strict quality gates without warnings.</constraint>
  </step>

  <step id="1.9" name="Promote Cleaned Rules to FATAL Severity &amp; Build Baseline Ledger">
    <action>In `@[scripts/_ast_guardrails.py]`, update visitor methods for QGR007, QGR023, QGR009, QGR008, QGR006, QGR011, QGR024, and QGR025 to unconditionally assign FATAL severity.</action>
    <action>Create [NEW] `@[scripts/audit_warning_baseline.py]` to record the exact warning count per rule code and assert total warnings never exceed 1,208 warnings and 0 fatals.</action>
    <action>Run full AST scan across backend_v2: verify 0 FATAL violations (down from 79 to 0) and total warnings reduced from 1,254 to 1,208.</action>
    <constraint invariant="neuro_symbolic_grounding_mandate">Rely on deterministic audit scripts to mathematically prove zero fatal regressions.</constraint>
  </step>

  <step id="1.10" name="Synchronize Agentic Workflows &amp; Quality Gate Alignment">
    <action>In `@[AGENTS.md]` and `@[.agents/workflows/tier2-execute.md]`, mandate strict AST mode by default (`uv run python scripts/backend_audit_loop.py <target_path> --test --ast-strict`) and enforce the Two-Stage Testing Pipeline (localized tests during steps; global completion gate `backend_audit_loop.py backend_v2/ --test` and `flutter_audit_loop.py client_app_v2/ --build` before closing any phase).</action>
    <action>Integrate `@[scripts/audit_plan_tracker_parity.py]` as a mandatory verification gate in `@[.agents/workflows/tier1-tracker-generator.md]`, `@[.agents/workflows/tier1-plan-tracker-generator.md]`, and `@[.agents/workflows/tier8-audit-plan.md]`.</action>
    <action>Integrate `@[scripts/audit_rules_staleness.py]` as a mandatory verification gate in `@[.agents/workflows/tier8-red-teaming-audit.md]` and `@[.agents/workflows/tier2-hardening-knowledge.md]`.</action>
    <action>Integrate `@[scripts/audit_epic_coverage.py]` as a mandatory verification gate in `@[.agents/workflows/tier0-create-epic.md]` and `@[.agents/workflows/tier0-research-epic.md]`.</action>
    <action>Integrate `@[scripts/audit_markdown_boundaries.py]` as a mandatory verification gate in `@[.agents/workflows/tier3-minify-customization.md]`.</action>
    <action>In `@[.agents/workflows/tier3-database-reset.md]`, replace vague audit commands with explicit executable commands: `uv run python backend_v2/seed/run_seed.py local` followed by `uv run python scripts/backend_audit_loop.py backend_v2/seed/ --test`.</action>
    <constraint invariant="universal_quality_gates">Zero tolerance for permissive workflow bypasses or orphaned audit scripts.</constraint>
  </step>

  <test_contracts>
    <test name="test_qgr024_string_quoted_annotation_raises_fatal" category="positive">
      <input>Source code with target: "StepOutputDTO"</input>
      <expected>QuorumGuardrailVisitor emits FATAL violation for QGR024</expected>
    </test>
    <test name="test_qgr024_literal_string_slice_permitted" category="boundary">
      <input>Source code with env: Literal['development', 'production']</input>
      <expected>QuorumGuardrailVisitor emits zero violations for QGR024</expected>
    </test>
    <test name="test_qgr024_annotated_metadata_description_permitted" category="boundary">
      <input>Source code with field: Annotated[int, 'Description string']</input>
      <expected>QuorumGuardrailVisitor emits zero violations for QGR024</expected>
    </test>
    <test name="test_qgr025_dynamic_dict_in_model_copy_raises_fatal" category="positive">
      <input>Source code with model.model_copy(update=untyped_dict)</input>
      <expected>QuorumGuardrailVisitor emits FATAL violation for QGR025</expected>
    </test>
    <test name="test_qgr025_typed_literal_dict_in_model_copy_permitted" category="boundary">
      <input>Source code with model.model_copy(update={'status': ExecutionStatus.RUNNING})</input>
      <expected>QuorumGuardrailVisitor emits zero violations for QGR025</expected>
    </test>
    <test name="test_clean_imports_detects_circular_dependency" category="error_path">
      <input>Two synthetic modules importing each other at top level</input>
      <expected>scripts/audit_clean_imports.py exits with non-zero code reporting circular import</expected>
    </test>
    <test name="test_backend_audit_loop_runs_all_8_stages" category="positive">
      <input>Run backend_audit_loop.py with target scripts/_ast_guardrails.py</input>
      <expected>Stages 1 through 8 execute sequentially and return exit code 0</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute AST guardrails on AST engine: `uv run python scripts/_ast_guardrails.py scripts/_ast_guardrails.py --strict`</action>
    <action>Execute AST unit tests: `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py`</action>
    <action>Execute clean import scanner test: `uv run pytest backend_v2/tests/unit/scripts/test_clean_imports.py`</action>
    <action>Execute clean import verification across all 896 modules: `uv run python scripts/audit_clean_imports.py`</action>
    <action>Execute warning baseline ledger: `uv run python scripts/audit_warning_baseline.py` (Assert: 0 FATAL errors, total warnings &lt;= 1,208)</action>
    <action>Execute active tooling AST check: `uv run python scripts/_ast_guardrails.py scripts/audit_database_atoms.py scripts/reconcile_storage.py scripts/audit_rules_staleness.py scripts/audit_matrix_auto_filler.py scripts/audit_matrix_manager.py scripts/matrix_slice_engine.py --strict`</action>
    <action>Execute 8-stage audit loop on touched tools: `uv run python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --test`</action>
  </validation_gate>
</execution_protocol>
```
