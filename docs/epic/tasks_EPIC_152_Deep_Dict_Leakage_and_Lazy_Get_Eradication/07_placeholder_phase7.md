# Phase 7: Full-Spectrum Verification, AST Guardrails & Live E2E Gate

**Overview:** Structured placeholder plan for Phase 7. Comprehensive neuro-symbolic audit verification, complete QGR018 AST sweep across all codebase targets, and execution of live E2E variance tests.
**Source:** @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] Phase 7: Full-Spectrum Verification, AST Guardrails & Live E2E Gate
**Target Files:**
- `[MODIFY]` @[scripts/audit_dict_eradication.py]
- `[MODIFY]` @[scripts/_ast_guardrails.py]
- `[MODIFY]` @[scripts/run_e2e_variance_test.py]
- `[MODIFY]` @[backend_v2/models/dtos/lightweight_matrix.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phases 1 through 6 completed all structural refactoring and DTO hardening.</action>
    <action>Look forward: Verify that zero dictionary leakages, lazy .get() calls, or Primitive Obsession nested dictionary antipatterns remain anywhere in the production execution pipeline.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_152_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication/07_placeholder_phase7.md] @[docs/epic/EPIC_152_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>AST audit script @[scripts/audit_dict_eradication.py] reports zero violations across all production packages, including exactly 0 naked dict annotations and 0 Primitive Obsession nested dictionary annotations (`dict[..., dict[...]]` regardless of key or value types) across models, DTOs, services, workers, and adapters.</item>
    <item>LightweightMatrixOutput.level_breakdown and ScoringResultDTO.breakdown in @[backend_v2/models/dtos/lightweight_matrix.py] are migrated from `dict[str, dict[str, int]]` to strongly typed `dict[str, LevelStatsDTO]`, with dot-notation access (.hits, .total) across all consumers and exactly 0 dictionary subscripting.</item>
    <item>End-to-end variance verification suite @[scripts/run_e2e_variance_test.py] passes 100%.</item>
    <item>Telemetry and monitoring summaries DiscoveredModelDTO, FinOpsMonitorSummaryDTO, and FinOpsFinalizeSummaryDTO verified.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
    <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
    <knowledge_item>@[ki_cartesian_variance_and_authenticity.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do NOT skip any failing tests in the full test suite.</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[scripts/audit_dict_eradication.py]</backend>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>@[scripts/run_e2e_variance_test.py]</backend>
    <backend>@[backend_v2/models/dtos/lightweight_matrix.py]</backend>
  </touched_artifacts>

  <step id="7.1" name="Codebase-Wide AST Guardrail Sweep &amp; Primitive Obsession Eradication">
    <action>Execute @[scripts/audit_dict_eradication.py] across entire backend_v2 directory with codebase-wide nested dictionary Primitive Obsession detection.</action>
    <action>Migrate LightweightMatrixOutput.level_breakdown and ScoringResultDTO.breakdown to strictly typed dict[str, LevelStatsDTO].</action>
    <action>Refactor consumers (MatrixExplanationService, scoring hooks, adapters) to static dot-notation (.hits, .total), eliminating dict subscripting.</action>
    <action>Verify zero QGR018, QGR001, and Primitive Obsession nested dictionary violations across all modules.</action>
  </step>

  <step id="7.2" name="Live End-to-End Variance Test Run">
    <action>Execute live test suite via @[scripts/run_e2e_variance_test.py].</action>
    <action>Verify FinOpsMonitorSummaryDTO and FinOpsFinalizeSummaryDTO telemetry contracts.</action>
  </step>

  <validation_gate>
    <action>Run full test suite: uv run pytest backend_v2/tests/</action>
  </validation_gate>
</execution_protocol>
```
