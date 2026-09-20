# Phase 5: LLM Context Orchestration, Dynamic Input Merging & Prompt Compiler Hardening

**Overview:** Structured placeholder plan for Phase 5. Hardening prompt compilation, dynamic input merging, and DAG execution to eliminate dictionary mutations and string-based context lookups.
**Source:** @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] Phase 5: LLM Context Orchestration, Dynamic Input Merging & Prompt Compiler Hardening
**Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/prompt_compiler.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/state_reducer.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 4 established typed hook deltas and context variables.</action>
    <action>Look forward: Verify that Phase 6 SDUI presentation layers receive strictly typed step outputs.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_152_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication/05_placeholder_phase5.md] @[docs/epic/EPIC_152_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>Prompt compiler in @[backend_v2/services/orchestrator/prompt_compiler.py] operates with PromptMappingDTO and LLMContextDataDTO.</item>
    <item>State reducer and DAG executor eradicate raw dictionary merging and manage LogicNodeStateDTO deterministically.</item>
    <item>Dynamic input merging is 100% typed with zero fallback access.</item>
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
    <forbidden>Do NOT modify SDUI mappers during Phase 5 (reserved for Phase 6).</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/prompt_compiler.py]</backend>
    <backend>@[backend_v2/services/orchestrator/state_reducer.py]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor.py]</backend>
  </touched_artifacts>

  <step id="5.1" name="Prompt Compiler &amp; Mapping DTO Hardening">
    <action>Refactor @[backend_v2/services/orchestrator/prompt_compiler.py] to accept PromptMappingDTO and LLMContextDataDTO.</action>
    <action>Eradicate loose dict unpacking during prompt template compilation.</action>
  </step>

  <step id="5.2" name="State Reducer &amp; DAG Executor Hardening">
    <action>Refactor @[backend_v2/services/orchestrator/state_reducer.py] and @[backend_v2/services/orchestrator/dag_executor.py] to utilize LogicNodeStateDTO.</action>
    <action>Enforce typed input reduction across all workflow nodes.</action>
  </step>

  <validation_gate>
    <action>Run backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompt_compiler.py --test</action>
  </validation_gate>
</execution_protocol>
```
