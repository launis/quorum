# Phase 7: AST Guardrail Hardening (Mathematical Drift Prevention)

**Phase Title:** Phase 7: AST Guardrail Hardening (Mathematical Drift Prevention)
**Objective:** Enforce `QGR001` (getattr/hasattr) and `QGR002` (.get(key, default)) at FATAL severity in `services/` and `hooks/`, introduce new rule `QGR012` (`isinstance(..., dict)` detection at FATAL severity in `services/` and `hooks/`), harden path normalization against relative path evasion, and add automated AST verification tests to make it mathematically impossible for new duck-typing or anti-patterns to enter the codebase.

**Source Reference:** @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L319-L329] (Phase 7: AST Guardrail Hardening)

**Expected Target Files:**
- `[MODIFY]` @[scripts/_ast_guardrails.py#L154-L598]
- `[MODIFY]` @[scripts/backend_audit_loop.py#L202-L318]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L636-L648]
- `[MODIFY]` @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/08_placeholder_phase7_ast_guardrails_hardening.md]

### Read-Only Context References
- `@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L319-L329]`
- `@[docs/epic/EPIC_149_tracker.md#L500-L572]`
- `@[C:\Users\risto\.gemini\antigravity-ide\knowledge\ast_guardrail_engine\artifacts\ki_ast_guardrail_engine.md]`

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; PRE-FLIGHT VERIFICATION">
    <action>Look backward: Read the actual codebase state left by Phase 6. Verify workers and cache boundaries are strictly typed.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[scripts/_ast_guardrails.py] and @[scripts/backend_audit_loop.py].</action>
    <constraint invariant="read_before_think_lock">Load rules and verify AST engine state using view_file before editing.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] `QGR001`, `QGR002`, and new `QGR012` [NEW] locked at `FATAL` severity for `services/` and `hooks/` in @[scripts/_ast_guardrails.py].
    - [x] Robust path normalization implemented to prevent relative path evasion.
    - [x] `backend_audit_loop.py` in @[scripts/backend_audit_loop.py] unconditionally fails on FATAL violations.
    - [x] Automated AST verification unit tests in @[backend_v2/tests/unit/scripts/test_ast_guardrails.py] verifying 0 unsuppressed violations across `backend_v2/services/` and `backend_v2/hooks/`.
    - [x] Quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_domain_model_prompt_separation.md]</knowledge_item>
    <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>@[scripts/backend_audit_loop.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT allow unsuppressed `FATAL` violations in `services/` or `hooks/`.
  </anti_targets>


  <step id="1" name="PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUP &amp; COVERAGE EXPANSION">
    <action>In `scripts/_ast_guardrails.py`, update module docstring to `(QGR000-QGR012)`.</action>
    <action>In `backend_v2/tests/unit/scripts/test_backend_audit_loop.py`, expand unit tests for `backend_audit_loop.py` missing branches to maintain strict >=90% test coverage.</action>
    <constraint invariant="scoped_boy_scout_rule">Clean technical debt exclusively in target files touched by Phase 7.</constraint>
  </step>

  <step id="2" name="IMPLEMENT QGR012 RULE &amp; ENFORCE FATAL SEVERITY FOR SERVICES/HOOKS">
    <action>Harden path normalization in `QuorumGuardrailVisitor` in `scripts/_ast_guardrails.py` using `set(norm_path.replace("\\", "/").strip("/").split("/")) & {"services", "hooks"}` to prevent relative path evasion.</action>
    <action>Add `QGR012` detection in `QuorumGuardrailVisitor.visit_Call` for `isinstance(..., dict)` and composite `isinstance(..., (..., dict, ...))` calls.</action>
    <action>Lock `QGR001`, `QGR002`, and `QGR012` at FATAL severity when target file is located within `services/` or `hooks/`.</action>
    <constraint invariant="zero_reflection_pattern_matching">Implement AST node matching strictly via match/case and isinstance type narrowing with zero getattr/hasattr.</constraint>
  </step>

  <step id="3" name="BACKEND AUDIT LOOP FATAL HARDENING &amp; STAGE 4 VERIFICATION">
    <action>In `scripts/backend_audit_loop.py`, verify Stage 4 unconditionally exits with code 1 if `fatal_violations` is non-empty.</action>
    <action>Verify strict mode (`--ast-strict` / `--strict`) exits with code 1 if any unsuppressed violation exists.</action>
    <constraint invariant="fail_fast">Never permit fatal AST violations to pass through audit pipeline.</constraint>
  </step>

  <step id="4" name="EXPAND ISTQB UNIT TESTS FOR QGR012 &amp; PATH NORMALIZATION">
    <action>In `backend_v2/tests/unit/scripts/test_ast_guardrails.py`, implement Partition 37 covering all positive, negative, boundary, and suppression test cases for `QGR012`.</action>
    <action>Implement relative path normalization tests asserting FATAL severity on `services/foo.py` and `hooks/bar.py`.</action>
    <action>Update `test_zero_reflection_self_verification` to audit `_ast_guardrails.py`, `backend_audit_loop.py`, and `test_ast_guardrails.py`.</action>
    <constraint invariant="anti_happy_path_mandate">Cover both valid (str, BaseModel, match/case) and invalid (dict, tuple with dict) partitions with negative tests.</constraint>
  </step>

  <step id="5" name="KNOWLEDGE BASE &amp; DOCUMENTATION SYNCHRONIZATION">
    <action>Update `ki_ast_guardrail_engine.md` with `QGR011` (Create DTO ID ban) and `QGR012` (isinstance dict ban) specifications and remediation table.</action>
    <constraint invariant="dual_axis_documentation_mandate">Maintain AI rules and Knowledge Items in strict synchronization with physical codebase implementation.</constraint>
  </step>

  <step id="6" name="TWO-STAGE QUALITY GATE &amp; FINAL E2E VERIFICATION">
    <action>Stage 1: Run isolated unit tests with strict coverage: `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py backend_v2/tests/unit/scripts/test_backend_audit_loop.py -v --cov=scripts._ast_guardrails --cov=scripts.backend_audit_loop --cov-fail-under=90`.</action>
    <action>Stage 2: Run global backend audit loop: `uv run python scripts/backend_audit_loop.py scripts/backend_audit_loop.py scripts/_ast_guardrails.py backend_v2/tests/unit/scripts/test_ast_guardrails.py backend_v2/tests/unit/scripts/test_backend_audit_loop.py --test --ast-strict`.</action>
    <action>Stage 3: Run full backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`.</action>
    <action>Stage 4: Execute Live E2E REST API Verification Gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.</action>
    <constraint invariant="atomic_checkpoint_mandate">Instruct atomic git commit after all quality gates pass 100%.</constraint>
  </step>

  <architectural_directives>
    ## 5-Column Architectural Directives Table

    | 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
    | :--- | :--- | :--- | :--- | :--- |
    | **AST Guardrail Visitor** (`scripts/_ast_guardrails.py` #L154-L598) | Banned relative path substring matching (`"backend_v2/services/" in norm_path`) that allows path evasion | Enforce robust segment matching `set(parts) & {"services", "hooks"}` and match/case AST inspection | Pruned redundant regex path matching and speculative visitor hooks | `test_relative_path_fatal_enforcement` proving `services/foo.py` triggers `FATAL` severity |
    | **QGR012 Rule Implementation** (`scripts/_ast_guardrails.py` #L211-L364) | Banned unsuppressed `isinstance(..., dict)` or `isinstance(..., (..., dict, ...))` in domain services and hooks | Enforce Discriminated Unions and Python 3.10+ `match/case` structural pattern matching; explicit `# noqa: QGR012 [REASON: ...]` for heterogenous DAG state | Pruned AST wrapper classes; direct `match node.func` in `visit_Call` | `test_qgr012_isinstance_dict_detection` verifying FATAL severity in `services/` |
    | **Audit Loop Stage 4 Gate** (`scripts/backend_audit_loop.py` #L202-L318) | Banned bypassing Stage 4 when fatal violations exist or in strict mode | Unconditional `sys.exit(1)` when `fatal_violations` is non-empty or `--ast-strict` contains unsuppressed warnings | Pruned secondary AST runner scripts; direct integration with `scan_files_for_guardrails` | `test_ast_gate_advisory_mode_fails_on_fatal_qgr000` & `test_ast_gate_strict_mode_fails_on_warning_violation` |
    | **AST ISTQB Test Suite** (`backend_v2/tests/unit/scripts/test_ast_guardrails.py` #L1-L777) | Banned happy-path-only tests or tests missing composite tuple checks | Implement Partition 37 covering positive, negative, composite tuple, and valid `# noqa` suppression with reasons | Pruned external file mocking bloat; direct in-memory `_scan_snippet` execution | `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py -v --cov=scripts._ast_guardrails --cov-fail-under=90` |
    | **Zero-Reflection Self Verification** (`backend_v2/tests/unit/scripts/test_ast_guardrails.py` #L636-L648) | Banned reflection calls (`getattr`/`hasattr`) in AST tooling and test files | Mandatory AST walker asserting 0 `getattr`/`hasattr` across `_ast_guardrails.py`, `backend_audit_loop.py`, and `test_ast_guardrails.py` | Pruned multi-pass file reading; single `ast.walk()` assertion | `test_zero_reflection_self_verification` passing 100% |
  </architectural_directives>

  <validation_gate>
    uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_ast_guardrails.py --test
    uv run python scripts/backend_audit_loop.py backend_v2/ --test
  </validation_gate>
</execution_protocol>

```
