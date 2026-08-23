# Phase 6: Layer 1 Global Mandates Injection & Compiler Foundation

**Overview:** Migrate Layer 1 global mandates into base system prompt static caching prefix across PromptFactory and MatrixSensorPromptBuilder, eliminate find_value_by_key reflection loop and hasattr/getattr calls in favor of MechanicalAnchorsPayload DTO, eradicate 7 get fallback chains via ExecutionTimeResolver, and replace localization compiler lazy fallback with Fail-Fast validation.
**Target Files:**
- `[MODIFY]` @[backend_v2/models/prompts/global_mandates.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L39-L290]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L45-L290]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L140-L169]
- `[MODIFY]` @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L18-L207]
- `[MODIFY]` @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L36-L91]
- `[MODIFY]` @[backend_v2/services/orchestrator/localization_compiler.py#L22-L195]
- `[MODIFY]` @[backend_v2/services/orchestrator/localization_compiler.py#L79-L115]

Source: @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md#L251-L273] Phase 6: Layer 1 Global Mandates Injection & Compiler Foundation

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Wave 1 (Phases 1-4). Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L39-L290], @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L18-L207], and @[backend_v2/services/orchestrator/localization_compiler.py#L22-L195].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `GLOBAL_MANDATES_XML` removed from user payload and injected into Layer 1 of `base_system_prompt` static prefix in @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L39-L290].
    - [ ] `GLOBAL_MANDATES_XML` prepended into Layer 1 of static caching prefix in @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L36-L91].
    - [ ] Reflection loop `find_value_by_key` and all `hasattr`/`getattr` calls eradicated from @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L140-L169], replaced by typed `MechanicalAnchorsPayload` model.
    - [ ] Hardcoded slug checks replaced by polymorphic type checking in `prompt_factory.py`.
    - [ ] 7 `.get()` fallback chains for `execution_time` eradicated in prompt_factory.py#L86-L132, replaced by `ExecutionTimeResolver`.
    - [ ] Lazy fallback `LANGUAGE_NAMES.get(..., "English")` in @[backend_v2/services/orchestrator/localization_compiler.py#L79-L115] replaced with Fail-Fast validation.
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
    <backend>@[backend_v2/models/prompts/global_mandates.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py]</backend>
    <backend>@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]</backend>
    <backend>@[backend_v2/services/orchestrator/localization_compiler.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT inject dynamic execution variables into Layer 1 static prefix.
    - Do NOT re-introduce `getattr` or `hasattr` reflection in compiler services.
    - Do NOT use naked dictionary lookups for context data.
  </anti_targets>

  <step id="1" name="Global Mandates Static Prefix Migration">
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L39-L290], remove `GLOBAL_MANDATES_XML` from user payload and inject into Layer 1 of `base_system_prompt` static prefix.</action>
    <action>In @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L36-L91], prepend `GLOBAL_MANDATES_XML.strip()` into Layer 1 of the static caching prefix.</action>
  </step>

  <step id="2" name="Compiler Refactoring &amp; Anti-Pattern Demolition">
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L140-L169], eliminate `find_value_by_key` reflection loop and all `hasattr`/`getattr` calls, replacing with typed `MechanicalAnchorsPayload` Pydantic model.</action>
    <demolish>REMOVE: `find_value_by_key` reflection loop at @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L140-L169]. REPLACE WITH: typed `MechanicalAnchorsPayload`.</demolish>
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L45-L290], eliminate hardcoded slug checks, replacing with polymorphic type checking.</action>
    <action>In prompt_factory.py#L86-L132, eliminate all 7 `.get()` fallback chains and naked dict probing for `execution_time`, replacing with `ExecutionTimeResolver` pure function.</action>
    <demolish>REMOVE: 7 `.get()` fallback chains at prompt_factory.py#L86-L132. REPLACE WITH: `ExecutionTimeResolver`.</demolish>
    <action>In @[backend_v2/services/orchestrator/localization_compiler.py#L79-L115], replace `LANGUAGE_NAMES.get(..., "English")` lazy fallback with Fail-Fast validation raising `AppException(VALIDATION_FAILED)`.</action>
    <demolish>REMOVE: `LANGUAGE_NAMES.get(..., "English")` at @[backend_v2/services/orchestrator/localization_compiler.py#L79-L115]. REPLACE WITH: Fail-Fast `AppException`.</demolish>
  </step>

  <validation_gate>
    <action>Execute Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py --test`</action>
    <action>Execute Localization Compiler Audit: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/localization_compiler.py --test`</action>
  </validation_gate>
</execution_protocol>
```
