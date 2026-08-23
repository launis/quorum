# Phase 7: Polymorphic AnyPromptBlock Discriminated Union & AST Guardrails

**Overview:** Refactor monolithic PromptBlock into strict Pydantic Discriminated Union AnyPromptBlock in backend_v2/models/domain/prompt_blocks.py and Freezed Sealed Class in Flutter, update seed registry with TypeAdapter(AnyPromptBlock), and enforce 10 AST guardrails in test_ast_prompt_xml_sovereignty.py.
**Target Files:**
- `[NEW]` @[backend_v2/models/domain/prompt_blocks.py]
- `[MODIFY]` @[backend_v2/models/v2_core.py#L380-L544]
- `[MODIFY]` @[backend_v2/models/v2_core.py#L461-L544]
- `[MODIFY]` @[backend_v2/seed/seed_registry.py]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/prompt_block.dart]
- `[NEW]` @[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py]

Source: @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md#L274-L364] Phase 7: Polymorphic AnyPromptBlock Discriminated Union & AST Guardrails

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 6. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/models/v2_core.py#L380-L544] and @[client_app_v2/lib/features/studio/models/prompt_block.dart].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `AnyPromptBlock` discriminated union with `MatrixPromptBlock`, `SystemRulePromptBlock`, `PersonaPromptBlock`, `ProtocolPromptBlock` created in [NEW] @[backend_v2/models/domain/prompt_blocks.py].
    - [ ] Monolithic flat `PromptBlock` and runtime duck-typing validator `pre_validate_block_consistency` removed from @[backend_v2/models/v2_core.py#L380-L544] and @[backend_v2/models/v2_core.py#L461-L544].
    - [ ] @[backend_v2/seed/seed_registry.py] maps `prompt_blocks` collection to `TypeAdapter(AnyPromptBlock)`.
    - [ ] Dart `PromptBlock` refactored to sealed union class with `@Freezed(unionKey: 'categoryId', equal: false)` in @[client_app_v2/lib/features/studio/models/prompt_block.dart].
    - [ ] 10 AST tests created in [NEW] @[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py] and passing.
    - [ ] Quality gates pass: `uv run python scripts/backend_audit_loop.py backend_v2/models/domain/prompt_blocks.py --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
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
    <backend>[NEW] @[backend_v2/models/domain/prompt_blocks.py]</backend>
    <backend>@[backend_v2/models/v2_core.py]</backend>
    <backend>@[backend_v2/seed/seed_registry.py]</backend>
    <frontend>@[client_app_v2/lib/features/studio/models/prompt_block.dart]</frontend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT keep flat monolithic PromptBlock with optional fields.
    - Do NOT allow default=None on required MatrixPromptBlock fields.
    - Do NOT allow catch-all unknown union types.
  </anti_targets>

  <step id="1" name="Pydantic Discriminated Union Creation">
    <action>Create [NEW] @[backend_v2/models/domain/prompt_blocks.py] defining `StrictStr`, `PromptBlockBase`, `MatrixPromptBlock`, `SystemRulePromptBlock`, `PersonaPromptBlock`, `ProtocolPromptBlock`, and `AnyPromptBlock` discriminated union.</action>
    <action>Update @[backend_v2/models/v2_core.py#L380-L544]: Re-export polymorphic models and eradicate legacy monolithic `PromptBlock` and `pre_validate_block_consistency` at @[backend_v2/models/v2_core.py#L461-L544].</action>
    <demolish>REMOVE: monolithic `PromptBlock` and `pre_validate_block_consistency` at @[backend_v2/models/v2_core.py#L380-L544] and @[backend_v2/models/v2_core.py#L461-L544]. REPLACE WITH: `AnyPromptBlock` discriminated union.</demolish>
    <action>Update @[backend_v2/seed/seed_registry.py]: Map `"prompt_blocks"` to `TypeAdapter(AnyPromptBlock)`.</action>
  </step>

  <step id="2" name="Flutter Freezed Sealed Class Synchronous Parity">
    <action>Refactor Dart `PromptBlock` in @[client_app_v2/lib/features/studio/models/prompt_block.dart] to Freezed Sealed Class structure using `@Freezed(unionKey: 'categoryId', equal: false) sealed class PromptBlock with _$PromptBlock`.</action>
    <action>Run build runner: `dart run build_runner build --delete-conflicting-outputs`.</action>
  </step>

  <step id="3" name="AST XML Sovereignty Guardrails">
    <action>Create [NEW] @[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py] with 10 static AST tests verifying model configs, discriminator usage, zero reflection calls, zero slug checks, and XML ordering.</action>
  </step>

  <validation_gate>
    <action>Execute AST Guardrails: `uv run pytest backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py`</action>
    <action>Execute Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2/models/domain/prompt_blocks.py --test`</action>
    <action>Execute Flutter Audit Loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build`</action>
  </validation_gate>
</execution_protocol>
```
