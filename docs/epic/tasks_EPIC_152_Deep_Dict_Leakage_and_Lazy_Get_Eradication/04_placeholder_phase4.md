# Phase 4: Hook Pipeline Hardening, Result Projector Segregation & Complete Emoji Eradication

**Overview:** Structured placeholder plan for Phase 4. Eradicate loose dictionary payload mutation across result projectors and matrix hooks. Enforce strict DTO contracts for hook deltas and global context variables, and eliminate all emoji-based status indicators in favor of typed enums.
**Source:** @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] Phase 4: Hook Pipeline Hardening, Result Projector Segregation & Complete Emoji Eradication
**Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/result_projector.py]
- `[MODIFY]` @[backend_v2/hooks/scoring/matrix_hook.py]
- `[NEW]` @[backend_v2/models/dtos/global_context.py]
- `[NEW]` @[backend_v2/models/dtos/hook_delta.py]
- `[NEW]` @[backend_v2/tests/unit/hooks/test_matrix_hook.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 3 established typed synthesis distillation contracts.</action>
    <action>Look forward: Verify that Phase 5 prompt compiler receives clean, typed context variables without loose dictionaries.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_152_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication/04_placeholder_phase4.md] @[docs/epic/EPIC_152_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>Result projector operates exclusively with ProjectedResultsDTO and MatrixProjectionResultDTO.</item>
    <item>Matrix hook returns strongly typed MatrixHookResultDTO and handles MissingContextDTO strictly.</item>
    <item>ContextVariablesDTO and HookDeltaDTO are strictly validated with frozen immutability in [NEW] @[backend_v2/models/dtos/global_context.py] and [NEW] @[backend_v2/models/dtos/hook_delta.py].</item>
    <item>Unit test coverage established in [NEW] @[backend_v2/tests/unit/hooks/test_matrix_hook.py].</item>
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
    <forbidden>Do NOT modify prompt compilation logic in Phase 4 (reserved for Phase 5).</forbidden>
    <forbidden>Do NOT mutate SDUI layout mappers in Phase 4 (reserved for Phase 6).</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/result_projector.py]</backend>
    <backend>@[backend_v2/hooks/scoring/matrix_hook.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/global_context.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/hook_delta.py]</backend>
  </touched_artifacts>

  <step id="4.1" name="Result Projector Segregation">
    <action>Refactor @[backend_v2/services/orchestrator/result_projector.py] to output ProjectedResultsDTO and MatrixProjectionResultDTO.</action>
    <action>Eliminate loose dictionary transformations and enforce typed projection.</action>
  </step>

  <step id="4.2" name="Matrix Hook Hardening &amp; Test Suite Creation">
    <action>Refactor @[backend_v2/hooks/scoring/matrix_hook.py] to utilize MatrixHookResultDTO, MissingContextDTO, and ContextVariablesDTO.</action>
    <action>Create [NEW] @[backend_v2/tests/unit/hooks/test_matrix_hook.py] to verify error paths and deterministic hook execution.</action>
  </step>

  <validation_gate>
    <action>Run backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring/matrix_hook.py --test</action>
  </validation_gate>
</execution_protocol>
```
