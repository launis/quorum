# Phase 4: Universal AST Strictness Lockdown, Mathematical Proof & Permanent CI Enforcement

**Overview:** Lock strict mode as the permanent default in all quality gates, reclassify all AST visitor rules unconditionally to FATAL severity, verify the Exhaustive Violation Eradication Ledger, assert clean imports and DTO parity, and mathematically prove zero warnings across all 896 backend files.

**Source:** `@[docs/epic/EPIC_156_Universal_AST_Strictness_and_Advisory_Warning_Eradication.md#L315-L337]`

**Target Files:**
- `[MODIFY]` `@[scripts/backend_audit_loop.py]`
- `[MODIFY]` `@[scripts/_ast_guardrails.py]`
- `[NEW]` `@[scripts/audit_warning_baseline.py]`

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 3 eradicated all duct-tape rules and achieved 100% mutant kill rate on mathematical cores.</action>
    <action>Look forward: Verify updated codebase state before generating granular execution steps for Phase 4 via /tier0-create-plan.</action>
    <constraint>Deferred phase placeholder. Invoke /tier0-create-plan to generate granular implementation plan when Phase 3 completes.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_156_Universal_AST_Strictness_and_Advisory_Warning_Eradication.md]) and the Tracker document (@[docs/epic/EPIC_156_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_156/04_phase4_plan.md] @[docs/epic/EPIC_156_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>Invert default flag in scripts/backend_audit_loop.py: ast_strict=True by default.</item>
    <item>Reclassify all visitor methods in scripts/_ast_guardrails.py to unconditionally emit FATAL severity.</item>
    <item>Execute Exhaustive Violation Eradication Ledger: prove 0 FATAL errors and 0 WARNINGS across 896 files.</item>
    <item>Execute clean imports, DTO parity, and mutation gates cleanly.</item>
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
    <anti_target>Permissive warning shims or fallback flags in production gates.</anti_target>
    <anti_target>Altering established public API schemas or DTO serialization contracts.</anti_target>
  </anti_targets>

  <touched_artifacts>
    <backend>@[scripts/backend_audit_loop.py]</backend>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>[NEW] @[scripts/audit_warning_baseline.py]</backend>
  </touched_artifacts>

  <step id="4.1" name="Invert Strict Default Flag &amp; Permanent CI Lockdown">
    <action>Detailed implementation steps to be expanded during /tier0-create-plan execution for Phase 4 based on updated codebase state.</action>
    <constraint invariant="universal_fail_fast">Enforce strict AST analysis and zero warning tolerance unconditionally.</constraint>
  </step>

  <test_contracts>
    <test name="test_backend_audit_loop_defaults_to_strict" category="positive">
      <input>Run backend_audit_loop.py without --ast-strict flag</input>
      <expected>Strict AST validation executes by default</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute full repository strict scan: `uv run python scripts/_ast_guardrails.py backend_v2 --strict` (Assert: 0 FATAL, 0 WARNING across 896 files)</action>
    <action>Execute baseline zero verification: `uv run python scripts/audit_warning_baseline.py --verify-zero`</action>
    <action>Execute 8-stage audit loop across entire backend: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
    <action>Execute final live E2E REST API gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`</action>
  </validation_gate>
</execution_protocol>
```
