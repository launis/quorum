# Phase 1: Cross-Domain DTO Parity, Freezed Code Generation Lock & Pre-Implementation Tech Debt Cleanups (Contract First & Zero Duct-Tape)

**Overview:** Synchronously update Python Pydantic V2 Step and StepRule models and Flutter Dart Freezed StepRule and NodeStrategy (llm and logic union variants) models with `is_system_core` and `is_synthesis_source`. Update SynthesisConfigDTO with matrix explanation overrides, add SYSTEM_PROTECTED_RESOURCE error code, update Settings with synthesis limits, remediate tech debt in SynthesisPayloadCompressor and StudioWorkflowService, lock Freezed code generation, and update unit tests.
**Target Files:**
- `[MODIFY]` @[backend_v2/models/v2_core.py#L712-L801]
- `[MODIFY]` @[backend_v2/models/v2_core.py#L804-L836]
- `[MODIFY]` @[backend_v2/models/v2_core.py#L1073-L1090]
- `[MODIFY]` @[backend_v2/settings.py#L51-L710]
- `[MODIFY]` @[backend_v2/exceptions.py#L99-L277]
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L17-L163]
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L20-L163]
- `[MODIFY]` @[backend_v2/services/studio/workflow_service.py#L448-L479]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/workflow.dart#L54-L116]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/workflow.dart#L54-L62]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/workflow.dart#L76-L116]
- `[MODIFY]` @[client_app_v2/test/features/studio/models/workflow_test.dart]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by previous epics (EPIC 144, EPIC 143). Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/models/v2_core.py#L712-L801], @[backend_v2/settings.py#L51-L710], and @[client_app_v2/lib/features/studio/models/workflow.dart#L54-L116].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `is_system_core: bool = False` added to Python `Step` model in @[backend_v2/models/v2_core.py#L712-L801].
    - [ ] `is_synthesis_source: bool = True` added to Python `StepRule` model in @[backend_v2/models/v2_core.py#L804-L836].
    - [ ] `max_quotes_per_matrix: int | None = None` and `max_unmet_criteria: int | None = None` added to `SynthesisConfigDTO` in @[backend_v2/models/v2_core.py#L1073-L1090].
    - [ ] `SYSTEM_PROTECTED_RESOURCE = "SYSTEM_PROTECTED_RESOURCE"` added to `ErrorCodes` in @[backend_v2/exceptions.py#L99-L277].
    - [ ] `max_synthesis_evaluations: int = 0` (unbounded default) and `max_synthesis_reasoning_length: int = 300` configured in @[backend_v2/settings.py#L51-L710].
    - [ ] `SynthesisPayloadCompressor` tech debt eliminated: replaced `model_copy(update={...})` with `DistilledEvaluation.model_validate()` and replaced magic number `[:300]` with `max_synthesis_reasoning_length` at @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L20-L163].
    - [ ] `StudioWorkflowService.save_step` duck-typing `getattr(data, "organization_id", None)` replaced with direct typed attribute `data.organization_id` at @[backend_v2/services/studio/workflow_service.py#L448-L479].
    - [ ] Dart Freezed models `StepRule` (@[client_app_v2/lib/features/studio/models/workflow.dart#L54-L62]) updated with `isSynthesisSource` (default true) and `NodeStrategy.llm` / `NodeStrategy.logic` (@[client_app_v2/lib/features/studio/models/workflow.dart#L76-L116]) updated with `isSystemCore` (default false).
    - [ ] Freezed code generation executed via `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/workflow.dart --build`.
    - [ ] `workflow_test.dart` updated and passing for new fields and defaults.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_neuro_symbolic_agentic_workflow.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/models/v2_core.py]</backend>
    <backend>@[backend_v2/settings.py]</backend>
    <backend>@[backend_v2/exceptions.py]</backend>
    <backend>@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]</backend>
    <backend>@[backend_v2/services/studio/workflow_service.py]</backend>
    <frontend>@[client_app_v2/lib/features/studio/models/workflow.dart]</frontend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `seed_data.json` in Phase 1 (reserved for Phase 2 Vault Protocol).
    - Do NOT modify `workflow_step_card.dart` or `step_builder_view.dart` UI widgets in Phase 1 (reserved for Phase 4).
    - Do NOT add loose fallback defaults or duck-typing `.get()` access in DTO models.
  </anti_targets>

  <step id="1" name="Pre-Implementation Technical Debt Cleanups">
    <action>In @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L20-L163], eliminate `lite_ev_obj.model_copy(update={...})` shallow copying and replace it with direct Pydantic re-validation: `DistilledEvaluation.model_validate(lite_ev_obj.model_dump(exclude_unset=True) | {"exact_quotes": [q[: settings.max_synthesis_quote_length] for q in valid_quotes], "semantic_reasoning": str(lite_ev_obj.semantic_reasoning)[: max_synthesis_reasoning_length] if lite_ev_obj.semantic_reasoning else None})`.</action>
    <demolish>REMOVE: existing lite_ev_obj.model_copy(update={...}) shallow copy pattern at @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L20-L163]. REPLACE WITH: DistilledEvaluation.model_validate(lite_ev_obj.model_dump(exclude_unset=True) | {...}) direct re-validation.</demolish>
    <demolish>REMOVE: hardcoded magic number [:300] for semantic_reasoning at @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L20-L163]. REPLACE WITH: max_synthesis_reasoning_length setting reference.</demolish>
    <action>In @[backend_v2/services/studio/workflow_service.py#L448-L479], eliminate duck-typing `getattr(data, "organization_id", None)` in `save_step` and replace with direct typed attribute access `data.organization_id`.</action>
    <demolish>REMOVE: getattr(data, "organization_id", None) duck-typing at @[backend_v2/services/studio/workflow_service.py#L448-L479]. REPLACE WITH: data.organization_id typed access.</demolish>
    <action>In @[client_app_v2/lib/features/studio/models/workflow.dart#L54-L116], replace Finnish docstring comment at line 69 with English equivalent: `/// Sealed Classes Mandate: Unknown/Fallback union types are strictly forbidden.`.</action>
    <demolish>REMOVE: Finnish docstring comment '/// Polymorfisille luokille ei sallita Unknown/Fallback -tyyppejä.' at @[client_app_v2/lib/features/studio/models/workflow.dart#L54-L116]. REPLACE WITH: '/// Sealed Classes Mandate: Unknown/Fallback union types are strictly forbidden.'.</demolish>
    <constraint invariant="touched_scope_tech_debt_mandate">All pre-existing technical debt in touched files must be resolved in Phase 1 before new features are added.</constraint>
  </step>

  <step id="2" name="Backend Pydantic Models & Settings Update">
    <action>In @[backend_v2/models/v2_core.py#L712-L801], add `is_system_core: Annotated[bool, Field(description="Whether this step blueprint is a protected system foundational component.")] = False` to `Step` model.</action>
    <action>In @[backend_v2/models/v2_core.py#L804-L836], add `is_synthesis_source: Annotated[bool, Field(description="Whether this step's narrative text output is forwarded to the synthesis LLM context.")] = True` to `StepRule` model.</action>
    <action>In @[backend_v2/models/v2_core.py#L1073-L1090], add `max_quotes_per_matrix: Annotated[int | None, Field(description="Per-profile override for quotes per matrix in explanations.")] = None` and `max_unmet_criteria: Annotated[int | None, Field(description="Per-profile override for unmet criteria per matrix.")] = None` to `SynthesisConfigDTO`.</action>
    <action>In @[backend_v2/exceptions.py#L99-L277], add `SYSTEM_PROTECTED_RESOURCE = "SYSTEM_PROTECTED_RESOURCE"` to `ErrorCodes`.</action>
    <action>In @[backend_v2/settings.py#L51-L710], add `max_synthesis_evaluations: Annotated[int, Field(ge=0, description="Max evaluations for synthesis token shield. Set to 0 for unbounded (no truncation by default).")] = 0` and `max_synthesis_reasoning_length: Annotated[int, Field(description="Maximum character length for semantic reasoning in synthesis payloads")] = 300` to `Settings`.</action>
    <constraint invariant="strict_configuration_segregation">Global limits must be stored in settings.py without magic numbers.</constraint>
  </step>

  <step id="3" name="Frontend Dart Freezed Models & Code Generation Lock">
    <action>In @[client_app_v2/lib/features/studio/models/workflow.dart#L54-L62], add `@Default(true) @JsonKey(name: 'is_synthesis_source') bool isSynthesisSource` to `StepRule` constructor.</action>
    <action>In @[client_app_v2/lib/features/studio/models/workflow.dart#L76-L116], add `@Default(false) @JsonKey(name: 'is_system_core') bool isSystemCore` to BOTH `NodeStrategy.llm` and `NodeStrategy.logic` sealed union variants.</action>
    <action>Run Freezed code generation: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/workflow.dart --build`.</action>
    <constraint invariant="sdui_contract_fracture_prevention">Backend and Frontend DTOs must maintain strict 1:1 cross-domain parity.</constraint>
  </step>

  <step id="4" name="Workflow Model Unit Tests">
    <action>Update @[client_app_v2/test/features/studio/models/workflow_test.dart] to test deserialization of `isSystemCore` and `isSynthesisSource` with defaults and explicit overrides.</action>
    <test_contracts>
      <test name="test_step_rule_deserializes_is_synthesis_source_default_true" category="positive">
        <input>{"id": "sr_1234567890abcdef", "task_blueprint": "sp_1234567890abcdef"}</input>
        <expected>isSynthesisSource == true</expected>
      </test>
      <test name="test_step_rule_deserializes_is_synthesis_source_explicit_false" category="positive">
        <input>{"id": "sr_1234567890abcdef", "task_blueprint": "sp_1234567890abcdef", "is_synthesis_source": false}</input>
        <expected>isSynthesisSource == false</expected>
      </test>
      <test name="test_node_strategy_llm_deserializes_is_system_core_default_false" category="positive">
        <input>{"id": "st_1234567890abcdef", "slug": "test", "name": {"default_locale": "en"}, "type": "llm", "model_strategy": "fast"}</input>
        <expected>isSystemCore == false</expected>
      </test>
      <test name="test_node_strategy_llm_deserializes_is_system_core_explicit_true" category="positive">
        <input>{"id": "st_1234567890abcdef", "slug": "test", "name": {"default_locale": "en"}, "type": "llm", "model_strategy": "fast", "is_system_core": true}</input>
        <expected>isSystemCore == true</expected>
      </test>
      <test name="test_node_strategy_logic_deserializes_is_system_core_explicit_true" category="positive">
        <input>{"id": "st_1234567890abcdef", "slug": "test", "name": {"default_locale": "en"}, "type": "logic", "hook": "my_hook", "is_system_core": true}</input>
        <expected>isSystemCore == true</expected>
      </test>
    </test_contracts>
  </step>

  <validation_gate>
    <action>Execute Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test`</action>
    <action>Execute Frontend Audit Loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/workflow.dart --test`</action>
    <action>Execute Workflow Model Test: `uv run flutter test client_app_v2/test/features/studio/models/workflow_test.dart`</action>
  </validation_gate>
</execution_protocol>
```
