# Phase 8: Clean Stack Compiler Layer Assembly

**Overview:** Update PromptFactory, LocalizationCompiler, SimulationService, and MatrixSensorPromptBuilder to use pattern matching across polymorphic AnyPromptBlock variants, assembling deterministic Zero-XML fields into strict XML hierarchies.
**Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L45-L290]
- `[MODIFY]` @[backend_v2/services/orchestrator/localization_compiler.py#L79-L115]
- `[MODIFY]` @[backend_v2/services/studio/simulation_service.py#L140-L195]
- `[MODIFY]` @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L36-L91]

Source: @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md#L365-L371] Phase 8: Clean Stack Compiler Layer Assembly

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 7. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L45-L290], @[backend_v2/services/orchestrator/localization_compiler.py#L79-L115], @[backend_v2/services/studio/simulation_service.py#L140-L195], and @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L36-L91].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `prompt_factory.py` dispatches polymorphic blocks via `match block:` to extract discrete instruction fields.
    - [ ] `localization_compiler.py` dispatches polymorphic blocks via `match block:` to extract discrete instruction fields.
    - [ ] `simulation_service.py` dispatches polymorphic blocks via `match data:` to extract discrete instruction fields without accessing `ai_description`.
    - [ ] `matrix_sensor_prompt_builder.py` compiles `objective`, `evaluation_rules`, and `banned_concepts` with XML wrappers and formats `theory_context`.
    - [ ] Quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py --test`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_matrix_boolean_evaluation_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_synthesis_payload_compression.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_pipeline.md]</knowledge_item>
    <knowledge_item>@[ki_strict_sdui_serialization.md]</knowledge_item>
    <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_adapter_pattern.md]</knowledge_item>
    <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py]</backend>
    <backend>@[backend_v2/services/orchestrator/localization_compiler.py]</backend>
    <backend>@[backend_v2/services/studio/simulation_service.py]</backend>
    <backend>@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT access non-existent `ai_description` on polymorphic sub-models.
    - Do NOT include `source_url` inside prompt context XML.
  </anti_targets>

  <step id="1" name="Polymorphic Compiler Dispatch Implementation">
    <action>Update @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L45-L290]: Replace `execution_persona_block.ai_description`, `role_block.ai_description`, and `protocol_block.ai_description` with polymorphic dispatch via `match block:`.</action>
    <action>Update @[backend_v2/services/orchestrator/localization_compiler.py#L79-L115]: Replace `block.ai_description` with polymorphic dispatch via `match block:`.</action>
    <action>Update @[backend_v2/services/studio/simulation_service.py#L140-L195]: Replace `data.ai_description or ""` with polymorphic dispatch via `match data:` to extract discrete instruction fields.</action>
    <action>Update @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L36-L91] to compile matrix `objective`, `evaluation_rules`, and `banned_concepts` with XML wrappers and wrap `theory_grounding.citation_reference` into `<theory_context>`.</action>
  </step>

  <validation_gate>
    <action>Execute Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py --test`</action>
    <action>Execute Simulation Service Audit: `uv run python scripts/backend_audit_loop.py backend_v2/services/studio/simulation_service.py --test`</action>
  </validation_gate>
</execution_protocol>
```
