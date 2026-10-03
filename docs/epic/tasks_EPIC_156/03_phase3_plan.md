# Phase 3: Domain & Service Layer Duct-Tape Eradication & Mutation Invariance (QGR020, QGR012, QGR016, QGR002, QGR019)

**Overview:** Systematically eliminate domain and service layer anti-patterns (mutable defaults, duck-typing, lazy ternary fallbacks, chained `.get()`, and in-place `dict.pop()`), promote each rule to FATAL severity, and verify mathematical core mutation invariance.

**Source:** `@[docs/epic/EPIC_156_Universal_AST_Strictness_and_Advisory_Warning_Eradication.md#L287-L314]`

**Target Files:**
- `[MODIFY]` `@[scripts/_ast_guardrails.py]`
- `[NEW]` `@[scripts/audit_mutation_coverage.py]`
- `[MODIFY]` `@[backend_v2/utils/scoring/unified_engine.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/topological_evaluator.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/dag_executor.py]`
- `[MODIFY]` `@[backend_v2/services/report_service.py]`

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 2 eliminated all 319 deceptive mocks and locked QGR014 to FATAL severity.</action>
    <action>Look forward: Verify updated codebase state before generating granular execution steps for Phase 3 via /tier0-create-plan.</action>
    <constraint>Deferred phase placeholder. Invoke /tier0-create-plan to generate granular implementation plan when Phase 2 completes.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_156_Universal_AST_Strictness_and_Advisory_Warning_Eradication.md]) and the Tracker document (@[docs/epic/EPIC_156_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_156/03_phase3_plan.md] @[docs/epic/EPIC_156_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>Clean and promote QGR020 (107 instances: mutable class defaults) to FATAL severity.</item>
    <item>Clean and promote QGR012 (116 instances: duck-typing) to FATAL severity.</item>
    <item>Clean and promote QGR016 (184 instances: ternary lazy fallbacks) to FATAL severity.</item>
    <item>Clean and promote QGR002 (340 instances: chained .get() lookups) to FATAL severity.</item>
    <item>Clean and promote QGR001 (83 instances: reflection) and QGR019 (42 instances: dict.pop) to FATAL severity.</item>
    <item>Automated mutation testing script scripts/audit_mutation_coverage.py implemented proving 100% mutant kill rate on UnifiedScoringEngine and TopologicalEvaluator.</item>
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
    <anti_target>Inverting default audit loop strictness flag (quarantined for Phase 4).</anti_target>
    <anti_target>Third-party mutation testing frameworks (mutmut, cosmic-ray) - banned per Axis 4.</anti_target>
  </anti_targets>

  <touched_artifacts>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>[NEW] @[scripts/audit_mutation_coverage.py]</backend>
    <backend>@[backend_v2/utils/scoring/unified_engine.py]</backend>
    <backend>@[backend_v2/services/orchestrator/topological_evaluator.py]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor.py]</backend>
    <backend>@[backend_v2/services/report_service.py]</backend>
  </touched_artifacts>

  <step id="3.1" name="Clean and Lock QGR020, QGR012, QGR016, QGR002, QGR001, QGR019">
    <action>Detailed implementation steps to be expanded during /tier0-create-plan execution for Phase 3 based on updated codebase state.</action>
    <constraint invariant="the_zero_compromise_pledge">Enforce strict Pydantic DTOs and eradicate loose dictionary lookups.</constraint>
  </step>

  <test_contracts>
    <test name="test_mutation_coverage_kills_all_arithmetic_mutants" category="positive">
      <input>scripts/audit_mutation_coverage.py run against UnifiedScoringEngine</input>
      <expected>100% mutant kill rate achieved</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute AST guardrails check across backend_v2: `uv run python scripts/_ast_guardrails.py backend_v2 --strict`</action>
    <action>Execute mutation testing: `uv run python scripts/audit_mutation_coverage.py`</action>
  </validation_gate>
</execution_protocol>
```
