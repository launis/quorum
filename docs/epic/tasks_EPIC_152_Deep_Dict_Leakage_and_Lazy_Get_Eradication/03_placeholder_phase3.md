# Phase 3: Phase 1 to Phase 2 Boundary & Synthesis DTO Hardening

**Overview:** Structured placeholder plan for Phase 3. Hardening two-pass atomizer, synthesis reducers, synthesis payload compressor, and domain event sourcing to eradicate loose dictionary passing across the pipeline boundary.
**Source:** @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] Phase 3: Phase 1 to Phase 2 Boundary & Synthesis DTO Hardening
**Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/two_pass_atomizer.py]
- `[MODIFY]` @[backend_v2/workers/synthesis_reducers.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]
- `[NEW]` @[backend_v2/events/domain_events.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 2 established typed IngressInputValue and frozen theory/schema manifests.</action>
    <action>Look forward: Verify that Phase 4 hook pipelines consume typed synthesis outputs.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_152_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication/03_placeholder_phase3.md] @[docs/epic/EPIC_152_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>Two-pass atomizer operates exclusively with strongly typed SynthesisDistillationDTO and FlatExecutionRecordDTO.</item>
    <item>Synthesis reducers and synthesis payload compressor eradicate loose dictionary mutations.</item>
    <item>Symbol NO_BLOCK is completely demolished from @[backend_v2/services/orchestrator/two_pass_atomizer.py].</item>
    <item>Domain event DataStarvationEvent and NodeExecutionUpdateDTO are strictly validated in [NEW] @[backend_v2/events/domain_events.py].</item>
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
    <forbidden>Do NOT modify SDUI presentation models or Flutter UI during Phase 3.</forbidden>
    <forbidden>Do NOT alter matrix hook execution pipeline during Phase 3 (reserved for Phase 4).</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/two_pass_atomizer.py]</backend>
    <backend>@[backend_v2/workers/synthesis_reducers.py]</backend>
    <backend>@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]</backend>
    <backend>[NEW] @[backend_v2/events/domain_events.py]</backend>
  </touched_artifacts>

  <step id="3.1" name="Two-Pass Atomizer Strict Synthesis DTO Hardening">
    <action>Refactor @[backend_v2/services/orchestrator/two_pass_atomizer.py] to eradicate NO_BLOCK and loose dictionary state passing.</action>
    <action>Enforce strongly typed SynthesisDistillationDTO, FlatExecutionRecordDTO, and NodeExecutionUpdateDTO contracts.</action>
    <demolish>REMOVE: `NO_BLOCK` sentinel in @[backend_v2/services/orchestrator/two_pass_atomizer.py]. REPLACE WITH: explicit None or typed NullBlockOption.</demolish>
  </step>

  <step id="3.2" name="Synthesis Reducers &amp; Payload Compressor Hardening">
    <action>Refactor @[backend_v2/workers/synthesis_reducers.py] and @[backend_v2/services/orchestrator/synthesis_payload_compressor.py] to eliminate dict mutations.</action>
    <action>Emit strongly typed DataStarvationEvent upon missing synthesis payloads.</action>
  </step>

  <validation_gate>
    <action>Run backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/two_pass_atomizer.py --test</action>
  </validation_gate>
</execution_protocol>
```
